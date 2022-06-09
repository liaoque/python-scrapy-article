import numpy as np
from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min
from django.core.mail import send_mail

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
        all = {}
        item = SharesDate.objects.order_by('-date_as').all()[0]
        all['one'] = self.check_block(item)

        item = SharesDate.objects.order_by('-date_as').all()[5]
        all['five'] = self.check_block(item)

        item = SharesDate.objects.order_by('-date_as').all()[20]
        all['twenty'] = self.check_block(item)

        self.sendMessage(all)

    def check_block(self, item):
        sql = """
               select 1 as id, mc_shares_join_block.block_code_id, mc_shares.code_id 
               from mc_shares_join_block 
               left join mc_shares on mc_shares.code_id = mc_shares_join_block.code_id 
               where mc_shares.date_as >= %s 
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
        return self.translate(aggregate_list, aggregate)

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
        # return res[:20]
        c = []
        for item in res[:20]:
            c.append([
                {n: all[n] for n in item[0]},
                l[item[0]]
            ])
            # print({n: all[n] for n in item[0]}, l[item[0]])
        return c
        # print(res[:10])
        # result = list(filter(lambda n: n.code_id in self.codeList, result))
        # l2 = {key: len(l[key]) for key in l if l[key] is not None}
        # print(l2)
        # print([{key: len(l[key])} for key in l])

    def sendMessage(self, send_data):
        tz = timezone(timedelta(hours=+8))
        s = "天\n"
        for item in send_data['one']:
            s += ",".join([all[n] for n in item[0]])
            s += "---------------"
            s += ",".join(item[1])
            s += "\n"

        s = "周\n"
        for item in send_data['five']:
            s += ",".join([all[n] for n in item[0]])
            s += "---------------"
            s += ",".join(item[1])
            s += "\n"

        s = "月\n"
        for item in send_data['twenty']:
            s += ",".join([all[n] for n in item[0]])
            s += "---------------"
            s += ",".join(item[1])
            s += "\n"

        print(s)
        # [[all[n] for n in item[0]] for item in send_data['one']]
        #
        # "天 %s" % ()

        # str = "天 %s" % (
        #     "\",\"".join([[all[n] for n in item[0]] for item in send_data['one']])
        # )

        # str = "董事会日期：%s\n 股东大会预案公告日期：%s\n 实施公告日：%s\n A股股权登记日：%s\n A股除权除息日：%s\n" % (
        #     "\",\"".join(send_data['directors_date_as']),
        #     "\",\"".join(send_data['shareholder_date_as']),
        #     "\",\"".join(send_data['implement_date_as']),
        #     "\",\"".join(send_data['register_date_as']),
        #     "\",\"".join(send_data['ex_date_as']))

        # send_mail(
        #     '分红%s' % (datetime.now(tz)),
        #     s,
        #     'lovemeand1314@163.com',
        #     ['844596330@qq.com'],
        #     fail_silently=False,
        # )
