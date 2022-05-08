import numpy as np
from datetime import datetime, date
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


# import numpy as np
# import talib
# import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '查公司股东数, 找出减少的股东人数'

    def handle(self, *args, **options):
        result = []
        for item in SharesName.objects.filter(status=1, code_type=1, ):
            stockMemberList = self.getStockMember(item)
            for item2 in stockMemberList:
                date_as = datetime.strptime(item2.date_as, '%Y-%m-%d %H:%M:%S').date().strftime("%Y-%m-%d")
                itemSharesMembers = SharesMembers.objects.filter(code_id=item.code, date_as=date_as)
                if len(itemSharesMembers) > 0:
                    return
                itemSharesMembers = SharesMembers(
                    code_id=item.code, date_as=date_as,
                    members=item2.HOLDER_TOTAL_NUM, info=item2.HOLD_FOCUS,
                    price=item2.PRICE *100,
                    avg_free_shares=item2.AVG_FREE_SHARES
                )
                itemSharesMembers.save()
        #
        #
        #     if len(stockMemberList) <= 1:
        #         continue
        #     if stockMemberList[0]['HOLDER_TOTAL_NUM'] < stockMemberList[1]['HOLDER_TOTAL_NUM'] and stockMemberList[
        #         0]['AVG_FREE_SHARES'] < stockMemberList[1]['AVG_FREE_SHARES']:
        #         print("%s--%s--%s", item.code, stockMemberList[0]['AVG_FREE_SHARES'], stockMemberList[0]['HOLD_FOCUS'])
        #
        #         result.append(item)
        #         pass
        # print("找到股东人数减少的股票有：")
        # print(",".join(["\"" + item.code + "\"" for item in result]))

    def getStockMember(self, shareName):
        if shareName.area_id == 1:
            url = 'http://emweb.securities.eastmoney.com/PC_HSF10/ShareholderResearch/PageAjax?code=SH' + shareName.code
        elif shareName.area_id == 2:
            url = 'http://emweb.securities.eastmoney.com/PC_HSF10/ShareholderResearch/PageAjax?code=SZ' + shareName.code
        else:
            url = 'http://emweb.securities.eastmoney.com/PC_HSF10/ShareholderResearch/PageAjax?code=BJ' + shareName.code
        r = requests.get(url)
        return r.json()["gdrs"]
