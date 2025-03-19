from urllib.parse import urlencode

import requests
import re

def fetch_weibo_cardlist(api_url, headers=None, params=None):
    # 如果未提供 headers，则使用默认 headers
    if headers is None:
        headers = {
            "User-Agent": "SM-G9810_7.1.2_weibo_11.6.0_android",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }

    # 发送HTTP GET请求
    response = requests.get(api_url, )

    # 检查响应状态码是否为200
    if response.status_code == 200:
        # 返回JSON数据
        return response.json()
    else:
        # 返回错误信息
        return f"Failed to fetch data: {response.status_code}"




if __name__ == '__main__':
    # 使用示例
    api_url = "https://api.weibo.cn/2/cardlist"

    # 定义参数字典
    params = {
        "c": "android",
        "s": "3d54939f",
        "from": "10B6095010",
        "gsid": "_2A25K3CEXDeRxGeVL7FsT8irMyD2IHXVnyDPfrDV6PUJbkdANLXf8kWpNTD9Ytyq_941zqq95zJqClQt6xGa4geCz",
        "containerid": "230771_-_Finance_Cardlist_Finder",
    }
    query_string = urlencode(params)
    api_url = f"{api_url}?{query_string}"
    # 调用函数并打印结果
    result = fetch_weibo_cardlist(api_url,)
    ts = [{
        'id':item['mblog']['id'],
        'user':{
            'user_id' :item['mblog']['user']['id'],
            'name' :item['mblog']['user']['name'],              #名字
            'verified' :item['mblog']['user']['verified_reason'],       #认证信息
            'followers_count' :item['mblog']['user']['followers_count'],    # 粉丝数量
            'verified_level' :item['mblog']['user'].get('verified_level',0),    # 粉丝数量
            'verified_type_ext' :item['mblog']['user'].get('verified_type_ext',''),    # 粉丝数量
        },

        'content':item['mblog']['text'],
        'created_at':item['mblog']['created_at'],
        'metrics':{
          "likes":  item['mblog']['multi_attitude'],    #  点赞数
          "reposts":  item['mblog']['multi_attitude'],  #   转发数
          "comments":  item['mblog']['multi_attitude'], #   评论数
        },
        'hashtags': re.findall(r'#[^#]+#', item['mblog']['text']),
        'media_urls': item['mblog']['pic_ids'],
        'location':item['mblog'].get('region_name', '').replace('发布于 ', ""),    #地址
    } for item in result['cards'] if item['card_type'] == 9]
    print(ts)
