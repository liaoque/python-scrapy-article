#!/bin/bash
export PATH=$PATH:/usr/local/bin
source /alidata/python/venv/bin/activate
cd /alidata/python/python-scrapy-article-master/stock && \
python manage.py kdj-listen
