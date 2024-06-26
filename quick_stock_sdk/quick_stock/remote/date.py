import remote.req as req
class TradeDays:
    _all_trade = None

    def get_all(self):
        if self._all_trade:
            return self._all_trade

        url = (
                  "http://25.push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid=%s&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1,f2,f3,f4,f5,f6&fields2=f51&klt=101&fqt=1&beg=0&end=20500101&lmt=1000000&_=1711101890918") % (
                  "1.000001"
        )
        self._all_trade = req.getDF(url)
        return self._all_trade


