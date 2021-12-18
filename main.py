# -*- coding: utf-8 -*-
__author__ = 'bobby'

from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", "baisibudejie"])
# execute(["scrapy", "crawl", "baozouribao"])
# execute(["scrapy", "crawl", "neihanduanzi"])
# execute(["scrapy", "crawl", "qiushibaike"])
# execute(["scrapy", "crawl", "xiaoshenlaile"])
# execute(["scrapy", "crawl", "lagou"])

# execute(["scrapy", "crawl", "q6m5m"])
# execute(["scrapy", "crawl", "q6m5mdownurl"])
# execute(["scrapy", "crawl", "shares"])
execute(["scrapy", "crawl", "shares_name"])
# execute(["scrapy", "crawl", "Shares_temper"])
# execute(["scrapy", "crawl", "Shares_temper_t"])