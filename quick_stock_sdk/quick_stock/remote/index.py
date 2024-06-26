import quick_stock.remote.req as req
from quick_stock import share as share


class TradeIndex:
    _all_trade = None
    _all_days = {}
    _all_weeks = {}
    _all_months = {}

    def get_all(self):
        if self._all_trade:
            return self._all_trade

        df = share.getTushare().index_basic()
        columns = df.columns.tolist()
        columns[0] = 'code'
        df.columns = columns
        self._all_trade = df
        return self._all_trade

    def daily(self, secid):
        if self._all_days[secid] :
            return self._all_days[secid]
        url = (
                  "http://25.push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid=%s&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f53&klt=101&fqt=1&beg=0&end=20500101&lmt=1000000&_=1711101890918") % (
                  secid)
        self._all_days[secid] = req.getDF(url)
        return self._all_days[secid]

    def weekly(self,secid):
        if self._all_weeks[secid] :
            return self._all_weeks[secid]
        url = (
                  "https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid=%s&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=102&fqt=1&end=20500101&lmt=10000&_=1713314412556"
              ) % (
                  secid)
        self._all_weeks[secid] = req.getDF(url)
        return self._all_weeks[secid]

    def monthly(self, secid):
        if self._all_months[secid] :
            return self._all_months[secid]
        url = (
                  "https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid=%s&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=103&fqt=1&end=20500101&lmt=120&_=1713314412640"
              ) % (
                  secid)
        self._all_months[secid] = req.getDF(url)
        return self._all_months[secid]


