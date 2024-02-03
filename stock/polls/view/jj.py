from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template import loader
import requests
import re
import json


def jj_data(request, code):
    # url = "https://fund.10jqka.com.cn/ifindRank/commonTypeAvgFqNet/%s.json" % (code)
    url = "https://fund.10jqka.com.cn/%s/json/jsondwjz.json" % (code)
    r = requests.get(url)
    match = re.search(r'var dwjz_\d+=\s*(\[\[.*?\]\])', r.text)
    if match:
        data_str = match.group(1)
        data_list = json.loads(data_str)
        transformed_data = [{date: value} for date, value in data_list]
    else:
        transformed_data = []
    response = JsonResponse(transformed_data)
    response["Access-Control-Allow-Origin"] = "*"
    return response
