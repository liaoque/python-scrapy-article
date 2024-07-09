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
        url = f"https://d.10jqka.com.cn/v4/time/bk_{secid}/last.js"
        html = req.getTongHuaShun(url)
        html = html[35:-1]
        data = json.loads(html)

        # url = f"https://d.10jqka.com.cn/v4/line/bk_{secid}/01/2024.js"
        # self._all_months[secid] = req.getDF(url)
        self._all_months[secid] = [{
            "date_at": x[0],
            "start": float(x[1]),
            "end": float(x[1]),
            "max": float(x[1]),
            "min": float(x[1]),
            "count": int(x[4]),  # 成交量
            "amount": float(x[2]),  # 成交额
            # "amplitude": float(x[7]),  # 振幅
            # "range": float(x[8]),  # 涨跌幅
            # "range_amount": float(x[9]),  # 涨跌额
            # "turnover_rate": float(x[10]),  # 换手率
        } for v in data[f"bk_{secid}"]["data"].split(';') for x in [v.split(',')]]
        return self._all_months[secid]

    def minute30(self, secid, start=None, end=None):
        if start == None:
            start = ""
        if end == None:
            end = "20500101"
        if secid in self._all_minute30:
            return self._all_minute30[secid]
        url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid={secid}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=30&fqt=1&beg={start}&end={end}&smplmt=100000&lmt=100&_="

        self._all_minute30[secid] = req.getDF(url)
        self._all_minute30[secid] = [{
            "date_at": x[0],
            "start": float(x[1]),
            "end": float(x[2]),
            "max": float(x[3]),
            "min": float(x[4]),
            "count": int(x[5]),  # 成交量
            "amount": float(x[6]),  # 成交额
            "amplitude": float(x[7]),  # 振幅
            "range": float(x[8]),  # 涨跌幅
            "range_amount": float(x[9]),  # 涨跌额
            "turnover_rate": float(x[10]),  # 换手率
        } for v in self._all_minute30[secid] for x in [v.split(',')]]
        return self._all_minute30[secid]

    def minute60(self, secid, start=None, end=None):
        if start == None:
            start = ""
        if end == None:
            end = "20500101"
        if secid in self._all_minute60:
            return self._all_minute60[secid]
        url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid={secid}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=60&fqt=1&beg={start}&end={end}&smplmt=100000&lmt=100&_="

        self._all_minute60[secid] = req.getDF(url)
        self._all_minute60[secid] = [{
            "date_at": x[0],
            "start": float(x[1]),
            "end": float(x[2]),
            "max": float(x[3]),
            "min": float(x[4]),
            "count": int(x[5]),  # 成交量
            "amount": float(x[6]),  # 成交额
            "amplitude": float(x[7]),  # 振幅
            "range": float(x[8]),  # 涨跌幅
            "range_amount": float(x[9]),  # 涨跌额
            "turnover_rate": float(x[10]),  # 换手率
        } for v in self._all_minute60[secid] for x in [v.split(',')]]
        return self._all_minute60[secid]

    def daily(self, secid, start=None, end=None):
        if start == None:
            start = ""
        if end == None:
            end = "20500101"
        if secid in self._all_days:
            return self._all_days[secid]
        url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid={secid}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=1&beg={start}&end={end}&smplmt=100000&lmt=100&_="

        self._all_days[secid] = req.getDF(url)
        self._all_days[secid] = [{
            "date_at": x[0],
            "start": float(x[1]),
            "end": float(x[2]),
            "max": float(x[3]),
            "min": float(x[4]),
            "count": int(x[5]),  # 成交量
            "amount": float(x[6]),  # 成交额
            "amplitude": float(x[7]),  # 振幅
            "range": float(x[8]),  # 涨跌幅
            "range_amount": float(x[9]),  # 涨跌额
            "turnover_rate": float(x[10]),  # 换手率
        } for v in self._all_days[secid] for x in [v.split(',')]]
        return self._all_days[secid]

    def weekly(self, secid, start=None, end=None):
        if start == None:
            start = ""
        if end == None:
            end = "20500101"
        if secid in self._all_weeks:
            return self._all_weeks[secid]
        url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid={secid}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=102&fqt=1&beg={start}&end={end}&smplmt=100000&lmt=100&_="

        self._all_weeks[secid] = req.getDF(url)
        self._all_weeks[secid] = [{
            "date_at": x[0],
            "start": float(x[1]),
            "end": float(x[2]),
            "max": float(x[3]),
            "min": float(x[4]),
            "count": int(x[5]),  # 成交量
            "amount": float(x[6]),  # 成交额
            "amplitude": float(x[7]),  # 振幅
            "range": float(x[8]),  # 涨跌幅
            "range_amount": float(x[9]),  # 涨跌额
            "turnover_rate": float(x[10]),  # 换手率
        } for v in self._all_weeks[secid] for x in [v.split(',')]]
        return self._all_weeks[secid]

    def monthly(self, secid, start=None, end=None):
        if start == None:
            start = ""
        if end == None:
            end = "20500101"
        if secid in self._all_months:
            return self._all_months[secid]
        url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid={secid}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=103&fqt=1&beg={start}&end={end}&smplmt=100000&lmt=100&_="

        self._all_months[secid] = req.getDF(url)
        self._all_months[secid] = [{
            "date_at": x[0],
            "start": float(x[1]),
            "end": float(x[2]),
            "max": float(x[3]),
            "min": float(x[4]),
            "count": int(x[5]),  # 成交量
            "amount": float(x[6]),  # 成交额
            "amplitude": float(x[7]),  # 振幅
            "range": float(x[8]),  # 涨跌幅
            "range_amount": float(x[9]),  # 涨跌额
            "turnover_rate": float(x[10]),  # 换手率
        } for v in self._all_months[secid] for x in [v.split(',')]]
        return self._all_months[secid]


if __name__ == "__main__":
    print(TongHuaShun().minute("886056"))
