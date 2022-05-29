import numpy as np
from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from shares.model.shares_name import SharesName
from shares.model.shares import Shares
from shares.model.shares_fh import SharesFH
import requests
from django.core.mail import send_mail


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
            "directors_date_as": {
                "up": 0,
                "low": 0,
            },
            "shareholder_date_as": {
                "up": 0,
                "low": 0,
            },
            "implement_date_as": {
                "up": 0,
                "low": 0,
            },
            "register_date_as": {
                "up": 0,
                "low": 0,
            },
            "ex_date_as": {
                "up": 0,
                "low": 0,
            }
        }

        for item in SharesName.objects.filter(status=1, code_type=1):
            # 写过了
            code = item.code

            json2 = SharesFH.objects.filter(code_id=code)
            if len(json2) == 0:
                continue

            for item in json2:
                if item.directors_date_as < '2022-01-01':
                    continue
                if item.directors_date_as is not None:
                    itemAll = Shares.objects.filter(date_as=item.directors_date_as, code_id=code)
                    if len(itemAll) > 0:
                        for item3 in itemAll:
                            if item3.p_start < item3.p_end:
                                all["directors_date_as"]["up"] += 1
                            else:
                                all["directors_date_as"]["low"] += 1

                if item.shareholder_date_as is not None:
                    itemAll = Shares.objects.filter(date_as=item.shareholder_date_as, code_id=code)
                    if len(itemAll) > 0:
                        for item3 in itemAll:
                            if item3.p_start < item3.p_end:
                                all["shareholder_date_as"]["up"] += 1
                            else:
                                all["shareholder_date_as"]["low"] += 1

                if item.implement_date_as is not None:
                    itemAll = Shares.objects.filter(date_as=item.implement_date_as, code_id=code)
                    if len(itemAll) > 0:
                        for item3 in itemAll:
                            if item3.p_start < item3.p_end:
                                all["implement_date_as"]["up"] += 1
                            else:
                                all["implement_date_as"]["low"] += 1

                if item.register_date_as is not None:
                    itemAll = Shares.objects.filter(date_as=item.register_date_as, code_id=code)
                    if len(itemAll) > 0:
                        for item3 in itemAll:
                            if item3.p_start < item3.p_end:
                                all["register_date_as"]["up"] += 1
                            else:
                                all["register_date_as"]["low"] += 1

                if item.ex_date_as is not None:
                    itemAll = Shares.objects.filter(date_as=item.ex_date_as, code_id=code)
                    if len(itemAll) > 0:
                        for item3 in itemAll:
                            if item3.p_start < item3.p_end:
                                all["ex_date_as"]["up"] += 1
                            else:
                                all["ex_date_as"]["low"] += 1
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
        all = {
            "directors_date_as": [],
            "shareholder_date_as": [],
            "implement_date_as": [],
            "register_date_as": [],
            "ex_date_as": []
        }
        for item in SharesName.objects.filter(status=1, code_type=1):
            # 写过了
            code = item.code
            json2 = SharesFH.objects.filter(code_id=code).order_by('-directors_date_as')
            if len(json2) == 0:
                continue
            item = json2[0]
            if item.directors_date_as is not None and item.directors_date_as == today:
                all['directors_date_as'].append(code)

            if item.shareholder_date_as is not None and item.shareholder_date_as == today:
                all['shareholder_date_as'].append(code)

            if item.implement_date_as is not None and item.implement_date_as == today:
                all['implement_date_as'].append(code)

            if item.register_date_as is not None and item.register_date_as == today:
                all['register_date_as'].append(code)

            if item.ex_date_as is not None and item.ex_date_as == today:
                all['ex_date_as'].append(code)

        self.sendMessage(all)
        pass

    def sendMessage(self, send_data):
        if len(send_data['notice']) == 0 and len(send_data['equity']) and len(send_data['ex']):
            return

        tz = timezone(timedelta(hours=+8))
        str = "董事会日期：%s\n 股东大会预案公告日期：%s\n 实施公告日：%s\n A股股权登记日：%s\n A股除权除息日：%s\n" % (
            "\",\"".join(send_data['directors_date_as']),
            "\",\"".join(send_data['shareholder_date_as']),
            "\",\"".join(send_data['implement_date_as']),
            "\",\"".join(send_data['register_date_as']),
            "\",\"".join(send_data['ex_date_as']))
        send_mail(
            '分红%s' % (datetime.now(tz)),
            str,
            'lovemeand1314@163.com',
            ['844596330@qq.com'],
            fail_silently=False,
        )
