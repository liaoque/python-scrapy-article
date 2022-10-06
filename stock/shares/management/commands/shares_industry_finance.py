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


# import numpy as np
# import talib
# import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '行业中位数财报分析'

    def handle(self, *args, **options):
        shares = SharesName.objects.filter(code_type=2)
        sharesFinanceDateAll = SharesFinance.objects.values("date_as").annotate(counts=Count(id))
        for item in shares:
            joinIndustry = SharesJoinIndustry.objects.filter(industry_code_id=item.code)
            for item_date in sharesFinanceDateAll:
                finance = SharesFinance.objects.filter(date_as=item_date['date_as'],
                                                       code_id__in=[item.code_id for item in joinIndustry])
                self.saveFinance(finance, item.industry_code_id)

    def saveFinance(self, finance, industry_code):
        l = len(finance)
        if l < 3:
            return
        print( finance.order_by())
        finance = finance.order_by()[1:-1]

        title = finance[0]['title']
        date_as = finance[0]['date_as']
        gpm = sum([item.gpm for item in finance]) / l
        npmos = sum([item.npmos for item in finance]) / l
        turnover_days = sum([item.turnover_days for item in finance]) / l
        goods_turnover_days = sum([item.goods_turnover_days for item in finance]) / l
        account_turnover_days = sum([item.account_turnover_days for item in finance]) / l
        turnover_rate = sum([item.turnover_rate for item in finance]) / l
        goods_turnover_rate = sum([item.goods_turnover_rate for item in finance]) / l
        account_turnover_rate = sum([item.account_turnover_rate for item in finance]) / l
        non_operating_incom = sum([item.non_operating_incom for item in finance]) / l
        non_operating_expenses = sum([item.non_operating_expenses for item in finance]) / l
        income_from_investment = sum([item.income_from_investment for item in finance]) / l
        notes_payable = sum([item.notes_payable for item in finance]) / l
        notes_receivable = sum([item.notes_receivable for item in finance]) / l
        prepayment = sum([item.prepayment for item in finance]) / l
        halfYear = SharesIndustryFinance(code_id=industry_code,title=title,date_as=date_as,
                                         gpm=gpm, npmos=npmos, turnover_days=turnover_days,goods_turnover_days=goods_turnover_days,
                                         account_turnover_days=account_turnover_days, turnover_rate=turnover_rate,
                                         goods_turnover_rate=goods_turnover_rate,account_turnover_rate=account_turnover_rate,
                                         non_operating_incom=non_operating_incom,non_operating_expenses=non_operating_expenses,
                                         income_from_investment=income_from_investment,notes_payable=notes_payable,
                                         notes_receivable=notes_receivable,prepayment=prepayment,
                                         )
        halfYear.save()
