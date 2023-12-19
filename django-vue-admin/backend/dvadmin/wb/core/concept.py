from dvadmin.wb.config import code_config

# concept2 = [
#     "富时罗素概念", "富时罗素概念股", "标普道琼斯A股", "沪股通", "深股通", "融资融券", "转融券标的", "送转填权",
#     "股权转让", "并购重组", "超跌", "MSCI概念", "一季报增长", "业绩增长", "年报增长", "超跌"
# ]


def filter1(data):
    data = [s.strip() for s in data]
    xia_xian = code_config.CodeConfig().getCodeConfig()
    concept = xia_xian['gvgn']
    a = [x for x in data if x not in concept and x != ""]
    return a


# def filter2(data):
#     data = [s.strip() for s in data]
#     return [x for x in data if x not in concept2 and x != ""]


