import datetime

import quick_stock.remote.req as req
from lxml import etree
import json
from lxml.cssselect import CSSSelector





# https://q.10jqka.com.cn/gn/
class TongHuaShun:
    _all_trade = {}
    _all_concept_stock = {}
    _all_days = {}
    _all_weeks = {}
    _all_months = {}
    _all_minute = {}
    _all_minute30 = {}
    _all_minute60 = {}

    def get_all(self):
        url = f"https://q.10jqka.com.cn/gn/"
        html = req.getTongHuaShun(url, headers={
            "HOST": "q.10jqka.com.cn",
        })
        root = etree.fromstring(html, etree.HTMLParser(encoding='utf-8'))
        value = root.cssselect('#gnSection')[0].get("value")
        values = json.loads(value)
        self._all_trade = [{
            "code": item["platecode"],
            "name": item["platename"],
            "cid": item["cid"],
        } for key, item in values.items()]
        return self._all_trade

    def get_all_concept_stock(self, concept):
        url = f"http://q.10jqka.com.cn/gn/detail/field/199112/order/desc/size/1000/page/1/ajax/1/code/" + concept
        html = req.getTongHuaShun(url)
        root = etree.fromstring(html, etree.HTMLParser(encoding='utf-8'))
        values = root.cssselect('tr td:nth-child(2) a')

        self._all_concept_stock[concept] = [{
            "code": item.text,
            "cid": concept,
        } for item in values]
        return self._all_concept_stock[concept]

    def minute(self, secid, end=None):
        # klt = 分钟
        if secid in self._all_months:
            return self._all_months[secid]
        # https://d.10jqka.com.cn/v4/line/bk_885943/61/last.js
        url = f"https://d.10jqka.com.cn/v4/time/bk_{secid}/last.js"
        year = datetime.date.today().year
        url = f"https://d.10jqka.com.cn/v4/line/bk_{secid}/61/{year}.js"
        html = req.getTongHuaShun(url)
        html = html[35:-1]
        data = json.loads(html)

        # url = f"https://d.10jqka.com.cn/v4/line/bk_{secid}/01/2024.js"
        # self._all_months[secid] = req.getDF(url)
        self._all_months[secid] = [{
            "date_at": x[0],
            "start": float(x[1]),
            "end": float(x[4]),
            "max": float(x[2]),
            "min": float(x[3]),
            "count": int(x[5]),  # 成交量
            "amount": float(x[6]),  # 成交额
            "amplitude": float(x[2] - x[3]),  # （当期最高价－当期最低价）/前一交易日收盘价×100%
            "range": float(0),  # 当日收盘价−前一交易日收盘价/前一交易日收盘价
            "range_amount": float(x[9]),  # 当前交易日的最新成交价（或收盘价） - 前一交易日的收盘价
            "turnover_rate": float(0),  # 换手率
        } for v in data[f"bk_{secid}"]["data"].split(';') for x in [v.split(',')]]
        return self._all_months[secid]

    def minute30(self, secid, start=None, end=None):
        # https://d.10jqka.com.cn/v4/line/bk_885943/41/last.js
        year = datetime.date.today().year
        d = []
        while year > 2014:
            url = f"https://d.10jqka.com.cn/v4/line/bk_{secid}/41/{year}.js"
            html = req.getTongHuaShun(url)
            if html == False:
                break
            html = html[38:-1]
            data = json.loads(html)

            d = d.extend([{
                "date_at": x[0],
                "start": float(x[1]),
                "end": float(x[4]),
                "max": float(x[2]),
                "min": float(x[3]),
                "count": int(x[5]),  # 成交量
                "amount": float(x[6]),  # 成交额
                "amplitude": float(x[2] - x[3]),  # （当期最高价－当期最低价）/前一交易日收盘价×100%
                "range": float(0),  # 当日收盘价−前一交易日收盘价/前一交易日收盘价
                "range_amount": float(x[9]),  # 当前交易日的最新成交价（或收盘价） - 前一交易日的收盘价
                "turnover_rate": float(0),  # 换手率
            } for v in data["data"].split(';') for x in [v.split(',')]])
        self._all_minute30[secid] = d
        return self._all_minute30[secid]


    def minute60(self, secid, start=None, end=None):
        # https://d.10jqka.com.cn/v4/line/bk_885943/51/last.js

        year = datetime.date.today().year
        d = []
        while year > 2014:
            url = f"https://d.10jqka.com.cn/v4/line/bk_{secid}/51/{year}.js"
            html = req.getTongHuaShun(url)
            if html == False:
                break
            html = html[38:-1]
            data = json.loads(html)

            d = d.extend([{
                "date_at": x[0],
                "start": float(x[1]),
                "end": float(x[4]),
                "max": float(x[2]),
                "min": float(x[3]),
                "count": int(x[5]),  # 成交量
                "amount": float(x[6]),  # 成交额
                "amplitude": float(x[2] - x[3]),  # （当期最高价－当期最低价）/前一交易日收盘价×100%
                "range": float(0),  # 当日收盘价−前一交易日收盘价/前一交易日收盘价
                "range_amount": float(x[9]),  # 当前交易日的最新成交价（或收盘价） - 前一交易日的收盘价
                "turnover_rate": float(0),  # 换手率
            } for v in data["data"].split(';') for x in [v.split(',')]])
        self._all_minute60[secid] = d
        return self._all_minute60[secid]

    def daily(self, secid, start=None, end=None):
        if secid in self._all_days:
            return self._all_days[secid]
        # url = f"https://d.10jqka.com.cn/v4/line/bk_{secid}/01/last.js"
        # html = req.getTongHuaShun(url)
        # html = html[37:-1]
        # data = json.loads(html)
        year = datetime.date.today().year
        d = []
        while year > 2014:
            # https://d.10jqka.com.cn/v4/line/bk_885943/01/2021.js
            url = f"https://d.10jqka.com.cn/v4/line/bk_{secid}/01/{year}.js"
            html = req.getTongHuaShun(url)
            if html == False:
                break
            html = html[38:-1]
            data = json.loads(html)

            d = d.extend([{
                "date_at": x[0],
                "start": float(x[1]),
                "end": float(x[4]),
                "max": float(x[2]),
                "min": float(x[3]),
                "count": int(x[5]),  # 成交量
                "amount": float(x[6]),  # 成交额
                "amplitude": float(x[2] - x[3]),  # （当期最高价－当期最低价）/前一交易日收盘价×100%
                "range": float(0),  # 当日收盘价−前一交易日收盘价/前一交易日收盘价
                "range_amount": float(x[9]),  # 当前交易日的最新成交价（或收盘价） - 前一交易日的收盘价
                "turnover_rate": float(0),  # 换手率
            } for v in data["data"].split(';') for x in [v.split(',')]])
        self._all_days[secid] = d
        return self._all_days[secid]

    def weekly(self, secid, start=None, end=None):
        if secid in self._all_weeks:
            return self._all_weeks[secid]
        year = datetime.date.today().year
        d = []
        while year > 2014:
            # https://d.10jqka.com.cn/v4/line/bk_885943/11/last.js
            url = f"https://d.10jqka.com.cn/v4/line/bk_{secid}/11/{year}.js"
            html = req.getTongHuaShun(url)
            if html == False:
                break
            html = html[38:-1]
            data = json.loads(html)

            d = d.extend([{
                "date_at": x[0],
                "start": float(x[1]),
                "end": float(x[4]),
                "max": float(x[2]),
                "min": float(x[3]),
                "count": int(x[5]),  # 成交量
                "amount": float(x[6]),  # 成交额
                "amplitude": float(x[2] - x[3]),  # （当期最高价－当期最低价）/前一交易日收盘价×100%
                "range": float(0),  # 当日收盘价−前一交易日收盘价/前一交易日收盘价
                "range_amount": float(x[9]),  # 当前交易日的最新成交价（或收盘价） - 前一交易日的收盘价
                "turnover_rate": float(0),  # 换手率
            } for v in data["data"].split(';') for x in [v.split(',')]])
        return self._all_weeks[secid]

    def monthly(self, secid, start=None, end=None):
        if secid in self._all_months:
            return self._all_months[secid]
        url = f"https://d.10jqka.com.cn/v4/line/bk_{secid}/21/last.js"
        html = req.getTongHuaShun(url)

        html = html[38:-1]
        data = json.loads(html)

        self._all_months[secid] = [{
            "date_at": x[0],
            "start": float(x[1]),
            "end": float(x[4]),
            "max": float(x[2]),
            "min": float(x[3]),
            "count": int(x[5]),  # 成交量
            "amount": float(x[6]),  # 成交额
            "amplitude": float(x[2] - x[3]),  # （当期最高价－当期最低价）/前一交易日收盘价×100%
            "range": float(0),  # 当日收盘价−前一交易日收盘价/前一交易日收盘价
            "range_amount": float(x[9]),  # 当前交易日的最新成交价（或收盘价） - 前一交易日的收盘价
            "turnover_rate": float(0),  # 换手率
        } for v in data["data"].split(';') for x in [v.split(',')]]
        return self._all_months[secid]


if __name__ == "__main__":
    print(TongHuaShun().minute("886056"))
