import json
import os

comp_id = "6734520"

filter_concept = ["分拆上市意愿", "人民币贬值受益", "富时罗素概念", "富时罗素概念股", "标普道琼斯A股", "沪股通", "深股通", "融资融券", "转融券标的", "再融资", "送转填权",
                  "股权转让","核准制次新股",
                  "并购重组", "超跌", "MSCI概念", "一季报增长", "一季报预增", "业绩增长", "年报增长", "超跌", "央企国企改革", "地方国企改革", "三季报增长", "半年报预增",
                  "中报增长",
                  "山东国企改革", "上海国企改革", "江苏国企改革", "深圳国企改革", "重庆国企改革", "广东国企改革", "北京国企改革", "天津国企改革", "甘肃国企改革", "河南国企改革",
                  "山西国企改革", "辽宁国企改革", "大连自贸区", "摘帽", "振兴东北", "东北亚经贸中心",
                  "浙江国企改革", "珠海国企改革", "四川国企改革", "上海", "深圳", "浙江", "湖南", "武汉", "海南", "科创板", "年报预增", "三季报预增", "证金持股",
                  "行业龙头", "新股与次新股", "注册制次新股",
                  "参股新三板", "同花顺漂亮100"]


def toCode(codes2):
    codes = []
    for item in codes2:
        code = item.get("股票代码", "")
        name = item.get("股票简称", "")
        type_ = item.get("股票市场类型", "")
        if type_ is not None:
            type_ = type_.split(";")

        industry = item.get("所属同花顺行业", "")
        if industry is not None:
            industry = industry.split("-")[-1:]

        concept = item.get("所属概念", "")
        if concept is not None:
            concept = concept.split(";")
            concept = [x for x in concept if x not in filter_concept]

        full = 0
        for key in item:
            if key.find("区间涨跌幅:", 0, len(key)) != -1:
                full = item.get(key, "")
                break
     
        jingjia = 0
        for key in item:
            if key.find("竞价未匹配金额", 0, len(key)) != -1:
                jingjia = item.get(key, "")
                break

        codes.append({
            "code": code,
            "name": name,
            "type": type_,
            "industry": industry,
            "concept": concept,
            "full": full,
            "jingjia": jingjia,
        })
    return codes


def toString(codes):
    cc = [item["code"][0:6] for item in codes]
    return "\",\"".join(cc)


def read_json_file(file_path):
    if not os.path.exists(file_path):  # 检测文件是否存在
        with open(file_path, 'w', encoding='utf-8') as new_file:
            json.dump({}, new_file)  # 创建一个新的空JSON文件，初始内容为一个空字典

    with open(file_path, 'r+', encoding='utf-8') as file:
        data = json.load(file)
    return data


def write_json_file(file_path, data):
    with open(file_path, 'w+', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_previous_key_value(d, target_key):
    # 对字典的键进行排序
    sorted_keys = sorted(d.keys())
    
    # 获取目标键的索引
    target_index = sorted_keys.index(target_key)
    
    # 如果目标键是第一个键，则没有前一个键
    if target_index == 0:
        return None
    
    # 获取前一个键，并返回其值
    previous_key = sorted_keys[target_index - 1]
    return d[previous_key]
