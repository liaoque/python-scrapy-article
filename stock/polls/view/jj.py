from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template import loader
import requests


def jj_data(request, code):
    url = "https://fund.10jqka.com.cn/ifindRank/commonTypeAvgFqNet/%s.json" % (code)
    r = requests.get(url)
    response = JsonResponse(r.json())
    response["Access-Control-Allow-Origin"] = "*"
    # 如果需要，可以添加更多CORS相关的头信息，例如：
    # response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    # response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response
