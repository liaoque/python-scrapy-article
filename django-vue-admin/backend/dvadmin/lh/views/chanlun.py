import os

from django.shortcuts import render
import json
# Create your views here.
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dvadmin.lh.utils.dfcf import gp as gp
from dvadmin.lh.utils.chanlun import bi, buy, zhongshu
from dvadmin.lh.utils.baostock import gp as baostockgp
import pandas as pd
import numpy as np
from django.views import View
from datetime import datetime


@method_decorator(csrf_exempt, name='dispatch')
class ChanlunView(View):
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    # self.client = MongoClient(DATABASES['wb']['CLIENT']['host'],
    #                           DATABASES['wb']['CLIENT']['port'])  # 默认连接到 localhost 和端口 27017
    # self.db = self.client['wb']  # 选择你的数据库

    # def __del__(self):
    # self.client.close()

    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        data = gp.GetGjList(code)
        data = [ item.split(",") for item in data["data"]["klines"]]
        df = pd.DataFrame({
            'date': [item[0] for item in data],
            'open': [float(item[1]) for item in data],
            'high': [float(item[3])  for item in data],
            'low': [float(item[4])  for item in data],
            'close': [float(item[2])  for item in data],
        })
        df.set_index('date', inplace=True)
        bi_list = bi.bi(df)

        data = baostockgp.GetGjList(code, data[0][0], data[-1][0], 30)
        df = pd.DataFrame({
            'date': [ datetime.strptime(item[1],  '%Y%m%d%H%M%S%f').strftime('%Y-%m-%d %H:%M:%S') for item in data],
            'open': [float(item[3]) for item in data],
            'high': [float(item[4]) for item in data],
            'low': [float(item[5]) for item in data],
            'close': [float(item[6]) for item in data],
        })
        df.set_index('date', inplace=True)
        bi_list30 = bi.bi(df)

        pivots = zhongshu.construct_zhongshu_with_tolerance(bi_list30, kline_df=df)
        signals = buy.generate_trading_signals(df, pivots, bi_list30, confirmation_count=3)
        pivots = zhongshu.convert_30m_pivot_to_daily(pivots)
        signals = buy.convert_30m_signal_to_daily(signals)
        return JsonResponse({
            "code": 2000,
            "msg": "success",
            "data": {
                "bi_list": bi_list,
                "pivots": pivots,
                "signals": signals,
            }
        })

    def post(self, request, *args, **kwargs):
        return JsonResponse({
            "code": 2000,
            "msg": "success",
            "data": {
            }
        })
