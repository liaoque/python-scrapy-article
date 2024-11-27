import requests

# https://xueqiu.com/query/v1/symbol/search/status.json?count=10&comment=0&symbol=SH000001&hl=0&source=all&sort=&page=1&q=&type=12&md5__1038=n4%2BxcDyDBDRD9jbD%2FD0YoY0QQeqmTvIhypD
# https://xueqiu.com/query/v1/symbol/search/status.json?count=10&comment=0&symbol=SH000001&hl=0&source=all&sort=&page=2&q=&type=12&md5__1038=n4jxR7exBCe05DI5YK0%3DGOQFqYvc4D%3DFWWa4D

def xueqiu(page, start, end):
    url = "https://xueqiu.com/query/v1/symbol/search/status.json?count=10&symbol=SH000001&md5__1038=eqRxcQqQqiwO3DsD7%2Bq0%3D3GQgg7f%3DD7TcGD&page=" + str(
        page)
    headers = {
        "cookie": "u=4493850983;",
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    cards = response.json()["list"]
    data = []
    for item in cards:
        data.append({
            "id": item["id"],
            "text": item["text"],
            "created_at": item["created_at"]
        })
    return data



if __name__ == "__main__":
    start = ""
    end = ""
    xueqiu(1, start, end)
