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
from pymongo import MongoClient
from os.path import dirname
from application.settings import DATABASES

@method_decorator(csrf_exempt, name='dispatch')
class YQView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = MongoClient(DATABASES['wb']['CLIENT']['host'],
                                  DATABASES['wb']['CLIENT']['port'])  # 默认连接到 localhost 和端口 27017
        self.db = self.client['lh']  # 选择你的数据库

    def __del__(self):
        self.client.close()

    def get(self, request, *args, **kwargs):
        current_time = request.GET.get('current_time')
        if current_time is None or current_time == "":
            return JsonResponse({"error": "current_time must"})
        table = self.db['yq']  # 选择你的数据
        res = table.find_one({
            "current_time" : current_time
        }, {"data": 1})

        return JsonResponse({
            "code": 2000,
            "msg": "success",
            "data": res
        })

    def post(self, request, *args, **kwargs):
        body_data = json.loads(request.body)
        current_time = body_data.get('current_time')
        data = body_data.get('data')
        if current_time is None or current_time == "":
            return JsonResponse({"error": "current_time must"})
        table = self.db['yq']  # 选择你的数据
        res = table.find_one({
            "current_time": current_time
        }, {"_id": 1})

        # 如果数据存在则更新， 不存在则创建
        if res:
            # 如果数据存在则更新
            table.update_one(
                {"current_time": current_time},
                {"$set": {"data": data}}
            )
            message = "Data updated successfully."
        else:
            # 如果数据不存在则创建
            table.insert_one({
                "current_time": current_time,
                "data": data
            })
            message = "Data created successfully."

        return JsonResponse({
            "code": 2000,
            "msg": message,
            "data": {}
        })
