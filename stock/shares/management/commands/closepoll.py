
from django.core.management.base import BaseCommand, CommandError
# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
# from ....shares.model.shares_kdj import SharesKdj
# from ....shares.model.shares import Shares
import numpy
# import talib

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
            print(item)
            break
        pass
