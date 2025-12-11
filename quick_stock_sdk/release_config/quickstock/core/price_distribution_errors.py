"""
涨跌分布统计专用异常定义

定义涨跌分布统计功能的异常层次结构和错误处理机制。

注意: SDK已移除缓存功能，PriceDistributionCacheError已被弃用。
"""

from typing import Dict, Any, Optional, List, Tuple
from .errors import QuickStockError, DataSourceError, ValidationError


class PriceDistributionError(QuickStockError):
    """涨跌分布统计专用异常基类"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None, 
                 suggestions: Optional[str] = None):
        """
        初始化涨跌分布统计异常
        
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详细信息
            suggestions: 用户友好的建议
        """
        super().__init__(message, error_code, details)
        self.suggestions = suggestions


class InvalidDistributionRangeError(PriceDistributionError, ValidationError):
    """无效分布区间异常"""
    
    def __init__(self, range_name: str = None, min_value: float = None, max_value: float = None, 
                 reason: str = None):
        """
        初始化无效分布区间异常
        
        Args:
            range_name: 区间名称
            min_value: 最小值
            max_value: 最大值
            reason: 无效原因
        """
        if range_name:
            if reason:
                message = f"无效的分布区间 '{range_name}': {reason}"
            else:
                message = f"无效的分布区间 '{range_name}'"
            
            if min_value is not None and max_value is not None:
                message += f" (范围: {min_value}% - {max_value}%)"
        else:
            message = f"分布区间定义无效: {reason}" if reason else "分布区间定义无效"
        
        suggestions = (
            "请检查区间定义是否正确：\n"
            "1. 最小值应小于最大值\n"
            "2. 区间名称应为有效字符串\n"
            "3. 区间范围不应重叠\n"
            "4. 数值应为有效的百分比值"
        )
        
        super().__init__(
            message=message,
            error_code="INVALID_DISTRIBUTION_RANGE",
            details={
                "range_name": range_name,
                "min_value": min_value,
                "max_value": max_value,
                "reason": reason
            },
            suggestions=suggestions
        )
        self.range_name = range_name
        self.min_value = min_value
        self.max_value = max_value
        self.reason = reason


class InsufficientPriceDataError(PriceDistributionError, DataSourceError):
    """价格数据不足异常"""
    
    def __init__(self, trade_date: str, available_count: int = None, required_count: int = None, 
                 missing_fields: List[str] = None, reason: str = None):
        """
        初始化价格数据不足异常
        
        Args:
            trade_date: 交易日期
            available_count: 可用股票数量
            required_count: 需要的最少股票数量
            missing_fields: 缺失的字段列表
            reason: 数据不足原因
        """
        if reason:
            message = f"日期 '{trade_date}' 的价格数据不足: {reason}"
        else:
            message = f"日期 '{trade_date}' 的价格数据不足，无法计算涨跌分布统计"
        
        if available_count is not None and required_count is not None:
            message += f" (可用: {available_count}, 需要: {required_count})"
        
        if missing_fields:
            message += f" (缺失字段: {', '.join(missing_fields)})"
        
        suggestions = (
            "请检查以下几点：\n"
            "1. 确认该日期是否为交易日\n"
            "2. 检查数据源是否正常工作\n"
            "3. 确认股票数据是否包含必要字段（开盘价、收盘价、涨跌幅等）\n"
            "4. 如果是最新交易日，数据可能尚未更新，请稍后重试"
        )
        
        super().__init__(
            message=message,
            error_code="INSUFFICIENT_PRICE_DATA",
            details={
                "trade_date": trade_date,
                "available_count": available_count,
                "required_count": required_count,
                "missing_fields": missing_fields,
                "reason": reason
            },
            suggestions=suggestions
        )
        self.trade_date = trade_date
        self.available_count = available_count
        self.required_count = required_count
        self.missing_fields = missing_fields
        self.reason = reason


class DistributionCalculationError(PriceDistributionError):
    """分布计算异常"""
    
    def __init__(self, calculation_type: str, reason: str = None, 
                 affected_stocks: List[str] = None, invalid_data_count: int = None):
        """
        初始化分布计算异常
        
        Args:
            calculation_type: 计算类型（如：区间分类、百分比计算等）
            reason: 计算失败原因
            affected_stocks: 受影响的股票代码列表
            invalid_data_count: 无效数据数量
        """
        if reason:
            message = f"分布计算失败 ({calculation_type}): {reason}"
        else:
            message = f"分布计算失败 ({calculation_type})"
        
        if invalid_data_count is not None:
            message += f" (无效数据: {invalid_data_count} 条)"
        
        if affected_stocks:
            stock_count = len(affected_stocks)
            if stock_count <= 5:
                message += f" (受影响股票: {', '.join(affected_stocks)})"
            else:
                message += f" (受影响股票: {stock_count} 只，包括 {', '.join(affected_stocks[:3])} 等)"
        
        suggestions = (
            "请检查以下几点：\n"
            "1. 确认股票价格数据的完整性和有效性\n"
            "2. 检查涨跌幅数据是否为有效数值\n"
            "3. 确认分布区间定义是否正确\n"
            "4. 如果问题持续存在，请尝试重新获取数据"
        )
        
        super().__init__(
            message=message,
            error_code="DISTRIBUTION_CALCULATION_ERROR",
            details={
                "calculation_type": calculation_type,
                "reason": reason,
                "affected_stocks": affected_stocks,
                "invalid_data_count": invalid_data_count
            },
            suggestions=suggestions
        )
        self.calculation_type = calculation_type
        self.reason = reason
        self.affected_stocks = affected_stocks
        self.invalid_data_count = invalid_data_count


class MarketClassificationError(PriceDistributionError):
    """市场分类异常"""
    
    def __init__(self, stock_codes: List[str] = None, classification_type: str = None, 
                 reason: str = None, unclassified_count: int = None):
        """
        初始化市场分类异常
        
        Args:
            stock_codes: 无法分类的股票代码列表
            classification_type: 分类类型（如：市场板块、ST分类等）
            reason: 分类失败原因
            unclassified_count: 未分类股票数量
        """
        if classification_type:
            if reason:
                message = f"市场分类失败 ({classification_type}): {reason}"
            else:
                message = f"市场分类失败 ({classification_type})"
        else:
            message = f"股票市场分类失败: {reason}" if reason else "股票市场分类失败"
        
        if unclassified_count is not None:
            message += f" (未分类股票: {unclassified_count} 只)"
        
        if stock_codes:
            stock_count = len(stock_codes)
            if stock_count <= 5:
                message += f" (股票代码: {', '.join(stock_codes)})"
            else:
                message += f" (包括: {', '.join(stock_codes[:3])} 等 {stock_count} 只股票)"
        
        suggestions = (
            "请检查以下几点：\n"
            "1. 确认股票代码格式是否正确\n"
            "2. 检查是否为有效的A股代码\n"
            "3. 新上市股票可能需要时间更新分类信息\n"
            "4. 系统将对未分类股票使用默认分类"
        )
        
        super().__init__(
            message=message,
            error_code="MARKET_CLASSIFICATION_ERROR",
            details={
                "stock_codes": stock_codes,
                "classification_type": classification_type,
                "reason": reason,
                "unclassified_count": unclassified_count
            },
            suggestions=suggestions
        )
        self.stock_codes = stock_codes
        self.classification_type = classification_type
        self.reason = reason
        self.unclassified_count = unclassified_count





class InvalidTradeDateError(PriceDistributionError, ValidationError):
    """无效交易日期异常"""
    
    def __init__(self, date: str, reason: str = None, valid_format: str = None):
        """
        初始化无效交易日期异常
        
        Args:
            date: 无效的日期
            reason: 无效原因
            valid_format: 有效的日期格式示例
        """
        if reason:
            message = f"无效的交易日期 '{date}': {reason}"
        else:
            message = f"无效的交易日期 '{date}'"
        
        if valid_format:
            message += f" (有效格式示例: {valid_format})"
        
        suggestions = (
            "请检查日期格式和有效性：\n"
            "1. 支持的格式：YYYY-MM-DD 或 YYYYMMDD\n"
            "2. 日期不能是未来日期\n"
            "3. 确认该日期是否为交易日\n"
            "4. 示例：'2024-01-15' 或 '20240115'"
        )
        
        super().__init__(
            message=message,
            error_code="INVALID_TRADE_DATE",
            details={
                "invalid_date": date,
                "reason": reason,
                "valid_format": valid_format
            },
            suggestions=suggestions
        )
        self.invalid_date = date
        self.reason = reason
        self.valid_format = valid_format


class StatisticsAggregationError(PriceDistributionError):
    """统计聚合异常"""
    
    def __init__(self, aggregation_type: str, reason: str = None, 
                 market_segments: List[str] = None, data_inconsistency: Dict[str, Any] = None):
        """
        初始化统计聚合异常
        
        Args:
            aggregation_type: 聚合类型（如：市场板块聚合、百分比计算等）
            reason: 聚合失败原因
            market_segments: 受影响的市场板块列表
            data_inconsistency: 数据不一致性详情
        """
        if reason:
            message = f"统计聚合失败 ({aggregation_type}): {reason}"
        else:
            message = f"统计聚合失败 ({aggregation_type})"
        
        if market_segments:
            message += f" (受影响板块: {', '.join(market_segments)})"
        
        if data_inconsistency:
            inconsistency_count = len(data_inconsistency)
            message += f" (数据不一致项: {inconsistency_count} 个)"
        
        suggestions = (
            "请检查以下几点：\n"
            "1. 确认输入数据的完整性和一致性\n"
            "2. 检查市场分类结果是否正确\n"
            "3. 验证分布计算结果是否有效\n"
            "4. 如果问题持续存在，请尝试重新计算"
        )
        
        super().__init__(
            message=message,
            error_code="STATISTICS_AGGREGATION_ERROR",
            details={
                "aggregation_type": aggregation_type,
                "reason": reason,
                "market_segments": market_segments,
                "data_inconsistency": data_inconsistency
            },
            suggestions=suggestions
        )
        self.aggregation_type = aggregation_type
        self.reason = reason
        self.market_segments = market_segments
        self.data_inconsistency = data_inconsistency


class PriceDistributionValidationError(PriceDistributionError, ValidationError):
    """涨跌分布统计验证异常"""
    
    def __init__(self, validation_type: str, field_name: str = None, field_value: Any = None, 
                 reason: str = None, expected_format: str = None):
        """
        初始化涨跌分布统计验证异常
        
        Args:
            validation_type: 验证类型（如：参数验证、数据验证等）
            field_name: 字段名称
            field_value: 字段值
            reason: 验证失败原因
            expected_format: 期望的格式
        """
        if field_name:
            if reason:
                message = f"{validation_type}验证失败，字段 '{field_name}': {reason}"
            else:
                message = f"{validation_type}验证失败，字段 '{field_name}' 值无效"
            
            if field_value is not None:
                message += f" (当前值: {field_value})"
            
            if expected_format:
                message += f" (期望格式: {expected_format})"
        else:
            message = f"{validation_type}验证失败: {reason}" if reason else f"{validation_type}验证失败"
        
        suggestions = (
            "请检查输入参数的格式和有效性：\n"
            "1. 确认所有必需参数都已提供\n"
            "2. 检查参数类型和格式是否正确\n"
            "3. 验证数值范围是否在有效区间内\n"
            "4. 参考API文档确认参数要求"
        )
        
        super().__init__(
            message=message,
            error_code="PRICE_DISTRIBUTION_VALIDATION_ERROR",
            details={
                "validation_type": validation_type,
                "field_name": field_name,
                "field_value": field_value,
                "reason": reason,
                "expected_format": expected_format
            },
            suggestions=suggestions
        )
        self.validation_type = validation_type
        self.field_name = field_name
        self.field_value = field_value
        self.reason = reason
        self.expected_format = expected_format


class PriceDistributionServiceError(PriceDistributionError):
    """涨跌分布统计服务异常"""
    
    def __init__(self, service_operation: str, reason: str = None, 
                 service_state: Dict[str, Any] = None, recovery_suggestion: str = None):
        """
        初始化涨跌分布统计服务异常
        
        Args:
            service_operation: 服务操作类型
            reason: 服务失败原因
            service_state: 服务状态信息
            recovery_suggestion: 恢复建议
        """
        if reason:
            message = f"涨跌分布统计服务操作失败 ({service_operation}): {reason}"
        else:
            message = f"涨跌分布统计服务操作失败 ({service_operation})"
        
        if service_state:
            state_info = []
            for key, value in service_state.items():
                state_info.append(f"{key}: {value}")
            if state_info:
                message += f" (服务状态: {', '.join(state_info)})"
        
        base_suggestions = (
            "请尝试以下解决方案：\n"
            "1. 检查服务依赖是否正常（数据源、缓存等）\n"
            "2. 确认网络连接是否稳定\n"
            "3. 稍后重试或使用不同的参数\n"
            "4. 如果问题持续存在，请联系技术支持"
        )
        
        if recovery_suggestion:
            suggestions = f"{recovery_suggestion}\n\n{base_suggestions}"
        else:
            suggestions = base_suggestions
        
        super().__init__(
            message=message,
            error_code="PRICE_DISTRIBUTION_SERVICE_ERROR",
            details={
                "service_operation": service_operation,
                "reason": reason,
                "service_state": service_state,
                "recovery_suggestion": recovery_suggestion
            },
            suggestions=suggestions
        )
        self.service_operation = service_operation
        self.reason = reason
        self.service_state = service_state
        self.recovery_suggestion = recovery_suggestion