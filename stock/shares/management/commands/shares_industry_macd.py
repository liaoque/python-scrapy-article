from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min
from django.db import connection

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares_industry import SharesIndustry
import time
import pandas as pd
import numpy as np
import talib


# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '看macd周期'

    def handle(self, *args, **options):
        #
        print(self.getData(7))

        print(self.getData(15))

        #
        print(self.getData(20))

        #
        print(self.getData(30))

    def getData(self, n_day):
        result = self.industry_half_month(n_day)
        l = []
        for item in result:
            macdDIFF1, macdDEA1, macd1 = self.talib_Macd(item['data'])
            macdDIFF = macdDIFF1[-2:]
            macdDEA = macdDEA1[-2:]
            if item['code_id'] == 'BK1046':
                print(item, macdDIFF1)

            if macdDIFF[0] > macdDIFF[1] or macdDEA[0] > macdDEA[1] or macdDIFF[1] < macdDEA[1]:
                continue
            l.append(item['code_id'])
        return l

    def industry_half_month(self, n_day):
        d = n_day
        sql = '''
        SELECT 1 as id, code_id, sum(p_start) as p_start, sum(p_end) as p_end,date_as  from (
            SELECT code_id, p_start, 0 as p_end,date_as
            FROM `mc_shares_industry`
            where date_as in (SELECT min(date_as) FROM  `mc_shares_industry`  GROUP BY  cast(UNIX_TIMESTAMP(date_as) / (%s*86400) as signed ))
            UNION ALL
            SELECT code_id, 0 as p_start, p_end,date_as
            FROM `mc_shares_industry`
            where date_as in (SELECT max(date_as) FROM  `mc_shares_industry`  GROUP BY  cast(UNIX_TIMESTAMP(date_as) / (%s*86400) as signed ))
        ) c
        GROUP BY code_id,cast(UNIX_TIMESTAMP(date_as) / (%s*86400) as signed );
        '''
        result = SharesIndustry.objects.raw(sql, params=(d, d, d))
        result = [{'code_id': x.code_id,
                   'p_start': x.p_start,
                   'p_end': x.p_end,
                   'date_as': x.date_as
                   } for x in result]
        df = pd.DataFrame(result)
        grouped = df.groupby('code_id')
        l = []
        for code_id, item in grouped:
            l.append({
                'code_id': code_id,
                'data': [{'code_id': x[0], 'p_start': x[1], 'p_end': x[2], 'date_as': x[3]} for x in
                         item.sort_values(by='date_as').values]
            })
        return l

    def talib_Macd(self, data):
        # 计算kd指标
        close_prices = [int(v['p_end']) / 100 for v in data]
        if len(close_prices) < 33:
            close_prices = [close_prices[0]] * 31 + close_prices
        close_prices = np.array(close_prices)
        macdDIFF, macdDEA, macd = talib.MACDEXT(close_prices, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1,
                                                signalperiod=9, signalmatype=1)
        macd = macd * 2
        return (macdDIFF, macdDEA, macd)

    def talib_Trix(self, data):
        # 计算kd指标
        close_prices = [int(v['p_end']) / 100 for v in data]
        close_prices = np.array(close_prices)
        output = talib.TRIX(close_prices, timeperiod=30)
        return output