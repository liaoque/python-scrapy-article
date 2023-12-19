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
    help = '观察32分涨停股票'

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

            if d["date"] != t2:
                return
            d2.append(d)

            first_zhangting_time = time2seconds(d["首次涨停时间"])
            print(d["首次涨停时间"], first_zhangting_time, start_seconds, end_seconds)
            if first_zhangting_time > start_seconds and first_zhangting_time < end_seconds:
                d["f32"] = 1
                continue

            if d["连续涨停天数"] >= 4:
                numbers = re.findall(r'\d+', d["几天几板"])
                number2 = int(numbers[1])  # 13
                if number2 >= 8:
                    #     高标
                    d["gaobiao"] = 1
                    continue

            if d["连续涨停天数"] >= 5:
                #     高标
                d["gaobiao"] = 1
                continue

        # 昨天日期
        sharesDate = SharesDate.objects.filter(date_as__lt=datetime.today().strftime('%Y-%m-%d')).order_by("-date_as")

        result = list(filter(lambda item: item["gaobiao"] == 1 or item["f32"] == 1, d2))
        result_f32 = [item["股票代码"] for item in result]
        if len(result) > 1:
            # 32分存在强势票
            # 查昨日高标
            # 合并后匹配概念
            sharesZhangTings = SharesZhangTings.objects.filter(date_as=sharesDate[0].date_as, gao_biao__gt=1)
            result = result_f32 + [item['code'] for item in sharesZhangTings]
            sql = """
                   select block_code_id, mc_shares_name.name, count(1) as c
                   left join mc_shares_name on mc_shares_name.code = mc_shares_join_block.block_code_id 
                            and mc_shares_name.code_type = 4
                   from mc_shares_join_block
                   where mc_shares_join_block.code_type = 2
                       and mc_shares_join_block.code in (
                       %s
                       )
                   group by block_code_id
                    having  c > 0
                """
            result = Shares.objects.raw(sql, params=(",".join([item["股票代码"] for item in result]),))

        # 查当天涨幅前三概念
        todayGns = list()
        yeasterdayGns = SharesBlockGns.objects.filter(date_as=sharesDate[0].date_as, gao_biao__gt=1).order_by(
            "-p_zhang_die_fu")[0:3]

        sharesJoinBlocks = SharesJoinBlock.objects.filter(code_type=2, code__in=result_f32)
        # for item in sharesJoinBlocks:
        #     todayGns.append(item.code)
        result_gns = {}
        for item in sharesJoinBlocks:
            if item.name not in result_gns:
                result_gns[item.name] = 1
            else:
                result_gns[item.name] += 1

        for item in yeasterdayGns:
            if item.name not in result_gns:
                result_gns[item.name] = 1
            else:
                result_gns[item.name] += 1

        for item in todayGns:
            if item.name not in result_gns:
                result_gns[item.name] = 1
            else:
                result_gns[item.name] += 1

        result_gns = filter(lambda item: item[1] > 1, result_gns.items())
        result_gns = sorted(list(result_gns), key=lambda item: item[1], reverse=True)
