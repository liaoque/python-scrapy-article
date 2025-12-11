"""
价格计算和验证工具

提供股票价格计算、比较和验证的实用函数
"""

import math
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from ..core.errors import ValidationError
from ..models import LIMIT_UP_THRESHOLDS


class PriceValidationError(ValidationError):
    """价格验证异常"""
    
    def __init__(self, message: str, price_data: Dict[str, Any] = None):
        """
        初始化价格验证异常
        
        Args:
            message: 错误消息
            price_data: 相关价格数据
        """
        super().__init__(message)
        self.price_data = price_data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'price_data': self.price_data
        }


class PriceComparisonError(PriceValidationError):
    """价格比较异常"""
    pass


class PriceCalculationError(PriceValidationError):
    """价格计算异常"""
    pass


@dataclass
class PriceValidationResult:
    """价格验证结果"""
    is_valid: bool                      # 是否有效
    errors: List[str]                   # 错误列表
    warnings: List[str]                 # 警告列表
    price_analysis: Dict[str, Any]      # 价格分析结果
    suggestions: List[str]              # 改进建议
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'price_analysis': self.price_analysis,
            'suggestions': self.suggestions
        }


@dataclass
class PriceComparisonResult:
    """价格比较结果"""
    are_equal: bool                     # 是否相等
    difference: float                   # 价格差异
    relative_difference: float          # 相对差异（百分比）
    tolerance_used: float               # 使用的容差
    comparison_details: Dict[str, Any]  # 比较详细信息
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'are_equal': self.are_equal,
            'difference': self.difference,
            'relative_difference': self.relative_difference,
            'tolerance_used': self.tolerance_used,
            'comparison_details': self.comparison_details
        }


