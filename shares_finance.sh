#!/bin/bash
export PATH=$PATH:/usr/local/bin
echo -n "开始执行爬虫"
source /alidata/python/venv/bin/activate
cd /alidata/python/python-scrapy-article-master/stock && \
python manage.py shares_finance