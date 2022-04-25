import numpy as np
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares_kdj import SharesKdj
from shares.model.shares import Shares
from shares.model.shares_date_listen import SharesDateListen
from shares.model.shares_macd import SharesMacd
from shares.model.shares_buys import SharesBuys
import numpy as np
import talib
import math


# 1. 先记录 j < 0 作为参考点
# 2. 记录 diff 的上涨走势 且 J < 40  作为买点
# 3. 判断 j 下调走势作为卖点，或者3天强制卖出

class Command(BaseCommand):
    help = '记录每天-10以下的kdj股票'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        print("开始计算-----")
        dateList = self.getAllDates()
        for item in dateList[-15:]:
            self.getkdj10(item.date_as)

            dateList = self.getAllDateListens()
            for item in dateList:
                allCodeIds = SharesDateListen.objects.filter(date_as=item.date_as, buy_date_as=None)
                print("寻找买入点-----")
                for codeItem in allCodeIds:
                    codeItemResult = self.findBuyPoint(codeItem)
                    if codeItemResult != None:
                        sharesItem = Shares.objects.filter(date_as=codeItemResult.date_as, code_id=codeItem.code_id)[0]
                        print("找到买入点--%s---%s", codeItemResult.date_as, sharesItem.p_end)
                        codeItem.buy_date_as = codeItemResult.date_as
                        codeItem.buy_start = sharesItem.p_end
                        codeItem.save()
                    pass

                allCodeIds = SharesDateListen.objects.filter(date_as=item.date_as, buy_start__gt=0)
                print("寻找卖出点-----")
                for codeItem in allCodeIds:
                    codeItemResult = self.findSellPoint(codeItem)
                    if codeItemResult == None:
                        continue
                    sharesItem = Shares.objects.filter(date_as=codeItemResult.date_as, code_id=codeItem.code_id)[0]
                    print("找到卖出点--%s---%s", codeItemResult.date_as, sharesItem.p_end)
                    buys = SharesBuys(
                        code_id=codeItem.code_id,
                        buy_date_as=codeItem.buy_date_as,
                        buy_start=codeItem.buy_start,
                        sell_date_as=codeItemResult.date_as,
                        sell_end=sharesItem.p_end,
                    )
                    buys.save()
                    if codeItem.buy_start <= sharesItem.p_end:
                        codeItem.delete()
                    else:
                        codeItem.date_as = codeItemResult.date_as
                        codeItem.save()
                # break

    def findSellPoint(self, codeItem):
        result = SharesKdj.objects.filter(code_id=codeItem.code_id, date_as__gte=codeItem.buy_date_as)
        sharesCollect = Shares.objects.filter(code_id=codeItem.code_id, date_as__gte=codeItem.buy_date_as)
        item = None
        key = 0
        for value in result:
            if key + 1 >= len(result):
                break
            # 倒锤头
            hammerMax = max(sharesCollect[key].p_end, sharesCollect[key].p_start)
            hammerMin = min(sharesCollect[key].p_end, sharesCollect[key].p_start)
            hammerBody = math.fabs(sharesCollect[key].p_end - sharesCollect[key].p_start)
            hammerHeader = math.fabs(sharesCollect[key].p_max - hammerMax)
            hammerFooter = math.fabs(sharesCollect[key].p_min - hammerMin)
            if hammerHeader < hammerBody and hammerBody * 2 < hammerFooter:
                print("倒锤头%s--%s--%d---%d---%d", sharesCollect[key].date_as, codeItem.code_id,
                      hammerHeader, hammerBody, hammerFooter)
                item = value
                break

            if value.j > result[key + 1].j:
                item = result[key + 1]
                break
            key += 1
        return item

    def findBuyPoint(self, codeItem):
        date_as = codeItem.date_as
        sharesBuysItem = SharesBuys.objects.filter(code_id=codeItem.code_id).order_by('-sell_date_as')
        if len(sharesBuysItem) > 0 and sharesBuysItem[0].sell_date_as > codeItem.date_as:
            date_as = sharesBuysItem[0].sell_date_as

        # 计算ema
        result = SharesMacd.objects.filter(code_id=codeItem.code_id, date_as__gte=date_as)
        item = None
        key = 0
        for value in result:
            if key + 1 >= len(result):
                break
            if result[key + 1].diff - value.diff > 0.01:
                sharesKdjItem = SharesKdj.objects.filter(code_id=value.code_id, date_as=value.date_as)[0]
                if sharesKdjItem.j > 50:
                    continue
                shares = Shares.objects.filter(date_as__lte=result[key + 1].date_as, code_id=codeItem.code_id).order_by(
                    '-date_as')[:6]
                sharesSum = sum([item.p_end for item in shares[1:]])
                print(sharesKdjItem.date_as, codeItem.code_id, [item.p_end for item in shares[1:]], sharesSum,
                      shares[0].p_end)
                if sharesSum / 5 > shares[0].p_end:
                    shares = Shares.objects.filter(date_as__lte=sharesKdjItem.date_as, code_id=codeItem.code_id)
                    close = [item.p_end / 100 for item in shares]
                    emaList = talib.EMA(np.array(close), timeperiod=7)
                    # print(emaList)
                    # preEma = (2 * x + (5 - 1) * emaList[-1]) / (5 + 1)
                    preEma = ((emaList[-1] + .01) * (7 + 1) - (7 - 1) * emaList[-1]) / 2
                    sharesItem = Shares.objects.filter(date_as__lte=result[key + 2].date_as, code_id=codeItem.code_id)[
                        0]
                    print(sharesKdjItem.date_as, codeItem.code_id,sharesItem.p_end, preEma, emaList[-1] )
                    if sharesItem and (sharesItem.p_end - sharesItem.p_start)/2 * sharesItem.p_start > preEma:
                        item = result[key + 1]
                break

                # shares = Shares.objects.filter(date_as__lte=sharesKdjItem.date_as, code_id=codeItem.code_id).order_by(
                #     '-date_as')[:14]
                # shares = shares[::-1]
                # close = [item.p_end / 100 for item in shares]
                # pre_end =shares[len(shares) -1].p_end / 100
                # close.append(pre_end)
                # emaList = talib.EMA(np.array(close), timeperiod=7)
                # print("%s--%s--%s--%s", sharesKdjItem.date_as, codeItem.code_id, emaList[len(emaList) - 1] , emaList[len(emaList) - 2])
                # if emaList[len(emaList) - 1] > emaList[len(emaList) - 2]:
                #     preShares = Shares.objects.filter(date_as__gte=sharesKdjItem.date_as, code_id=codeItem.code_id)
                #     if len(preShares) and (preShares[0].p_end - preShares[0].p_start) /2 + preShares[0].p_start > pre_end:
                #         item = result[key + 1]
                #         break
            key += 1

        # if item != None:
        #     sharesItem = Shares.objects.filter(date_as=item.date_as, code_id=codeItem.code_id)[0]
        #     sharesCollect = Shares.objects.filter(date_as__gt=item.date_as, code_id=codeItem.code_id)
        #     #  如果买入价，大于当前收盘价，卖出
        #     if sharesItem.p_end * 0.994 > sharesCollect[0].p_start:
        #         print("不符合买入价%s--%s---%s", codeItem.code_id, sharesItem.p_end * 0.994, sharesCollect[0].p_start)
        #         item = None

        return item

    def getkdj10(self, date):
        sql = '''
            select 1 as id, a.code_id,c.p_end,a.date_as  from mc_shares_kdj  a
            left join ( select code_id,p_end from mc_shares where date_as = %s ) c  on a.code_id = c.code_id
            where a.date_as = %s  
               and a.code_id not in ( select code_id from mc_shares_date_listen )
               and a.j < -10
               and (a.code_id < 300000 or a.code_id > 600000)
               and a.code_id < 680000
               and a.code_id not in (SELECT code FROM `mc_shares_name` where name like %s )
            ;
            '''

        result = SharesKdj.objects.raw(sql, params=(date, date, '%ST%',))
        print(result)
        print("%s-挑选出-10的股票：%s个" % (date, len(result)))
        print(",".join(["\"" + item.code_id + "\"" for item in result]))
        for item in result:
            if len(SharesDateListen.objects.filter(code_id=item.code_id)):
                continue
            listen = SharesDateListen(
                code_id=item.code_id,
                p_start=item.p_end,
                date_as=item.date_as,
                type=1,
            )
            listen.save()

    def getAllDateListens(self):
        sql = '''
            select 1 as id, date_as from mc_shares_date_listen group by date_as ;
            '''
        return SharesDateListen.objects.raw(sql)

    def getAllDates(self):
        sql = '''
            select 1 as id, date_as from mc_shares_date where date_as >= '2021-12-01' ;
            '''
        return SharesDateListen.objects.raw(sql)
