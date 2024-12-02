import requests
from datetime import datetime


def baiduzhishu():
    d = datetime.now().strftime("%Y-%m-%d")
    url = "https://index.baidu.com/api/SearchApi/index?area=0&word=[[%7B%22name%22:%22%E4%B8%8A%E8%AF%81%E6%8C%87%E6%95%B0%22,%22wordType%22:1%7D]]&startDate=" + d + "&endDate=" + d
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'cookie': 'BDUSS=WZ-THk1cFppOUZva0hFeUd0RXNUbUlGd3JEWXp0SjZkeElBa2xpNG55SGFQUTVuSVFBQUFBJCQAAAAAAAAAAAEAAAD5bRGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANqw5mbasOZme; ',
        'cipher-text': '1733133748512_1733156142059_EFJDjkCAyrwnDSs9bf4VK0HJWbIm8r371P90t1E4CwMgKzvj2vSLjqBYUJMSWXy2y8D4VYiVSHTWzr9vpb06CNZC/m8+Km7rw5Z9pgw8Ph9amccDx4fq4zS/aOtkgwxu1BHFgS175MIbbHi5amcNDqAYzoU0WaAG+eAmNV+Vgpzx1ml1tlg2LpSEMUzmSjH6izXB2KJKRHHskwYgfZTM6XmAEH+KWzq518zlOzE932kz81VXaU8Ut/y80q14ULGCgk9/aMw4tx6hD7KVMhsh5/Escp8HdfDEo2AVFaZvPYxHS6uLTaFmVAYhVtKCnf/Tdd40pfzPGG3VYcZa2HSZbLT2x/XoqVwOItNOVucijYo1w5+tUsCG1bKVAWqc32p+DdA2Z6OQKB8fFM0Bgy/NMonqw1O3AmzJYvXioCPC1HbkCml0oDtGqzcO5Fjrg5vN',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    codes2 = response.json()
    if codes2["status"] != 0:
        return

    dat = codes2["data"]["userIndexes"][0]["all"]["data"]
    pc = codes2["data"]["userIndexes"][0]["pc"]["data"]
    wise = codes2["data"]["userIndexes"][0]["wise"]["data"]
    uniqid = codes2["data"]["uniqid"]

    url = "https://index.baidu.com/Interface/ptbk?uniqid=" + uniqid
    response = requests.get(url, headers=headers)
    codes3 = response.json()
    if codes3["status"] != 0:
        return

    all = dcode(codes3["data"], dat)
    pc = dcode(codes3["data"], pc)
    wise = dcode(codes3["data"], wise)
    return {
        "all": all,
        "pc": pc,
        "wise": wise,
    }


def baiduzixun():
    d = datetime.now().strftime("%Y-%m-%d")
    url = "https://index.baidu.com/api/FeedSearchApi/getFeedIndex?area=0&word=[[%7B%22name%22:%22%E4%B8%8A%E8%AF%81%E6%8C%87%E6%95%B0%22,%22wordType%22:1%7D]]&startDate=" + d + "&endDate=" + d
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'cookie': 'BDUSS=WZ-THk1cFppOUZva0hFeUd0RXNUbUlGd3JEWXp0SjZkeElBa2xpNG55SGFQUTVuSVFBQUFBJCQAAAAAAAAAAAEAAAD5bRGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANqw5mbasOZme; ',
        'cipher-text': '1733133748512_1733156142059_EFJDjkCAyrwnDSs9bf4VK0HJWbIm8r371P90t1E4CwMgKzvj2vSLjqBYUJMSWXy2y8D4VYiVSHTWzr9vpb06CNZC/m8+Km7rw5Z9pgw8Ph9amccDx4fq4zS/aOtkgwxu1BHFgS175MIbbHi5amcNDqAYzoU0WaAG+eAmNV+Vgpzx1ml1tlg2LpSEMUzmSjH6izXB2KJKRHHskwYgfZTM6XmAEH+KWzq518zlOzE932kz81VXaU8Ut/y80q14ULGCgk9/aMw4tx6hD7KVMhsh5/Escp8HdfDEo2AVFaZvPYxHS6uLTaFmVAYhVtKCnf/Tdd40pfzPGG3VYcZa2HSZbLT2x/XoqVwOItNOVucijYo1w5+tUsCG1bKVAWqc32p+DdA2Z6OQKB8fFM0Bgy/NMonqw1O3AmzJYvXioCPC1HbkCml0oDtGqzcO5Fjrg5vN',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    codes2 = response.json()
    if codes2["status"] != 0:
        return

    dat = codes2["data"]["index"][0]["data"]
    uniqid = codes2["data"]["uniqid"]

    url = "https://index.baidu.com/Interface/ptbk?uniqid=" + uniqid
    response = requests.get(url, headers=headers)
    codes3 = response.json()
    if codes3["status"] != 0:
        return

    all = dcode(codes3["data"], dat)
    return {
        "all": all,
    }

def dcode(t, e):
    if not t:
        return ""

    i = list(t)
    n = list(e)
    a = {}
    r = []

    for A in range(len(i) // 2):
        a[i[A]] = i[len(i) // 2 + A]

    for o in range(len(e)):
        r.append(a[n[o]])

    return ''.join(r)

print(baiduzixun())