class PriceUtils:
    """价格工具类
    
    提供价格计算、比较和验证的实用功能
    """
    
    # 默认价格容差
    DEFAULT_PRICE_TOLERANCE = 0.005  # 0.5分
    
    # 价格精度设置
    PRICE_PRECISION = 2  # 保留2位小数
    
    # 异常价格变动阈值
    UNUSUAL_CHANGE_THRESHOLD = 0.5  # 50%
    
    def __init__(self, price_tolerance: float = None, logger: Optional[logging.Logger] = None):
        """
        初始化价格工具
        
        Args:
            price_tolerance: 价格比较容差
            logger: 日志记录器
        """
        self.price_tolerance = price_tolerance or self.DEFAULT_PRICE_TOLERANCE
        self.logger = logger or logging.getLogger(__name__)
    
    def calculate_limit_price(self, base_price: float, change_rate: float, 
                            price_type: str = 'limit_up') -> float:
        """
        计算涨停或跌停价格
        
        Args:
            base_price: 基准价格（通常是前收盘价）
            change_rate: 变动比率（如0.10表示10%）
            price_type: 价格类型 ('limit_up' 或 'limit_down')
            
        Returns:
            计算后的价格
            
        Raises:
            PriceCalculationError: 计算参数无效
        """
        if base_price <= 0:
            raise PriceCalculationError(
                f"Base price must be positive: {base_price}",
                {'base_price': base_price, 'change_rate': change_rate}
            )
        
        if not isinstance(change_rate, (int, float)) or change_rate < 0:
            raise PriceCalculationError(
                f"Change rate must be non-negative number: {change_rate}",
                {'base_price': base_price, 'change_rate': change_rate}
            )
        
        if price_type == 'limit_up':
            calculated_price = base_price * (1 + change_rate)
        elif price_type == 'limit_down':
            calculated_price = base_price * (1 - change_rate)
        else:
            raise PriceCalculationError(
                f"Invalid price type: {price_type}. Must be 'limit_up' or 'limit_down'",
                {'base_price': base_price, 'change_rate': change_rate, 'price_type': price_type}
            )
        
        return self.round_price(calculated_price)
    
    def calculate_limit_up_price(self, base_price: float, stock_type: str = 'normal') -> float:
        """
        计算涨停价格
        
        Args:
            base_price: 基准价格
            stock_type: 股票类型
            
        Returns:
            涨停价格
        """
        if stock_type not in LIMIT_UP_THRESHOLDS:
            raise PriceCalculationError(
                f"Unknown stock type: {stock_type}",
                {'base_price': base_price, 'stock_type': stock_type}
            )
        
        change_rate = LIMIT_UP_THRESHOLDS[stock_type]
        return self.calculate_limit_price(base_price, change_rate, 'limit_up')
    
    def calculate_limit_down_price(self, base_price: float, stock_type: str = 'normal') -> float:
        """
        计算跌停价格
        
        Args:
            base_price: 基准价格
            stock_type: 股票类型
            
        Returns:
            跌停价格
        """
        if stock_type not in LIMIT_UP_THRESHOLDS:
            raise PriceCalculationError(
                f"Unknown stock type: {stock_type}",
                {'base_price': base_price, 'stock_type': stock_type}
            )
        
        # 跌停使用相同的阈值
        change_rate = LIMIT_UP_THRESHOLDS[stock_type]
        return self.calculate_limit_price(base_price, change_rate, 'limit_down')
    
    def calculate_price_change(self, current_price: float, previous_price: float) -> Dict[str, float]:
        """
        计算价格变动
        
        Args:
            current_price: 当前价格
            previous_price: 前一价格
            
        Returns:
            包含绝对变动和相对变动的字典
        """
        if previous_price <= 0:
            raise PriceCalculationError(
                f"Previous price must be positive: {previous_price}",
                {'current_price': current_price, 'previous_price': previous_price}
            )
        
        absolute_change = current_price - previous_price
        relative_change = (absolute_change / previous_price) * 100
        
        return {
            'absolute_change': round(absolute_change, self.PRICE_PRECISION),
            'relative_change': round(relative_change, 2),  # 百分比保留2位小数
            'current_price': current_price,
            'previous_price': previous_price
        }
    
    def compare_prices(self, price1: float, price2: float, 
                      tolerance: float = None) -> PriceComparisonResult:
        """
        比较两个价格是否相等（考虑浮点精度容差）
        
        Args:
            price1: 价格1
            price2: 价格2
            tolerance: 容差（可选，使用默认容差）
            
        Returns:
            价格比较结果
        """
        tolerance = tolerance if tolerance is not None else self.price_tolerance
        
        if not all(isinstance(p, (int, float)) for p in [price1, price2]):
            raise PriceComparisonError(
                "Prices must be numeric",
                {'price1': price1, 'price2': price2}
            )
        
        difference = abs(price1 - price2)
        are_equal = difference <= tolerance
        
        # 计算相对差异
        avg_price = (price1 + price2) / 2
        relative_difference = (difference / avg_price * 100) if avg_price > 0 else 0
        
        comparison_details = {
            'price1': price1,
            'price2': price2,
            'absolute_difference': difference,
            'average_price': avg_price,
            'tolerance_ratio': difference / tolerance if tolerance > 0 else float('inf')
        }
        
        return PriceComparisonResult(
            are_equal=are_equal,
            difference=difference,
            relative_difference=relative_difference,
            tolerance_used=tolerance,
            comparison_details=comparison_details
        )
    
    def is_price_equal(self, price1: float, price2: float, tolerance: float = None) -> bool:
        """
        判断两个价格是否相等（便利函数）
        
        Args:
            price1: 价格1
            price2: 价格2
            tolerance: 容差
            
        Returns:
            是否相等
        """
        result = self.compare_prices(price1, price2, tolerance)
        return result.are_equal
    
    def round_price(self, price: float, precision: int = None) -> float:
        """
        按照股票价格规则进行精度处理
        
        Args:
            price: 原始价格
            precision: 精度（小数位数）
            
        Returns:
            处理后的价格
        """
        precision = precision or self.PRICE_PRECISION
        
        # 使用Decimal进行精确的四舍五入
        decimal_price = Decimal(str(price))
        rounded_price = decimal_price.quantize(
            Decimal('0.' + '0' * precision), 
            rounding=ROUND_HALF_UP
        )
        
        return float(rounded_price)
    
    def validate_price_data(self, price_data: Dict[str, float], 
                          required_fields: List[str] = None) -> PriceValidationResult:
        """
        验证价格数据的完整性和有效性
        
        Args:
            price_data: 价格数据字典
            required_fields: 必需字段列表
            
        Returns:
            价格验证结果
        """
        required_fields = required_fields or ['open', 'high', 'low', 'close']
        
        errors = []
        warnings = []
        suggestions = []
        
        # 检查必需字段
        missing_fields = []
        for field in required_fields:
            if field not in price_data or price_data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            errors.append(f"Missing required fields: {', '.join(missing_fields)}")
        
        # 检查价格有效性
        invalid_prices = []
        for field, value in price_data.items():
            if value is not None:
                if not isinstance(value, (int, float)):
                    invalid_prices.append(f"{field}: not numeric ({type(value).__name__})")
                elif value <= 0:
                    invalid_prices.append(f"{field}: must be positive ({value})")
                elif math.isnan(value) or math.isinf(value):
                    invalid_prices.append(f"{field}: invalid value ({value})")
        
        if invalid_prices:
            errors.extend(invalid_prices)
        
        # 如果基本验证通过，进行逻辑验证
        if not errors and all(field in price_data for field in ['open', 'high', 'low', 'close']):
            logic_errors = self._validate_price_logic(price_data)
            errors.extend(logic_errors)
        
        # 检查异常情况
        if not errors:
            price_warnings = self._check_price_warnings(price_data)
            warnings.extend(price_warnings)
        
        # 生成建议
        if errors:
            suggestions.append("请检查并修正价格数据中的错误")
        if warnings:
            suggestions.append("请注意价格数据中的异常情况")
        if not errors and not warnings:
            suggestions.append("价格数据验证通过")
        
        # 价格分析
        price_analysis = self._analyze_price_data(price_data)
        
        return PriceValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            price_analysis=price_analysis,
            suggestions=suggestions
        )
    
    def validate_ohlc_relationship(self, open_price: float, high_price: float, 
                                 low_price: float, close_price: float) -> Dict[str, Any]:
        """
        验证OHLC价格关系的有效性
        
        Args:
            open_price: 开盘价
            high_price: 最高价
            low_price: 最低价
            close_price: 收盘价
            
        Returns:
            验证结果
        """
        validation_result = {
            'is_valid': True,
            'violations': [],
            'relationships': {}
        }
        
        prices = {
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price
        }
        
        # 检查基本有效性
        for name, price in prices.items():
            if not isinstance(price, (int, float)) or price <= 0:
                validation_result['violations'].append(f"{name} price is invalid: {price}")
                validation_result['is_valid'] = False
        
        if not validation_result['is_valid']:
            return validation_result
        
        # 检查OHLC关系
        relationships = {
            'high_ge_open': high_price >= open_price,
            'high_ge_close': high_price >= close_price,
            'high_ge_low': high_price >= low_price,
            'low_le_open': low_price <= open_price,
            'low_le_close': low_price <= close_price,
            'open_between_high_low': low_price <= open_price <= high_price,
            'close_between_high_low': low_price <= close_price <= high_price
        }
        
        validation_result['relationships'] = relationships
        
        # 检查违反的关系
        violations = []
        if not relationships['high_ge_open']:
            violations.append(f"High ({high_price}) should be >= Open ({open_price})")
        if not relationships['high_ge_close']:
            violations.append(f"High ({high_price}) should be >= Close ({close_price})")
        if not relationships['high_ge_low']:
            violations.append(f"High ({high_price}) should be >= Low ({low_price})")
        if not relationships['low_le_open']:
            violations.append(f"Low ({low_price}) should be <= Open ({open_price})")
        if not relationships['low_le_close']:
            violations.append(f"Low ({low_price}) should be <= Close ({close_price})")
        
        if violations:
            validation_result['violations'].extend(violations)
            validation_result['is_valid'] = False
        
        return validation_result
    
    def calculate_price_statistics(self, prices: List[float]) -> Dict[str, float]:
        """
        计算价格统计信息
        
        Args:
            prices: 价格列表
            
        Returns:
            统计信息字典
        """
        if not prices:
            return {}
        
        valid_prices = [p for p in prices if isinstance(p, (int, float)) and p > 0]
        
        if not valid_prices:
            return {}
        
        sorted_prices = sorted(valid_prices)
        n = len(sorted_prices)
        
        statistics = {
            'count': n,
            'min': sorted_prices[0],
            'max': sorted_prices[-1],
            'mean': sum(sorted_prices) / n,
            'range': sorted_prices[-1] - sorted_prices[0]
        }
        
        # 中位数
        if n % 2 == 0:
            statistics['median'] = (sorted_prices[n//2 - 1] + sorted_prices[n//2]) / 2
        else:
            statistics['median'] = sorted_prices[n//2]
        
        # 标准差
        mean = statistics['mean']
        variance = sum((p - mean) ** 2 for p in sorted_prices) / n
        statistics['std_dev'] = math.sqrt(variance)
        
        # 变异系数
        statistics['coefficient_of_variation'] = statistics['std_dev'] / mean if mean > 0 else 0
        
        return statistics
    
    def _validate_price_logic(self, price_data: Dict[str, float]) -> List[str]:
        """验证价格逻辑关系"""
        errors = []
        
        # 获取OHLC价格
        open_price = price_data.get('open')
        high_price = price_data.get('high')
        low_price = price_data.get('low')
        close_price = price_data.get('close')
        
        if all(p is not None for p in [open_price, high_price, low_price, close_price]):
            ohlc_validation = self.validate_ohlc_relationship(open_price, high_price, low_price, close_price)
            if not ohlc_validation['is_valid']:
                errors.extend(ohlc_validation['violations'])
        
        return errors
    
    def _check_price_warnings(self, price_data: Dict[str, float]) -> List[str]:
        """检查价格异常情况"""
        warnings = []
        
        # 检查价格相等情况
        open_price = price_data.get('open')
        high_price = price_data.get('high')
        low_price = price_data.get('low')
        close_price = price_data.get('close')
        
        if all(p is not None for p in [high_price, low_price]):
            if self.is_price_equal(high_price, low_price):
                warnings.append("High price equals low price (possible data issue)")
        
        if all(p is not None for p in [open_price, close_price, high_price, low_price]):
            if all(self.is_price_equal(p, open_price) for p in [close_price, high_price, low_price]):
                warnings.append("All OHLC prices are equal (possible data issue)")
        
        # 检查异常价格变动
        prev_close = price_data.get('pre_close')
        if prev_close is not None and close_price is not None and prev_close > 0:
            change_rate = abs((close_price - prev_close) / prev_close)
            if change_rate > self.UNUSUAL_CHANGE_THRESHOLD:
                warnings.append(f"Unusual price change: {change_rate:.1%}")
        
        return warnings
    
    def _analyze_price_data(self, price_data: Dict[str, float]) -> Dict[str, Any]:
        """分析价格数据"""
        analysis = {
            'field_count': len(price_data),
            'valid_fields': [],
            'invalid_fields': [],
            'price_range': None,
            'volatility': None
        }
        
        # 分析字段有效性
        for field, value in price_data.items():
            if isinstance(value, (int, float)) and value > 0:
                analysis['valid_fields'].append(field)
            else:
                analysis['invalid_fields'].append(field)
        
        # 计算价格范围和波动性
        valid_prices = [v for k, v in price_data.items() if k in analysis['valid_fields']]
        if len(valid_prices) >= 2:
            price_stats = self.calculate_price_statistics(valid_prices)
            analysis['price_range'] = price_stats.get('range', 0)
            analysis['volatility'] = price_stats.get('coefficient_of_variation', 0)
        
        return analysis


# 便利函数
def calculate_limit_up_price(base_price: float, stock_type: str = 'normal') -> float:
    """
    便利函数：计算涨停价格
    
    Args:
        base_price: 基准价格
        stock_type: 股票类型
        
    Returns:
        涨停价格
    """
    utils = PriceUtils()
    return utils.calculate_limit_up_price(base_price, stock_type)


def calculate_limit_down_price(base_price: float, stock_type: str = 'normal') -> float:
    """
    便利函数：计算跌停价格
    
    Args:
        base_price: 基准价格
        stock_type: 股票类型
        
    Returns:
        跌停价格
    """
    utils = PriceUtils()
    return utils.calculate_limit_down_price(base_price, stock_type)


def compare_prices(price1: float, price2: float, tolerance: float = None) -> bool:
    """
    便利函数：比较两个价格是否相等
    
    Args:
        price1: 价格1
        price2: 价格2
        tolerance: 容差
        
    Returns:
        是否相等
    """
    utils = PriceUtils()
    return utils.is_price_equal(price1, price2, tolerance)


def round_price(price: float, precision: int = 2) -> float:
    """
    便利函数：价格精度处理
    
    Args:
        price: 原始价格
        precision: 精度
        
    Returns:
        处理后的价格
    """
    utils = PriceUtils()
    return utils.round_price(price, precision)


def validate_ohlc_prices(open_price: float, high_price: float, 
                        low_price: float, close_price: float) -> bool:
    """
    便利函数：验证OHLC价格关系
    
    Args:
        open_price: 开盘价
        high_price: 最高价
        low_price: 最低价
        close_price: 收盘价
        
    Returns:
        是否有效
    """
    utils = PriceUtils()
    result = utils.validate_ohlc_relationship(open_price, high_price, low_price, close_price)
    return result['is_valid']