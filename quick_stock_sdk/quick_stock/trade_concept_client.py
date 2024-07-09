import datetime
import time

from quick_stock.d import getDClient
from quick_stock.remote.index import TradeIndex
from quick_stock.remote.tonghuashun import TongHuaShun
import pandas as pd


class TradeConceptClient:
    dClient = None

    def __init__(self):
        self.dClient = getDClient()

    def get_all_concept(self, platform="THS"):
        """
        :return: list - string
        """
        if platform == "THS":
            df = self.dClient.select("select * from mc_concept_ths_basic")
            if df.empty or datetime.date.today().day == 1:
                data = TongHuaShun().get_all()
                df = pd.DataFrame(data)
                self.dClient.save(df, 'mc_concept_ths_basic')
            return df
        return pd.DataFrame([])

    def get_all_concept_stock(self, code, platform="THS"):
        """
        :return: list - string
        """

        concepts = self.get_all_concept()
        concepts = concepts[concepts['code'] == code]
        if len(concepts) == 0:
            return pd.DataFrame([])

        concept = concepts['cid'].iloc[0]

        if platform == "THS":
            df = self.dClient.select("select * from mc_concept_ths_stock_basic")
            if df.empty or datetime.date.today().day == 1 or df[df["cid"] == concept].empty:
                data = TongHuaShun().get_all_concept_stock(concept)
                concept2 = pd.DataFrame(data)
                df = pd.concat([df[df["cid"] != concept], concept2], axis=0)
                self.dClient.save(df, 'mc_concept_ths_stock_basic')
            return df
        return pd.DataFrame([])

    def minute(self, code):
        return TongHuaShun().minute(code)

    def minute30(self, code, start=None, end=None):
        return TongHuaShun().minute30(code, start, end)

    def minute60(self, code, start=None, end=None):
        return TongHuaShun().minute60(code, start, end)

    def daily(self, code, start=None, end=None):
        return TongHuaShun().daily(code, start, end)

    def weekly(self, code, start=None, end=None):
        return TongHuaShun().weekly(code, start, end)

    def monthly(self, code, start=None, end=None):
        return TongHuaShun().monthly(code, start, end)


if __name__ == "__main__":
    print(TradeConceptClient().get_all_concept_stock("885333"))
