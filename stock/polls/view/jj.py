
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template import loader
import requests

def jj_data(request, code):
    url = "https://fund.10jqka.com.cn/ifindRank/commonTypeAvgFqNet/%s.json"%(code)
    r = requests.get(url)
    return JsonResponse(r.json())
