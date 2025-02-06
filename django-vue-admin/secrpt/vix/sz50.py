import requests

def baiduzhishu(keyword):
    url = "https://index.baidu.com/api/SearchApi/index?area=0&word=[[{\"name\":\"" + keyword + "\",\"wordType\":1}]]&startDate=" + start + "&endDate=" + end
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
    endDate = codes2["data"]["userIndexes"][0]["all"]["endDate"]
    pc = codes2["data"]["userIndexes"][0]["pc"]["data"]
    wise = codes2["data"]["userIndexes"][0]["wise"]["data"]
    uniqid = codes2["data"]["uniqid"]

    url = "https://index.baidu.com/Interface/ptbk?uniqid=" + uniqid
    response = requests.get(url, headers=headers)
    codes3 = response.json()
    if codes3["status"] != 0:
        return

    return {
        "all": all.split(","),
        "endDate": endDate,
        # "pc": pc,
        # "wise": wise,
    }