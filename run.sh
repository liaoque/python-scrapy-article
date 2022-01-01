#!/bin/bash
export PATH=$PATH:/usr/local/bin
echo -n "开始执行爬虫"
source /alidata/python/venv/bin/activate
cd /alidata/python/python-scrapy-article-master && nohup python main3.py
cd /alidata/python/python-scrapy-article-master && nohup python main5.py
cd /alidata/python/python-scrapy-article-master && nohup python main2.py
cd /alidata/python/python-scrapy-article-master && nohup python main.py
cd /alidata/python/python-scrapy-article-master && nohup python shares-zl.py
cd /alidata/python/python-scrapy-article-master && nohup python shares.py