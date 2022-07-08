import numpy as np
# from datetime import datetime, date
from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min
from django.db import connection

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares import Shares
from shares.model.shares_industry import SharesIndustry
from shares.model.shares_industry_month import SharesIndustryMonth
import time
import requests
from shares.model.stock_members import SharesMembers
from shares.model.shares_date import SharesDate
from shares.model.stock_index import StockIndex


# import numpy as np
# import talib
# import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '格雷厄姆指数'

    def handle(self, *args, **options):
        # 取国债
        self.country()

        # 取 沪深300指数
        # SH000010
        self.SH000010()

        self.GLEM()
        pass

    def GLEM(self):
        date_as = datetime.today().date()
        res = StockIndex.objects.filter(
            code_id="GLEM", date_as=date_as)
        if len(res):
            return
        sh = StockIndex.objects.filter(
            code_id="SH000010", date_as=date_as)
        if len(sh) == 0:
            return
        year10 = StockIndex.objects.filter(
            code_id="GCNY10YR", date_as=date_as)
        if len(year10) == 0:
            return
        glem = sh[0].pb / year10[0].val
        StockIndex(
            code_id="GCNY10YR",
            date_as=date_as,
            val=glem,
        ).save()

    def SH000010(self):
        url = "https://danjuanapp.com/djapi/index_eva/detail/SH000010"
        r = requests.get(url, headers={
                "Host": "danjuanapp.com",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        })

        json2 = r.json()
        pb = json2['data']['pb']
        pe = json2['data']['pe']
        ts = json2['data']['ts']
        tz = timezone(timedelta(hours=+8))
        data_as = datetime.utcfromtimestamp(int(ts) / 1000).astimezone(tz).strftime("%Y-%m-%d")
        res = StockIndex.objects.filter(code_id="SH000010", date_as=data_as)
        if len(res):
            return
        StockIndex(
            code_id="SH000010",
            date_as=data_as,
            pb=pb,
            pe=pe,
        ).save()

    def country(self):
        url = "https://markets.tradingeconomics.com/chart?s=gcny10yr:gov&interval=1d&span=1d&securify=new&url=/china/government-bond-yield&AUTH=K8t7E1iGf9YG%2FmZyx2Nm4oFXpVAVW%2FwgYN%2BZEijTewhqirxDKJwbCthm%2BnVaUZN%2F&ohlc=0"
        r = requests.get(url)
        json2 = r.json()
        data = json2['series'][0]['data']
        for item in data:
            res = StockIndex.objects.filter(code_id="GCNY10YR", date_as=item['date'][:10])
            if len(res):
                continue
            StockIndex(
                code_id="GCNY10YR",
                date_as=item['date'][:10],
                val=item['y'],
            ).save()
            pass
