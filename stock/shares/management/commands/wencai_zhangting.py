import requests
import re
import numpy as np
from datetime import datetime, timedelta

from shares.management.commands.wencai2 import trend, trendCode, acodes, common, pic_n, zhangTing
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from collections import OrderedDict
from shares.model.shares import Shares

def time2seconds(time_str):
    time_format = '%H:%M:%S'  # 时间字符串的格式
    time_obj = datetime.strptime(time_str, time_format)
    return timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second).total_seconds()


class Command(BaseCommand):
    help = '观察32分涨停股票'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        t = datetime.today().strftime('[%Y%m%d]')
        codes = zhangTing.zhangTing(t)

        time_str = '09:30:00'
        start_seconds = time2seconds(time_str)

        time_str = '09:32:00'
        end_seconds = time2seconds(time_str)
        d2 = []
        for item in codes:
            d = {}
            d["股票代码"] = item["股票代码"]
            d["股票简称"] = item["股票简称"]
            d["所属概念"] = item["所属概念"]
            d["所属同花顺行业"] = item["所属同花顺行业"]
            d["gaobiao"] = 0
            d["f32"] = 0
            for key, value in item.items():
                if "首次涨停时间[" in key:
                    d["首次涨停时间"] = value.replace(" ", "")
                    d["date"] = key[-9:-1]
                if "几天几板[" in key:
                    d["几天几板"] = value
                if "连续涨停天数[" in key:
                    d["连续涨停天数"] = value
                if "最终涨停时间[" in key:
                    d["最终涨停时间"] = value.replace(" ", "")
                if "a股市值(不含限售股)[" in key:
                    d["a股市值流通市值"] = value

            d2.append(d)

            first_zhangting_time = time2seconds(d["首次涨停时间"])
            print(d["首次涨停时间"], first_zhangting_time, start_seconds, end_seconds)
            if first_zhangting_time > start_seconds and first_zhangting_time < end_seconds:
                d["f32"] = 1
                continue

            if d["连续涨停天数"] >= 4 :
                numbers = re.findall(r'\d+', d["几天几板"])
                # number1 = int(numbers[0])  # 22
                number2 = int(numbers[1])  # 13
                if number2 >= 8:
                #     高标
                    d["gaobiao"] = 1
                    continue
                pass

            if d["连续涨停天数"] >= 5 :
                #     高标
                d["gaobiao"] = 1
                continue


        result = list(filter(lambda item: item["gaobiao"] == 1 or item["f32"] == 1, d2))
        if len(result) > 1:
            sql = """
                   select block_code_id, count(1) as c
                   from mc_shares_join_block
                   where mc_shares_join_block.code_type = 2
                       and mc_shares_join_block.code not in (
                       %s
                       )
                   group by block_code_id
                    having  c > 0
                """
            result = Shares.objects.raw(sql, params=(",".join([item["股票代码"][:-3] for item in result]),))
