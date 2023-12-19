import requests
import re
import numpy as np
from datetime import datetime, timedelta

from shares.management.commands.wencai2 import trend, trendCode, acodes, common, pic_n, zhangTing
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from collections import OrderedDict
from shares.model.shares import Shares
from shares.model.shares_zhang_tings import SharesZhangTings
from shares.model.shares_block_gns import SharesBlockGns
from shares.model.shares_date import SharesDate
from shares.model.shares_join_block import SharesJoinBlock


def time2seconds(time_str):
    time_format = '%H:%M:%S'  # 时间字符串的格式
    time_obj = datetime.strptime(time_str, time_format)
    return timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second).total_seconds()


class Command(BaseCommand):
    help = '15点收盘以后记录数据'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        t = datetime.today().strftime('[%Y%m%d]')
        t2 = datetime.today().strftime('%Y%m%d')
        codes = zhangTing.zhangTing(t)

        time_str = '09:30:00'
        start_seconds = time2seconds(time_str)

        time_str = '09:32:00'
        end_seconds = time2seconds(time_str)
        for item in codes:
            d = {}
            d["股票代码"] = item["股票代码"]
            d["股票简称"] = item["股票简称"]
            d["所属概念"] = item["所属概念"]
            d["所属同花顺行业"] = item["所属同花顺行业"]
            d["gao_biao"] = 0
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

            if "最终涨停时间" not in d.keys():
                print(item)
                continue

            if d["date"] != t2:
                return

            first_zhangting_time = time2seconds(d["首次涨停时间"])
            if first_zhangting_time > start_seconds and first_zhangting_time < end_seconds:
                d["f32"] = 1

            if d["连续涨停天数"] >= 4:
                numbers = re.findall(r'\d+', d["几天几板"])
                # number1 = int(numbers[0])  # 22
                number2 = int(numbers[1])  # 13
                if number2 >= 8:
                    #     高标
                    d["gao_biao"] = 1

            if d["连续涨停天数"] >= 5:
                #     高标
                d["gao_biao"] = 1


            date_obj = datetime.strptime(d["date"], '%Y%m%d')
            formatted_date = date_obj.strftime('%Y-%m-%d')
            if SharesZhangTings.objects.filter(code_id=d["股票代码"], date_as=formatted_date).count():
                continue

            sharesZhangTings = SharesZhangTings(
                code_id=d["股票代码"],
                name=d["股票简称"],
                gn=d["所属概念"],
                hy=d["所属同花顺行业"],
                first_zhang_ting=d["首次涨停时间"],
                last_zhang_ting=d["最终涨停时间"],
                n_day_n_zhang_ting=d["几天几板"],
                continuous_zhang_ting=d["连续涨停天数"],
                liu_tong_shi_zhi=int(float(d["a股市值流通市值"])),
                date_as=formatted_date,
                f32=d["f32"],
                gao_biao=d["gao_biao"]
            )
            sharesZhangTings.save()

        # 保存到 SharesZhangTings
        # SharesZhangTings.objects.filter(date_as=sharesDate[0].date_as, gao_biao__gt=1)

        # 取当天热门概念 保存到 SharesBlockGns
        #
        t = datetime.today().strftime('%Y%m%d')
        codes = zhangTing.zhangTingGns(t)
        for item in codes:
            d = {}
            d["指数代码"] = item["指数代码"]
            d["指数简称"] = item["指数简称"]
            for key, value in item.items():
                if "指数@开盘价:不复权[" in key:
                    d["开盘价"] = value.replace(" ", "")
                    d["date"] = key[-9:-1]
                if "指数@收盘价:不复权[" in key:
                    d["收盘价"] = value
                if "指数@最低价:不复权[" in key:
                    d["最低价"] = value
                if "指数@最高价:不复权[" in key:
                    d["最高价"] = value.replace(" ", "")
                if "指数@涨跌幅:前复权[" in key:
                    d["涨跌幅"] = value

            date_obj = datetime.strptime(d["date"], '%Y%m%d')
            formatted_date = date_obj.strftime('%Y-%m-%d')
            if SharesBlockGns.objects.filter(code_id=d["指数代码"], date_as=formatted_date).count():
                continue

            sharesZhangTings = SharesBlockGns(
                code_id=d["指数代码"],
                name=d["指数简称"],
                p_min=d["最低价"],
                p_max=d["最高价"],
                p_start=d["开盘价"],
                p_end=d["收盘价"],
                p_zhang_die_fu=d["涨跌幅"],
                date_as=formatted_date,
            )
            sharesZhangTings.save()
