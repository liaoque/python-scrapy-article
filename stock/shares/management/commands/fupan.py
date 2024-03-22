from django.core.management.base import BaseCommand, CommandError
# import talib
import numpy as np
import os

from shares.model.shares_join_block import SharesJoinBlock
from shares.model.shares_name import SharesName
from shares.model.shares_macd import SharesMacd
from shares.management.commands.wencai2 import rediangainnian
from shares.model.shares_date import SharesDate
from datetime import datetime, timedelta
from shares.model.shares_date_listen import SharesDateListen
from shares.model.shares_buys import SharesBuys


class Command(BaseCommand):
    help = "对每天进行复盘"

    etfs = []
    gns = []
    gps = []
    codes = []
    date = ""

    fp = 0
    fp_start = ""
    fp_end = ""
    fp_dates = ""

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
        self.date = "20240301"
        self.a()

        #
        # if self.fp == 1:
        #     self.fp_dates = SharesDate.objects.filter(date_as__gte=self.fp_start, date_as__lte=self.fp_start).order_by(
        #         'date_as')
        # else:
        #     self.fp_dates = SharesDate.objects.filter(date_as__lte=datetime.now().strftime('%Y%m%d')).order_by(
        #         '-date_as')
        # for i, d in self.fp_dates:
        #     self.date = d
        #     if not self.a():
        #         return
        #     if not self.etf():
        #         return
        #     self.gn()
        #     self.gp()
        #     self.saveGC()
        #
        # for i, d in self.fp_dates:
        #     self.hcGC(i)

    def macd(self, data):
        # 计算kd指标
        close_prices = np.array(data)
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
        if len(gn.gns) == 0:
            return
        self.gns = [item for item in list(set(gn.gns)) if item not in gn.dtgn]

    def gp(self):
        """
        根据 etf和gns 选出符合概念的股票
        获得股票池
        :return:
        """
        for gn in self.gns:
            codes = rediangainnian.codes(self.date, gn, self.etfs)
            # 计算macd，
            for code in codes:
                sharesKdjList = SharesMacd.objects.filter(code_id=codes).order_by('-date_as')[:3]
                if len(sharesKdjList) < 10:
                    continue
                last = sharesKdjList[0]
                last2 = sharesKdjList[1]
                last3 = sharesKdjList[2]
                if last > 0:
                    self.codes.append(code)
                elif last < 0:
                    if last > last2 > last3:
                        self.codes.append(code)
        #

    def saveGC(self):
        """
        股池
        :return:
        """
        for code in self.codes:
            transformed_data = SharesDateListen.objects.filter(date_as=self.date, code_id=code, type=11)
            if len(transformed_data) > 0:
                return
            SharesDateListen(
                buy_start=0,  # 4日涨跌幅
                date_as=self.date,
                code_id=code,
                p_start=0,
                buy_pre=0,
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
        if i + 2 >= len(self.fp_dates):
            return

        # 当天股池取前10
        codes = SharesDateListen.objects.filter(date_as=self.date, type=11).order_by('-buy_start')[:10]
        if len(codes) == 0:
            return

        """
        匹配4日涨跌幅，每个概念取前10个股票
        第二天强势概念 + 在以上10个股票里排序，然后取能买到的前排股票
        """

        # 查第二天强势概念， 32分之前涨停的股票，计算出的概念
        gps = []
        blocks = SharesJoinBlock.objects.filter(date_as=self.date, code_id__in=gps)
        gns = []
        for code in codes:
            d2 = SharesJoinBlock.objects.filter(date_as=self.date, code_id__in=codes)
            if len(d2) == 0:
                continue
            # d2 = d

        # SharesDateListen.objects.filter(date_as=self.date, code_id=code)

        for code in codes:
            """
            买入算第一天
            卖出算第三天
            检查有没有持有中的股票，如果有不操作， 如果没有设置买入价格
            再检查是否在股池里面， 如果在就持有，如果不再，以第二天开盘价卖掉
            
            持有股票检测方法
            1. 今天之前的股池
            2. 买入 > 0
            3. 卖出 = 0
            """
            d2 = SharesDateListen.objects.filter(date_as__lte=self.date, type=11, code_id=code, p_start=0,
                                                 buy_pre__gte=0)
            if len(d2) == 0:
                # 查当前最高价， 算当天最高价买入
                b = SharesBuys(
                    code_id=code,
                    buy_date_as=self.date,
                    buy_start=self.date,
                )
                c = SharesDateListen.objects.filter(date_as=self.date, code_id=code)
                code.p_start = c.m
                code.buy_date_as = self.date
                code.save()
            else:
                # 持有
                code.date_as = self.date
                code.save()

        """
        查持有的股票
        第二天该股票没在股池， 则按第三天的开盘价卖掉
        """
        codes = SharesDateListen.objects.filter(date_as=self.date, p_start=0, buy_pre__gte=0, type=11)
        for code in codes:
            d2 = SharesDateListen.objects.filter(date_as=self.dates[i + 1], type=11, code_id=code)
            if len(d2) == 0:
                # 查当前最高价， 算当天最高价买入
                c = SharesDateListen.objects.filter(date_as=self.dates[i + 2], code_id=code)
                code.p_start = c.m
                code.save()

    def tgYk(self):
        """
        统计盈亏
        select sum(p_start- buy_pre) from mc_shares_date_listen where buy_pre >0 and type=11 and p_start=0
        :return:
        """
