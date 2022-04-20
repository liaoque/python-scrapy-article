import numpy as np
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares_kdj_hours import SharesKdjHours
from shares.model.shares_hours import SharesHours
from shares.model.shares_kdj_compute import SharesKdjCompute
from shares.model.shares_kdj_compute_detail import SharesKdjComputeDetail
# from ....shares.model.shares_kdj import SharesKdj
# from ....shares.model.shares import Shares
import numpy as np
import talib

# " /bin/cp /alidata/python/python-scrapy-article/stock/* /alidata/python/python-scrapy-article-master/stock -rf"


class Command(BaseCommand):
    help = '计算各种指标'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        self.calculateKdj()
        print("开始计算kdj-----")
        pass

    def calculateKdj(self):
        today = datetime.now().date().strftime('%Y-%m-%d')
        # today = '2021-12-27'
        today = '2022-02-16'
        for item in SharesName.objects.filter(status=1,code_type=1):

            # 写过了
            code = item.code
            # sharesKdjList = SharesKdj.objects.filter(code_id=code, date_as=today)
            # if len(sharesKdjList):
            #     continue

            # 数据不存在
            itemList = SharesHours.objects.filter(code_id=code).order_by('date_as').all()
            if len(itemList) == 0:
                continue

            # 数据不是今天的
            # shares = np.array(itemList)[-1:][0]
            # date_as = str(shares.date_as)
            # if date_as != today:
            #     continue

            # 计算kdj
            # print(code + "：" + date_as + "：开始计算kdj")
            kd2 = self.talib_KDJ(itemList)

            i = 0
            for item in itemList:
                i +=1
                if item.date_as.strftime('%Y-%m-%d') != today:
                    continue
                ky = kd2['k'][i]
                kj = kd2['j'][i]
                kd = kd2['d'][i]
                if repr(ky) in ("inf", "nan") or repr(kj) in ("inf", "nan") or repr(kd) in ("inf", "nan"):
                    print("计算出未知数据", (code, ky, kd, kj))
                    continue

                sharesKdjList = SharesKdjHours.objects.filter(code_id=code, date_as=item.date_as)
                if len(sharesKdjList):
                    continue

                b = SharesKdjHours(code_id=code, k=ky, d=kd, j=kj, cycle_type=1, date_as=item.date_as)
                b.save()
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


