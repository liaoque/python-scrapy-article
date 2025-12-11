"""
QuickStock SDK - 现代化的金融数据获取SDK

提供统一、高效、可扩展的金融数据访问接口，支持多数据源集成，
具备完善的错误处理能力。

主要功能:
- 股票、指数、基金等金融数据获取
- 多数据源支持 (东方财富, 同花顺, Baostock等)
- 统一的数据格式
- 异步数据获取支持
- 智能股票代码格式转换

使用示例:
    >>> from quickstock import QuickStockClient
    >>> client = QuickStockClient()
    >>> data = client.stock_basic()
"""

from .client import QuickStockClient
from .config import Config
from .core.errors import (
    QuickStockError,
    DataSourceError,
    ValidationError,
    RateLimitError,
    NetworkError,
    DatabaseError
)

__version__ = "1.0.3"
__author__ = "QuickStock Team"

__all__ = [
    "QuickStockClient",
    "Config",
    "QuickStockError",
    "DataSourceError",
    "ValidationError",
    "RateLimitError",
    "NetworkError",
    "DatabaseError",
]