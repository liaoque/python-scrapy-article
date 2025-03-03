def construct_zhongshu(bi_list, min_strokes=3):
    """
    根据连续的笔构造中枢。

    参数：
      bi_list: list，包含已构造好的笔，每一笔为一个字典，至少包含字段：
               'start_index', 'end_index', 'start_value', 'end_value'
      min_strokes: int，构成有效中枢所需的最小笔数（默认3笔）

    返回：
      List，每个元素是一个字典，描述一个有效中枢，包含：
          - start_index: 中枢起始笔的起始时刻/序号
          - end_index: 中枢结束笔的结束时刻/序号
          - L_pivot: 中枢价格区间下界
          - H_pivot: 中枢价格区间上界
          - strokes: 参与构成中枢的笔列表
          - stroke_count: 中枢包含的笔数量
    """
    pivots = []
    n = len(bi_list)
    i = 0
    while i < n - 1:
        # 用bi_list[i]和bi_list[i+1]构造候选中枢
        # 计算第i笔的价格区间
        bi_i = bi_list[i]
        L_i = min(bi_i['start_value'], bi_i['end_value'])
        H_i = max(bi_i['start_value'], bi_i['end_value'])

        # 如果没有后续笔，则退出
        if i + 1 >= n:
            break

        bi_next = bi_list[i + 1]
        L_next = min(bi_next['start_value'], bi_next['end_value'])
        H_next = max(bi_next['start_value'], bi_next['end_value'])

        # 初步候选中枢的交集
        candidate_L = max(L_i, L_next)
        candidate_H = min(H_i, H_next)

        # 如果前两笔没有交集，则无法构成中枢，从下一笔重新开始
        if candidate_L > candidate_H:
            i += 1
            continue

        # 初始化候选中枢所包含的笔
        candidate_strokes = [bi_i, bi_next]
        j = i + 2  # 从下一笔开始尝试扩展候选中枢

        # 依次加入后续的笔，更新候选中枢区间
        while j < n:
            bi_j = bi_list[j]
            L_j = min(bi_j['start_value'], bi_j['end_value'])
            H_j = max(bi_j['start_value'], bi_j['end_value'])
            # 更新候选区间
            new_candidate_L = max(candidate_L, L_j)
            new_candidate_H = min(candidate_H, H_j)
            if new_candidate_L <= new_candidate_H:
                # 加入当前笔后候选区间仍存在交集，更新候选区间，并保存该笔
                candidate_L, candidate_H = new_candidate_L, new_candidate_H
                candidate_strokes.append(bi_j)
                j += 1
            else:
                # 当前笔使候选中枢失效，退出扩展
                break

        # 检查候选中枢笔数是否满足要求
        if len(candidate_strokes) >= min_strokes:
            # 根据公式，理论上中枢价格区间也可重新计算为：
            # L_pivot = max(L_i, L_{i+1}, ..., L_{i+m-1})
            # H_pivot = min(H_i, H_{i+1}, ..., H_{i+m-1})
            # 此处 candidate_L, candidate_H 已是交集结果
            pivot = {
                'start_index': candidate_strokes[0]['start_index'],
                'end_index': candidate_strokes[-1]['end_index'],
                'L_pivot': candidate_L,
                'H_pivot': candidate_H,
                'strokes': candidate_strokes,
                'stroke_count': len(candidate_strokes)
            }
            pivots.append(pivot)
        # 以当前导致候选中枢失效的那一笔作为新的起点，继续识别
        i = j
    return pivots


# ----------------------------
# 示例：利用前面构造的“笔”数据进行中枢识别
if __name__ == '__main__':
    # 假设已有构造好的笔列表（bi_list）
    # 这里构造一个简单示例，模拟若干“笔”
    bi_list = [
        {'start_index': '2022-01-01', 'end_index': '2022-01-02', 'start_value': 100, 'end_value': 110,
         'direction': 'up'},
        {'start_index': '2022-01-02', 'end_index': '2022-01-03', 'start_value': 110, 'end_value': 105,
         'direction': 'down'},
        {'start_index': '2022-01-03', 'end_index': '2022-01-04', 'start_value': 105, 'end_value': 115,
         'direction': 'up'},
        {'start_index': '2022-01-04', 'end_index': '2022-01-05', 'start_value': 115, 'end_value': 112,
         'direction': 'down'},
        {'start_index': '2022-01-05', 'end_index': '2022-01-06', 'start_value': 112, 'end_value': 118,
         'direction': 'up'},
        # 可根据实际情况增加更多笔数据
    ]

    pivots = construct_zhongshu(bi_list, min_strokes=3)
    print("识别出的中枢：")
    for pivot in pivots:
        print(pivot)
