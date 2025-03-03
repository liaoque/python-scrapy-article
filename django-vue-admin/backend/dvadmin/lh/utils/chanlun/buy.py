import pandas as pd


def detect_breakthrough_signal(kline_df, pivot, confirmation_count=3):
    """
    检测中枢突破信号

    参数：
      kline_df: pd.DataFrame，最新的K线数据，要求至少包含'close'列，按时间升序排列
      pivot: dict，最后一个有效中枢信息，包含 'L_pivot'（中枢下界）和 'H_pivot'（中枢上界）
      confirmation_count: int，用于确认突破的连续K线数量（默认3根）

    返回：
      dict，包含可能的突破信号：
        'bullish_breakthrough': True 表示看多（买入）信号
        'bearish_breakthrough': True 表示看空（卖出）信号
    """
    signals = {}
    recent = kline_df.tail(confirmation_count)
    if recent.empty:
        return signals

    # 看多突破信号：最新确认K线的收盘价均高于中枢上界
    if (recent['close'] > pivot['H_pivot']).all():
        signals['bullish_breakthrough'] = True

    # 看空突破信号：最新确认K线的收盘价均低于中枢下界
    if (recent['close'] < pivot['L_pivot']).all():
        signals['bearish_breakthrough'] = True

    return signals


def detect_divergence_signal(bi_list):
    """
    检测背驰信号（Divergence Signal）

    参数：
      bi_list: list，包含构造好的“笔”，每个笔为字典，至少包含：
               'start_value', 'end_value', 'direction'
               其中价格区间统一定义为：[min(start_value, end_value), max(start_value, end_value)]

    返回：
      dict，包含可能的背驰信号：
         'bullish_divergence': True 表示看多背驰（买入）信号
         'bearish_divergence': True 表示看空背驰（卖出）信号
    """
    signals = {}

    # 分离上升笔与下降笔
    upward_pens = [pen for pen in bi_list if pen.get('direction') == 'up']
    downward_pens = [pen for pen in bi_list if pen.get('direction') == 'down']

    # 看多背驰：适用于下降趋势中出现的上升笔
    # 要求当前上升笔低点抬高（L_curr > L_prev），但高点未能创新高（H_curr < H_prev）
    if len(upward_pens) >= 2:
        pen_prev = upward_pens[-2]
        pen_curr = upward_pens[-1]
        L_prev = min(pen_prev['start_value'], pen_prev['end_value'])
        H_prev = max(pen_prev['start_value'], pen_prev['end_value'])
        L_curr = min(pen_curr['start_value'], pen_curr['end_value'])
        H_curr = max(pen_curr['start_value'], pen_curr['end_value'])
        if (L_curr > L_prev) and (H_curr < H_prev):
            signals['bullish_divergence'] = True

    # 看空背驰：适用于上升趋势中出现的下降笔
    # 要求当前下降笔高点降低（H_curr < H_prev），但低点未创新低（L_curr > L_prev）
    if len(downward_pens) >= 2:
        pen_prev = downward_pens[-2]
        pen_curr = downward_pens[-1]
        L_prev = min(pen_prev['start_value'], pen_prev['end_value'])
        H_prev = max(pen_prev['start_value'], pen_prev['end_value'])
        L_curr = min(pen_curr['start_value'], pen_curr['end_value'])
        H_curr = max(pen_curr['start_value'], pen_curr['end_value'])
        if (H_curr < H_prev) and (L_curr > L_prev):
            signals['bearish_divergence'] = True

    return signals


def generate_trading_signals(kline_df, pivots, bi_list, confirmation_count=3):
    """
    根据中枢突破和背驰两个条件生成买卖点信号

    参数：
      kline_df: pd.DataFrame，最新的K线数据
      pivots: list，已识别的中枢列表（按照时间顺序排列）
      bi_list: list，已构造的笔列表
      confirmation_count: int，用于中枢突破信号确认的K线数量（默认3根）

    返回：
      dict，包含检测到的信号。可能的信号有：
         'bullish_breakthrough', 'bearish_breakthrough',
         'bullish_divergence', 'bearish_divergence'
    """
    signals = {}

    # 1. 中枢突破信号：以最后一个有效中枢作为参考
    if pivots:
        last_pivot = pivots[-1]
        pivot_signals = detect_breakthrough_signal(kline_df, last_pivot, confirmation_count=confirmation_count)
        signals.update(pivot_signals)

    # 2. 背驰信号
    divergence_signals = detect_divergence_signal(bi_list)
    signals.update(divergence_signals)

    return signals


# ----------------------------
# 示例：利用模拟数据演示信号检测
if __name__ == '__main__':
    # 模拟部分K线数据（实际数据应为从行情接口获取的A股K线数据）
    dates = pd.date_range(start='2022-01-01', periods=10, freq='D')
    data = {
        'date': dates,
        'open': [100, 102, 105, 107, 110, 112, 115, 117, 120, 122],
        'high': [102, 105, 107, 110, 112, 115, 117, 120, 122, 125],
        'low': [98, 100, 103, 105, 108, 110, 113, 115, 118, 120],
        'close': [101, 104, 106, 109, 111, 114, 116, 119, 121, 124]
    }
    kline_df = pd.DataFrame(data).set_index('date')

    # 假设已识别的中枢（示例数据）
    pivots = [{
        'start_index': dates[1],
        'end_index': dates[5],
        'L_pivot': 105,  # 假设中枢下界
        'H_pivot': 115,  # 假设中枢上界
        'strokes': None,
        'stroke_count': 3
    }]

    # 假设已构造的笔（bi）数据，示例中包含几段上升和下降笔
    bi_list = [
        {'start_index': dates[0], 'end_index': dates[1], 'start_value': 100, 'end_value': 104, 'direction': 'up'},
        {'start_index': dates[1], 'end_index': dates[2], 'start_value': 104, 'end_value': 106, 'direction': 'up'},
        {'start_index': dates[2], 'end_index': dates[3], 'start_value': 106, 'end_value': 109, 'direction': 'up'},
        {'start_index': dates[3], 'end_index': dates[4], 'start_value': 109, 'end_value': 107, 'direction': 'down'},
        {'start_index': dates[4], 'end_index': dates[5], 'start_value': 107, 'end_value': 111, 'direction': 'up'},
        {'start_index': dates[5], 'end_index': dates[6], 'start_value': 111, 'end_value': 110, 'direction': 'down'},
    ]

    # 检测信号
    signals = generate_trading_signals(kline_df, pivots, bi_list, confirmation_count=3)
    print("检测到的交易信号：")
    print(signals)
