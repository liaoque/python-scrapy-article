import requests
from datetime import datetime
from common import dingding,clean


def hot(last_id, page):
    url = "https://xueqiu.com/statuses/hot/listV3.json"
    headers = {
        "cookie": "xq_a_token=1169815cd1a60e20132bf2204e68a05d40fc7f7f",
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    params ={
        "source": "hot",
        "last_id": last_id,
        "page": page,
        "_": page,
        "md5__1038": "n4+xyDgDBADQeGKG=GODlcj5YiKA+4hBAxbTD",

    }
    response = requests.get(url, params=params, headers=headers)
    cards = response.json()["list"]
    data = []
    for item in cards:
        created_at = datetime.utcfromtimestamp(int(item["created_at"]/1000)).strftime("%Y-%m-%d %H:%M:%S")

        data.append({
            "id": item["id"],
            "text": item["text"],
            "created_at": created_at,
            "type": 1
        })
    return data


