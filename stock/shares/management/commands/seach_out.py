import numpy as np
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares_kdj import SharesKdj
from shares.model.shares import Shares
from shares.model.shares_join_block import SharesJoinBlock
import numpy as np
import talib
import requests

# " /bin/cp /alidata/python/python-scrapy-article/stock/* /alidata/python/python-scrapy-article-master/stock -rf"


class Command(BaseCommand):
    help = '查印度，印尼，缅甸，老挝，越南'



    def handle(self, *args, **options):
        l = []
        for item in SharesJoinBlock.objects.filter(block_code_id='BK0712', code_id="603556"):
            code = item.code_id
            url = "http://basic.10jqka.com.cn/" +str(code)+"/operate.html"
            r = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            })
            t = r.text.encode('latin-1').decode('gbk').encode('utf-8')
            t = str(t)
            print(t)
            if t.find("印度") != -1:
                l.append(code)
                continue
            if t.find("印尼") != -1:
                l.append(code)
                continue
            if t.find("缅甸") != -1:
                l.append(code)
                continue
            if t.find("老挝") != -1:
                l.append(code)
                continue
            if t.find("越南") != -1:
                l.append(code)
                continue

        print('","'.join(l))