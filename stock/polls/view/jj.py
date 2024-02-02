
import requests

def jj_data(request, code):
    url = "https://fund.10jqka.com.cn/ifindRank/commonTypeAvgFqNet/%s.json"%(code)
    r = requests.get(url)
    return r.json()
