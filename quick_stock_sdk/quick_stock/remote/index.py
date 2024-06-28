import quick_stock.remote.req as req
from quick_stock import share as share


class TradeIndex:
    _all_trade = None
    _all_days = {}
    _all_weeks = {}
    _all_months = {}
    _all_minute = {}
    _all_minute30 = {}
    _all_minute60 = {}

    def get_all(self):
        if self._all_trade:
            return self._all_trade

        df = share.getTushare().index_basic()
        columns = df.columns.tolist()
        columns[0] = 'code'
        df.columns = columns
        self._all_trade = df
        return self._all_trade

    def minute(self, secid, end=None):
        if end == None:
            end = "20500101"
        # klt = 分钟
        if secid in self._all_months:
            return self._all_months[secid]
        url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid={secid}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=1&fqt=1&beg=0&end={end}&smplmt=460&lmt=1000000&_=1719483528271"
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

    def minute30(self, secid, start=None,  end=None):
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

    def minute60(self, secid, start=None,  end=None):
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
    print(TradeIndex().weekly(1.000001))