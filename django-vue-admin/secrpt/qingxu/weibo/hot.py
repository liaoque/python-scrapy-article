import requests

def fetch_weibo_cardlist(api_url, headers=None, params=None):
    # 如果未提供 headers，则使用默认 headers
    if headers is None:
        headers = {
            "X-Validator": "RZx6PjBGqzbcJTpIcTu93bzneOpnsf/he8RFzwxNYqQ=",
            "X-Log-Uid": "3579224031",
            "X-Sessionid": "2bee6664-60b8-4412-adb9-4bdc82728150",
            "User-Agent": "SM-G9810_7.1.2_weibo_11.6.0_android",
            "Authorization": "WB-SUT _2A95K3CEXDeRxGeVL7FsT8irMyD2IHXVnyDPfrDV6PUJbkdANLWn7kWpNTD9Yt3tLUsvIradO2GvMEYkO9OJ4q-3P",
            "Host": "api.weibo.cn",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }

    # 发送HTTP GET请求
    response = requests.get(api_url, headers=headers, params=params)

    # 检查响应状态码是否为200
    if response.status_code == 200:
        # 返回JSON数据
        return response.json()
    else:
        # 返回错误信息
        return f"Failed to fetch data: {response.status_code}"

# 使用示例
api_url = "https://api.weibo.cn/2/cardlist"

# 定义参数字典
params = {
    "networktype": "wifi",
    "image_type": "heif",
    "launchid": "10000365--x",
    "orifid": "5$$$0$$5",
    "uicode": "10000327",
    "ul_hid": "7d9bdb52-fe84-43ff-b9a4-4e9daea3df45",
    "ul_sid": "7d9bdb52-fe84-43ff-b9a4-4e9daea3df45",
    "moduleID": "708",
    "featurecode": "10000084",
    "wb_version": "5017",
    "card159164_emoji_enable": "1",
    "lcardid": "top_icon_category_all_1288",
    "c": "android",
    "s": "3d54939f",
    "ft": "0",
    "ua": "samsung-SM-G9810__weibo__11.6.0__android__android7.1.2",
    "wm": "2468_1001",
    "aid": "01A9CZ5vwg8-qUABOuifv9KYpG2ytFN9_HqyvN6pBHq19545s.",
    "fid": "230771_-_Finance_Cardlist_Finder",
    "uid": "3579224031",
    "v_f": "2",
    "v_p": "89",
    "from": "10B6095010",
    "gsid": "_2A25K3CEXDeRxGeVL7FsT8irMyD2IHXVnyDPfrDV6PUJbkdANLXf8kWpNTD9Ytyq_95zJqClQt6xGa4geCz",
    "imsi": "460075639459304",
    "lang": "zh_CN",
    "lfid": "5",
    "page": "1",
    "skin": "default",
    "count": "20",
    "oldwm": "2468_1001",
    "sflag": "1",
    "oriuicode": "10000495_0_10000495_0_10000495",
    "containerid": "230771_-_Finance_Cardlist_Finder",
    "ignore_inturrpted_error": "true",
    "luicode": "10000495",
    "android_id": "813a2130fd1b9da8",
    "client_key": "d41d8cd98f00b204e9800998ecf8427e",
    "show_layer": "1",
    "need_new_pop": "1",
    "ul_ctime": "1742231492528",
    "need_head_cards": "0",
    "cum": "E5C1F2EE"
}

# 调用函数并打印结果
result = fetch_weibo_cardlist(api_url, params=params)
print(result)
