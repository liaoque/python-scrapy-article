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
from collections import OrderedDict

def resonancePairs(table, current_time, target_day_stocks):
    recent_dates = list(table.aggregate([
        {"$match": {"date": {"$gte": current_time}}},
        {"$group": {"_id": "$date"}},
        {"$sort": {"_id": -1}},
        {"$limit": 30}
    ]))
    recent_dates = [d["_id"] for d in recent_dates]

    date_stock_map = {}  # {date: set(stock_codes)}
    for r in table.find({"date": {"$in": recent_dates}}, {'date': 1, 'code': 1}):
        date_stock_map.setdefault(r['date'], set()).add(r['code'])

    resonance_pairs = {}
    for date, stocks in date_stock_map.items():
        if date == current_time:
            continue

        # 计算交集 - 即同时出现在目标日和历史日的股票
        common_stocks = target_day_stocks & stocks

        if len(common_stocks) >= 2:  # 至少有2只股票同时出现
            resonance_pairs[date] = list(common_stocks)
    sorted_resonance_pairs = OrderedDict(sorted(resonance_pairs.items(), key=lambda item: item[0]))

    # If you want to convert it back to a regular dict (optional)
    resonance_pairs = dict(sorted_resonance_pairs)
    return resonance_pairs


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
        table_d = self.db['limitdown_records']  # 选择你的数据

        names = {}
        target_day_stocks = set()
        for r in table.find({"date": current_time}, {'code': 1, 'name': 1}):
            if "ST" in r['name']:
                continue
            target_day_stocks.add(r['code'])
            names[r['code']] = r['name']

        resonance_pairs = resonance_pairs_d = []
        if  target_day_stocks:
            resonance_pairs = resonancePairs(table, current_time, target_day_stocks)
            resonance_pairs_d = resonancePairs(table_d, current_time, target_day_stocks)

        return JsonResponse({
            "code": 2000,
            "msg": "success",
            "data": {
                'names' : names,
                'resonance_pairs' : resonance_pairs,
                'resonance_pairs_d' : resonance_pairs_d,
            }
        })

    def post(self, request, *args, **kwargs):
        return JsonResponse({
            "code": 2000,
            "msg": "success",
            "data": {}
        })
