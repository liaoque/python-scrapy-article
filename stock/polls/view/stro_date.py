from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template import loader
import requests
import re
import json
from ..model.shares_date_listen import SharesDateListen


def stro_date(request):
    response = JsonResponse({}, safe=False)
    if request.method == 'POST':
        # 获取POST请求中的数据
        data = request.POST
        # 处理数据，例如保存到数据库等
        # ...
        # for item in data["data"]["z"]["yellow"]:
        #     transformed_data = SharesDateListen.objects.filter(date_as=data["d"], code=item["code"],type=5)
        #     if len(transformed_data) > 0:
        #         continue
        #     SharesDateListen(
        #         buy_date_as=data["d"],
        #         date_as=data["d"],
        #         code=data["code"],
        #         p_start=0,
        #         buy_pre=0,
        #         type=5
        #     )
        #     pass
        # for item in data["data"]["z"]["orange"]:
        #     pass
        # for item in data["data"]["z"]["purple"]:
        #     pass
        # for item in data["data"]["c"]["yellow"]:
        #     pass
        # for item in data["data"]["c"]["orange"]:
        #     pass
        # for item in data["data"]["c"]["purple"]:
        #     pass


        response = JsonResponse(data, safe=False)

    response["Access-Control-Allow-Origin"] = "*"
    return response
