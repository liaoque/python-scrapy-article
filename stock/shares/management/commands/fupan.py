from django.core.management.base import BaseCommand, CommandError
import talib
import numpy as np

from q6m5mdown import data
from shares.model.shares_join_block import SharesJoinBlock
from shares.model.shares_name import SharesName
from shares.model.shares_macd import SharesMacd
from shares.management.commands.wencai2 import rediangainian
from shares.model.shares_date import SharesDate
from datetime import datetime, timedelta
from shares.model.shares_date_listen import SharesDateListen


class Command(BaseCommand):
    help = "对每天进行复盘"

    etfs = []
    gns = []
    gps = []
    codes = []
    date = ""

    def handle(self, *args, **options):
        self.date = SharesDate.objects.filter(date_as__lte=datetime.now().strftime('%Y%m%d')).order_by('-date_as')[0]
        if not self.a():
            return
        if not self.etf():
            return
        self.gn()
        self.gp()

    def macd(self, data):
        # 计算kd指标
        close_prices = np.array([v.p_end / 100 for v in data])
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

            return 1
        elif last < 0:
            print("a: macd < 0")
            if last > last2 > last3:
                print("a: 适量低吸")
                return 2
            elif last < last2:
                print("a: 停止交易")
                return 0
        else:
            print("保持现状")

        return 3

    def a(self):
        """
        对大盘进行复盘
        :return:
        """
        self.computeMacd(data)

    def etf(self):
        """
        对 A50， 沪深300，中证500，中证1000，中证2000
        :return:
        """
        if self.A50():
            self.etfs.append("A50")
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
        return self.computeMacd(data)

    def hs300(self):
        """
        对 沪深300 复盘
        :return:
        """
        return self.computeMacd(data)

    def zt500(self):
        """
        对中小板复盘
        :return:
        """
        return self.computeMacd(data)

    def zt1000(self):
        """
        对中小板复盘
        :return:
        """
        return self.computeMacd(data)

    def zt2000(self):
        """
        对中小板复盘
        :return:
        """
        return self.computeMacd(data)

    def gn(self):
        """
        近期热点概念, 并排除跌停和炸板的概念
        :return:
        """
        gn = rediangainian.rdgainian(self.date)
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
            codes = rediangainian.codes(self.date, gn, self.etfs)
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
        无脑选股，排除利空
         匹配4日涨跌幅，每个概念取前10个股票
        第二天强势概念 + 在以上10个股票里排序，然后取能买到的前排股票
        :return:
        """
        for code in self.codes:
            transformed_data = SharesDateListen.objects.filter(date_as=self.date, code_id=code, type=11)
            if len(transformed_data) > 0:
                return
            SharesDateListen(
                buy_date_as=self.date,
                date_as=self.date,
                code_id=code,
                p_start=0,
                buy_pre=0,
                type=11
            ).save()
