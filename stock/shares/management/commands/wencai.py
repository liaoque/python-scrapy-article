import requests
import numpy as np
from datetime import datetime, timedelta



comp_id = "6734520"


def trend(today):
    s = '%s去除ST，去除北交所，%s去除新股，所属行业，所属概念，%s开盘价=%s涨停价，%s竞价未匹配金额，%s涨跌幅降序' % (
        today, today, today, today, today, today,
    )

    url = 'http://www.iwencai.com/gateway/urp/v7/landing/getDataList'
    data = {
        'business_cat': 'soniu',
        'comp_id': comp_id,
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

    codes = []
    for item in codes2:
        code = item.get("股票代码", "")
        name = item.get("股票简称", "")
        type_ = item.get("股票市场类型", "")
        if type_ is not None:
            type_ = type_.split(";")

        industry = item.get("所属同花顺行业", "")
        if industry is not None:
            industry = industry.split("-")

        concept = item.get("所属概念", "")
        if concept is not None:
            concept = concept.split(";")

        codes.append({
            "code": code,
            "name": name,
            "type": type_,
            "industry": industry,
            "concept": concept,
        })

    return codes


def trendCode(today, yeasterday):
    s = '%smacd向上，%s收盘价高于开盘价，%s收盘价高于5日均价，%s回踩5日均线，概念，行业' % (
        today, today, today,yeasterday
    )
    # s = '%s去除ST，去除北交所，%s去除新股，所属行业，所属概念，%s开盘价=%s涨停价，%s竞价未匹配金额，%s涨跌幅降序' % (
    #     today, today, today, today, today, today,
    # )

    url = 'http://www.iwencai.com/gateway/urp/v7/landing/getDataList'
    data = {
        'business_cat': 'soniu',
        'comp_id': comp_id,
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
    codes = response.json()["answer"]["components"][0]["data"]["datas"]
    return [{
        "code": item["股票代码"],
        "name": item["股票简称"],
        "type": item["股票市场类型"].split(";"),
        "industry": item["所属同花顺行业"].split("-"),
        "concept": item["所属概念"].split(";"),
    } for item in codes]


if __name__ == '__main__':


    today =   datetime.today().strftime('%Y-%m-%d')

    yeasterday = ""

    date_obj = datetime.strptime(today, '%Y-%m-%d')
    yeasterday = date_obj - timedelta(days=1)

    codes = trend(today)
    item = [ code["concept"] for code in codes]
    arr_2d = np.array(item)
    concept = arr_2d.flatten()

    codes = trendCode(today, yeasterday)
    arr_2d = np.array(codes)

    filtered_codes = []
    concept_set = set(concept)

    for item in codes:
        # 将industry和concept字段转为集合，以便进行集合操作
        industry_set = set(item["concept"])
        # 检查industry集合是否包含concept集合的任何一个元素
        if any(concept in concept_set for concept in industry_set):
            # 如果不包含，就加入到filtered_codes列表中
            filtered_codes.append(item)

    # 将过滤后的codes转为numpy数组
    arr_2d_filtered = np.array(filtered_codes)
    print(arr_2d_filtered)

