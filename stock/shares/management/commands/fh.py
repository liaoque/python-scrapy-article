import numpy as np
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from shares.model.shares_name import SharesName
from shares.model.shares import Shares
import requests


# " /bin/cp /alidata/python/python-scrapy-article/stock/* /alidata/python/python-scrapy-article-master/stock -rf"


class Command(BaseCommand):
    help = '分红检测'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):

        today = datetime.now().date().strftime('%Y-%m-%d')
        self.calculateCheck(today)
        pass

    def calculateCheck(self, today):
        all = {
            "notice": {
                "up": 0,
                "low": 0,
            },
            "equity": {
                "up": 0,
                "low": 0,
            },
            "ex": {
                "up": 0,
                "low": 0,
            }
        }

        for item in SharesName.objects.filter(status=1, code_type=1):
            # 写过了
            code = item.code
            # https://emweb.securities.eastmoney.com/BonusFinancing/PageAjax?code=SH603662

            url = self.getUrl(item)
            # print(url)
            r = requests.get(url)
            json2 = r.json()
            # 公告日期
            if len(json2["fhyx"]) == 0:
                pass

            for item in json2["fhyx"]:
                if item["NOTICE_DATE"] is not None:
                    time1 = datetime.strptime(item["NOTICE_DATE"], '%Y-%m-%d 00:00:00').date()
                    itemAll = Shares.objects.filter(date_as=time1, code_id=code)
                    if len(itemAll) > 0:
                        for item3 in itemAll:
                            print(item3)
                            if item3.p_start < item3.p_end:
                                all["notice"]["up"] += 1
                            else:
                                all["notice"]["low"] += 0

                if item["EQUITY_RECORD_DATE"] is not None:
                    time1 = datetime.strptime(item["EQUITY_RECORD_DATE"], '%Y-%m-%d 00:00:00').date()
                    itemAll = Shares.objects.filter(date_as=time1, code_id=code)
                    if len(itemAll) > 0:
                        for item3 in itemAll:
                            if item3.p_start < item3.p_end:
                                all["equity"]["up"] += 1
                            else:
                                all["equity"]["low"] += 0
                        pass

                if item["EX_DIVIDEND_DATE"] is not None:
                    time1 = datetime.strptime(item["EX_DIVIDEND_DATE"], '%Y-%m-%d 00:00:00').date()
                    itemAll = Shares.objects.filter(date_as=time1, code_id=code)
                    if len(itemAll) > 0:
                        for item3 in itemAll:
                            if item3.p_start < item3.p_end:
                                all["ex"]["up"] += 1
                            else:
                                all["ex"]["low"] += 0
                        pass
                break

        print(all)
        pass

    def getUrl(self, item):
        area_map = {
            1: "SH",
            2: "SZ",
            3: "BJ",
        }
        return "https://emweb.securities.eastmoney.com/BonusFinancing/PageAjax?code=%s%s" % (
            area_map[item.area_id], item.code)

    def calculate(self, today):
        for item in SharesName.objects.filter(status=1, code_type=1):
            # 写过了
            code = item.code
            # https://emweb.securities.eastmoney.com/BonusFinancing/PageAjax?code=SH603662

            url = "https://emweb.securities.eastmoney.com/BonusFinancing/PageAjax?code=SH603662"
            r = requests.get(url)
            json2 = r.json()
            # 公告日期
            all = {
                "notice": [],
                "equity": [],
                "ex": []
            }
            if len(json2["fhyx"]) > 0:
                # 公告日
                time1 = datetime.strptime(item["NOTICE_DATE"], '%Y-%m-%d 00:00:00').date()
                if time1 == today:
                    all["notice"].append(code)

                # 登记日期
                time1 = datetime.strptime(item["EQUITY_RECORD_DATE"], '%Y-%m-%d 00:00:00').date()
                if time1 == today:
                    all["equity"].append(code)

                # 除权日
                time1 = datetime.strptime(item["EX_DIVIDEND_DATE"], '%Y-%m-%d 00:00:00').date()
                if time1 == today:
                    all["ex"].append(code)


        print(all)
        pass
