import json
import os
import time

import requests
from datetime import datetime, timezone
from common import dingding, clean
from urllib.parse import urlencode, quote_plus
import execjs


def hot(last_id='', page=1):
    url = "https://xueqiu.com/statuses/hot/listV3.json"
    headers = {
        "cookie": "xq_a_token=03e5fa2f7b05e5086ee61a943a151625ececb6e2",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }
    params = {
        "source": "hot",
        "page": page,
        "_": int(time.time()),
    }
    if len(last_id):
        params['last_id'] = last_id
    query_string = urlencode(params)
    url = f"{url}?{query_string}"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ctx = execjs.compile(open(current_dir + '/sign/sign.js').read())
    md51038 = ctx.call('signNew', quote_plus(url))
    url = f"{url}&md5__1038={md51038}"

    response = requests.get(url, headers=headers)
    cards = response.json()["list"]
    data = []
    for item in cards:
        created_at = datetime.fromtimestamp(int(item["created_at"] / 1000), tz=timezone.utc)
        # created_at = datetime.utcfromtimestamp(int(item["created_at"]/1000)).strftime("%Y-%m-%d %H:%M:%S")
        item['meta_keywords'] = {}
        if len(item['meta_keywords']):
            item['meta_keywords'] = json.load(item['meta_keywords'])

        data.append({
            "id": item["id"],
            "user": {
                "user_id": item["user"]['id'],  ##用户唯一标识
                "screen_name":item["user"]['screen_name'], ##用户昵称
                "verified": item["user"]['verified'], ##是否认证（雪球中部分用户可能会有认证标志）
                # "avatar_url": "string"  ##头像链接（可选）
                'followers_count': item["user"]['followers_count'],  # 粉丝数量
            },
            "title": item["title"],  ##帖子标题（如果有）
            "content": item["text"],  ##帖子详细内容
            "created_at": created_at,  ##发帖时间
            "metrics": {
                "comments": item["reply_count"], ##评论数
                "likes": item["like_count"],  ##点赞数
                "reposts": item["retweet_count"],     ##转发
            },
            "stock_codes": item['stockCorrelation'],  ##帖子中涉及的股票代码（若提及）
            "tags": [],  ##用户打上的相关标签或话题
            'location': item['meta_keywords'].get('ip_location', ''),  # 地址
        })
    return data


if __name__ == '__main__':
    hot()
