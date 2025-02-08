import os

from django.shortcuts import render
import json
# Create your views here.
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dvadmin.lh.utils.ths import  hot as ths
from dvadmin.lh.utils.dfcf import  hot as dfcf
from dvadmin.lh.utils.tdx import  hot as tdx

# from application.settings import DATABASES
# import time
# from pymongo import MongoClient
# import string

from django.views import View
from dvadmin.wb.config import code_config

@method_decorator(csrf_exempt, name='dispatch')
class BangDanView(View):
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
        # self.client = MongoClient(DATABASES['wb']['CLIENT']['host'],
        #                           DATABASES['wb']['CLIENT']['port'])  # 默认连接到 localhost 和端口 27017
        # self.db = self.client['wb']  # 选择你的数据库

    # def __del__(self):
        # self.client.close()

    def get(self, request, *args, **kwargs):
        name = request.GET.get('name')
        if name == 'ths':
            data = ths.hotStockList()
            data = data["data"]["stock_list"]
            data = [{
                'code': item["code"],
                'name': item["name"],
                'fudu': item["rise_and_fall"],
                'now_price': 0,
                'date': "",
                'bk': ",".join([ str(item)for item in item["tag"]["concept_tag"]]),
                'reason': item.get("analyse", ""),
                'riseDay': item["tag"].get("popularity_tag", ""),
                'ranking': item["order"],
                'totalCount': item["rate"],
                'change_rank': 0,
            } for item in data]

        elif name == 'dfcf':
            data =  dfcf.hotStockList()
            dataInfo = dfcf.getExtInfoList([item['code'] for item in data])
            data2 = dfcf.hotStockList(page=1)
            dataInfo2 = dfcf.getExtInfoList([item['code'] for item in data2])
            data = data + data2
            dataInfo = dataInfo["data"]["diff"] + dataInfo2["data"]["diff"]
            dataInfo = [(item["f12"], item) for item in dataInfo]
            dataInfo = dict(dataInfo)
            data = [ {
                'code': item["code"],
                'change_rank': item["changeNumber"],
                'name': dataInfo[item["code"]]["f14"],
                'fudu': dataInfo[item["code"]]["f3"],
                'now_price': dataInfo[item["code"]]["f2"],
                'date': item['exactTime'],
                'bk': "",
                'reason': "",
                'riseDay': "",
                'ranking': item["rankNumber"],
                'totalCount': "",
            } for item in data]



        elif name == 'tdx':
            data = tdx.hotStockList()
            data = [ {
                'code': item[1],
                'name': item[2],
                'fudu': item[3],
                'now_price': item[4],
                'date': item[5],
                'bk': ",".join([ str(item["name"])for item in json.loads(item[6])]),
                'reason': item[7],
                'riseDay': item[8],
                'ranking': item[10],
                'totalCount': item[11],
                'change_rank': 0,
            } for item in data[3:]]


        # current_time = request.GET.get('current_time')


        return JsonResponse({
            "code": 2000,
            "msg": "success",
            "data": data[:30]
        })

    def post(self, request, *args, **kwargs):



        return JsonResponse({
            "code": 2000,
            "msg": "success",
            "data": {
            }
        })
