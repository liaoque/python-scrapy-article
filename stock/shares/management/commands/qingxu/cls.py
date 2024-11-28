import requests
from datetime import datetime
# https://www.cls.cn/v3/depth/home/assembled/1000?app=CailianpressWeb&os=web&sv=8.4.6&sign=9f8797a1f4de66c2370f7a03990d2737


# https://www.cls.cn/detail/1871761

# https://www.cls.cn/v3/depth/home/assembled/1003?app=CailianpressWeb&os=web&sv=8.4.6&sign=9f8797a1f4de66c2370f7a03990d2737
"""
 {app: "CailianpressWeb",os: "web",sv: "8.4.6"}
 p(a({}, r))
  function a(e) {
            for (var t = 1; t < arguments.length; t++) {
                var n = null != arguments[t] ? arguments[t] : {};
                t % 2 ? i(Object(n), !0).forEach((function(t) {
                    r(e, t, n[t])
                }
                )) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : i(Object(n)).forEach((function(t) {
                    Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t))
                }
                ))
            }
            return e
        }
 e.exports = function(e) {
            var t = e && s(u(e).map((function(t) {
                return c(t, e[t])
            }
            )));
            return t = r.sync(t),
            t = o(t)
        }

"""
# 财联社头条
def clstop(page, start, end):
    url = "https://www.cls.cn/v3/depth/home/assembled/1000?app=CailianpressWeb&os=web&sv=8.4.6&sign=9f8797a1f4de66c2370f7a03990d2737&page=" + str(
        page)
    headers = {
        "cookie": "SUB=_2A25KQYrPDeRhGeVL7FsT8irMyD2IHXVpPoIHrDV8PUNbmtAGLWjSkW9NTD9Yt3m0jJK7Ip88YDDdqn-eC8TAC_r1;",
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    data = response.json()["data"]
    data2 = []
    for item in data["top_article"]:
        for item2 in item["article_rec"]:
            data2.append({
                "id": item2["article_id"],
                "text": item2["brief"],
                "created_at": item2["ctime"]
            })
    for item in item["depth_list"]:
        data2.append({
            "id": item["article_id"],
            "text": item["brief"],
            "created_at": item["ctime"]
        })

    if len(data2) == 0:
        return []

    if data2[len(data2) - 1]["created_at"] < end:
        data2.extend(clstop(page + 1, start, end))
    return data


def clsaa(page, start, end):
    url = "https://www.cls.cn/v3/depth/home/assembled/1003?app=CailianpressWeb&os=web&sv=8.4.6&sign=9f8797a1f4de66c2370f7a03990d2737&page=" + str(
        page)
    headers = {
        "cookie": "SUB=_2A25KQYrPDeRhGeVL7FsT8irMyD2IHXVpPoIHrDV8PUNbmtAGLWjSkW9NTD9Yt3m0jJK7Ip88YDDdqn-eC8TAC_r1;",
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    data = response.json()["data"]
    data2 = []
    for item in data["top_article"]:
        for item2 in item["article_rec"]:
            data2.append({
                "id": item2["article_id"],
                "text": item2["brief"],
                "created_at": item2["ctime"]
            })
    for item in item["depth_list"]:
        data2.append({
            "id": item["article_id"],
            "text": item["brief"],
            "created_at": item["ctime"]
        })

    if len(data2) == 0:
        return []

    if data2[len(data2) - 1]["created_at"] < end:
        data2.extend(clstop(page + 1, start, end))
    return data

if __name__ == "__main__":
    start = ""
    end = ""
    clstop(1, start, end)