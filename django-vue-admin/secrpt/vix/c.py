import requests
import xmltodict
import json

def req(month, day):
    url = "http://www.cffex.com.cn/sj/hqsj/rtj/"+month+"/"+day+"/index.xml?id=0"
    response = requests.get(url, headers={})
    xml_data = response.text
    # 将XML字符串解析为字典
    data_dict = xmltodict.parse(xml_data)
    return data_dict["dailydata"]["dailydata"]

io = {}
ho = {}
mo = {}
def reqData(month, day):
    data  = req(month, day)

    for item in data:
        if "HO" in item["instrumentid"]:
            xqj = item["instrumentid"][9:]
            break
        elif "MO" in item["instrumentid"]:
            xqj = item["instrumentid"][9:]
            break
        elif "IO" in item["instrumentid"]:

            if "-P-" in item["instrumentid"]:
                key = item["instrumentid"].repalce("-P-", "-")  # 看跌
                xqj = item["instrumentid"][9:]  # 行权价
                tradingday = item["tradingday"] # 当前日期
                expiredate = item["expiredate"] # 到期时间
                closeprice = item["closeprice"] # 收盘价
                io[key]["p"] = closeprice
            else:
                key = item["instrumentid"].repalce("-C-", "-")  # 看涨
                xqj = item["instrumentid"][9:]  # 行权价
                tradingday = item["tradingday"]  # 当前日期
                expiredate = item["expiredate"]  # 到期时间
                closeprice = item["closeprice"]  # 收盘价
                io[key]["c"] = closeprice
            io[key]["xqj"] = xqj
            io[key]["tradingday"] = tradingday
            io[key]["expiredate"] = expiredate
            break

reqData("202412", "20")