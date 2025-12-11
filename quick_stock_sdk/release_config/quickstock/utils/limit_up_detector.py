"""
涨停检测工具

提供股票涨停检测和价格计算功能
"""

import math
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from ..core.errors import ValidationError
from ..models import StockDailyData, LIMIT_UP_THRESHOLDS


class LimitUpDetectionError(ValidationError):
    """涨停检测异常"""
    
    def __init__(self, message: str, stock_code: str = None, detection_details: Dict[str, Any] = None):
        """
        初始化涨停检测异常
        
        Args:
            message: 错误消息
            stock_code: 导致错误的股票代码
            detection_details: 检测详细信息
        """
        super().__init__(message)
        self.stock_code = stock_code
        self.detection_details = detection_details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'stock_code': self.stock_code,
            'detection_details': self.detection_details
        }


class InsufficientPriceDataError(LimitUpDetectionError):
    """价格数据不足异常"""
    
    def __init__(self, stock_code: str, missing_fields: List[str]):
        """
        初始化价格数据不足异常
        
        Args:
            stock_code: 股票代码
            missing_fields: 缺失的字段列表
        """
        message = f"股票 {stock_code} 缺少必要的价格数据: {', '.join(missing_fields)}"
        super().__init__(message, stock_code, {
            'missing_fields': missing_fields,
            'required_fields': ['open', 'close', 'high', 'pre_close']
        })


class InvalidPriceDataError(LimitUpDetectionError):
    """无效价格数据异常"""
    
    def __init__(self, stock_code: str, validation_errors: List[str]):
        """
        初始化无效价格数据异常
        
        Args:
            stock_code: 股票代码
            validation_errors: 验证错误列表
        """
        message = f"股票 {stock_code} 价格数据无效: {'; '.join(validation_errors)}"
        super().__init__(message, stock_code, {
            'validation_errors': validation_errors
        })


@dataclass
class LimitUpDetectionResult:
    """涨停检测结果"""
    ts_code: str                    # 股票代码
    is_limit_up: bool              # 是否涨停
    confidence: float              # 检测置信度 (0.0-1.0)
    limit_up_price: float          # 理论涨停价
    actual_close_price: float      # 实际收盘价
    price_difference: float        # 价格差异
    threshold_used: float          # 使用的涨停阈值
    stock_type: str               # 股票类型
    detection_details: Dict[str, Any]  # 检测详细信息
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'ts_code': self.ts_code,
            'is_limit_up': self.is_limit_up,
            'confidence': self.confidence,
            'limit_up_price': self.limit_up_price,
            'actual_close_price': self.actual_close_price,
            'price_difference': self.price_difference,
            'threshold_used': self.threshold_used,
            'stock_type': self.stock_type,
            'detection_details': self.detection_details
        }


