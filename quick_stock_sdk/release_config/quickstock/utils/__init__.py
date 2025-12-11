"""
工具模块

包含各种辅助函数和工具类
"""

from .validators import (
    ValidationError,
    validate_stock_code,
    validate_date_format,
    validate_date_range,
    validate_frequency,
    validate_numeric_range,
    validate_list_length,
    validate_fields,
    validate_params,
    validate_data_request,
    StockDataValidator,
    IndexDataValidator,
    FundDataValidator,
    TradeCalValidator
)

from .stock_classifier import (
    StockCodeClassifier,
    ClassificationResult,
    StockClassificationError,
    UnknownStockCodeError,
    MissingStockNameError,
    classify_market,
    is_st_stock,
    classify_stock
)

from .limit_up_detector import (
    LimitUpDetector,
    LimitUpDetectionResult,
    LimitUpDetectionError,
    InsufficientPriceDataError,
    InvalidPriceDataError,
    detect_limit_up,
    calculate_limit_up_price,
    get_limit_up_threshold
)

from .price_utils import (
    PriceUtils,
    PriceValidationResult,
    PriceComparisonResult,
    PriceValidationError,
    PriceComparisonError,
    PriceCalculationError,
    calculate_limit_down_price,
    compare_prices,
    round_price,
    validate_ohlc_prices
)

from .distribution_calculator import (
    DistributionCalculator,
    DistributionResult,
    DistributionCalculationError,
    create_default_ranges,
    classify_stocks_by_change,
    calculate_distribution_stats
)

__all__ = [
    "ValidationError",
    "validate_stock_code",
    "validate_date_format", 
    "validate_date_range",
    "validate_frequency",
    "validate_numeric_range",
    "validate_list_length",
    "validate_fields",
    "validate_params",
    "validate_data_request",
    "StockDataValidator",
    "IndexDataValidator", 
    "FundDataValidator",
    "TradeCalValidator",
    "StockCodeClassifier",
    "ClassificationResult",
    "StockClassificationError",
    "UnknownStockCodeError",
    "MissingStockNameError",
    "classify_market",
    "is_st_stock",
    "classify_stock",
    "LimitUpDetector",
    "LimitUpDetectionResult",
    "LimitUpDetectionError",
    "InsufficientPriceDataError",
    "InvalidPriceDataError",
    "detect_limit_up",
    "calculate_limit_up_price",
    "get_limit_up_threshold",
    "PriceUtils",
    "PriceValidationResult",
    "PriceComparisonResult",
    "PriceValidationError",
    "PriceComparisonError",
    "PriceCalculationError",
    "calculate_limit_down_price",
    "compare_prices",
    "round_price",
    "validate_ohlc_prices",
    "DistributionCalculator",
    "DistributionResult",
    "DistributionCalculationError",
    "create_default_ranges",
    "classify_stocks_by_change",
    "calculate_distribution_stats"
]