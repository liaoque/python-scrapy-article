import requests
from datetime import datetime


def weibo(page, start, end):
    url = "https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D%E4%B8%8A%E8%AF%81%E6%8C%87%E6%95%B0%26t%3D&page_type=searchall&page=" + str(
        page)
    headers = {
        "cookie": "SUB=_2A25KQYrPDeRhGeVL7FsT8irMyD2IHXVpPoIHrDV8PUNbmtAGLWjSkW9NTD9Yt3m0jJK7Ip88YDDdqn-eC8TAC_r1;",
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    cards = response.json()["data"]["cards"]

    data = []
    time_format = '%a %b %d %H:%M:%S %z %Y'
    for item in cards:
        if item["card_type"] == 11:
            for item2 in item["card_group"]:
                if item2["card_type"] == 9:
                    data.append({
                        "id": item2["mblog"]["id"],
                        "text": item2["mblog"]["text"],
                        "created_at": datetime.strptime(item2["mblog"]["created_at"], time_format)
                    })
            continue
        elif item["card_type"] == 9:
            data.append({
                "id": item["mblog"]["id"],
                "text": item["mblog"]["text"],
                "created_at": datetime.strptime(item["mblog"]["created_at"], time_format)
            })
    if len(data) == 0:
        return []

    if data[len(data) - 1]["created_at"] < end:
        data.extend(weibo(page + 1, start, end))
    return data


if __name__ == "__main__":
    start = ""
    end = ""
    weibo(1, start, end)
