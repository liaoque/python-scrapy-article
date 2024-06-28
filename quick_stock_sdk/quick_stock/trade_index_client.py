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
            self.dClient.save(df, 'mc_index_basic')
        return df

    def daily(self, code, start=None, end=None):
        return TradeIndex().daily(code,start,end)

    def weekly(self, code, start=None, end=None):
        return TradeIndex().weekly(code,start,end)

    def monthly(self, code, start=None, end=None):
        return TradeIndex().monthly(code,start,end)

if __name__ == "__main__":
    print(TradeIndexClient().daily("0.000001"))

