import os

from django.shortcuts import render
import json
# Create your views here.
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dvadmin.wb.core import init_data, streak_rise, bu_zhang, suo_shu_gai_nian, pi_pei_gai_nian, gn, jie_guo, \
    biao_shai_xuan, yuan_yin_data
from application.settings import DATABASES
import time
from pymongo import MongoClient
import string

from django.views import View
from dvadmin.wb.config import code_config

@method_decorator(csrf_exempt, name='dispatch')
class Config(View):
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
        # self.client = MongoClient(DATABASES['wb']['CLIENT']['host'],
        #                           DATABASES['wb']['CLIENT']['port'])  # 默认连接到 localhost 和端口 27017
        # self.db = self.client['wb']  # 选择你的数据库

    # def __del__(self):
        # self.client.close()

    def get(self, request, *args, **kwargs):
        config = code_config.CodeConfig().getCodeConfig()


        return JsonResponse({
            "code": 2000,
            "msg": "success",
            "data": {
                "gvgn": config["gvgn"],
                "chuang_ye_set": config["chuang_ye_set"],
                "zhu_set": config["zhu_set"],
                "cm10": config["10cm"],
                "cm10": config["20cm"],
                "lian_ban_code_black": config["lian_ban_code_black"],
            }
        })

    def post(self, request, *args, **kwargs):
        info = json.loads(request.body.decode())
        configfile = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', 'config/data.json'))
        with open(configfile, "w+") as outfile:
            json.dump({
                "fd": 0,
                "yd": 0,
                "gvgn": info["gvgn"],
                "chuang_ye_set": info["chuang_ye_set"],
                "zhu_set": info["zhu_set"],
                "10cm": info["cm10"],
                "20cm": info["cm20"],
                "lian_ban_code_black": info["lian_ban_code_black"],
            }, outfile)

        return JsonResponse({
            "code": 200,
            "msg": "success",
            "data": {
            }
        })
