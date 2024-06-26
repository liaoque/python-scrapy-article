import datetime
from quick_stock import getDClient
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

    def daily(self, code):
        return TradeStock().daily(code)

    def weekly(self, code):
        return TradeStock().weekly(code)

    def monthly(self, code):
        return TradeStock().monthly(code)


if __name__ == "__main__":
    TradeStockClient().get_all_stock()
