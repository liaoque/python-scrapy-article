
import requests

d = [
    "20230901","20230904","20230905","20230906","20230907","20230908","20230911","20230912",
"20230913","20230914",
 ]

for item in d:
    data = requests.get("http://127.0.0.1:8000/polls?current_time="+item)
    d2 = data.json()
    print("%s", item)
    print("qx：%s", d2["qing_xu"])
    b = ""
    if  d2["bu_zhang"]["chuang"]:
        b = d2["bu_zhang"]["chuang"]["briefname"] + "----" + ",".join( d2["bu_zhang"]["chuang"]["suoshugainian"])
    print("bu_zhang-chuang：%s", b)
    b = ""
    if d2["bu_zhang"]["zhu"]:
        b = d2["bu_zhang"]["zhu"]["briefname"] + "---" + ",".join(d2["bu_zhang"]["zhu"]["suoshugainian"])
    print("bu_zhang-zhu：%s", b)

    b = ""
    if d2["n"]["chuang"]:
        b = d2["n"]["chuang"]["briefname"] + "---" + ",".join(d2["n"]["chuang"]["suoshugainian"])
    print("n-chuang：%s", b)
    b = ""
    if d2["n"]["zhu"]:
        b = d2["n"]["zhu"]["briefname"] + "---" + ",".join(d2["n"]["zhu"]["suoshugainian"])
    print("n-zhu：%s", b)
