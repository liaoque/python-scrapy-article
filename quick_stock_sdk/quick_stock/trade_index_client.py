import datetime
from quick_stock.d import getDClient
from quick_stock.remote.index import TradeIndex

class TradeIndexClient:
    dClient = None

    def __init__(self):
        self.dClient = getDClient()

    def get_all_index(self):
        """
        :return: list - string
        """
        df = self.dClient.select("select * from mc_index_basic")
        if df.empty or datetime.date.today().day == 1:
            df = TradeIndex().get_all()
            self.dClient.save(df, 'mc_stock_basic')
        return df

    def daily(self):
        pass

    def weekly(self):
        pass

    def monthly(self):
        pass

if __name__ == "__main__":
    TradeIndexClient().get_all_index()

