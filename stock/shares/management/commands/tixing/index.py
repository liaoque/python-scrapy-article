import requests
import json
import os
from datetime import datetime

def dingding(s):
    if len(s) == 0:
        return
    # 涨停股票,首次涨停时间从小到大，流通市值，几天几板，连续涨停天数，去除st，涨停原因类别，所属概念
    # s = "半年报预增，所属概念，s去除ST，去除北交所，去除新股"
    url = 'https://oapi.dingtalk.com/robot/send?access_token=f51bee16742b25506373378cd7a33def2c1ce7d253998c59bfbdff28ffaf15d5'

    data = """
    {
        'msgtype': 'text',
        'text': {
            'content':'%s'
        }
    }
    """%(s)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.post(url, data=data.encode("utf-8"), headers=headers)
    print(data, response.json())
    return response.json()

def getData():
    url = 'https://28.push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=50&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=&fs=b:MK0010&fields=f3,f12,f14'
    data = {
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "http://quote.eastmoney.com/zs000001.html",
    }

    response = requests.get(url, params=data, headers=headers)
    codes2 = response.json()
    # {"rc": 0, "rt": 6, "svr": 182481189, "lt": 1, "full": 1, "dlmkts": "", "data": {"total": 33, "diff": [
    #     {"f3": 1.8, "f12": "000001", "f14": "上证指数"}, {"f3": 1.0, "f12": "399001", "f14": "深证成指"},
    #     {"f3": -0.66, "f12": "899050", "f14": "北证50"}, {"f3": 0.51, "f12": "399006", "f14": "创业板指"},
    #     {"f3": 0.07, "f12": "000688", "f14": "科创50"}, {"f3": 1.14, "f12": "399750", "f14": "深主板50"},
    #     {"f3": 1.4, "f12": "000300", "f14": "沪深300"}, {"f3": 1.54, "f12": "000016", "f14": "上证50"},
    #     {"f3": 1.0, "f12": "399850", "f14": "深证50"}, {"f3": 0.5, "f12": "399005", "f14": "中小100"},
    #     {"f3": 1.4, "f12": "000905", "f14": "中证500"}, {"f3": 1.26, "f12": "000852", "f14": "中证1000"},
    #     {"f3": 1.63, "f12": "000010", "f14": "上证180"}, {"f3": 1.29, "f12": "000009", "f14": "上证380"},
    #     {"f3": 0.62, "f12": "000132", "f14": "上证100"}, {"f3": 0.56, "f12": "000133", "f14": "上证150"},
    #     {"f3": 3.97, "f12": "000003", "f14": "Ｂ股指数"}, {"f3": -0.01, "f12": "000012", "f14": "国债指数"},
    #     {"f3": 0.02, "f12": "000013", "f14": "企债指数"}, {"f3": 1.12, "f12": "000011", "f14": "基金指数"},
    #     {"f3": 1.0, "f12": "399002", "f14": "深成指R"}, {"f3": 1.54, "f12": "399003", "f14": "成份Ｂ指"},
    #     {"f3": 1.25, "f12": "399106", "f14": "深证综指"}, {"f3": 0.88, "f12": "399004", "f14": "深证100R"},
    #     {"f3": 0.91, "f12": "399007", "f14": "深证300"}, {"f3": 0.75, "f12": "399008", "f14": "中小300"},
    #     {"f3": 0.65, "f12": "399293", "f14": "创业大盘"}, {"f3": 0.86, "f12": "399019", "f14": "创业200"},
    #     {"f3": 0.96, "f12": "399020", "f14": "创业小盘"}, {"f3": 1.27, "f12": "399100", "f14": "新指数"},
    #     {"f3": 1.34, "f12": "399550", "f14": "央视50"}, {"f3": 1.2, "f12": "000903", "f14": "中证100"},
    #     {"f3": 1.4, "f12": "000906", "f14": "中证800"}]}}
    return codes2["data"]["diff"]

def check(data, json_data, key):
    if "ff" not in json_data[key]:
        data[key]["ff"] = 0
    if data[key]["f3"] > 0.03 and ("ff" not in json_data[key] or  json_data[key]["ff"] != 0.03):
        dingding(json.dumps(data[key], ensure_ascii=False))
        data[key]["ff"] = 0.03

    if data[key]["f3"] < -0.03 and ("ff" not in json_data[key] or  json_data[key]["ff"] != -0.03):
        dingding(json.dumps(data[key], ensure_ascii=False))
        data[key]["ff"] = -0.03
    return data

def diffCode():
    # time.time()
    file_path = './file.json'
    current_time = datetime.now()
    hour = current_time.hour
    minute = current_time.minute
    if hour <= 9 and minute <= 25:
        if os.path.exists(file_path):
            os.remove(file_path)
        return
    if hour > 15:
        return

    data = getData()
    data = {item['f12']: item for item in data}

    # 读文件
    if os.path.exists(file_path):
        with open(file_path, 'r+', encoding='utf-8') as file:
            content = file.read()
        if len(content) != 0:
            json_data = json.loads(content)
            json_data = {item['f12']: item for item in json_data}

            data = check(data, json_data, "000001")
            data = check(data, json_data, "399001")
            data = check(data, json_data, "899050")
            data = check(data, json_data, "399006")
            data = check(data, json_data, "000688")


    with open(file_path, 'w+') as f:
        json.dump(data, f)


if __name__ == "__main__":
    diffCode()
