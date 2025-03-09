import pandas as pd
import numpy as np
import talib

def detect_breakthrough_signal(kline_df, pivot, confirmation_count=3, min_breakthrough_ratio=0.005):
    signals = []
    recent = kline_df.tail(confirmation_count)
    if recent.empty:
        return signals

    final_close = recent['close'].iloc[-1]
    final_date = recent.index[-1]

    # 看多突破 (增加突破幅度要求)
    if (recent['close'] > pivot['H_pivot']).all() and \
       (final_close - pivot['H_pivot']) / pivot['H_pivot'] >= min_breakthrough_ratio:
        signals.append({
            'time': final_date,
            'price': final_close,
            'type': 'buy',
            'reason': '突破中枢(增强版)'
        })

    # 看空突破 (增加突破幅度要求)
    if (recent['close'] < pivot['L_pivot']).all() and \
       (pivot['L_pivot'] - final_close) / pivot['L_pivot'] >= min_breakthrough_ratio:
        signals.append({
            'time': final_date,
            'price': final_close,
            'type': 'sell',
            'reason': '突破中枢(增强版)'
        })

    return signals


def detect_divergence_signal(bi_list, kline_df):
    signals = []

    # 计算MACD（TA-Lib示例）
    kline_df['macd'], kline_df['macd_signal'], kline_df['macd_hist'] = talib.MACD(kline_df['close'])

    # 上升背驰（加入MACD确认）
    upward_pens = [pen for pen in bi_list if pen['direction'] == 'up']
    if len(upward_pens) >= 2:
        prev, curr = upward_pens[-2], upward_pens[-1]
        L_prev, H_prev = min(prev['start_value'], prev['end_value']), max(prev['start_value'], prev['end_value'])
        L_curr, H_curr = min(curr['start_value'], curr['end_value']), max(curr['start_value'], curr['end_value'])

        # 背驰条件
        if L_curr > L_prev and H_curr < H_prev:
            # MACD确认（动能减弱）
            if kline_df.loc[curr['end_index'], 'macd_hist'] < kline_df.loc[prev['end_index'], 'macd_hist']:
                signals.append({
                    'time': curr['end_index'],
                    'price': curr['end_value'],
                    'type': 'buy',
                    'reason': '上升背驰(MACD确认)'
                })

    # 下降背驰（MACD辅助）
    downward_pens = [pen for pen in bi_list if pen['direction'] == 'down']
    if len(downward_pens) >= 2:
        prev, curr = downward_pens[-2], downward_pens[-1]
        L_prev, H_prev = min(prev['start_value'], prev['end_value']), max(prev['start_value'], prev['end_value'])
        L_curr, H_curr = min(curr['start_value'], curr['end_value']), max(curr['start_value'], curr['end_value'])

        if H_curr < H_prev and L_curr > L_prev:
            # MACD确认（动能减弱）
            if kline_df.loc[curr['end_index'], 'macd_hist'] > kline_df.loc[prev['end_index'], 'macd_hist']:
                signals.append({
                    'time': curr['end_index'],
                    'price': curr['end_value'],
                    'type': 'sell',
                    'reason': '下降背驰(MACD确认)'
                })

    return signals

def generate_trading_signals(kline_df, pivots, bi_list, confirmation_count=3, min_breakthrough_ratio=0.005):
    all_signals = []

    if pivots:
        last_pivot = pivots[-1]
        breakthrough_signals = detect_breakthrough_signal(
            kline_df, last_pivot, confirmation_count, min_breakthrough_ratio)
        all_signals.extend(breakthrough_signals)

    divergence_signals = detect_divergence_signal(bi_list, kline_df)
    all_signals.extend(divergence_signals)

    return all_signals



def convert_30m_signal_to_daily(signal):
    daily_pivots = []
    for zs in signal:
        start_date = zs['time'][:10]
        daily_pivots.append({
            'time': start_date,
            'type': zs['type'],
            'reason': zs['reason'],
            'price': round(zs['price'], 3),
        })
    return daily_pivots

# ----------------------------
# 示例数据和演示（可以直接运行）

if __name__ == '__main__':
    # 示例K线数据
    dates = pd.date_range(start='2022-01-01', periods=10, freq='D')
    kline_data = {
        'date': dates,
        'open': [100, 102, 105, 107, 110, 112, 115, 117, 120, 122],
        'high': [102, 105, 107, 110, 112, 115, 117, 120, 122, 125],
        'low': [98, 100, 103, 105, 108, 110, 113, 115, 118, 120],
        'close': [101, 104, 106, 109, 111, 114, 116, 119, 121, 124]
    }
    kline_df = pd.DataFrame(kline_data).set_index('date')
    # print(kline_df.index[-1])
    # 示例中枢
    pivots = [{
        'start_index': dates[1],
        'end_index': dates[5],
        'L_pivot': 105,
        'H_pivot': 115,
        'strokes': None,
        'stroke_count': 3
    }]

    # 示例笔
    bi_list = [
        {'start_index': dates[0], 'end_index': dates[1], 'start_value': 100, 'end_value': 104, 'direction': 'up'},
        {'start_index': dates[1], 'end_index': dates[2], 'start_value': 104, 'end_value': 106, 'direction': 'up'},
        {'start_index': dates[2], 'end_index': dates[3], 'start_value': 106, 'end_value': 109, 'direction': 'up'},
        {'start_index': dates[3], 'end_index': dates[4], 'start_value': 109, 'end_value': 107, 'direction': 'down'},
        {'start_index': dates[4], 'end_index': dates[5], 'start_value': 107, 'end_value': 111, 'direction': 'up'},
        {'start_index': dates[5], 'end_index': dates[6], 'start_value': 111, 'end_value': 110, 'direction': 'down'},
    ]

    # 生成信号
    signals = generate_trading_signals(kline_df, pivots, bi_list)

    print("\n--- 生成的买卖点信号 ---")
    for s in signals:
        print(s)
