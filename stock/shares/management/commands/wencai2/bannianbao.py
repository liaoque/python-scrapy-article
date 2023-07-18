import requests
import wencai2.common


def bannianbao(today):
    s = "半年报预增，所属概念，s去除ST，去除北交所，去除新股"
    url = 'http://www.iwencai.com/gateway/urp/v7/landing/getDataList'
    data = {
        'business_cat': 'soniu',
        'comp_id': wencai2.common.comp_id,
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

    codes = wencai2.common.toCode(codes2)

    return codes


