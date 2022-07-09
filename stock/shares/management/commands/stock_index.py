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
from django.core.mail import send_mail

# import numpy as np
# import talib
# import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '沪深300格雷厄姆指数'

    def handle(self, *args, **options):
        # 取 上证
        # SH000001
        # self.SH000001()
        # return

        # 取国债
        self.country()

        # 取 沪深300指数
        # SH000010
        self.SH000300()

        glem = self.GLEM()
        self.senmail(glem)
        pass

    def GLEM(self):
        date_as = datetime.today().date()
        res = StockIndex.objects.filter(
            code_id="GLEM", date_as=date_as)
        if len(res):
            return
        sh = StockIndex.objects.filter(
            code_id="SH000300", date_as=date_as)
        if len(sh) == 0:
            return
        year10 = StockIndex.objects.filter(
            code_id="GCNY10YR", date_as=date_as)
        if len(year10) == 0:
            return
        glem = (1 / sh[0].pe * 100) / year10[0].val
        StockIndex(
            code_id="GLEM",
            date_as=date_as,
            val=glem,
        ).save()
        return glem

    def SH000001(self):
        url = "https://www.touzid.com/index.php?/indice/ajax/chart_spe/"
        r = requests.post(url, json={
            "et": "2022-07-08",
            "idx_name": "沪深全A",
            "st": "2022-07-08",
            "symbol": [
                "tz100000"
            ],
            "tableFields": [
                "pe_aw"
            ]
        }, headers={
            "cookie": "rwe__user_login=PbetF%2BvHCAFjcDXrRj9Ssz1jcw5gcetVsWFcIY277OMLn%2BfjEKBmUz7xkf9r5DiI%2FqHU9WKbjgEpyL%2Bytb0X7l9MpdyKbq%2F9F%2BUeL4TolMCzv2uaj6bUOnEbk6SrFwar;",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        })
        print(r.content)

        # json2 = r.json()
        # pb = json2['data']['pb']
        # pe = json2['data']['pe']
        # ts = json2['data']['ts']
        # tz = timezone(timedelta(hours=+8))
        # data_as = datetime.utcfromtimestamp(int(ts) / 1000).astimezone(tz).strftime("%Y-%m-%d")
        # res = StockIndex.objects.filter(code_id="SH000001", date_as=data_as)
        # if len(res):
        #     return
        # StockIndex(
        #     code_id="SH000001",
        #     date_as=data_as,
        #     pb=pb,
        #     pe=pe,
        # ).save()

    def SH000300(self):
        url = "https://danjuanapp.com/djapi/index_eva/detail/SH000300"
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
        res = StockIndex.objects.filter(code_id="SH000300", date_as=data_as)
        if len(res):
            return
        StockIndex(
            code_id="SH000300",
            date_as=data_as,
            pb=pb,
            pe=pe,
        ).save()

    def country(self):
        url = "https://markets.tradingeconomics.com/chart?s=gcny10yr:gov&interval=10d&span=1d&securify=new&url=/china/government-bond-yield&AUTH=K8t7E1iGf9YG%2FmZyx2Nm4oFXpVAVW%2FwgYN%2BZEijTewhqirxDKJwbCthm%2BnVaUZN%2F&ohlc=0"
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

    def senmail(self, glem):
        if glem >= 3.13:
            send_mail(
                '观测到进场时机,可逐步定投',
                "沪深300格雷厄姆指数：" + str(glem),
                'lovemeand1314@163.com',
                ['844596330@qq.com'],
                fail_silently=False,
            )
        elif glem <= 1.85:
            send_mail(
                '观测到风险，要逐步减仓',
                "沪深300格雷厄姆指数：" + str(glem),
                'lovemeand1314@163.com',
                ['844596330@qq.com'],
                fail_silently=False,
            )

        pass
