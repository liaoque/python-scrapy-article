import pandas as pd
import numpy as np


def sma(series, window=5):
    """
    简单移动平均平滑数据
    :param series: pd.Series 数据序列
    :param window: int 平均窗口大小
    :return: pd.Series 平滑后的序列
    """
    return series.rolling(window=window, min_periods=1).mean()


def detect_local_extrema(series, window=3):
    """
    利用滑动窗口检测局部极值（局部高点和低点）
    :param series: pd.Series 要检测的价格序列（如收盘价或平滑后的序列）
    :param window: int 前后对比的数据点数
    :return: list 包含局部极值的字典，格式为 { 'index': 索引, 'type': 'high'/'low', 'value': 价格 }
    """
    extrema = []
    # 遍历数据，注意边界需要留足 window 个数据
    for i in range(window, len(series) - window):
        current = series.iloc[i]
        prev = series.iloc[i - window:i]
        nxt = series.iloc[i + 1:i + window + 1]
        # 判断局部高点：当前点大于前后所有点
        if current > prev.max() and current > nxt.max():
            extrema.append({'index': series.index[i], 'type': 'high', 'value': current})
        # 判断局部低点：当前点小于前后所有点
        elif current < prev.min() and current < nxt.min():
            extrema.append({'index': series.index[i], 'type': 'low', 'value': current})
    return extrema


def compute_atr(df, period=14):
    """
    计算ATR（平均真实波幅）
    :param df: 包含 'high', 'low', 'close' 列的 DataFrame
    :param period: ATR计算周期
    :return: pd.Series ATR序列
    """
    high = df['high']
    low = df['low']
    close = df['close']
    prev_close = close.shift(1)
    tr = pd.concat([high - low,
                    (high - prev_close).abs(),
                    (low - prev_close).abs()], axis=1).max(axis=1)
    atr = tr.rolling(window=period, min_periods=1).mean()
    return atr


def filter_extrema(extrema, series, threshold_percentage=0.03, atr_series=None, atr_multiplier=1.0):
    """
    对初步检测到的局部极值进行噪音过滤，要求两极值之间的价格变动达到一定幅度。
    :param extrema: list 局部极值列表
    :param series: pd.Series 用于计算价格变动（如平滑后的价格序列）
    :param threshold_percentage: float 固定百分比阈值（如0.03 表示3%）
    :param atr_series: dict 可选，映射索引到 ATR 值，用于动态阈值
    :param atr_multiplier: float ATR 阈值倍数
    :return: list 过滤后的局部极值列表
    """
    if not extrema:
        return []

    filtered = [extrema[0]]  # 保留第一个极值作为起点
    last_value = extrema[0]['value']

    for ext in extrema[1:]:
        # 计算当前极值与上一个确认极值之间的百分比变化
        price_change = abs(ext['value'] - last_value) / last_value
        if atr_series is not None:
            # 利用 ATR 动态设置阈值，ATR值从 atr_series 字典中获取
            atr_value = atr_series.get(ext['index'], np.nan)
            # 动态阈值计算（这里简单地将 ATR 除以当前价格再乘以倍数）
            dynamic_threshold = atr_multiplier * (atr_value / last_value)
            if price_change >= dynamic_threshold:
                filtered.append(ext)
                last_value = ext['value']
        else:
            if price_change >= threshold_percentage:
                filtered.append(ext)
                last_value = ext['value']
    return filtered


