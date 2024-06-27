import quick_stock.remote.req as req
from quick_stock import share as share


class TradeStock:
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

        df = share.getTushare().stock_basic()
        columns = df.columns.tolist()
        columns[0] = 'code'
        df.columns = columns
        self._all_trade = df
        return self._all_trade

    def minute(self, secid):
        if secid in self._all_minute:
            return self._all_minute[secid]
        url = (
                  "http://25.push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid=%s&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f53&klt=101&fqt=1&beg=0&end=20500101&lmt=1000000&_=1711101890918") % (
                  secid)
        self._all_minute[secid] = req.getDF(url)
        return self._all_minute[secid]

    def minute30(self, secid):
        if secid in self._all_minute30:
            return self._all_minute30[secid]
        url = (
                  "http://25.push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid=%s&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f53&klt=101&fqt=1&beg=0&end=20500101&lmt=1000000&_=1711101890918") % (
                  secid)
        self._all_minute30[secid] = req.getDF(url)
        return self._all_minute30[secid]

    def minute60(self, secid):
        if secid in self._all_minute60:
            return self._all_minute60[secid]
        url = (
                  "http://25.push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid=%s&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f53&klt=101&fqt=1&beg=0&end=20500101&lmt=1000000&_=1711101890918") % (
                  secid)
        self._all_minute60[secid] = req.getDF(url)
        return self._all_minute60[secid]

    def daily(self, code):
        if code in self._all_days:
            return self._all_days[code]
        url = "https://push2.eastmoney.com/api/qt/stock/get?" \
        "ut=fa5fd1943c7b386f172d6893dbfba10b&fltt=2&invt=2&" \
        "fields=f120,f121,f122,f174,f175,f59,f163,f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,f268,f255,f256,f257,f258,f127,f199,f128,f198,f259,f260,f261,f171,f277,f278,f279,f288,f152,f250,f251,f252,f253,f254,f269,f270,f271,f272,f273,f274,f275,f276,f265,f266,f289,f290,f286,f285,f292,f293,f294,f295" \
        "&secid=" + str(code) + "&cb=&_=1653740799012"
        self._all_days[code] = req.getDF(url)
        return self._all_days[code]

    def weekly(self, code):
        if code in self._all_weeks:
            return self._all_weeks[code]
        days = 10000
        url = 'https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=' + \
            str(code) + '&cb=&klt=102&fqt=1&lmt=' + str(days) + \
            '&end=20500101&iscca=1&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55'
        self._all_weeks[code] = req.getDF(url)
        return self._all_weeks[code]

    def monthly(self, code):
        if code in self._all_months:
            return self._all_months[code]
        days = 10000
        url = 'https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=' + \
              str(code) + '&cb=&klt=103&fqt=1&lmt=' + str(days) + \
              '&end=20500101&iscca=1&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55'
        self._all_months[code] = req.getDF(url)
        return self._all_months[code]



