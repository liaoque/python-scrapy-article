from urllib.parse import urlencode

import requests
import re
from datetime import datetime

def fetch_weibo_container(params=None):
    # 如果未提供 headers，则使用默认 headers
    api_url = "https://m.weibo.cn/api/container/getIndex"
    containerid = params['containerid']
    params['containerid'] =  str("%s_-_WEIBO_SECOND_PROFILE_WEIBO"%(params['containerid']))
    query_string = urlencode(params)
    api_url = f"{api_url}?{query_string}"

    # 发送HTTP GET请求
    response = requests.get(api_url, )

    # 检查响应状态码是否为200
    if response.status_code == 200:
        # 返回JSON数据
        result = response.json()
        ts = [{
            'weiboid': item['mblog']['id'],
            'containerid': containerid,
            'content': remove_html_tags(item['mblog']['text']),
            'created_at': datetime.strptime(item['mblog']['created_at'], "%a %b %d %H:%M:%S %z %Y").strftime("%Y-%m-%d %H:%M:%S"),
            'scheme': item['scheme'],
        } for item in result['data']['cards'] if item['card_type'] == 9]
        return ts
    else:
        # 返回错误信息
        return f"Failed to fetch data: {response.status_code}"


def remove_html_tags(text):
    # 定义一个正则表达式模式，用于匹配HTML标签
    clean = re.compile('<.*?>')
    # 使用sub()方法替换所有匹配的HTML标签为空字符串
    return re.sub(clean, '', text)


if __name__ == '__main__':
    # 使用示例

    # 定义参数字典
    params = {
        "containerid": "2304133194506490_-_WEIBO_SECOND_PROFILE_WEIBO",
        "page_type": "03",
        "since_id": "",
    }

    # 调用函数并打印结果
    result = fetch_weibo_container(params, )
    ts = [{
        'id': item['mblog']['id'],
        'content': remove_html_tags(item['mblog']['text']),
        'created_at': item['mblog']['created_at'],
        'scheme': item['scheme'],
    } for item in result['data']['cards'] if item['card_type'] == 9]
