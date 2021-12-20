import numpy as np
from django.core.management.base import BaseCommand, CommandError
# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
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
        for item in SharesName.objects.all():
            # print(map(lambda item: {
            #     'close': item.p_end / 100,
            #     'height': item.p_max / 100,
            #     'low': item.p_min / 100,
            # }, item.shares_set.all().values()))
            itemList  = item.shares_set.all()
            kd = self.talib_KDJ(itemList)
            itemListLen = len(itemList)
            x = np.array([v for v in range(0,  itemListLen)])
            ky = kd['k']
            kj = kd['j']
            kd = kd['d']


            print(kj)
            break
        pass

    def talib_KDJ(self, data, fastk_period=9, slowk_period=3, slowd_period=3):
        indicators = {}
        # 计算kd指标
        high_prices = np.array([v.p_max / 100 for v in data])
        low_prices = np.array([v.p_min / 100 for v in data])
        close_prices = np.array([v.p_end / 100 for v in data])
        indicators['k'], indicators['d'] = talib.STOCH(high_prices, low_prices, close_prices,
                                                       fastk_period=fastk_period,
                                                       slowk_period=slowk_period,
                                                       slowk_matype=0,
                                                       slowd_period=slowd_period,
                                                       slowd_matype=0)
        # indicators['j'] = 3 * indicators['k'] - 2 * indicators['d']
        # indicators['j'] = 3 * indicators['d'] - 2 * indicators['k']
        indicators['j'] = list(map(lambda x, y: 3 * x - 2 * y, indicators['k'], indicators['d']))
        return indicators
