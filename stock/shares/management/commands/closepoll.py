import numpy as np
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares_kdj import SharesKdj
from shares.model.shares import Shares
from shares.model.shares_kdj_compute import SharesKdjCompute
from shares.model.shares_kdj_compute_detail import SharesKdjComputeDetail
# from ....shares.model.shares_kdj import SharesKdj
# from ....shares.model.shares import Shares
import numpy as np
import talib

" /bin/cp /alidata/python/python-scrapy-article/stock/* /alidata/python/python-scrapy-article-master/stock -rf"


class Command(BaseCommand):
    help = '计算各种指标'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        # self.calculateKdj()
        self.KdjCompute()

        pass

    def calculateKdj(self):
        today = datetime.now().date().strftime('%Y-%m-%d')
        for item in SharesName.objects.filter(status=1):

            # 写过了
            code = item.code
            sharesKdjList = SharesKdj.objects.filter(code_id=code, date_as=today)
            # print(len(sharesKdjList))
            if len(sharesKdjList):
                continue

            # print(map(lambda item: {
            #     'close': item.p_end / 100,
            #     'height': item.p_max / 100,
            #     'low': item.p_min / 100,
            # }, item.shares_set.all().values()))

            # 数据不存在
            itemList = item.shares_set.all()
            # print(str(len(itemList)) +"---")
            if len(itemList) == 0:
                continue

            # 数据不是今天的
            shares = np.array(itemList)[-1:][0]
            date_as = str(shares.date_as)
            if date_as != today:
                continue

            # 计算kdj
            print(code + "：" + date_as + "：开始计算kdj")
            kd = self.talib_KDJ(itemList)
            # print("计算出未知数据", (code,  kd))
            # itemListLen = len(itemList)
            # x = np.array([v for v in range(0, itemListLen)])
            ky = kd['k'][-1:][0]
            kj = kd['j'][-1:][0]
            kd = kd['d'][-1:][0]

            if repr(ky) in ("inf", "nan") or repr(kj) in ("inf", "nan") or repr(kd) in ("inf", "nan"):
                print("计算出未知数据", (code, ky, kd, kj))
                continue

            b = SharesKdj(code_id=code, k=ky, d=kd, j=kj, cycle_type=1, date_as=date_as)
            b.save()
            # SharesKdj
            # print(shares, ky, kj, kd, shares.code_id)
            # break
        pass

    def talib_KDJ(self, data, fastk_period=9, slowk_period=3, slowd_period=3):
        indicators = {}
        # 计算kd指标
        high_prices = np.array([v.p_max / 100 for v in data])
        low_prices = np.array([v.p_min / 100 for v in data])
        close_prices = np.array([v.p_end / 100 for v in data])
        slowk_period = 2 * slowk_period - 1
        slowd_period = 2 * slowd_period - 1
        indicators['k'], indicators['d'] = talib.STOCH(high_prices, low_prices, close_prices,
                                                       fastk_period=fastk_period,
                                                       slowk_period=slowk_period,
                                                       slowk_matype=1,
                                                       slowd_period=slowd_period,
                                                       slowd_matype=1)
        # indicators['j'] = 3 * indicators['k'] - 2 * indicators['d']
        # indicators['j'] = 3 * indicators['d'] - 2 * indicators['k']
        indicators['j'] = np.array(list(map(lambda x, y: 3 * x - 2 * y, indicators['k'], indicators['d'])))
        return indicators

    def KdjCompute(self):
        today = datetime.now().date().strftime('%Y-%m-%d')
        today = '2021-12-24'
        data = Shares.objects.filter(date_as=today)[:1]
        if len(data) == 0:
            # 当天不 需要计算
            return
        result = np.array(SharesKdj.objects.values('date_as').all())[-5:]
        print(result, len(result))
        # first, second, third, fourth, fifth = SharesKdj.objects.values('date_as')[-5:]
        # print(first, second, third, fourth, fifth)
        # intersection_total = SharesKdjCompute.Compute.intersection_total(third, fourth, fifth)
        # intersection_today = SharesKdjCompute.Compute.intersection_today(third, fourth, fifth)
        # intersection_pre = SharesKdjCompute.Compute.intersection_pre(second, third, fourth, fifth)
        # turn_total = SharesKdjCompute.Compute.turn_total(third, fourth, fifth)
        # turn_tomorrow = SharesKdjCompute.Compute.turn_tomorrow(third, fourth, fifth)
        # print(intersection_total, intersection_today, intersection_pre,turn_total, turn_tomorrow)

        # shill_type = SharesName.skill_type.kdj
        # SharesKdjCompute.saveSharesKdjCompute(intersection_pre_num=len(intersection_pre),
        #                           intersection_num=len(intersection_today),
        #                           intersection_total=intersection_total[0]['c'],
        #                           turn_num=len(turn_tomorrow),
        #                           turn_total=turn_total[0]['c'],
        #                           shill_type=shill_type,
        #                           date_as=today)






