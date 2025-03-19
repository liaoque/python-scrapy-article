
import requests
import re

def fetch_weibo_commit(params=None):
    # 如果未提供 headers，则使用默认 headers

    api_url = "https://api.weibo.cn/2/comments/build_comments"
    # 发送HTTP GET请求
    response = requests.post(api_url, data=params)

    # 检查响应状态码是否为200
    if response.status_code == 200:
        # 返回JSON数据
        return response.json()
    else:
        # 返回错误信息
        return f"Failed to fetch data: {response.status_code}"




if __name__ == '__main__':
    # 定义参数字典
    params = {
        "id": "5145903959903797",
        "is_show_bulletin": "2",
        "c": "android",
        "s": "3d54939f",
        "from": "10B6095010",
        "gsid": "_2A25K3CEXDeRxGeVL7FsT8irMyD2IHXVnyDPfrDV6PUJbkdANLXf8kWpNTD9Ytyq_941zqq95zJqClQt6xGa4geCz",
        "containerid": "230771_-_Finance_Cardlist_Finder",
    }
    # 调用函数并打印结果
    result = fetch_weibo_commit(params)
    ts = [ {
        'id': item['id'],
        'post_id': result['id'],
        'user':{
            'user_id': item['user']['id'],
            'name': item['user']['name'],  # 名字
            'verified': item['user']['verified_reason'],  # 认证信息
            'followers_count': item['user']['followers_count'],  # 粉丝数量
            'verified_level': item['user'].get('verified_level', 0),  # 粉丝数量
            'verified_type_ext': item['user'].get('verified_type_ext', ''),  # 粉丝数量
        },
        'content': item['text'],
        'created_at': item['created_at'],
        'metrics':{
          "likes":  item['like_counts'],    #  点赞数
          "replies":  item['total_number'], #   回复数
        },
    } for item in result['root_comments']]
    print(ts)
