import datetime
import time

from quick_stock.d import getDClient
from quick_stock.remote.index import TradeIndex
import pandas as pd

class TradeIndexClient:
    dClient = None

    def __init__(self):
        self.dClient = getDClient()

    def get_all_index(self):
        """
        :return: list - string
        """
        df = self.dClient.select("select * from mc_index_basic where exp_date is not NULL")
        if df.empty or datetime.date.today().day == 1 :
            df = TradeIndex().get_all()
            time.sleep(30)

            df2 = TradeIndex().get_all("MSCI")
            df = pd.concat([df, df2], axis=0)
            time.sleep(30)

            df2 = TradeIndex().get_all("CSI")
            df = pd.concat([df, df2], axis=0)
            time.sleep(30)

            df2 = TradeIndex().get_all("SZSE")
            df = pd.concat([df, df2], axis=0)
            time.sleep(30)

            df2 = TradeIndex().get_all("CICC")
            df = pd.concat([df, df2], axis=0)
            time.sleep(30)

            df2 = TradeIndex().get_all("SW")
            df = pd.concat([df, df2], axis=0)
            time.sleep(30)

            df2 = TradeIndex().get_all("OTH")
            df = pd.concat([df, df2], axis=0)
            self.dClient.save(df, 'mc_index_basic')

        return df

    def minute(self, code):
        return TradeIndex().minute(code)

    def minute30(self, code, start=None, end=None):
        return TradeIndex().minute30(code,start,end)

    def minute60(self, code, start=None, end=None):
        return TradeIndex().minute60(code,start,end)

    def daily(self, code, start=None, end=None):
        return TradeIndex().daily(code,start,end)

    def weekly(self, code, start=None, end=None):
        return TradeIndex().weekly(code,start,end)

    def monthly(self, code, start=None, end=None):
        return TradeIndex().monthly(code,start,end)

if __name__ == "__main__":
    print(TradeIndexClient().get_all_index())

