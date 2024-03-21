from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template import loader
import requests
import re
import json
from ..model.shares_date_listen import SharesDateListen
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def stro_date(request):
    response = JsonResponse({}, safe=False)
    if request.method == 'POST':
        # 获取POST请求中的数据
        data = json.loads(request.body)
        # 处理数据，例如保存到数据库等
        # ...
        for code in data["data"]["z"]["yellow"]:
            saveCode(code, data, 5)
            pass
        for code in data["data"]["z"]["orange"]:
            saveCode(code, data, 6)
            pass
        for code in data["data"]["z"]["purple"]:
            saveCode(code, data, 7)
            pass
        for code in data["data"]["c"]["yellow"]:
            saveCode(code, data, 5)
            pass
        for code in data["data"]["c"]["orange"]:
            saveCode(code, data, 6)
            pass
        for code in data["data"]["c"]["purple"]:
            saveCode(code, data, 7)
            pass

        response = JsonResponse(data, safe=False)

    response["Access-Control-Allow-Origin"] = "*"
    return response


def saveCode(code, data, type):
    transformed_data = SharesDateListen.objects.filter(date_as=data["d"], code=code, type=type)
    if len(transformed_data) > 0:
        return
    SharesDateListen(
        buy_date_as=data["d"],
        date_as=data["d"],
        code=code,
        p_start=0,
        buy_pre=0,
        type=type
    )
