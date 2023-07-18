import numpy as np
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares_macd import SharesMacd
from shares.model.shares import Shares
from shares.model.shares_kdj_compute import SharesKdjCompute
from shares.model.shares_kdj_compute_detail import SharesKdjComputeDetail
from shares.model.shares_industry import SharesIndustry
from shares.model.shares_join_industry import SharesJoinIndustry
from shares.model.shares_industry_finance import SharesIndustryFinance

import numpy as np
import talib
import sys
from shares.model.shares_date import SharesDate
from django.db import connection
from shares.model.shares_finance import SharesFinance


class Command(BaseCommand):
    help = '计算p_rate2'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        shares = SharesName.objects.filter(code_type=1)
        total = 0
        for item in shares:
            code_id = item.code
            twenty_start = "2021-12-31"
            twenty_end = "2020-12-31"

            # if self.financeCheck(code_id, twenty_start, twenty_end) != True:
            #     return

            #  开始回测
            twenty_start = "2022-01-01"
            twenty_end = "2022-12-31"
            total = total + self.buy_sell(code_id, twenty_start, twenty_end)

        print(total)

    def buy_sell(self, code_id, twenty_start, twenty_end):
        dateList = SharesDate.objects.filter(date_as__gte=twenty_start, date_as__lte=twenty_end, )

        buyList = []
        sellList = []
        codeList = []
        for item in dateList:
            if code_id in codeList:
                end = item.date_as
                sharesKdjList = SharesMacd.objects.filter(code_id=code_id, date_as__lte=end).order_by('-date_as')[0:3]
                if len(sharesKdjList) < 3:
                    continue
                # print(sharesKdjList[0].dea , sharesKdjList[0].diff , sharesKdjList[2].dea , sharesKdjList[2].diff)
                # print(sharesKdjList[0].dea , sharesKdjList[2].dea , sharesKdjList[2].diff , sharesKdjList[1].diff)
                if (sharesKdjList[0].dea > sharesKdjList[0].diff and sharesKdjList[2].dea < sharesKdjList[2].diff) \
                        or \
                        (sharesKdjList[0].dea < sharesKdjList[2].dea and sharesKdjList[2].diff < sharesKdjList[1].diff):
                    codeList.remove(code_id)
                    sell = Shares.objects.filter(code_id=code_id, date_as=end)
                    if len(sell) == 0:
                        print("缺失数据%s -- %s"%(code_id, end) )
                        continue
                    sell = sell[0]
                    sellList.append(sell)
                    print("卖出 %s, 日期 %s， 价格%s" % (sell.code_id, sell.date_as, sell.p_start))
                continue

            if item.date_as > dateList[len(dateList) - 10].date_as:
                print("到了最后几天，停止买入 %s" % (dateList[len(dateList) - 10].date_as))
                break

            # 10个交易日连续7天跑赢大盘
            result = Shares.objects.filter(code_id=code_id, date_as__lte=item.date_as).order_by('-date_as')[0:11]
            if len(result) < 11:
                continue
            buy = result[0]
            p_range_win = sum([x.p_range_win for x in result[1:11]])
            if p_range_win < 6:
                continue

            start = result[1].date_as
            end = result[3].date_as

            sharesKdjList = SharesMacd.objects.filter(code_id=code_id, date_as__lte=start, date_as__gte=end).order_by('-date_as')
            if len(sharesKdjList) < 3:
                continue
            print(sharesKdjList[0].macd, sharesKdjList[1].macd, sharesKdjList[2].macd)
            if sharesKdjList[0].macd > sharesKdjList[1].macd and sharesKdjList[1].macd > sharesKdjList[2].macd:
                # 买入股票，
                buyList.append(buy)
                codeList.append(buy.code_id)
                print("买入 %s, 买入 %s， 买入%s" % (buy.code_id, buy.date_as, buy.p_start))

        p_start_buy = sum([x.p_start for x in buyList])
        p_start_sell = sum([x.p_start for x in sellList])
        print("买入 %s  卖出 %s 获利 %s" % (str(p_start_buy), str(p_start_sell), str(p_start_sell - p_start_buy)))
        if p_start_sell - p_start_buy > 0:
            return 1
        elif p_start_sell - p_start_buy == 0:
            return 0
        return -1

    def financeCheck(self, code_id, twenty_start, twenty_end):
        all = SharesFinance.objects.filter(code_id=code_id, date_as=twenty_start)
        if len(all) == 0:
            return False
        sharesFinanceItem = all[0]

        oldSharesFinance = SharesFinance.objects.filter(code_id=code_id, date_as=twenty_end)
        oldSharesFinance = oldSharesFinance[0]
        # 销售净利率 低增长的
        if sharesFinanceItem.npmos <= oldSharesFinance.npmos:
            return False

        if sharesFinanceItem.parentnetprofit == 0:
            print("净利润没拉取到：" + sharesFinanceItem.code + "：" + str(all[0].date_as))
            return False

        # 非营业收入 不超过净利润的5%
        if sharesFinanceItem.non_operating_incom / sharesFinanceItem.parentnetprofit > 0.09:
            return False

        # 低于前期 存货周转率
        if sharesFinanceItem.goods_turnover_rate < oldSharesFinance.goods_turnover_rate:
            return False

        # 低于前期 应收款周转率
        if sharesFinanceItem.account_turnover_rate < oldSharesFinance.account_turnover_rate:
            return False

        sharesJoinIndustryList = SharesJoinIndustry.objects.filter(code_id=code_id);
        if len(sharesJoinIndustryList) == 0:
            print(code_id, "++++++")
            return False

        sharesJoinIndustry = sharesJoinIndustryList[0]
        if sharesJoinIndustry.industry_code_id in ['BK0475', 'BK0474', 'BK0473']:
            return False

        ic = SharesIndustryFinance.objects.filter(code_id=sharesJoinIndustry.industry_code_id)[0]

        # 净利润 低于行业净利润
        if all[0].npmos < ic.npmos:
            return False

        # 低于行业 存货周转率
        if all[0].goods_turnover_rate < ic.goods_turnover_rate:
            return False
        # 低于行业 应收款周转率
        if all[0].account_turnover_rate < ic.account_turnover_rate:
            return False

        return True
