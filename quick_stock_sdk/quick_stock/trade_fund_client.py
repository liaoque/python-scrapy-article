import datetime
from quick_stock.d import getDClient
from quick_stock.remote.fund import TradeFund


class TradeFundClient:
    dClient = None

    def __init__(self):
        self.dClient = getDClient()

    def get_all_fund(self):
        """
        :return: list - string
        """
        df = self.dClient.select("select * from mc_fund_basic")
        if df.empty or datetime.date.today().day == 1:
            df = TradeFund().get_all()
            self.dClient.save(df, 'mc_fund_basic')
        return df

    def daily(self, code):
        return TradeFund().daily(code)

    def weekly(self, code):
        return TradeFund().weekly(code)

    def monthly(self, code):
        return TradeFund().monthly(code)


if __name__ == "__main__":
    TradeFundClient().get_all_fund()
