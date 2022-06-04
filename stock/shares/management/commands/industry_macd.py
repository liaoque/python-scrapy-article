import numpy as np
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from shares.model.shares_name import SharesName
from shares.model.shares_industry_macd import SharesIndustryMacd

import numpy as np
import talib


# " /bin/cp /alidata/python/python-scrapy-article/stock/* /alidata/python/python-scrapy-article-master/stock -rf"


class Command(BaseCommand):
    help = '计算行业macd'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        today = datetime.now().date().strftime('%Y-%m-%d')
        self.calculateMacd(today)
        print("开始计算kdj-----")

        pass

    def calculateMacd(self, today):
        # today = '2021-12-27'
        for item in SharesName.objects.filter(status=1, code_type=2):
            # 写过了
            code = item.code
            sharesKdjList = SharesIndustryMacd.objects.filter(code_id=code, date_as=today)
            # print(len(sharesKdjList))
            if len(sharesKdjList):
                continue

            # print(map(lambda item: {
            #     'close': item.p_end / 100,
            #     'height': item.p_max / 100,
            #     'low': item.p_min / 100,
            # }, item.shares_set.all().values()))

            # 数据不存在
            itemList = item.sharesindustry_set.filter(date_as__lte=today).order_by('date_as').all()
            if len(itemList) == 0:
                continue

            # 数据不是今天的
            shares = np.array(itemList)[-1:][0]
            date_as = str(shares.date_as)
            # print(code + "：" + str(date_as) + "---" + str(today) + "----" + str(len(itemList)))
            # if date_as != today:
            #     continue

            # 计算kdj
            print(code + "：" + date_as + "：开始计算macd")
            macdDIFF1, macdDEA1, macd1 = self.talib_Macd(itemList)
            key = 0
            for item in macdDIFF1:
                macdDIFF = macdDIFF1[key][0]
                macdDEA = macdDEA1[key][0]
                macd = macd1[key][0]
                key + 1
                if repr(macdDIFF) in ("inf", "nan") or repr(macdDEA) in ("inf", "nan") or repr(macd) in ("inf", "nan"):
                    print("计算出未知数据", (code, macdDIFF, macdDEA, macd))
                    continue

                b = SharesIndustryMacd(code_id=code, diff=macdDIFF, macd=macd, dea=macdDEA, cycle_type=1,
                                       date_as=date_as)
                b.save()
            # SharesKdj
            # print(shares, ky, kj, kd, shares.code_id)
            # break
        pass

    def talib_Macd(self, data):
        # 计算kd指标
        close_prices = np.array([v.p_end / 100 for v in data])
        macdDIFF, macdDEA, macd = talib.MACDEXT(close_prices, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1,
                                                signalperiod=9, signalmatype=1)
        macd = macd * 2
        return (macdDIFF, macdDEA, macd)
