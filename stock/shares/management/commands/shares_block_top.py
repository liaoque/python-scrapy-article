import numpy as np
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares import Shares
from shares.model.shares_season import SharesSeason
import time


# import numpy as np
# import talib
import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '板块排行'

    def handle(self, *args, **options):
        sql = """
        select 1 as id, mc_shares_join_block.block_code_id, mc_shares.code_id 
        from mc_shares_join_block 
        left join mc_shares on mc_shares.code_id = mc_shares_join_block.code_id 
        where mc_shares.date_as = %s 
            and code_type = 2
            and mc_shares.p_end > mc_shares.p_start 
            and (mc_shares.p_end - mc_shares.p_start) / mc_shares.p_start >= 0.05
        """
        aggregate = {}
        aggregate_list = []
        result = Shares.objects.raw(sql, params=(date.today().strftime("%Y-%m-%d"),))
        for item in result:
            if item.block_code_id not in aggregate:
                aggregate[item.block_code_id] = set()
            aggregate[item.block_code_id].add(item.code_id)
            aggregate_list.append(item.block_code_id)
        self.translate(aggregate_list, aggregate)

    def translate(self, aggregate_list, aggregate):
        one = aggregate_list[0]
        l = {}
        key = 0
        for one in aggregate_list:
            key2 = key + 1
            for two in aggregate_list[key2:]:
                key3 = key + 2
                for three in aggregate_list[key3:]:
                    key = "%s-%s-%s" % (one, two, three)
                    d = aggregate[one].intersection(aggregate[two], aggregate[three])
                    if '885954' == one and two == '885403' and '885841' == three:
                        print(key, d, aggregate[one], aggregate[two], aggregate[three])
                    if d is None or len(d) == 0:
                        continue
                    l[key] = d
            key += 1
                # sys.exit(0)
                # break
        # print(l)
        # result = list(filter(lambda n: n.code_id in self.codeList, result))
        l2 = {key: len(l[key]) for key in l if l[key] is not None}
        print(l2)
        # print([{key: len(l[key])} for key in l])
