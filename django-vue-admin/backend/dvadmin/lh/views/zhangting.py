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
from itertools import combinations


@method_decorator(csrf_exempt, name='dispatch')
class ZhangTingView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = MongoClient(DATABASES['mg']['CLIENT']['host'],
                                  DATABASES['mg']['CLIENT']['port'])  # 默认连接到 localhost 和端口 27017
        self.db = self.client[DATABASES['mg']['NAME']] # 选择你的数据库

    def __del__(self):
        self.client.close()

    def get(self, request, *args, **kwargs):
        current_time = request.GET.get('current_time')
        if current_time is None or current_time == "":
            return JsonResponse({"error": "current_time must"})

        table = self.db['limitup_records']  # 选择你的数据

        target_day_stocks = set()
        for r in table.find({"date": current_time}, {'code': 1}):
            target_day_stocks.add(r['code'])

        if not target_day_stocks:
            print(f"目标日期 {current_time} 没有涨停股票数据")
            return JsonResponse({"error": "目标日期 {current_time} 没有涨停股票数据"})

        recent_dates = list(table.aggregate([
            {"$match": {"date": {"$lte": current_time}}},
            {"$group": {"_id": "$date"}},
            {"$sort": {"_id": -1}},
            {"$limit": 30}
        ]))
        recent_dates = [d["_id"] for d in recent_dates]
        # recent_dates = table.distinct(
        #     "date",
        #     {"date": {"$lt": current_time}},  # 不包括目标日期本身
        #     sort=[("date", -1)],
        #     limit=30
        # )

        date_stock_map = {}  # {date: set(stock_codes)}
        for r in table.find({"date": {"$in": recent_dates}}, {'date': 1, 'code': 1}):
            date_stock_map.setdefault(r['date'], set()).add(r['code'])

        resonance_pairs = {}
        for date, stocks in date_stock_map.items():
            # 计算交集 - 即同时出现在目标日和历史日的股票
            common_stocks = target_day_stocks & stocks

            if len(common_stocks) >= 2:  # 至少有2只股票同时出现
                resonance_pairs[date] = common_stocks

        return JsonResponse({
            "code": 2000,
            "msg": "success",
            "data": resonance_pairs
        })

    def post(self, request, *args, **kwargs):
        return JsonResponse({
            "code": 2000,
            "msg": "success",
            "data": {}
        })
