#!/bin/bash
export PATH=$PATH:/usr/local/bin
source /alidata/python/venv/bin/activate
cd /alidata/python/python-scrapy-article-master/stock && \
python manage.py stock_index
cd /alidata/python/python-scrapy-article-master/stock && \
python manage.py stock_large_day

## 格雷厄姆指标， 每天一次提醒即可