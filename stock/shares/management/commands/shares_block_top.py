import numpy as np
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares import Shares
from shares.model.shares_season import SharesSeason
import time
from shares.model.shares_date import SharesDate
# import numpy as np
# import talib
import sys


# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '板块排行'

    def handle(self, *args, **options):
        item = SharesDate.objects.order_by('-date_as').all()[0]
        print(item)
        sql = """
        select 1 as id, mc_shares_join_block.block_code_id, mc_shares.code_id 
        from mc_shares_join_block 
        left join mc_shares on mc_shares.code_id = mc_shares_join_block.code_id 
        where mc_shares.date_as = %s 
            and code_type = 1
            and mc_shares.p_end > mc_shares.p_start 
            and (mc_shares.p_end - mc_shares.p_start) / mc_shares.p_start >= 0.05
            and mc_shares_join_block.block_code_id not in (
            'BK0815', 'BK1050', 'BK0596', 'BK0879', 'BK0971', 'BK0501', 'BK0701', 
            'BK0707', 'BK0804','BK0867','BK0816','BK0571','BK1051','BK0817',
            'BK0570', 'BK0552', 'BK0705','BK0742','BK0568','BK0638','BK0697','BK0498',
            'BK0514','BK0594','BK0821','BK0500','BK0612'
            )
        """
        aggregate = {}
        aggregate_list = []
        result = Shares.objects.raw(sql, params=(item.date_as,))
        for item in result:
            if item.block_code_id not in aggregate:
                aggregate[item.block_code_id] = set()
            aggregate[item.block_code_id].add(item.code_id)
            aggregate_list.append(item.block_code_id)
        self.translate(aggregate_list, aggregate)

    def translate(self, aggregate_list, aggregate):
        aggregate_list = list(set(aggregate_list))
        l = {}
        ite = 0
        slen = len(aggregate_list)
        for one in aggregate_list:
            key2 = ite + 1
            if key2 == slen:
                continue
            for two in aggregate_list[key2:]:
                key3 = key2 + 1
                if key3 == slen:
                    continue
                for three in aggregate_list[key3:]:
                    key = (one, two, three)
                    d = aggregate[one].intersection(aggregate[two], aggregate[three])
                    if '885954' == one and two == '885403' and '885841' == three:
                        print(key, d, aggregate[one], aggregate[two], aggregate[three])
                    if d is None or len(d) < 2:
                        continue
                    l[key] = d
                key2 += 1
            ite += 1
            # sys.exit(0)
            # break

        all = SharesName.objects.filter(code_type=3)
        all = {item.code: item.name for item in all}
        l2 = {key: len(l[key]) for key in l if l[key] is not None}
        res = sorted(l2.items(), key=lambda d: d[1], reverse=True)
        for item in res[:20]:
            print({n: all[n] for n in item[0]}, l[item[0]])

        # print(res[:10])
        # result = list(filter(lambda n: n.code_id in self.codeList, result))
        # l2 = {key: len(l[key]) for key in l if l[key] is not None}
        # print(l2)
        # print([{key: len(l[key])} for key in l])
