"""
QuickStock SDK核心模块

包含数据管理、格式化、错误处理等核心功能
"""

from .data_manager import DataManager
from .connection_pool import ConnectionPool
from .formatter import DataFormatter
from .errors import (
    QuickStockError,
    DataSourceError,
    ValidationError,
    RateLimitError,
    NetworkError,
    ErrorHandler
)

__all__ = [
    "DataManager",
    "DataFormatter",
    "QuickStockError",
    "DataSourceError",
    "ValidationError",
    "RateLimitError",
    "NetworkError",
    "ErrorHandler",
    "ConnectionPool",
]