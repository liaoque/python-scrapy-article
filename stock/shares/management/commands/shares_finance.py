import numpy as np
from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min
from django.db import connection

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares import Shares
from shares.model.shares_finance import SharesFinance
from shares.model.shares_industry_finance import SharesIndustryFinance
from shares.model.shares_join_industry import SharesJoinIndustry
import time
import requests
from django.core.mail import send_mail
from shares.model.shares_name import SharesName

# import numpy as np
# import talib
# import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '财报分析'

    def handle(self, *args, **options):
        SharesName.objects.filter(code_type=1).update(finance_up=0)
        shares = SharesName.objects.filter(code_type=1)
        sharesFinanceItem = SharesFinance.objects.order_by('-date_as').all()[0]
        allList = []
        for item in shares:
            if SharesFinance.objects.filter(date_as=sharesFinanceItem.date_as, code_id=item.code).count() == 0:
                continue
            all = SharesFinance.objects.filter(code_id=item.code).order_by('-date_as')[:2]
            # 销售净利率 低增长的
            if all[0].npmos <= all[1].npmos:
                continue

            if all[0].parentnetprofit == 0:
                print("净利润没拉取到：" + item.code +"：" + str(all[0].date_as))
                continue

            # 非营业收入 不超过净利润的5%
            if all[1].non_operating_incom > 0 and all[0].non_operating_incom  / all[0].parentnetprofit > 0.05:
                continue

            sss =  all[0].date_as.timetuple()
            # time.strptime(all[0].date_as, '%Y-%m-%d')
            date_as_t =  str(sss.tm_year - 1) + "-" + str(sss.tm_mon) + "-" + str(sss.tm_mday)
            # print(date_as_t)
            oldSharesFinance = SharesFinance.objects.filter(code_id=item.code, date_as=date_as_t)
            if len(oldSharesFinance) > 0:
                oldSharesFinance = oldSharesFinance[0]
                # # 净利率低增长的
                # if all[0].npmos <= oldSharesFinance.npmos:
                #     continue
                # 低于前期 存货周转率
                if all[0].goods_turnover_rate < oldSharesFinance.goods_turnover_rate:
                    continue
                # 低于前期 应收款周转率
                if all[0].account_turnover_rate < oldSharesFinance.account_turnover_rate:
                    continue


            # 银行，证券，保险不要
            sharesJoinIndustryList = SharesJoinIndustry.objects.filter(code_id=item.code);
            if len(sharesJoinIndustryList) == 0:
                print(item.code, "++++++")
                continue

            sharesJoinIndustry = sharesJoinIndustryList[0]
            if sharesJoinIndustry.industry_code_id in ['BK0475', 'BK0474', 'BK0473']:
                continue

            ic = SharesIndustryFinance.objects.filter(code_id=sharesJoinIndustry.industry_code_id)[0]

            # 净利润 低于行业净利润
            if all[0].npmos < ic.npmos:
                continue

            # 低于行业 存货周转率
            if all[0].goods_turnover_rate < ic.goods_turnover_rate:
                continue
            # 低于行业 应收款周转率
            if all[0].account_turnover_rate < ic.account_turnover_rate:
                continue
            SharesName.objects.filter(code=all[0].code_id).update(finance_up=1)
            allList.append(all[0])
        self.sendMessage(allList)

    def sendMessage(self, allList):
        tz = timezone(timedelta(hours=+8))
        str_con = "找到基本面相对较好的公司：%s" % (
            "\",\"".join([item.code_id for item in allList])
        )
        send_mail(
            '特别提醒%s' % (datetime.now(tz)),
            str_con,
            'lovemeand1314@163.com',
            ['844596330@qq.com'],
            fail_silently=False,
        )
