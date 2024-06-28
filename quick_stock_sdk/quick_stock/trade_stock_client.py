import datetime
from quick_stock.d import getDClient
from quick_stock.remote.stock import TradeStock


class TradeStockClient:
    dClient = None

    def __init__(self):
        self.dClient = getDClient()

    def get_all_stock(self):
        """
        :return: list - string
        """
        df = self.dClient.select("select * from mc_stock_basic")
        if df.empty or datetime.date.today().day == 1:
            df = TradeStock().get_all()
            self.dClient.save(df, 'mc_stock_basic')
        return df

    def daily(self, code, start=None, end=None):
        return TradeStock().daily(code,start,end)

    def weekly(self, code, start=None, end=None):
        return TradeStock().weekly(code,start,end)

    def monthly(self, code, start=None, end=None):
        return TradeStock().monthly(code,start,end)


if __name__ == "__main__":
    TradeStockClient().get_all_stock()
