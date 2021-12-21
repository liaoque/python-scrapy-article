import numpy as np
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares_kdj import SharesKdj
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
        self.calculateKdj()

        pass

    def calculateKdj(self):
        today = datetime.now().date().strftime('%Y-%m-%d')
        for item in SharesName.objects.filter(status=1):

            # 写过了
            code = item.code
            sharesKdjList = SharesKdj.objects.filter(code_id=code, date_as=today)
            if len(sharesKdjList):
                continue

            # print(map(lambda item: {
            #     'close': item.p_end / 100,
            #     'height': item.p_max / 100,
            #     'low': item.p_min / 100,
            # }, item.shares_set.all().values()))

            # 数据不是今天的
            itemList = item.shares_set.all()
            shares = np.array(itemList)[-1:][0]
            date_as = shares.date_as
            if date_as != today:
                continue

            # 计算kdj
            kd = self.talib_KDJ(itemList)
            itemListLen = len(itemList)
            x = np.array([v for v in range(0, itemListLen)])
            ky = kd['k'][-1:]
            kj = kd['j'][-1:]
            kd = kd['d'][-1:]

            info = SharesKdj.objects.filter(code_id=code, date_as=date_as)
            if info == None:
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
