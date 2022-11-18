import numpy as np
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min

from shares.model.shares_name import SharesName
from shares.model.shares_industry_macd import SharesIndustryMacd
from shares.model.shares_industry import SharesIndustry

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
            if date_as != today:
                continue

            # 计算kdj
            print(code + "：" + date_as + "：开始计算macd")
            macdDIFF1, macdDEA1, macd1 = self.talib_Macd(itemList)
            key = 0
            for item in itemList:
                macdDIFF = macdDIFF1[key]

                macdDEA = macdDEA1[key]
                macd = macd1[key]
                key += 1
                if repr(macdDIFF) in ("inf", "nan") or repr(macdDEA) in ("inf", "nan") or repr(macd) in ("inf", "nan"):
                    print("计算出未知数据", (code, macdDIFF, macdDEA, macd))
                    continue

                b = SharesIndustryMacd(code_id=code, diff=macdDIFF, macd=macd, dea=macdDEA, cycle_type=1,
                                       date_as=item.date_as)
                b.save()
                # print(b,key)
                # break
            # break
            # SharesKdj
            # print(shares, ky, kj, kd, shares.code_id)
            # break

        # 归一处理
        for item in SharesName.objects.filter(status=1, code_type=2):
            # 写过了
            code = item.code
            if item.four_year_day == 0:
                # 当前板块最小的值
                item.four_year_day = SharesIndustry.objects.filter(code_id=item.code).aggregate(Min('p_end'))[
                    "p_end__min"]
                item.save()
                pass

            sharesList = SharesIndustry.objects.filter(code_id=code).order_by('-date_as')
            if len(sharesList) == 0:
                continue

            # 按比例归一
            sharesIndustry = sharesList[-1:][0]
            sharesIndustry.avg_p_min_rate = sharesIndustry.p_min / item.four_year_day

            sharesListMacd = SharesIndustryMacd.objects.filter(code_id=code).order_by('-date_as')[-3:]
            if sharesListMacd > 3 and sharesListMacd[0].diff > sharesListMacd[3].diff:
                sharesIndustry.macd = 1

            sharesList10 = sharesList[-10:]
            sharesIndustry.avg10 = sum([item.p_end for item in sharesList10]) / len(sharesList10)
            sharesIndustry.avg10_rate = sharesIndustry.avg10 / item.four_year_day

            sharesList20 = sharesList[-20:]
            sharesIndustry.avg20 = sum([item.p_end for item in sharesList20]) / len(sharesList20)
            sharesIndustry.avg20_rate = sharesIndustry.avg20 / item.four_year_day
            print(sharesIndustry)
            sharesIndustry.save()

        pass

    def talib_Macd(self, data):
        # 计算kd指标
        close_prices = np.array([v.p_end / 100 for v in data])
        macdDIFF, macdDEA, macd = talib.MACDEXT(close_prices, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1,
                                                signalperiod=9, signalmatype=1)
        macd = macd * 2
        return (macdDIFF, macdDEA, macd)
