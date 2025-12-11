"""
数据模型包

包含各种数据模型和请求对象
"""

# Import from main models.py to avoid circular imports
import sys
import os

# Add parent directory to path to import from models.py
parent_dir = os.path.dirname(os.path.dirname(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from quickstock.models import (
        DataRequest,
        LimitUpStatsRequest,
        StockDailyData,
        LimitUpStats,
        FinancialReport,
        EarningsForecast,
        FlashReport,
        FinancialReportsRequest,
        EarningsForecastRequest,
        FlashReportsRequest,
        LIMIT_UP_THRESHOLDS,
        MARKET_CLASSIFICATION_RULES,
        ST_PATTERNS,
        OHLCV_COLUMNS,
        STOCK_BASIC_COLUMNS,
        INDEX_BASIC_COLUMNS,
        FUND_BASIC_COLUMNS,
        TRADE_CAL_COLUMNS
    )
except ImportError:
    # Fallback for direct imports
    import importlib.util
    models_path = os.path.join(os.path.dirname(__file__), '..', 'models.py')
    spec = importlib.util.spec_from_file_location("models", models_path)
    models_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models_module)
    
    DataRequest = models_module.DataRequest
    LimitUpStatsRequest = models_module.LimitUpStatsRequest
    StockDailyData = models_module.StockDailyData
    LimitUpStats = models_module.LimitUpStats
    FinancialReport = models_module.FinancialReport
    EarningsForecast = models_module.EarningsForecast
    FlashReport = models_module.FlashReport
    FinancialReportsRequest = models_module.FinancialReportsRequest
    EarningsForecastRequest = models_module.EarningsForecastRequest
    FlashReportsRequest = models_module.FlashReportsRequest
    LIMIT_UP_THRESHOLDS = models_module.LIMIT_UP_THRESHOLDS
    MARKET_CLASSIFICATION_RULES = models_module.MARKET_CLASSIFICATION_RULES
    ST_PATTERNS = models_module.ST_PATTERNS
    OHLCV_COLUMNS = models_module.OHLCV_COLUMNS
    STOCK_BASIC_COLUMNS = models_module.STOCK_BASIC_COLUMNS
    INDEX_BASIC_COLUMNS = models_module.INDEX_BASIC_COLUMNS
    FUND_BASIC_COLUMNS = models_module.FUND_BASIC_COLUMNS
    TRADE_CAL_COLUMNS = models_module.TRADE_CAL_COLUMNS

# Import price distribution models
try:
    from .price_distribution_models import (
        DistributionRange,
        PriceDistributionRequest,
        PriceDistributionStats,
        DEFAULT_DISTRIBUTION_RANGES,
        MARKET_TYPES
    )
except ImportError:
    # Define minimal versions if import fails
    DistributionRange = None
    PriceDistributionRequest = None
    PriceDistributionStats = None
    DEFAULT_DISTRIBUTION_RANGES = {}
    MARKET_TYPES = {}

__all__ = [
    'DataRequest',
    'LimitUpStatsRequest',
    'StockDailyData',
    'LimitUpStats',
    'FinancialReport',
    'EarningsForecast',
    'FlashReport',
    'FinancialReportsRequest',
    'EarningsForecastRequest',
    'FlashReportsRequest',
    'LIMIT_UP_THRESHOLDS',
    'MARKET_CLASSIFICATION_RULES',
    'ST_PATTERNS',
    'OHLCV_COLUMNS',
    'STOCK_BASIC_COLUMNS',
    'INDEX_BASIC_COLUMNS',
    'FUND_BASIC_COLUMNS',
    'TRADE_CAL_COLUMNS',
    'DistributionRange',
    'PriceDistributionRequest',
    'PriceDistributionStats',
    'DEFAULT_DISTRIBUTION_RANGES',
    'MARKET_TYPES'
]