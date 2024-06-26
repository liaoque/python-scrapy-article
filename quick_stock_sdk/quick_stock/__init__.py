from quick_stock.d import d as QuickStockClient
import quick_stock.remote.date as TradeDays
from .trade_date_client import TradeDateClient
from .trade_index_client import TradeIndexClient
from .trade_stock_client import TradeStockClient

__all__ = ["TradeDateClient", "TradeIndexClient","TradeStockClient"]

dClient = QuickStockClient.DClient()
tradeDays = TradeDays.TradeDays()


def getDClient():
    return dClient


def getTradeDays():
    return tradeDays
