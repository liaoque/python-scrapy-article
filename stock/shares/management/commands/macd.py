import numpy as np
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares_macd import SharesMacd
from shares.model.shares import Shares
from shares.model.shares_kdj_compute import SharesKdjCompute
from shares.model.shares_kdj_compute_detail import SharesKdjComputeDetail
# from ....shares.model.shares_kdj import SharesKdj
# from ....shares.model.shares import Shares
import numpy as np
import talib

" /bin/cp /alidata/python/python-scrapy-article/stock/* /alidata/python/python-scrapy-article-master/stock -rf"


class Command(BaseCommand):
    help = '计算各种指标'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        today = datetime.now().date().strftime('%Y-%m-%d')
        # self.calculateKdj(today)
        # print("开始计算kdj-----")
        # today = datetime.now().date().strftime('%Y-%m-%d')
        # self.KdjCompute(today)
        dateList = self.getAllDates()
        yesterday = dateList[-2].date_as
        sql = """
                SELECT 1 as id, m.code_id, m.diff,m.dea, t.diff as diff2,t.dea as dea2
                from (select * from mc_shares_macd where date_as = %s) m
                LEFT JOIN (select * from mc_shares_macd where date_as = %s) t 
                    ON t.code_id = m.code_id 
                """
        result = Shares.objects.raw(sql, params=(today, yesterday,))
        print(result)
        for item in result:
            shareName2 = SharesName.objects.filter(code=item.code_id)
            if len(shareName2) > 0:
                if item.diff > item.diff2 and item.dea > item.dea2:
                    shareName2.macd_up = 1
                else:
                    shareName2.macd_up = 2
                shareName2.update()
        pass

    def calculateKdj(self, today):
        # today = '2021-12-27'
        for item in SharesName.objects.filter(status=1, code_type=1):

            # 写过了
            code = item.code
            sharesKdjList = SharesMacd.objects.filter(code_id=code, date_as=today)
            # print(len(sharesKdjList))
            if len(sharesKdjList):
                continue
            # 数据不存在
            itemList = item.shares_set.all()
            # print(str(len(itemList)) +"---")
            if len(itemList) == 0:
                continue

            # 数据不是今天的
            shares = np.array(itemList)[-1:][0]
            date_as = str(shares.date_as)
            if date_as != today:
                continue

            # 计算kdj
            print(code + "：" + date_as + "：开始计算macd")
            macdDIFF1, macdDEA1, macd1 = self.talib_Macd(itemList)
            macdDIFF = macdDIFF1[-1:][0]
            macdDEA = macdDEA1[-1:][0]
            macd = macd1[-1:][0]

            if repr(macdDIFF) in ("inf", "nan") or repr(macdDEA) in ("inf", "nan") or repr(macd) in ("inf", "nan"):
                print("计算出未知数据", (code, macdDIFF, macdDEA, macd))
                continue

            b = SharesMacd(code_id=code, diff=macdDIFF, macd=macd, dea=macdDEA, cycle_type=1, date_as=date_as)
            b.save()
        pass

    def talib_Macd(self, data):
        # 计算kd指标
        close_prices = np.array([v.p_end / 100 for v in data])
        macdDIFF, macdDEA, macd = talib.MACDEXT(close_prices, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1,
                                                signalperiod=9, signalmatype=1)
        macd = macd * 2
        return (macdDIFF, macdDEA, macd)

    def getAllDates(self):
        sql = '''
                select 1 as id, date_as from mc_shares_date where date_as >= '2021-12-01';
                '''
        return SharesKdjCompute.objects.raw(sql)
