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
        elif name == 'dfcf':
            data =  dfcf.hotStockList()
        elif name == 'tdx':
            data = tdx.hotStockList()



        # current_time = request.GET.get('current_time')


        return JsonResponse({
            "code": 2000,
            "msg": "success",
            "data": data
        })

    def post(self, request, *args, **kwargs):



        return JsonResponse({
            "code": 2000,
            "msg": "success",
            "data": {
            }
        })
