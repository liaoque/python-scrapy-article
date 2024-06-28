import quick_stock.remote.req as req
from quick_stock import share as share


class TradeFund:
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

        df = share.getTushare().fund_basic()
        columns = df.columns.tolist()
        columns[0] = 'code'
        df.columns = columns
        self._all_trade = df
        return self._all_trade

    def minute(self, secid, end=None):
        if end == None:
            end = "20500101"
        if secid in self._all_minute:
            return self._all_minute[secid]
        url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid={secid}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=1&fqt=1&end={end}&lmt=120&_=1719485357860"

        self._all_minute[secid] = req.getDF(url)
        self._all_minute[secid] = [{
            "date_at": x[0],
            "start": x[1],
            "end": x[2],
            "max": x[3],
            "min": x[4],
            "count": x[5],  # 成交量
            "amount": x[6],  # 成交额
            "amplitude": x[7],  # 振幅
            "range": x[8],  # 涨跌幅
            "range_amount": x[9],  # 涨跌额
            "turnover_rate": x[10],  # 换手率
        } for v in self._all_minute[secid] for x in [v.split(',')]]
        return self._all_minute[secid]

    def minute30(self, secid, end=None):
        if end == None:
            end = "20500101"
        if secid in self._all_minute30:
            return self._all_minute30[secid]
        url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid={secid}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=30&fqt=1&end={end}&lmt=120&_=1719485357860"

        self._all_minute30[secid] = req.getDF(url)
        self._all_minute30[secid] = [{
            "date_at": x[0],
            "start": x[1],
            "end": x[2],
            "max": x[3],
            "min": x[4],
            "count": x[5], # 成交量
            "amount": x[6], #成交额
            "amplitude": x[7],  # 振幅
            "range": x[8], # 涨跌幅
            "range_amount": x[9], # 涨跌额
            "turnover_rate": x[10], # 换手率
        } for v in self._all_minute30[secid] for x in [v.split(',')]]

        return self._all_minute30[secid]

    def minute60(self, secid, end=None):
        if end == None:
            end = "20500101"
        if secid in self._all_minute60:
            return self._all_minute60[secid]
        url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid={secid}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=60&fqt=1&end={end}&lmt=120&_=1719485357860"

        self._all_minute60[secid] = req.getDF(url)
        self._all_minute60[secid] = [{
            "date_at": x[0],
            "start": x[1],
            "end": x[2],
            "max": x[3],
            "min": x[4],
            "count": x[5],  # 成交量
            "amount": x[6],  # 成交额
            "amplitude": x[7],  # 振幅
            "range": x[8],  # 涨跌幅
            "range_amount": x[9],  # 涨跌额
            "turnover_rate": x[10],  # 换手率
        } for v in self._all_minute60[secid] for x in [v.split(',')]]
        return self._all_minute60[secid]

    def daily(self, code, end=None):
        if end == None:
            end = "20500101"
        if code in self._all_days:
            return self._all_days[code]
        url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid={code}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=1&beg=0&end={end}&lmt=1000000&_=1719485357933"

        self._all_days[code] = req.getDF(url)
        self._all_days[code] = [{
            "date_at": x[0],
            "start": x[1],
            "end": x[2],
            "max": x[3],
            "min": x[4],
            "count": x[5],  # 成交量
            "amount": x[6],  # 成交额
            "amplitude": x[7],  # 振幅
            "range": x[8],  # 涨跌幅
            "range_amount": x[9],  # 涨跌额
            "turnover_rate": x[10],  # 换手率
        } for v in self._all_days[code] for x in [v.split(',')]]
        return self._all_days[code]

    def weekly(self, code, end=None):
        if end == None:
            end = "20500101"
        if code in self._all_weeks:
            return self._all_weeks[code]
        url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid={code}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=102&fqt=1&beg=0&end={end}&lmt=1000000&_=1719485357982"

        self._all_weeks[code] = req.getDF(url)
        self._all_weeks[code] = [{
            "date_at": x[0],
            "start": x[1],
            "end": x[2],
            "max": x[3],
            "min": x[4],
            "count": x[5],  # 成交量
            "amount": x[6],  # 成交额
            "amplitude": x[7],  # 振幅
            "range": x[8],  # 涨跌幅
            "range_amount": x[9],  # 涨跌额
            "turnover_rate": x[10],  # 换手率
        } for v in self._all_weeks[code] for x in [v.split(',')]]
        return self._all_weeks[code]

    def monthly(self, code, end=None):
        if end == None:
            end = "20500101"
        if code in self._all_months:
            return self._all_months[code]
        url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid={code}&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=103&fqt=1&beg=0&end={end}&lmt=1000000&_=1719485357982"

        self._all_months[code] = req.getDF(url)
        self._all_months[code] = [{
            "date_at": x[0],
            "start": x[1],
            "end": x[2],
            "max": x[3],
            "min": x[4],
            "count": x[5],  # 成交量
            "amount": x[6],  # 成交额
            "amplitude": x[7],  # 振幅
            "range": x[8],  # 涨跌幅
            "range_amount": x[9],  # 涨跌额
            "turnover_rate": x[10],  # 换手率
        } for v in self._all_months[code] for x in [v.split(',')]]
        return self._all_months[code]



if __name__ == "__main__":
    print(TradeFund().weekly(0.159537))