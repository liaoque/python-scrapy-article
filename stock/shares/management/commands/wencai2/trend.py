import requests
import shares.management.commands.wencai2.common


def trendFirst(today):
    s = '%s去除ST，去除北交所，%s去除新股，所属行业，所属概念，%s 9:25的开盘价=%s 9:25的涨停价，%s竞价未匹配大于0，%s竞价未匹配金额，%s涨跌幅降序，5日涨跌幅' % (
        today, today, today, today, today, today, today,
    )
    print(s)
    # s = "半年报预增，所属概念，s去除ST，去除北交所，去除新股"
    url = 'http://www.iwencai.com/gateway/urp/v7/landing/getDataList'
    data = {
        'business_cat': 'soniu',
        'comp_id': shares.management.commands.wencai2.common.comp_id,
        'page': '1',
        'perpage': '100',
        'query': s,
        'uuid': '24087'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.post(url, data=data, headers=headers)
    # print(response.json()["answer"]["components"][0]['data']["datas"])
    codes2 = response.json()["answer"]["components"][0]["data"]["datas"]

    codes = shares.management.commands.wencai2.common.toCode(codes2)

    return codes


def trendNight(today, filter_concept=True):
    s = '%s去除ST，%s去除北交所，%s去除新股，所属行业，所属概念，%s收盘价=%s涨停价，%s涨停封单额，%s首次涨停时间，%s涨停封板时长，%s涨停价成交量*收盘价，%s涨停类型，%s竞价涨幅降序，5日涨跌幅降序' % (
        today, today, today, today, today, today, today, today, today, today, today
    )
    print(s)
    # s = "半年报预增，所属概念，s去除ST，去除北交所，去除新股"
    url = 'http://www.iwencai.com/gateway/urp/v7/landing/getDataList'
    data = {
        'business_cat': 'soniu',
        'comp_id': shares.management.commands.wencai2.common.comp_id,
        'page': '1',
        'perpage': '100',
        'query': s,
        'uuid': '24087'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.post(url, data=data, headers=headers)
    # print(response.json()["answer"]["components"][0]['data']["datas"])
    codes2 = response.json()["answer"]["components"][0]["data"]["datas"]
    if filter_concept:
        codes = shares.management.commands.wencai2.common.toCode(codes2)
    else:
        codes = shares.management.commands.wencai2.common.toCode(codes2, False)

    return codes


from collections import defaultdict


def top(codes, filter_industry=True):
    concept_dict = defaultdict(lambda: {"concept": "", "count": 0, "codes": [], "codes2": []})
    # key = ""
    # item = codes[0]

    for item in codes:
        if item["code"] > "680000":
            continue
        # 拆分concept字符串
        concepts = item["concept"]

        if concepts != None:
            for concept in concepts:
                if concept in shares.management.commands.wencai2.common.filter_concept:
                    continue
                concept_dict[concept]["concept"] = concept
                concept_dict[concept]["count"] += 1
                concept_dict[concept]["codes"].append(item["code"])
                concept_dict[concept]["codes2"].append(item)
            # concept_dict[concept]["full"] = max(concept_dict[concept]["full"], item["full"])

        if filter_industry == False:
            continue;
        industries = item["industry"]
        if industries != None:
            for industry in industries:
                if industry in shares.management.commands.wencai2.common.filter_concept:
                    continue
                concept_dict[industry]["concept"] = industry
                concept_dict[industry]["count"] += 1
                concept_dict[industry]["codes"].append(item["code"])
                concept_dict[industry]["codes2"].append(item)

    for concept in concept_dict:
        concept_dict[concept]['codes2'] = sorted(concept_dict[concept]['codes2'], key=lambda x: x['full'], reverse=True)

    # 将字典转化为列表
    concepts = list(concept_dict.values())
    concepts_sorted = sorted(concepts, key=lambda x: x['count'], reverse=True)
    concepts_sorted = concepts_sorted[0:5]
    return concepts_sorted
