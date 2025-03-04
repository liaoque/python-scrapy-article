import pandas as pd

def detect_breakthrough_signal(kline_df, pivot, confirmation_count=3):
    """
    检测中枢突破信号，返回带价格和时间的信号数组
    """
    signals = []
    recent = kline_df.tail(confirmation_count)
    if recent.empty:
        return signals

    # 最近K线的最后一个收盘价
    final_close = recent['close'].iloc[-1]
    final_date = recent.index[-1].strftime('%Y-%m-%d')

    # 看多突破
    if (recent['close'] > pivot['H_pivot']).all():
        signals.append({
            'time': final_date,
            'price': final_close,
            'type': 'buy',
            'reason': '突破中枢'
        })

    # 看空突破
    if (recent['close'] < pivot['L_pivot']).all():
        signals.append({
            'time': final_date,
            'price': final_close,
            'type': 'sell',
            'reason': '突破中枢'
        })

    return signals

def detect_divergence_signal(bi_list):
    """
    检测背驰信号，返回带价格和时间的信号数组
    """
    signals = []

    # 上升背驰检测
    upward_pens = [pen for pen in bi_list if pen['direction'] == 'up']
    if len(upward_pens) >= 2:
        prev, curr = upward_pens[-2], upward_pens[-1]
        if (min(curr['start_value'], curr['end_value']) > min(prev['start_value'], prev['end_value']) and
            max(curr['start_value'], curr['end_value']) < max(prev['start_value'], prev['end_value'])):
            signals.append({
                'time': curr['end_index'].strftime('%Y-%m-%d'),
                'price': curr['end_value'],
                'type': 'buy',
                'reason': '上升背驰'
            })

    # 下降背驰检测
    downward_pens = [pen for pen in bi_list if pen['direction'] == 'down']
    if len(downward_pens) >= 2:
        prev, curr = downward_pens[-2], downward_pens[-1]
        if (max(curr['start_value'], curr['end_value']) < max(prev['start_value'], prev['end_value']) and
            min(curr['start_value'], curr['end_value']) > min(prev['start_value'], prev['end_value'])):
            signals.append({
                'time': curr['end_index'].strftime('%Y-%m-%d'),
                'price': curr['end_value'],
                'type': 'sell',
                'reason': '下降背驰'
            })

    return signals

def generate_trading_signals(kline_df, pivots, bi_list, confirmation_count=3):
    """
    生成所有买卖点信号（带价格和时间）

    返回:
        signals: list，格式：
        [
            {'time': '2022-01-08', 'price': 115, 'type': 'buy', 'reason': '突破中枢'},
            {'time': '2022-01-09', 'price': 112, 'type': 'sell', 'reason': '下降背驰'}
        ]
    """
    all_signals = []

    if pivots:
        last_pivot = pivots[-1]
        breakthrough_signals = detect_breakthrough_signal(kline_df, last_pivot, confirmation_count)
        all_signals.extend(breakthrough_signals)

    divergence_signals = detect_divergence_signal(bi_list)
    all_signals.extend(divergence_signals)

    return all_signals

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
