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
        # 股东数持续减少的, 并排出了 银行，证券，保险
        # sql = """
        # select * from (
        # SELECT mc_stock_members.* from mc_stock_members
        #         LEFT JOIN (SELECT code_id, date_as, avg_free_shares FROM `mc_stock_members` GROUP by code_id ORDER BY date_as desc) t
        #         ON t.code_id = mc_stock_members.code_id
        #         where t.date_as > mc_stock_members.date_as
        #         and ( mc_stock_members.code_id < '300000' or (mc_stock_members.code_id > '600000' and mc_stock_members.code_id < '700000' ) )
        #         GROUP by mc_stock_members.code_id
        #         ORDER BY mc_stock_members.date_as desc
        # ) as s
        # LEFT JOIN (SELECT code_id, date_as, avg_free_shares  FROM `mc_stock_members`  GROUP by code_id ORDER BY date_as desc) t
        #     ON t.code_id = s.code_id
        # where t.avg_free_shares > 50000
        #     and t.avg_free_shares > s.avg_free_shares
        #     and ( s.code_id < '300000' or (s.code_id > '600000' and s.code_id < '700000' ) )
        #     and s.code_id  not in (select code_id from mc_shares_join_industry where industry_code_id in ('BK0475', 'BK0474', 'BK0473'));
        # """
        # result = Shares.objects.raw(sql)
        # print(
        #     "股东数持续减少的",
        #     ",".join(["\"" + item.code_id + "\"" for item in result])
        # )
        #
        # #        并排出了 银行，证券，保险
        # sql = """
        #     select * from (
        #     SELECT mc_stock_members.* from mc_stock_members
        #             LEFT JOIN (SELECT code_id, date_as, avg_free_shares FROM `mc_stock_members` GROUP by code_id ORDER BY date_as desc) t
        #             ON t.code_id = mc_stock_members.code_id
        #             where t.date_as > mc_stock_members.date_as
        #             and ( mc_stock_members.code_id < '300000' or (mc_stock_members.code_id > '600000' and mc_stock_members.code_id < '700000' ) )
        #             GROUP by mc_stock_members.code_id
        #             ORDER BY mc_stock_members.date_as desc
        #     ) as s
        #     LEFT JOIN (SELECT code_id, date_as, avg_free_shares,price  FROM `mc_stock_members`  GROUP by code_id ORDER BY date_as desc) t
        #         ON t.code_id = s.code_id
        #     where t.avg_free_shares > 50000
        #         and t.avg_free_shares < s.avg_free_shares
        #         and t.price < s.price
        #         and ( s.code_id < '300000' or (s.code_id > '600000' and s.code_id < '700000' ) )
        #         and s.code_id  not in (select code_id from mc_shares_join_industry where industry_code_id in ('BK0475', 'BK0474', 'BK0473'));
        #         """
        # result = Shares.objects.raw(sql)
        # print(
        #     "股东人数增加，股价基本没涨的股票, 还在调整",
        #     ",".join(["\"" + item.code_id + "\"" for item in result])
        # )

        # for item in SharesName.objects.filter(status=1, code_type=1, ):
        #     stockMemberList = self.getStockMember(item)
        #     for item2 in stockMemberList:
        #         date_as = datetime.strptime(item2['END_DATE'], '%Y-%m-%d %H:%M:%S').date().strftime("%Y-%m-%d")
        #         itemSharesMembers = SharesMembers.objects.filter(code_id=item.code, date_as=date_as)
        #         if len(itemSharesMembers) > 0:
        #             continue
        #         if item2['HOLDER_TOTAL_NUM'] is None:
        #             item2['HOLDER_TOTAL_NUM'] = 0
        #         if item2['HOLD_FOCUS'] is None:
        #             item2['HOLD_FOCUS'] = ''
        #         if item2['PRICE'] is None:
        #             item2['PRICE'] = 0
        #         if item2['AVG_FREE_SHARES'] is None:
        #             item2['AVG_FREE_SHARES'] = 0
        #         itemSharesMembers = SharesMembers(
        #             code_id=item.code, date_as=date_as,
        #             members=item2['HOLDER_TOTAL_NUM'], info=item2['HOLD_FOCUS'],
        #             price=item2['PRICE'] * 100,
        #             avg_free_shares=item2['AVG_FREE_SHARES']
        #         )
        #         itemSharesMembers.save()

        sql = """
        SELECT 1 as id, mc_stock_members.code_id,mc_stock_members.members,t.members as tmembers from mc_stock_members 
                LEFT JOIN (SELECT code_id, date_as, avg_free_shares,members FROM `mc_stock_members` GROUP by code_id ORDER BY date_as desc) t 
                ON t.code_id = mc_stock_members.code_id 
                where t.date_as > mc_stock_members.date_as
                GROUP by mc_stock_members.code_id 
                ORDER BY mc_stock_members.code_id asc;
        """
        result = Shares.objects.raw(sql)
        for item in result:
            shareName2 = SharesName.objects.filter(code=item.code_id)
            if len(shareName2) > 0:
                if item.members >= item.tmembers:
                    shareName2 = SharesName(code=item.code_id, member_up=2)
                else:
                    shareName2 = SharesName(code=item.code_id, member_up=1)
                shareName2.save()


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

        json2 = r.json()
        if "gdrs" in json2:
            return json2["gdrs"]
        return []
