import requests
import re
import numpy as np
from datetime import datetime, timedelta

from shares.management.commands.wencai2 import trend, trendCode, acodes, common, pic_n, zhangTing, dingding
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
    f32GN = None
    s = ""

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def codeGetCode(self, d2, yesterday):
        result32 = list(filter(lambda item: item["f32"] == 1, d2))
        if len(result32) == 0:
            return
        # 取高标股票概念
        resultGB = list(filter(lambda item: item["gao_biao"] == 1, d2))
        sharesZhangTings = SharesZhangTings.objects.filter(date_as=yesterday, gao_biao=1)
        result = [item['股票代码'] for item in resultGB] + [item.code_id for item in sharesZhangTings]
        blockGBGN = SharesJoinBlock.objects.filter(code_id__in=result, code_type=2)
        blockGBGN = [item.block_code_id for item in blockGBGN]

        resultF32 = [item["股票代码"] for item in result32]
        # 32分存在强势票
        # 查昨日高标
        # 合并后匹配概念
        sql = """
               select 1 as id, block_code_id, mc_shares_block_gns.name, count(1) as c
                from mc_shares_join_block
                left join (select code_id,name from mc_shares_block_gns group by code_id) as mc_shares_block_gns on mc_shares_block_gns.code_id = mc_shares_join_block.block_code_id 
                where mc_shares_join_block.code_type = 2 and mc_shares_join_block.code_id in ( 
                %s
                ) and mc_shares_join_block.block_code_id not in (301639)
                group by block_code_id
                having  c > 1
            """ % (",".join(resultF32))
        # print(sql)
        self.s = "32分涨停股票：" + ",".join(resultF32)

        result = SharesJoinBlock.objects.raw(sql, params=())
        if len(result) == 0:
            return []

        self.f32GN = [item.block_code_id for item in result]
        for item in result:
            if item.block_code_id in blockGBGN:
                item.c += 1

        # 排序, 取前3
        result = sorted(result, key=lambda x: x.c, reverse=True)
        # print(result)
        if len(result) > 2:
            c = result[2].c
        else:
            c = result[len(result) - 1].c
        result = "且".join([item.name for item in list(filter(lambda item: item.c >= c, result))])
        self.s = self.s + "\n\r" + result
        # 查對應概念股票
        codes = zhangTing.search(result)
        return codes

    def handle(self, *args, **options):
        # 昨天日期
        yesterday = SharesDate.objects.filter(date_as__lt=datetime.today().strftime('%Y-%m-%d')).order_by("-date_as")[
            0].date_as

        t = datetime.today().strftime('%Y%m%d')
        t2 = datetime.today().strftime('%Y%m%d')
        codes = zhangTing.zhangTing(t)
        time_str = '09:30:00'
        start_seconds = time2seconds(time_str)

        time_str = '09:32:00'
        end_seconds = time2seconds(time_str)
        d2 = []
        for item in codes:
            d = self.initD(item, start_seconds, end_seconds)
            if d["date"] != t2:
                return
            d2.append(d)

        # 取f32股票
        codes = self.codeGetCode(d2, yesterday)
        # print(codes)
        if codes != None:
            self.s = self.s + "\n\r".join([item["股票简称"] + " ---- " + item["最新涨跌幅"] for item in codes])

        # 查当天涨幅前2概念
        d2 = []
        for i in range(5):
            codes = zhangTing.zhangTingGns(t2, i)
            for item in codes:
                d = self.initD2(item)
                d2.append(d)
        unique_arr = set()
        d3 = []
        for d in d2:
            if d['指数代码'] in unique_arr:
                continue
            unique_arr.add(d['指数代码'])
            d3.append(d)

        d2 = d3
        result = sorted(d2, key=lambda x: x["涨跌幅"], reverse=True)[0:2]

        # 今日前2概念对应股票
        todaySharesJoinBlocks = SharesJoinBlock.objects.filter(block_code_id__in=[item['指数代码'] for item in result])

        # 昨天涨幅前2概念
        yeasterdayGns = SharesBlockGns.objects.filter(date_as=yesterday).order_by(
            "-p_zhang_die_fu")[0:2]

        # 昨天涨幅前2概念对应股票
        yeasterSharesJoinBlocks = SharesJoinBlock.objects.filter(block_code_id__in=[item.code_id for item in yeasterdayGns])

        # 股票中昨天涨停的股票
        yesterdayZhangTings = SharesZhangTings.objects.filter(date_as=yesterday,
                                                              code_id__in=[item.code_id for item in yeasterSharesJoinBlocks]
                                                              )

        # 当天概念
        # 匹配前天涨停股票
        self.s = "\n\r".join([
            self.s,
            "今日概念发酵: " + " , ".join(
                [item["指数简称"] for item in result]),
            "昨晚概念：" + " , ".join(
                [item.name for item in yeasterdayGns]),
            "持续股票："+ " , ".join(
                [
                    item.code_id for item in list(filter(lambda x:x.code_id in [item.code_id for item in todaySharesJoinBlocks]  , yesterdayZhangTings))
                ]),
        ])
        dingding.dingding(self.s)

        # 查复盘股票

        for item in result:
            code = item["指数简称"]


        # yeasterdayGnIds = [yeasterdayGns.code_id]
        # 32分强势票概念

        # if item["指数代码"] not in self.f32GN:
        #     continue
        # if item["指数代码"]  in yeasterdayGnIds:
        #     continue
        # yeasterdayGns.append(item["指数代码"])

        # print(item["股票简称"], yeasterdayGns.name)

    def initD(self, item, start_seconds, end_seconds):
        d = {}
        d["股票代码"] = item["股票代码"][:-3]
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

        first_zhangting_time = time2seconds(d["首次涨停时间"])
        if first_zhangting_time > start_seconds and first_zhangting_time < end_seconds:
            # print(d)
            d["f32"] = 1
            return d

        if d["连续涨停天数"] >= 4:
            numbers = re.findall(r'\d+', d["几天几板"])
            number2 = int(numbers[1])  # 13
            if number2 >= 8:
                #     高标
                d["gao_biao"] = 1
                return d

        if d["连续涨停天数"] >= 5:
            #     高标
            d["gao_biao"] = 1
            return d
        return d

    def initD2(self, item):
        d = {}
        d["指数代码"] = item["指数代码"][:-3]
        d["指数简称"] = item["指数简称"]
        for key, value in item.items():
            if "指数@开盘价:不复权[" in key:
                d["开盘价"] = value
                d["date"] = key[-9:-1]
            if "指数@收盘价:不复权[" in key:
                d["收盘价"] = value
            if "指数@最低价:不复权[" in key:
                d["最低价"] = value
            if "指数@最高价:不复权[" in key:
                d["最高价"] = value
            if "指数@涨跌幅:前复权[" in key:
                d["涨跌幅"] = value
        return d
