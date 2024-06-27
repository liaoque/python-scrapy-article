import datetime
import pandas as pd
import numpy as np
from quick_stock.d import getDClient
from quick_stock.remote import getTradeDays


class TradeDateClient:
    dClient = None
    tradeDays = None

    def __init__(self):
        self.dClient = getDClient()
        self.tradeDays = getTradeDays()

    def get_all_days(self):
        """
        :return: list - string
        """
        df = self.dClient.select("select date_at from mc_dates")
        if df.empty or df.iloc[-1]['date_at'] != datetime.date.today():
            data = self.tradeDays.get_all()
            df = pd.DataFrame({"date_at": data})
            self.dClient.save(df, 'mc_dates')
        else:
            data = df['date_at']
        return data

    def get_trade_days(self, start_date=None, end_date=None, count=None):
        days = np.array(self.get_all_days())
        if start_date:
            days = days[days > start_date]
        if end_date:
            days = days[days < end_date]
        if count:
            days = days[:count]

        return days



