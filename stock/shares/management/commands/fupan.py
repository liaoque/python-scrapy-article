from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

import talib
import numpy as np
import os
import re

from shares.model.shares_join_block import SharesJoinBlock
from shares.model.shares_name import SharesName
from shares.model.shares_macd import SharesMacd
from shares.management.commands.wencai2 import rediangainnian, zhangTing
from shares.model.shares_date import SharesDate
from datetime import datetime, timedelta
from shares.model.shares_date_listen import SharesDateListen
from shares.model.shares_buys import SharesBuys
from shares.model.shares_zhang_tings import SharesZhangTings
from shares.model.shares import Shares


def time2seconds(time_str):
    time_format = '%H:%M:%S'  # 时间字符串的格式
    time_obj = datetime.strptime(time_str, time_format)
    return timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second).total_seconds()


class Command(BaseCommand):
    help = "对每天进行复盘"

    etfs = []
    gns = []
    gps = []
    codes = []
    date = ""

    fp = 1
    fp_start = "2024-01-01"
    fp_end = ""
    fp_dates = "2024-04-01"

    stop = False

    data = {
        "a": [],
        "a50": [],
        "hs300": [],
        "zt500": [],
        "zt1000": [],
        "zt2000": [],
    }

    def handle(self, *args, **options):
        """
        fp 是否开启复盘回测
        fp_start 开启复盘回测的具体开始日期
        fp_end 开启复盘回测的具体结束日期
        fp_dates 开始日期和结束日期的所有日期
        :param args:
        :param options:
        :return:
        """
        if self.fp == 1:
            self.fp_dates = SharesDate.objects.filter(date_as__gte=self.fp_start, date_as__lte=self.fp_dates).order_by(
                'date_as')
        else:
            self.fp_dates = SharesDate.objects.filter(date_as__lte=datetime.now().strftime('%Y-%m-%d')).order_by(
                '-date_as')[:2]
            self.fp_dates = sorted(self.fp_dates, key=lambda x: x.date_as, reverse=False)

        for d in self.fp_dates:
            break
            self.etfs = []
            self.gns = []
            self.gps = []
            self.codes = []
            self.date = d.date_as.strftime("%Y%m%d")
            self.a()
            self.etf()
            self.gn()
            self.gp()
            self.saveGC()

        i = 0
        for d in self.fp_dates:
            self.date = d.date_as.strftime("%Y%m%d")
            self.hcGC(i)
            i += 1

    def macd(self, data):
        # 计算kd指标
        close_prices = np.array([float(item) for item in data])
        macdDIFF, macdDEA, macd = talib.MACDEXT(close_prices, fastperiod=12, fastmatype=1, slowperiod=26,
                                                slowmatype=1,
                                                signalperiod=9, signalmatype=1)
        macd = macd * 2
        return (macdDIFF, macdDEA, macd)

    def computeMacd(self, data):
        macdDIFF, macdDEA, macd = self.macd(data)
        last = macd[len(macd) - 1]
        last2 = macd[len(macd) - 2]
        last3 = macd[len(macd) - 3]
        if last > 0:
            return True
        elif last < 0:
            if last > last2 > last3:
                return True
            elif last < last2:
                self.stop = True
                return False
        return True

    def a(self):
        """
        对大盘进行复盘
        :return:
        """
        self.stop = False
        data = self.data["a"]
        if len(self.data["a"]) == 0:
            data = self.data["a"] = rediangainnian.zhishu("1.000001")
        data = [item.split(",")[1] for item in data if
                item.split(",")[0].replace("-", "") <= self.date]
        return self.computeMacd(data)

    def etf(self):
        """
        对 中证A50， 沪深300，中证500，中证1000，中证2000
        :return:
        """
        self.etfs = []
        if self.A50():
            self.etfs.append("a50")
        if self.hs300():
            self.etfs.append("hs300")
        if self.zt500():
            self.etfs.append("zt500")
        if self.zt1000():
            self.etfs.append("zt1000")
        if self.zt2000():
            self.etfs.append("zt2000")

    def A50(self):
        """
        对 A50 复盘
        :return:
        """
        data = self.data["a50"]
        if len(self.data["a50"]) == 0:
            data = self.data["a50"] = rediangainnian.zhishu("2.930050")
        data = [item.split(",")[1] for item in data if
                item.split(",")[0].replace("-", "") <= self.date]
        return self.computeMacd(data)

    def hs300(self):
        """
        对 沪深300 复盘
        :return:
        """
        data = self.data["hs300"]
        if len(self.data["hs300"]) == 0:
            data = self.data["hs300"] = rediangainnian.zhishu("1.000300")
        data = [item.split(",")[1] for item in data if
                item.split(",")[0].replace("-", "") <= self.date]
        return self.computeMacd(data)

    def zt500(self):
        """
        对中小板复盘
        :return:
        """
        data = self.data["zt500"]
        if len(self.data["zt500"]) == 0:
            data = self.data["zt500"] = rediangainnian.zhishu("1.000905")
        data = [item.split(",")[1] for item in data if
                item.split(",")[0].replace("-", "") <= self.date]
        return self.computeMacd(data)

    def zt1000(self):
        """
        对中小板复盘
        :return:
        """
        data = self.data["zt1000"]
        if len(self.data["zt1000"]) == 0:
            data = self.data["zt1000"] = rediangainnian.zhishu("1.000852")
        data = [item.split(",")[1] for item in data if
                item.split(",")[0].replace("-", "") <= self.date]
        return self.computeMacd(data)

    def zt2000(self):
        """
        对中小板复盘
        :return:
        """
        data = self.data["zt2000"]
        if len(self.data["zt2000"]) == 0:
            data = self.data["zt2000"] = rediangainnian.zhishu("2.932000")
        data = [item.split(",")[1] for item in data if
                item.split(",")[0].replace("-", "") <= self.date]
        return self.computeMacd(data)

    def gn(self):
        """
        近期热点概念, 并排除跌停和炸板的概念
        :return:
        """
        gn = rediangainnian.rdgainian(self.date)

        if len(gn["gn"]) == 0:
            return
        print(list(set(gn["gn"])))
        print(list(set(gn["dtgn"])))
        self.gns = [item for item in list(set(gn["gn"])) if item not in gn["dtgn"]]

    def gp(self):
        """
        根据 etf和gns 选出符合概念的股票
        获得股票池
        :return:
        """
        etf = {
            "a50": "上证50",
            "hs300": "沪深300",
            "zt500": "中证500",
            "zt1000": "中证1000",
            "zt2000": "中证2000",
        }
        date_obj = datetime.strptime(self.date, "%Y%m%d")
        cdate = SharesDate.objects.filter(date_as__lte=date_obj.strftime("%Y-%m-%d")).order_by('-date_as')[:125]
        self.codes = []
        etfs = "或".join([etf[item] for item in self.etfs])
        code33 = []
        for gn in self.gns:
            codes = rediangainnian.codes(cdate, gn, etfs)
            # 计算macd，
            for code in codes:
                if code["code"] in code33:
                    continue

                sharesKdjList = SharesMacd.objects.filter(code_id=code["code"]).order_by('-date_as')[:11]
                if len(sharesKdjList) < 10:
                    continue
                last = sharesKdjList[0].macd
                last2 = sharesKdjList[1].macd
                last3 = sharesKdjList[2].macd
                if last > 0:
                    self.codes.append(code)
                    code33.append(code["code"])
                elif 0 > last > last2 > last3:
                    self.codes.append(code)
                    code33.append(code["code"])
        #

    def saveGC(self):
        """
        股池
        :return:
        """
        new_date_str = self.date[:4] + "-" + self.date[4:6] + "-" + self.date[6:]
        codes = self.codes
        for code in codes:
            print(code["code"], new_date_str)
            # return
            transformed_data = SharesDateListen.objects.filter(date_as=new_date_str, code_id=code["code"], type=11)
            if len(transformed_data) > 0:
                continue
            # fr = code["区间涨跌幅:前复权[%s]"%(self.date)]
            for key, item in code.items():
                if key.find("区间涨跌幅:前复权[") != -1:
                    fr = code[key]
            print(fr)
            # return
            SharesDateListen(
                buy_start=0,
                date_as=new_date_str,
                code_id=code["code"],
                p_start=0,
                buy_pre=fr * 1000,  # 4日涨跌幅
                type=11
            ).save()

    def hcGC(self, i):
        """
        回测, 做多两种逻辑， 1买入反转， 2买入持续，这个是2
        :return:
        """
        if self.fp != 1:
            return
        if i == 0:
            return

        new_date_str = self.date[:4] + "-" + self.date[4:6] + "-" + self.date[6:]
        """
        查当天强势概念， 32分之前涨停的股票，计算出的概念
        找出这些概念的所有的相关股票
        """
        f32Gns = self.codeGetGn()
        # print(f32Gns)
        f32Gns2 = [item["block_code_id"] for item in f32Gns]
        f32Result = SharesJoinBlock.objects.filter(block_code_id__in=f32Gns2)
        f32Codes = [code.code_id for code in f32Result]

        """
        查持有的股票，买入时间是今天之前的，且与当天概念不匹配的股票
        按今天收盘价卖出
        跌停价无法卖出
        """
        codes2 = SharesBuys.objects.filter(~Q(code_id__in=f32Codes), buy_date_as__lt=new_date_str, sell_end=0)
        for code in codes2:
            result = Shares.objects.filter(code_id=code.code_id, date_as=new_date_str)
            if len(result) == 0:
                print("no found sell ", code.code_id, new_date_str)
                continue
            result = result[0]
            if result.p_range <= -9.7:
                continue
            code.sell_end = result.p_end
            code.sell_date_as = new_date_str
            code.save()

        if self.stop:
            return

        """
        根据强势概念相关的股票匹配股池的股票
        匹配4日涨跌幅，取前3
        """
        date = self.fp_dates[i - 1].date_as
        codes2 = SharesDateListen.objects.filter(date_as=date, type=11, code_id__in=f32Codes).order_by("-buy_pre")
        if len(codes2) == 0:
            return

        codes2 = codes2[:5]
        for code in codes2:
            """
            买入价是当天最高价
            涨停价无法买入，且只买一个股票
            """
            d2 = SharesBuys.objects.filter(buy_date_as__lt=new_date_str, code_id=code.code_id, buy_start__gte=0)
            if len(d2) == 0:
                result = Shares.objects.filter(code_id=code.code_id, date_as=new_date_str)
                if len(result) == 0:
                    print("no found buy", code.code_id, new_date_str)
                    continue
                result = result[0]
                if result.p_range >= 9.7:
                    continue
                # 查当前最高价， 算当天最高价买入
                b = SharesBuys(
                    code_id=code.code_id,
                    buy_date_as=new_date_str,
                    buy_start=result.p_max,
                )
                b.save()
                break

    def tgYk(self):
        """
        统计盈亏
        select sum(p_start- buy_pre) from mc_shares_date_listen where buy_pre >0 and type=11 and p_start=0
        :return:
        """

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

    def codeGetGn(self):
        codes = zhangTing.zhangTing(self.date)
        time_str = '09:30:00'
        start_seconds = time2seconds(time_str)

        time_str = '09:32:00'
        end_seconds = time2seconds(time_str)
        d2 = []
        for item in codes:
            d = self.initD(item, start_seconds, end_seconds)
            d2.append(d)

        result32 = list(filter(lambda item: item["f32"] == 1, d2))
        if len(result32) == 0:
            return []
        # 32分涨停股票
        resultF32 = [item["股票代码"] for item in result32]

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
        result = SharesJoinBlock.objects.raw(sql, params=())
        if len(result) == 0:
            return []
        f32GN = {}
        for item in result:
            if item.block_code_id not in f32GN:
                f32GN[item.block_code_id] = {
                    "block_code_id": item.block_code_id,
                    "c": 0
                }
            f32GN[item.block_code_id]["c"] += 1

        gns = [item[1]["c"] for item in f32GN.items()]
        result2 = sorted(list(set(gns)), key=lambda x: x, reverse=True)[:2]
        minGn = min(result2)
        result = filter(lambda item: item[1]["c"] >= minGn, f32GN.items())

        return [item[1] for item in result]
