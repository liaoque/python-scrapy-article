from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template import loader
import requests
import re
import json
from ..model.dapan import DaPan


def da_pan(request):
    # url = "https://fund.10jqka.com.cn/ifindRank/commonTypeAvgFqNet/%s.json" % (code)
    transformed_data = DaPan.objects.order_by('-date_as')

    response = JsonResponse({"data": list(transformed_data.values())}, safe=False)
    response["Access-Control-Allow-Origin"] = "*"
    return response