class LimitUpDetector:
    """涨停检测器
    
    提供股票涨停检测和价格计算功能
    """
    
    # 价格比较容差（用于处理浮点精度问题）
    PRICE_TOLERANCE = 0.005  # 0.5分的容差
    
    # 股票类型映射
    STOCK_TYPE_MAPPING = {
        'shanghai': 'normal',
        'shenzhen': 'normal', 
        'star': 'star',
        'beijing': 'beijing'
    }
    
    def __init__(self, price_tolerance: float = None, logger: Optional[logging.Logger] = None):
        """
        初始化涨停检测器
        
        Args:
            price_tolerance: 价格比较容差
            logger: 日志记录器
        """
        self.price_tolerance = price_tolerance or self.PRICE_TOLERANCE
        self.logger = logger or logging.getLogger(__name__)
    
    def is_limit_up(self, 
                   open_price: float, 
                   close_price: float, 
                   high_price: float, 
                   prev_close: float = None,
                   stock_type: str = 'normal',
                   ts_code: str = None) -> bool:
        """
        检测是否涨停
        
        Args:
            open_price: 开盘价
            close_price: 收盘价
            high_price: 最高价
            prev_close: 前收盘价（用于计算涨停价）
            stock_type: 股票类型 ('normal', 'st', 'star', 'beijing', 'new_stock')
            ts_code: 股票代码（用于日志）
            
        Returns:
            是否涨停
            
        Raises:
            InvalidPriceDataError: 价格数据无效
        """
        result = self.detect_limit_up_with_details(
            open_price, close_price, high_price, prev_close, stock_type, ts_code
        )
        return result.is_limit_up
    
    def detect_limit_up_with_details(self,
                                   open_price: float,
                                   close_price: float, 
                                   high_price: float,
                                   prev_close: float = None,
                                   stock_type: str = 'normal',
                                   ts_code: str = None) -> LimitUpDetectionResult:
        """
        检测涨停并返回详细信息
        
        Args:
            open_price: 开盘价
            close_price: 收盘价
            high_price: 最高价
            prev_close: 前收盘价
            stock_type: 股票类型
            ts_code: 股票代码
            
        Returns:
            涨停检测结果
        """
        ts_code = ts_code or "UNKNOWN"
        
        # 验证价格数据
        self._validate_price_data(open_price, close_price, high_price, prev_close, ts_code)
        
        # 使用前收盘价或开盘价计算涨停价
        base_price = prev_close if prev_close is not None else open_price
        
        # 计算理论涨停价
        limit_up_price = self.calculate_limit_up_price(base_price, stock_type)
        
        # 检测是否涨停
        price_diff = abs(close_price - limit_up_price)
        is_within_tolerance = price_diff <= self.price_tolerance
        
        # 额外检查：收盘价是否等于最高价（涨停的典型特征）
        close_equals_high = abs(close_price - high_price) <= self.price_tolerance
        
        # 综合判断
        is_limit_up = is_within_tolerance and close_equals_high
        
        # 计算置信度
        confidence = self._calculate_detection_confidence(
            close_price, limit_up_price, high_price, price_diff, is_within_tolerance, close_equals_high
        )
        
        # 获取使用的阈值
        threshold = self.get_limit_up_threshold(stock_type)
        
        # 构建检测详细信息
        detection_details = {
            'base_price': base_price,
            'price_difference': price_diff,
            'tolerance_used': self.price_tolerance,
            'is_within_tolerance': is_within_tolerance,
            'close_equals_high': close_equals_high,
            'pct_change': ((close_price - base_price) / base_price) * 100 if base_price > 0 else 0,
            'expected_pct_change': threshold * 100,
            'detection_method': 'price_and_high_match'
        }
        
        self.logger.debug(f"Limit-up detection for {ts_code}: {is_limit_up} (confidence: {confidence:.2f})")
        
        return LimitUpDetectionResult(
            ts_code=ts_code,
            is_limit_up=is_limit_up,
            confidence=confidence,
            limit_up_price=limit_up_price,
            actual_close_price=close_price,
            price_difference=price_diff,
            threshold_used=threshold,
            stock_type=stock_type,
            detection_details=detection_details
        )
    
    def calculate_limit_up_price(self, prev_close: float, stock_type: str = 'normal') -> float:
        """
        计算涨停价格
        
        Args:
            prev_close: 前收盘价
            stock_type: 股票类型
            
        Returns:
            涨停价格
            
        Raises:
            ValueError: 参数无效
        """
        if prev_close <= 0:
            raise ValueError(f"Previous close price must be positive: {prev_close}")
        
        threshold = self.get_limit_up_threshold(stock_type)
        limit_up_price = prev_close * (1 + threshold)
        
        # 根据股票价格进行价格精度处理
        return self._round_price(limit_up_price)
    
    def get_limit_up_threshold(self, stock_type: str) -> float:
        """
        获取涨停阈值
        
        Args:
            stock_type: 股票类型
            
        Returns:
            涨停阈值
            
        Raises:
            ValueError: 未知股票类型
        """
        if stock_type not in LIMIT_UP_THRESHOLDS:
            raise ValueError(f"Unknown stock type: {stock_type}. Valid types: {list(LIMIT_UP_THRESHOLDS.keys())}")
        
        return LIMIT_UP_THRESHOLDS[stock_type]
    
    def batch_detect_limit_up(self, stock_data_list: List[StockDailyData]) -> List[LimitUpDetectionResult]:
        """
        批量检测涨停
        
        Args:
            stock_data_list: 股票数据列表
            
        Returns:
            涨停检测结果列表
        """
        results = []
        
        for stock_data in stock_data_list:
            try:
                # 根据股票代码推断股票类型
                stock_type = self._infer_stock_type_from_code(stock_data.ts_code, stock_data.name)
                
                result = self.detect_limit_up_with_details(
                    open_price=stock_data.open,
                    close_price=stock_data.close,
                    high_price=stock_data.high,
                    prev_close=stock_data.pre_close,
                    stock_type=stock_type,
                    ts_code=stock_data.ts_code
                )
                
                results.append(result)
                
            except Exception as e:
                # 创建失败结果
                error_result = LimitUpDetectionResult(
                    ts_code=stock_data.ts_code,
                    is_limit_up=False,
                    confidence=0.0,
                    limit_up_price=0.0,
                    actual_close_price=stock_data.close,
                    price_difference=0.0,
                    threshold_used=0.0,
                    stock_type='unknown',
                    detection_details={
                        'error': str(e),
                        'error_type': type(e).__name__
                    }
                )
                
                results.append(error_result)
                self.logger.error(f"Failed to detect limit-up for {stock_data.ts_code}: {e}")
        
        return results
    
    def validate_price_data_completeness(self, stock_data: StockDailyData) -> Dict[str, Any]:
        """
        验证价格数据完整性
        
        Args:
            stock_data: 股票数据
            
        Returns:
            验证结果
        """
        validation_result = {
            'is_complete': True,
            'missing_fields': [],
            'invalid_fields': [],
            'warnings': [],
            'ts_code': stock_data.ts_code
        }
        
        # 检查必需字段
        required_fields = ['open', 'close', 'high', 'low', 'pre_close']
        for field in required_fields:
            value = getattr(stock_data, field, None)
            if value is None:
                validation_result['missing_fields'].append(field)
                validation_result['is_complete'] = False
            elif not isinstance(value, (int, float)) or value <= 0:
                validation_result['invalid_fields'].append(f"{field}: {value}")
                validation_result['is_complete'] = False
        
        # 检查价格逻辑关系
        if validation_result['is_complete']:
            try:
                self._validate_price_data(
                    stock_data.open, stock_data.close, stock_data.high, stock_data.pre_close, stock_data.ts_code
                )
            except InvalidPriceDataError as e:
                validation_result['invalid_fields'].extend(e.detection_details.get('validation_errors', []))
                validation_result['is_complete'] = False
        
        # 检查可能的异常情况
        if validation_result['is_complete']:
            # 检查是否有异常的价格变动
            if stock_data.pre_close > 0:
                pct_change = abs((stock_data.close - stock_data.pre_close) / stock_data.pre_close)
                if pct_change > 0.5:  # 超过50%的变动
                    validation_result['warnings'].append(f"Unusual price change: {pct_change:.1%}")
            
            # 检查是否有异常的价格关系
            if stock_data.high == stock_data.low:
                validation_result['warnings'].append("High equals low (possible data issue)")
        
        return validation_result
    
    def _validate_price_data(self, open_price: float, close_price: float, 
                           high_price: float, prev_close: float = None, ts_code: str = None) -> None:
        """
        验证价格数据有效性
        
        Args:
            open_price: 开盘价
            close_price: 收盘价
            high_price: 最高价
            prev_close: 前收盘价
            ts_code: 股票代码
            
        Raises:
            InvalidPriceDataError: 价格数据无效
        """
        ts_code = ts_code or "UNKNOWN"
        validation_errors = []
        
        # 检查价格是否为正数
        prices = {'open': open_price, 'close': close_price, 'high': high_price}
        if prev_close is not None:
            prices['prev_close'] = prev_close
        
        for name, price in prices.items():
            if not isinstance(price, (int, float)) or price <= 0:
                validation_errors.append(f"{name} price must be positive: {price}")
        
        if validation_errors:
            raise InvalidPriceDataError(ts_code, validation_errors)
        
        # 检查价格逻辑关系
        if close_price > high_price + self.price_tolerance:
            validation_errors.append(f"Close price ({close_price}) cannot be higher than high price ({high_price})")
        
        if open_price > high_price + self.price_tolerance:
            validation_errors.append(f"Open price ({open_price}) cannot be higher than high price ({high_price})")
        
        if validation_errors:
            raise InvalidPriceDataError(ts_code, validation_errors)
    
    def _calculate_detection_confidence(self, close_price: float, limit_up_price: float, 
                                      high_price: float, price_diff: float,
                                      is_within_tolerance: bool, close_equals_high: bool) -> float:
        """
        计算检测置信度
        
        Args:
            close_price: 收盘价
            limit_up_price: 理论涨停价
            high_price: 最高价
            price_diff: 价格差异
            is_within_tolerance: 是否在容差范围内
            close_equals_high: 收盘价是否等于最高价
            
        Returns:
            置信度 (0.0-1.0)
        """
        if not is_within_tolerance:
            return 0.0
        
        # 基础置信度
        confidence = 0.5
        
        # 如果收盘价等于最高价，增加置信度
        if close_equals_high:
            confidence += 0.4
        
        # 根据价格差异调整置信度
        if price_diff <= self.price_tolerance * 0.1:  # 非常接近
            confidence += 0.1
        elif price_diff <= self.price_tolerance * 0.5:  # 比较接近
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _infer_stock_type_from_code(self, ts_code: str, stock_name: str = None) -> str:
        """
        根据股票代码和名称推断股票类型
        
        Args:
            ts_code: 股票代码
            stock_name: 股票名称
            
        Returns:
            股票类型
        """
        # 首先检查是否为ST股票
        if stock_name and self._is_st_stock_by_name(stock_name):
            return 'st'
        
        # 根据股票代码推断市场类型
        try:
            from .stock_classifier import StockCodeClassifier
            classifier = StockCodeClassifier()
            market = classifier.classify_market(ts_code)
            return self.STOCK_TYPE_MAPPING.get(market, 'normal')
        except Exception:
            # 如果分类失败，返回默认类型
            return 'normal'
    
    def _is_st_stock_by_name(self, stock_name: str) -> bool:
        """
        根据股票名称判断是否为ST股票
        
        Args:
            stock_name: 股票名称
            
        Returns:
            是否为ST股票
        """
        if not stock_name:
            return False
        
        import re
        st_patterns = [r'\*ST', r'ST', r'退市', r'暂停']
        
        for pattern in st_patterns:
            if re.search(pattern, stock_name, re.IGNORECASE):
                return True
        
        return False
    
    def _round_price(self, price: float) -> float:
        """
        根据价格区间进行价格精度处理
        
        Args:
            price: 原始价格
            
        Returns:
            处理后的价格
        """
        # 中国股市价格精度规则：
        # 价格 >= 1000: 精确到分 (0.01)
        # 价格 < 1000: 精确到分 (0.01)
        # 这里统一精确到分
        return round(price, 2)


# 便利函数
def detect_limit_up(open_price: float, close_price: float, high_price: float, 
                   prev_close: float = None, stock_type: str = 'normal') -> bool:
    """
    便利函数：检测是否涨停
    
    Args:
        open_price: 开盘价
        close_price: 收盘价
        high_price: 最高价
        prev_close: 前收盘价
        stock_type: 股票类型
        
    Returns:
        是否涨停
    """
    detector = LimitUpDetector()
    return detector.is_limit_up(open_price, close_price, high_price, prev_close, stock_type)


def calculate_limit_up_price(prev_close: float, stock_type: str = 'normal') -> float:
    """
    便利函数：计算涨停价格
    
    Args:
        prev_close: 前收盘价
        stock_type: 股票类型
        
    Returns:
        涨停价格
    """
    detector = LimitUpDetector()
    return detector.calculate_limit_up_price(prev_close, stock_type)


def get_limit_up_threshold(stock_type: str) -> float:
    """
    便利函数：获取涨停阈值
    
    Args:
        stock_type: 股票类型
        
    Returns:
        涨停阈值
    """
    detector = LimitUpDetector()
    return detector.get_limit_up_threshold(stock_type)