def construct_bi(extrema):
    """
    根据过滤后的局部极值构造“笔”，确保极值交替出现（低点-高点或高点-低点）
    :param extrema: list 过滤后的局部极值列表（顺序按时间排列）
    :return: list 每一笔用一个字典表示，包含起止点和方向信息
    """
    if not extrema:
        return []

    # 先调整相邻的极值类型相同的情况，保留更极端的那一个
    filtered_extrema = [extrema[0]]
    for ext in extrema[1:]:
        # 如果当前极值和上一个极值类型相同，则判断哪一个更极端
        if ext['type'] == filtered_extrema[-1]['type']:
            if ext['type'] == 'high' and ext['value'] > filtered_extrema[-1]['value']:
                filtered_extrema[-1] = ext
            elif ext['type'] == 'low' and ext['value'] < filtered_extrema[-1]['value']:
                filtered_extrema[-1] = ext
        else:
            filtered_extrema.append(ext)

    # 构造“笔”，两两极值构成一笔，记录起点、终点及方向
    bi_list = []
    for i in range(len(filtered_extrema) - 1):
        start = filtered_extrema[i]
        end = filtered_extrema[i + 1]
        # 根据极值类型判断方向（低到高为上升笔，高到低为下降笔）
        if start['type'] == 'low' and end['type'] == 'high':
            direction = 'up'
        elif start['type'] == 'high' and end['type'] == 'low':
            direction = 'down'
        else:
            # 如果连续两个极值类型不符合交替要求，则忽略（一般不会出现这种情况）
            continue
        bi = {
            'start_index': start['index'],
            'start_value': start['value'],
            'end_index': end['index'],
            'end_value': end['value'],
            'direction': direction
        }
        bi_list.append(bi)
    return bi_list


def bi(df):

    # 对收盘价做平滑处理
    df['close_sma'] = sma(df['close'], window=5)

    # 计算ATR（这里用14日周期）
    df['atr'] = compute_atr(df, period=14)

    # 1. 检测局部极值（以平滑后的收盘价为例）
    extrema = detect_local_extrema(df['close_sma'], window=3)
    # print("检测到的局部极值:")
    # for ext in extrema:
    #     print(ext)

    # 2. 利用固定百分比阈值或ATR动态阈值过滤噪音（示例使用ATR）
    atr_series = df['atr'].to_dict()  # 将ATR转换为字典，便于按索引取值
    filtered_extrema = filter_extrema(extrema, df['close_sma'], threshold_percentage=0.03,
                                      atr_series=atr_series, atr_multiplier=1.0)

    # print("\n过滤后的局部极值:")
    # for ext in filtered_extrema:
    #     print(ext)

    # 3. 构造“笔”
    bi_list = construct_bi(filtered_extrema)
    # print("\n构造的'笔':")
    # for bi in bi_list:
    #     print(bi)

    return bi_list

# ----------------------------
# 示例：模拟数据并验证各个模块
if __name__ == '__main__':
    # 生成示例数据：模拟随机游走序列作为价格数据
    dates = pd.date_range(start='2022-01-01', periods=100, freq='D')
    np.random.seed(42)
    prices = np.cumsum(np.random.randn(100)) + 100  # 随机游走
    # 构造简单的K线数据，注意这里只是示例
    df = pd.DataFrame({
        'date': dates,
        'open': prices + np.random.randn(100) * 0.5,
        'high': prices + np.random.rand(100) * 2,
        'low': prices - np.random.rand(100) * 2,
        'close': prices + np.random.randn(100) * 0.5
    })
    df.set_index('date', inplace=True)

    # 对收盘价做平滑处理
    df['close_sma'] = sma(df['close'], window=5)

    # 计算ATR（这里用14日周期）
    df['atr'] = compute_atr(df, period=14)

    # 1. 检测局部极值（以平滑后的收盘价为例）
    extrema = detect_local_extrema(df['close_sma'], window=3)
    print("检测到的局部极值:")
    for ext in extrema:
        print(ext)

    # 2. 利用固定百分比阈值或ATR动态阈值过滤噪音（示例使用ATR）
    atr_series = df['atr'].to_dict()  # 将ATR转换为字典，便于按索引取值
    filtered_extrema = filter_extrema(extrema, df['close_sma'], threshold_percentage=0.03,
                                      atr_series=atr_series, atr_multiplier=1.0)
    print("\n过滤后的局部极值:")
    for ext in filtered_extrema:
        print(ext)

    # 3. 构造“笔”
    bi_list = construct_bi(filtered_extrema)
    print("\n构造的'笔':")
    for bi in bi_list:
        print(bi)
