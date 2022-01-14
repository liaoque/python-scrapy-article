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
        # today = datetime.now().date().strftime('%Y-%m-%d')
        # self.calculateKdj(today)
        # print("开始计算kdj-----")
        # today = datetime.now().date().strftime('%Y-%m-%d')
        # self.KdjCompute(today)
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
            macdDIFF, macdDEA, macd = self.talib_Macd(itemList)
            i = 0
            while i < len(macd):
                macdDIFF = macdDIFF[i]
                macdDEA = macdDEA[i]
                macd = macd[i]
                i += 1
                if repr(macdDIFF) in ("inf", "nan") or repr(macdDEA) in ("inf", "nan") or repr(macd) in ("inf", "nan"):
                    print("计算出未知数据", (code, macdDIFF, macdDEA, macd))
                    continue
                b = SharesMacd(code_id=code, diff=macdDIFF, macd=macd, dea=macdDEA, cycle_type=1, date_as=date_as)
                b.save()


            # macdDIFF = macdDIFF[-1:][0]
            # macdDEA = macdDEA[-1:][0]
            # macd = macd[-1:][0]
            #
            # if repr(macdDIFF) in ("inf", "nan") or repr(macdDEA) in ("inf", "nan") or repr(macd) in ("inf", "nan"):
            #     print("计算出未知数据", (code, macdDIFF, macdDEA, macd))
            #     continue
            #
            # b = SharesMacd(code_id=code, diff=macdDIFF, macd=macd, dea=macdDEA, cycle_type=1, date_as=date_as)
            # b.save()
            # break
        pass

    def talib_Macd(self, data):
        # 计算kd指标
        close_prices = np.array([v.p_end / 100 for v in data])
        macdDIFF, macdDEA, macd = talib.MACDEXT(close_prices, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1,
                                                signalperiod=9, signalmatype=1)
        macd = macd * 2
        return (macdDIFF, macdDEA, macd)

    # def KdjCompute(self, today):
    #     # today = '2021-12-24'
    #     data = Shares.objects.filter(date_as=today)[:1]
    #     if len(data) == 0:
    #         # 当天不 需要计算
    #         return
    # 
    #     # result = np.array(SharesKdj.objects.values('date_as').annotate(counts=Count(id)))[-5:]
    #     # third, fourth, fifth = [x['date_as'].strftime('%Y-%m-%d') for x in result]
    #     # intersection_total = SharesKdjCompute.Compute.intersection_total(first=third, second=fourth, third=fifth)
    #     # intersection_total = intersection_total[0].c
    #     # print(intersection_total)
    # 
    #     result = np.array(SharesKdj.objects.filter(date_as__lte=today).values('date_as').annotate(counts=Count(id)))[-5:]
    #     if len(result) < 4:
    #         return
    #     if len(result) == 4:
    #         second, third, fourth, fifth = [x['date_as'].strftime('%Y-%m-%d') for x in result]
    #     else:
    #         first, second, third, fourth, fifth = [x['date_as'].strftime('%Y-%m-%d') for x in result]
    # 
    #     turn_total = 0
    #     turn_tomorrow = []
    #     intersection_total = SharesKdjCompute.Compute.intersection_total(first=second, second=third, third=fourth)
    #     intersection_today = SharesKdjCompute.Compute.intersection_today(first=second, second=third, third=fourth,
    #                                                                      fourth=fifth)
    #     intersection_pre = SharesKdjCompute.Compute.intersection_pre(first=second, second=third, third=fourth)
    #     intersection_pre_total_amount = sum([x.buy_amount - x.buy_amount_end for x in intersection_pre])
    #     intersection_total_amount = sum([x.buy_amount - x.buy_amount_end for x in intersection_today])
    #     turn_total_amount = 0
    #     if len(result) > 4:
    #         turn_total_result = SharesKdjCompute.Compute.turn_total(first=first, second=second, third=third)
    #         turn_total = turn_total_result[0].c
    #         turn_tomorrow = SharesKdjCompute.Compute.turn_tomorrow(first=first, second=second, third=third, fifth=fifth)
    #         turn_total_amount = sum([x.buy_amount - x.buy_amount_end for x in turn_tomorrow])
    #     # print(intersection_total, intersection_today, intersection_pre,turn_total, turn_tomorrow)
    # 
    #     shill_type = SharesName.SkillType.kdj
    #     SharesKdjCompute.saveSharesKdjCompute(intersection_pre_num=len(intersection_pre),
    #                                           intersection_num=len(intersection_today),
    #                                           intersection_total=intersection_total[0].c,
    #                                           turn_num=len(turn_tomorrow),
    #                                           turn_total=turn_total,
    #                                           shill_type=shill_type,
    #                                           intersection_pre_total_amount=intersection_pre_total_amount,
    #                                           intersection_total_amount=intersection_total_amount,
    #                                           turn_total_amount=turn_total_amount,
    #                                           date_as=today)
    # 
    #     shill_account_type = SharesName.SkillType.AccountType.intersection_pre
    #     for item in intersection_pre:
    #         SharesKdjComputeDetail.saveSharesKdjComputeDetail(
    #             code=item.code_id, buy_amount=item.buy_amount, buy_date_as=item.buy_date_as.strftime('%Y-%m-%d'),
    #             buy_amount_end=item.buy_amount_end, buy_date_as_end=item.buy_date_as_end.strftime('%Y-%m-%d'),
    #             shill_type=shill_type,
    #             shill_account_type=shill_account_type, date_as=today
    #         )
    # 
    #     shill_account_type = SharesName.SkillType.AccountType.intersection_today
    #     for item in intersection_today:
    #         SharesKdjComputeDetail.saveSharesKdjComputeDetail(
    #             code=item.code_id, buy_amount=item.buy_amount, buy_date_as=item.buy_date_as.strftime('%Y-%m-%d'),
    #             buy_amount_end=item.buy_amount_end, buy_date_as_end=item.buy_date_as_end.strftime('%Y-%m-%d'),
    #             shill_type=shill_type,
    #             shill_account_type=shill_account_type, date_as=today
    #         )
    # 
    #     shill_account_type = SharesName.SkillType.AccountType.turn_tomorrow
    #     for item in turn_tomorrow:
    #         SharesKdjComputeDetail.saveSharesKdjComputeDetail(
    #             code=item.code_id, buy_amount=item.buy_amount, buy_date_as=item.buy_date_as.strftime('%Y-%m-%d'),
    #             buy_amount_end=item.buy_amount_end, buy_date_as_end=item.buy_date_as_end.strftime('%Y-%m-%d'),
    #             shill_type=shill_type,
    #             shill_account_type=shill_account_type, date_as=today
    #         )
