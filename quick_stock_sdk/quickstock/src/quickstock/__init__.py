"""
QuickStock SDK

一个易于使用的金融数据SDK，用于获取股票、指数和基金数据
默认使用Baostock作为数据源
"""

from .client import QuickStockClient
from .errors import (QuickStockError, DataSourceError, ValidationError, 
                     AuthenticationError, NetworkError, DataNotFoundError)

__version__ = "1.0.8"
__all__ = [
    "QuickStockClient",
    "QuickStockError",
    "DataSourceError",
    "ValidationError",
    "AuthenticationError",
    "NetworkError",
    "DataNotFoundError"
]
