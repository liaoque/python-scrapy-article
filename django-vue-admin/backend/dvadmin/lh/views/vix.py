import os
import sqlite3
from django.shortcuts import render
import json
# Create your views here.
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import numpy as np
from django.views import View
from datetime import datetime
from os.path import dirname

@method_decorator(csrf_exempt, name='dispatch')
class VixView(View):
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    # self.client = MongoClient(DATABASES['wb']['CLIENT']['host'],
    #                           DATABASES['wb']['CLIENT']['port'])  # 默认连接到 localhost 和端口 27017
    # self.db = self.client['wb']  # 选择你的数据库

    # def __del__(self):
    # self.client.close()

    def get(self, request, *args, **kwargs):
        dbname = dirname(dirname(dirname(__file__))) + "/backend/vix.db"
        # conn = sqlite3.connect(dbname)
        # conn.row_factory = sqlite3.Row
        # cursor = conn.cursor()
        #
        # cursor.close()
        # conn.close()


        return JsonResponse({
            "code": 2000,
            "msg": "success",
            "data": {
                "dbname": dbname,
            }
        })

    def post(self, request, *args, **kwargs):
        return JsonResponse({
            "code": 2000,
            "msg": "success",
            "data": {
            }
        })
