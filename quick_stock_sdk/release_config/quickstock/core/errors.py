"""
异常定义和错误处理

定义SDK的异常层次结构和错误处理机制。

异常层次结构:
    QuickStockError (基础异常类)
    ├── DataSourceError (数据源相关异常)
    │   ├── FinancialDataError (财务数据专用异常)
    │   │   ├── ReportNotFoundError (财务报告未找到)
    │   │   ├── ForecastDataError (业绩预告数据异常)
    │   │   ├── FlashReportError (业绩快报异常)
    │   │   └── FinancialDataValidationError (财务数据验证异常)
    │   └── PriceDistributionError (涨跌分布统计异常，如果已导入)
    ├── ValidationError (参数验证异常)
    │   └── FinancialDataValidationError (财务数据验证异常，多重继承)
    ├── RateLimitError (速率限制异常)
    ├── NetworkError (网络相关异常)
    ├── DatabaseError (数据库相关异常)
    │   └── LimitUpDatabaseError (涨停统计数据库异常)
    └── LimitUpStatsError (涨停统计专用异常)
        ├── InvalidTradeDateError (无效交易日期)
        ├── InsufficientDataError (数据不足)
        ├── LimitUpDatabaseError (涨停统计数据库异常，多重继承)
        ├── StockClassificationError (股票分类异常)
        └── LimitUpDetectionError (涨停检测异常)

注意: SDK已移除缓存功能，不再包含CacheError异常类。
"""

import logging
import time
from typing import Callable, Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from ..config import Config


class QuickStockError(Exception):
    """SDK基础异常类"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        """
        初始化异常
        
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详细信息
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class DataSourceError(QuickStockError):
    """数据源相关异常"""
    pass


class ValidationError(QuickStockError):
    """参数验证异常"""
    pass


class RateLimitError(QuickStockError):
    """速率限制异常"""
    pass


class NetworkError(QuickStockError):
    """网络相关异常"""
    pass


class DatabaseError(QuickStockError):
    """数据库相关异常"""
    pass


class LimitUpStatsError(QuickStockError):
    """涨停统计专用异常基类"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None, 
                 suggestions: Optional[str] = None):
        """
        初始化涨停统计异常
        
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详细信息
            suggestions: 用户友好的建议
        """
        super().__init__(message, error_code, details)
        self.suggestions = suggestions


class InvalidTradeDateError(LimitUpStatsError):
    """无效交易日期异常"""
    
    def __init__(self, date: str, reason: str = None):
        """
        初始化无效交易日期异常
        
        Args:
            date: 无效的日期
            reason: 无效原因
        """
        if reason:
            message = f"无效的交易日期 '{date}': {reason}"
        else:
            message = f"无效的交易日期 '{date}'"
        
        suggestions = (
            "请检查日期格式是否正确（支持 YYYY-MM-DD 或 YYYYMMDD 格式），"
            "确保日期不是未来日期，且为有效的交易日"
        )
        
        super().__init__(
            message=message,
            error_code="INVALID_TRADE_DATE",
            details={"invalid_date": date, "reason": reason},
            suggestions=suggestions
        )
        self.invalid_date = date
        self.reason = reason


class InsufficientDataError(LimitUpStatsError):
    """数据不足异常"""
    
    def __init__(self, date: str, missing_data_type: str = None, available_count: int = None, 
                 required_count: int = None):
        """
        初始化数据不足异常
        
        Args:
            date: 相关日期
            missing_data_type: 缺失的数据类型
            available_count: 可用数据数量
            required_count: 需要的数据数量
        """
        if missing_data_type:
            message = f"日期 '{date}' 的{missing_data_type}数据不足"
            if available_count is not None and required_count is not None:
                message += f"（可用: {available_count}, 需要: {required_count}）"
        else:
            message = f"日期 '{date}' 的数据不足，无法计算涨停统计"
        
        suggestions = (
            "请检查该日期是否为交易日，或稍后重试。"
            "如果问题持续存在，可能是数据源暂时不可用"
        )
        
        super().__init__(
            message=message,
            error_code="INSUFFICIENT_DATA",
            details={
                "date": date,
                "missing_data_type": missing_data_type,
                "available_count": available_count,
                "required_count": required_count
            },
            suggestions=suggestions
        )
        self.date = date
        self.missing_data_type = missing_data_type
        self.available_count = available_count
        self.required_count = required_count


class LimitUpDatabaseError(DatabaseError, LimitUpStatsError):
    """涨停统计数据库异常"""
    
    def __init__(self, operation: str, message: str = None, original_error: Exception = None):
        """
        初始化涨停统计数据库异常
        
        Args:
            operation: 数据库操作类型
            message: 错误消息
            original_error: 原始异常
        """
        if message:
            full_message = f"数据库操作 '{operation}' 失败: {message}"
        else:
            full_message = f"数据库操作 '{operation}' 失败"
        
        if original_error:
            full_message += f" (原因: {str(original_error)})"
        
        suggestions = (
            "请检查数据库连接是否正常，确保有足够的磁盘空间。"
            "如果问题持续存在，请检查数据库文件权限或尝试重新初始化数据库"
        )
        
        super().__init__(
            message=full_message,
            error_code="DATABASE_OPERATION_FAILED",
            details={
                "operation": operation,
                "original_error": str(original_error) if original_error else None
            },
            suggestions=suggestions
        )
        self.operation = operation
        self.original_error = original_error


class StockClassificationError(LimitUpStatsError):
    """股票分类异常"""
    
    def __init__(self, stock_code: str, reason: str = None):
        """
        初始化股票分类异常
        
        Args:
            stock_code: 无法分类的股票代码
            reason: 分类失败原因
        """
        if reason:
            message = f"无法分类股票代码 '{stock_code}': {reason}"
        else:
            message = f"无法分类股票代码 '{stock_code}'"
        
        suggestions = (
            "请检查股票代码格式是否正确。"
            "如果是新上市股票或特殊代码，系统将使用默认分类"
        )
        
        super().__init__(
            message=message,
            error_code="STOCK_CLASSIFICATION_FAILED",
            details={"stock_code": stock_code, "reason": reason},
            suggestions=suggestions
        )
        self.stock_code = stock_code
        self.reason = reason


class LimitUpDetectionError(LimitUpStatsError):
    """涨停检测异常"""
    
    def __init__(self, stock_code: str, reason: str = None, price_data: Dict[str, float] = None):
        """
        初始化涨停检测异常
        
        Args:
            stock_code: 相关股票代码
            reason: 检测失败原因
            price_data: 价格数据
        """
        if reason:
            message = f"股票 '{stock_code}' 涨停检测失败: {reason}"
        else:
            message = f"股票 '{stock_code}' 涨停检测失败"
        
        suggestions = (
            "请检查股票价格数据是否完整和有效。"
            "确保开盘价、收盘价、最高价等数据都存在且为正数"
        )
        
        super().__init__(
            message=message,
            error_code="LIMIT_UP_DETECTION_FAILED",
            details={
                "stock_code": stock_code,
                "reason": reason,
                "price_data": price_data
            },
            suggestions=suggestions
        )
        self.stock_code = stock_code
        self.reason = reason
        self.price_data = price_data


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, config: 'Config'):
        """
        初始化错误处理器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.logger = self._setup_logger()
        self._error_stats = {
            'total_errors': 0,
            'retry_attempts': 0,
            'successful_retries': 0,
            'failed_retries': 0,
            'error_types': {}
        }
        self._rate_limit_tracker = {}
    
    def _setup_logger(self) -> logging.Logger:
        """
        设置日志记录器
        
        Returns:
            配置好的日志记录器
        """
        logger = logging.getLogger('quickstock.errors')
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
        
        # 设置日志级别
        log_level = getattr(self.config, 'log_level', 'INFO')
        if isinstance(log_level, str):
            logger.setLevel(getattr(logging, log_level.upper()))
        else:
            logger.setLevel(logging.INFO)  # 默认级别
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 添加控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 如果配置了日志文件，添加文件处理器
        log_file = getattr(self.config, 'log_file', None)
        if log_file and isinstance(log_file, str):
            try:
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"无法创建日志文件处理器: {e}")
        
        return logger
    
    async def handle_with_retry(self, func: Callable, *args, **kwargs):
        """
        带重试的错误处理
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
        """
        import asyncio
        
        last_error = None
        retry_count = 0
        start_time = time.time()
        
        for attempt in range(self.config.max_retries + 1):
            try:
                result = await func(*args, **kwargs)
                
                # 更新统计信息（成功）
                if last_error:
                    self._update_error_stats(last_error, attempt, True)
                    execution_time = time.time() - start_time
                    self.logger.info(
                        f"函数 {func.__name__} 在第{attempt + 1}次尝试后成功，"
                        f"总耗时: {execution_time:.2f}秒"
                    )
                
                return result
                
            except Exception as error:
                last_error = error
                
                # 记录错误
                context = {
                    'attempt': attempt + 1,
                    'max_retries': self.config.max_retries,
                    'function': func.__name__,
                    'args': str(args)[:100],  # 限制长度避免日志过长
                    'kwargs': str(kwargs)[:100],
                    'execution_time': time.time() - start_time
                }
                self.log_error(error, context)
                
                # 跟踪速率限制
                if isinstance(error, RateLimitError):
                    provider = kwargs.get('provider', 'unknown')
                    self._track_rate_limit(provider, error)
                
                # 判断是否应该停止重试
                if self._should_stop_retrying(error, attempt):
                    break
                
                # 判断是否应该重试
                if self.should_retry(error):
                    # 计算延迟时间
                    delay = self._calculate_retry_delay(attempt, error)
                    self.logger.info(
                        f"第{attempt + 1}次尝试失败，{delay:.2f}秒后重试: {error}"
                    )
                    await asyncio.sleep(delay)
                    continue
                else:
                    # 不应该重试，直接退出
                    break
        
        # 更新统计信息（失败）
        self._update_error_stats(last_error, attempt, False)
        
        # 所有重试都失败了，抛出最后的异常
        raise last_error
        
    def should_retry(self, error: Exception) -> bool:
        """
        判断是否应该重试
        
        Args:
            error: 异常对象
            
        Returns:
            是否应该重试
        """
        # 网络相关错误应该重试
        if isinstance(error, (NetworkError, ConnectionError, TimeoutError)):
            return True
        
        # 财务数据特定错误的重试逻辑（需要在DataSourceError之前检查，因为财务错误继承自DataSourceError）
        if hasattr(error, '__class__') and 'FinancialDataError' in [cls.__name__ for cls in error.__class__.__mro__]:
            result = self._should_retry_financial_error(error)
            return result
        
        # 数据源临时错误应该重试
        if isinstance(error, DataSourceError):
            # 检查错误消息中是否包含临时性错误的关键词
            error_msg = str(error).lower()
            temporary_keywords = [
                'timeout', 'connection', 'network', 'temporary', 
                'server error', '502', '503', '504'
            ]
            return any(keyword in error_msg for keyword in temporary_keywords)
        
        # 速率限制错误应该重试
        if isinstance(error, RateLimitError):
            return True
        
        # 参数验证错误不应该重试
        if isinstance(error, ValidationError):
            return False
        
        # 其他未知错误，默认不重试
        return False
    
    def _should_retry_financial_error(self, error: 'FinancialDataError') -> bool:
        """
        判断财务数据错误是否应该重试
        
        Args:
            error: 财务数据异常对象
            
        Returns:
            是否应该重试
        """
        # 数据验证错误不应该重试
        if 'FinancialDataValidationError' in error.__class__.__name__:
            return False
        
        # 报告未找到错误通常不应该重试，除非是临时性问题
        if 'ReportNotFoundError' in error.__class__.__name__:
            # 检查是否是临时性问题
            if hasattr(error, 'details') and error.details:
                # 检查details中是否有temporary标记
                if error.details.get('temporary') is True:
                    return True
                # 或者检查字符串中是否包含temporary关键词
                if 'temporary' in str(error.details).lower():
                    return True
            return False
        
        # 预告数据错误和快报错误可能是临时性的，可以重试
        if any(cls_name in error.__class__.__name__ for cls_name in ['ForecastDataError', 'FlashReportError']):
            # 预告和快报错误默认都重试，因为它们可能是临时性问题
            return True
        
        # 其他财务数据错误默认重试一次
        return True
    
    async def handle_financial_data_error(self, error: 'FinancialDataError', context: Dict[str, Any]) -> Optional[Any]:
        """
        处理财务数据错误并尝试恢复
        
        Args:
            error: 财务数据异常
            context: 错误上下文，包含请求参数等信息
            
        Returns:
            恢复后的数据或None
        """
        self.logger.warning(f"处理财务数据错误: {error}")
        
        # 记录错误详情
        error_context = {
            'error_type': type(error).__name__,
            'error_code': error.error_code,
            'suggestions': getattr(error, 'suggestions', None),
            'context': context
        }
        self.log_error(error, error_context)
        
        # 根据错误类型尝试不同的恢复策略
        if 'ReportNotFoundError' in error.__class__.__name__:
            return await self._recover_from_report_not_found(error, context)
        elif 'ForecastDataError' in error.__class__.__name__:
            return await self._recover_from_forecast_error(error, context)
        elif 'FlashReportError' in error.__class__.__name__:
            return await self._recover_from_flash_report_error(error, context)
        elif 'FinancialDataValidationError' in error.__class__.__name__:
            return await self._recover_from_validation_error(error, context)
        
        return None
    
    async def _recover_from_report_not_found(self, error: 'ReportNotFoundError', context: Dict[str, Any]) -> Optional[Any]:
        """
        从财务报告未找到错误中恢复
        
        Args:
            error: 报告未找到异常
            context: 错误上下文
            
        Returns:
            恢复后的数据或None
        """
        # 尝试查找相近日期的报告
        if 'start_date' in context and 'end_date' in context:
            self.logger.info(f"尝试扩大日期范围查找股票 {error.ts_code} 的财务报告")
            # 这里可以实现扩大日期范围的逻辑
            # 实际实现需要调用相应的服务方法
        
        # 返回空数据结构而不是None，让调用方知道没有数据但操作成功
        return {
            'ts_code': error.ts_code,
            'report_date': error.report_date,
            'report_type': error.report_type,
            'data': [],
            'message': '未找到指定期间的财务报告数据'
        }
    
    async def _recover_from_forecast_error(self, error: 'ForecastDataError', context: Dict[str, Any]) -> Optional[Any]:
        """
        从业绩预告错误中恢复
        
        Args:
            error: 预告数据异常
            context: 错误上下文
            
        Returns:
            恢复后的数据或None
        """
        self.logger.info(f"尝试从业绩预告错误中恢复: {error.ts_code}")
        
        # 返回空的预告数据结构
        return {
            'ts_code': error.ts_code,
            'forecasts': [],
            'message': '该股票暂无业绩预告数据'
        }
    
    async def _recover_from_flash_report_error(self, error: 'FlashReportError', context: Dict[str, Any]) -> Optional[Any]:
        """
        从业绩快报错误中恢复
        
        Args:
            error: 快报异常
            context: 错误上下文
            
        Returns:
            恢复后的数据或None
        """
        self.logger.info(f"尝试从业绩快报错误中恢复: {error.ts_code}")
        
        # 返回空的快报数据结构
        return {
            'ts_code': error.ts_code,
            'flash_reports': [],
            'message': '该股票暂无业绩快报数据'
        }
    
    async def _recover_from_validation_error(self, error: 'FinancialDataValidationError', context: Dict[str, Any]) -> Optional[Any]:
        """
        从数据验证错误中恢复
        
        Args:
            error: 验证异常
            context: 错误上下文
            
        Returns:
            恢复后的数据或None
        """
        self.logger.warning(f"财务数据验证失败，尝试数据清理: {error.field_name}")
        
        # 对于验证错误，通常不能自动恢复，但可以提供清理后的数据
        # 这里返回None，让上层决定如何处理
        return None
        
    def log_error(self, error: Exception, context: Dict[str, Any]):
        """
        记录错误信息
        
        Args:
            error: 异常对象
            context: 错误上下文信息
        """
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        }
        
        # 如果是QuickStockError，记录额外信息
        if isinstance(error, QuickStockError):
            error_info.update({
                'error_code': error.error_code,
                'details': error.details
            })
        
        # 根据错误类型选择日志级别
        if isinstance(error, (ValidationError,)):
            self.logger.warning(f"参数验证错误: {error_info}")
        elif isinstance(error, (NetworkError, DataSourceError)):
            self.logger.error(f"数据获取错误: {error_info}")
        elif isinstance(error, RateLimitError):
            self.logger.warning(f"速率限制错误: {error_info}")
        elif isinstance(error, DatabaseError):
            self.logger.error(f"数据库错误: {error_info}")
        else:
            self.logger.error(f"未知错误: {error_info}")
    
    def create_error(self, error_type: str, message: str, 
                    error_code: str = None, details: Dict[str, Any] = None) -> QuickStockError:
        """
        创建特定类型的错误
        
        Args:
            error_type: 错误类型，支持的类型包括:
                - 'data_source': 数据源错误
                - 'validation': 参数验证错误
                - 'rate_limit': 速率限制错误
                - 'network': 网络错误
                - 'database': 数据库错误
            message: 错误消息
            error_code: 错误代码
            details: 错误详细信息
            
        Returns:
            对应的异常对象
        """
        error_classes = {
            'data_source': DataSourceError,
            'validation': ValidationError,
            'rate_limit': RateLimitError,
            'network': NetworkError,
            'database': DatabaseError
        }
        
        error_class = error_classes.get(error_type, QuickStockError)
        return error_class(message, error_code, details)
    
    def get_error_stats(self) -> Dict[str, Any]:
        """
        获取错误统计信息
        
        Returns:
            错误统计数据
        """
        return self._error_stats.copy()
    
    def reset_error_stats(self):
        """重置错误统计"""
        self._error_stats = {
            'total_errors': 0,
            'retry_attempts': 0,
            'successful_retries': 0,
            'failed_retries': 0,
            'error_types': {}
        }
        self._rate_limit_tracker.clear()
    
    def _update_error_stats(self, error: Exception, retry_count: int, success: bool):
        """
        更新错误统计信息
        
        Args:
            error: 异常对象
            retry_count: 重试次数
            success: 是否最终成功
        """
        self._error_stats['total_errors'] += 1
        self._error_stats['retry_attempts'] += retry_count
        
        if success and retry_count > 0:
            self._error_stats['successful_retries'] += 1
        elif not success and retry_count > 0:
            self._error_stats['failed_retries'] += 1
        
        # 统计错误类型
        error_type = type(error).__name__
        self._error_stats['error_types'][error_type] = (
            self._error_stats['error_types'].get(error_type, 0) + 1
        )
    
    def _calculate_retry_delay(self, attempt: int, error: Exception) -> float:
        """
        计算重试延迟时间
        
        Args:
            attempt: 当前尝试次数（从0开始）
            error: 异常对象
            
        Returns:
            延迟时间（秒）
        """
        base_delay = self.config.retry_delay
        
        # 对于速率限制错误，使用更长的延迟
        if isinstance(error, RateLimitError):
            # 检查是否有速率限制信息
            if hasattr(error, 'details') and error.details:
                retry_after = error.details.get('retry_after')
                if retry_after:
                    return float(retry_after)
            
            # 默认使用更长的延迟
            base_delay = max(base_delay, 5.0)
        
        # 指数退避，但有最大限制
        delay = base_delay * (2 ** attempt)
        max_delay = 60.0  # 默认最大延迟60秒
        
        return min(delay, max_delay)
    
    def _should_stop_retrying(self, error: Exception, attempt: int) -> bool:
        """
        判断是否应该停止重试
        
        Args:
            error: 异常对象
            attempt: 当前尝试次数
            
        Returns:
            是否应该停止重试
        """
        # 达到最大重试次数
        if attempt >= self.config.max_retries:
            return True
        
        # 对于某些错误类型，立即停止重试
        if isinstance(error, ValidationError):
            return True
        
        # 对于认证错误，不重试
        if isinstance(error, DataSourceError):
            error_msg = str(error).lower()
            auth_keywords = ['authentication', 'unauthorized', 'invalid token', 'api key']
            if any(keyword in error_msg for keyword in auth_keywords):
                return True
        
        return False
    
    def _track_rate_limit(self, provider: str, error: RateLimitError):
        """
        跟踪速率限制信息
        
        Args:
            provider: 数据提供者名称
            error: 速率限制错误
        """
        now = datetime.now()
        
        if provider not in self._rate_limit_tracker:
            self._rate_limit_tracker[provider] = {
                'last_error': now,
                'error_count': 0,
                'reset_time': None
            }
        
        tracker = self._rate_limit_tracker[provider]
        tracker['last_error'] = now
        tracker['error_count'] += 1
        
        # 如果错误包含重置时间信息
        if hasattr(error, 'details') and error.details:
            reset_after = error.details.get('reset_after')
            if reset_after:
                tracker['reset_time'] = now + timedelta(seconds=float(reset_after))
    
    def is_rate_limited(self, provider: str) -> bool:
        """
        检查指定提供者是否仍在速率限制中
        
        Args:
            provider: 数据提供者名称
            
        Returns:
            是否仍在速率限制中
        """
        if provider not in self._rate_limit_tracker:
            return False
        
        tracker = self._rate_limit_tracker[provider]
        reset_time = tracker.get('reset_time')
        
        if reset_time and datetime.now() < reset_time:
            return True
        
        return False


# ==================== 财务数据相关异常 ====================

class FinancialDataError(DataSourceError):
    """财务数据专用异常基类"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None, 
                 suggestions: Optional[str] = None):
        """
        初始化财务数据异常
        
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详细信息
            suggestions: 用户友好的建议
        """
        super().__init__(message, error_code, details)
        self.suggestions = suggestions


class ReportNotFoundError(FinancialDataError):
    """财务报告未找到异常"""
    
    def __init__(self, ts_code: str, report_date: str = None, report_type: str = None):
        """
        初始化财务报告未找到异常
        
        Args:
            ts_code: 股票代码
            report_date: 报告日期
            report_type: 报告类型
        """
        if report_date and report_type:
            message = f"未找到股票 '{ts_code}' 在 '{report_date}' 的 '{report_type}' 财务报告"
        elif report_date:
            message = f"未找到股票 '{ts_code}' 在 '{report_date}' 的财务报告"
        else:
            message = f"未找到股票 '{ts_code}' 的财务报告"
        
        suggestions = (
            "请检查股票代码是否正确，确认报告日期是否为有效的报告期。"
            "某些股票可能尚未发布相应期间的财务报告"
        )
        
        super().__init__(
            message=message,
            error_code="FINANCIAL_REPORT_NOT_FOUND",
            details={
                "ts_code": ts_code,
                "report_date": report_date,
                "report_type": report_type
            },
            suggestions=suggestions
        )
        self.ts_code = ts_code
        self.report_date = report_date
        self.report_type = report_type


class ForecastDataError(FinancialDataError):
    """业绩预告数据异常"""
    
    def __init__(self, ts_code: str, reason: str = None, forecast_date: str = None):
        """
        初始化业绩预告数据异常
        
        Args:
            ts_code: 股票代码
            reason: 错误原因
            forecast_date: 预告日期
        """
        if reason:
            message = f"股票 '{ts_code}' 的业绩预告数据异常: {reason}"
        else:
            message = f"股票 '{ts_code}' 的业绩预告数据异常"
        
        if forecast_date:
            message += f" (预告日期: {forecast_date})"
        
        suggestions = (
            "请检查股票代码是否正确，确认该股票是否发布了业绩预告。"
            "某些股票可能不会发布业绩预告或预告数据可能延迟更新"
        )
        
        super().__init__(
            message=message,
            error_code="FORECAST_DATA_ERROR",
            details={
                "ts_code": ts_code,
                "reason": reason,
                "forecast_date": forecast_date
            },
            suggestions=suggestions
        )
        self.ts_code = ts_code
        self.reason = reason
        self.forecast_date = forecast_date


class FlashReportError(FinancialDataError):
    """业绩快报异常"""
    
    def __init__(self, ts_code: str, reason: str = None, report_date: str = None):
        """
        初始化业绩快报异常
        
        Args:
            ts_code: 股票代码
            reason: 错误原因
            report_date: 报告日期
        """
        if reason:
            message = f"股票 '{ts_code}' 的业绩快报异常: {reason}"
        else:
            message = f"股票 '{ts_code}' 的业绩快报异常"
        
        if report_date:
            message += f" (报告日期: {report_date})"
        
        suggestions = (
            "请检查股票代码是否正确，确认该股票是否发布了业绩快报。"
            "业绩快报通常在正式财务报告发布前发布，可能存在时间差"
        )
        
        super().__init__(
            message=message,
            error_code="FLASH_REPORT_ERROR",
            details={
                "ts_code": ts_code,
                "reason": reason,
                "report_date": report_date
            },
            suggestions=suggestions
        )
        self.ts_code = ts_code
        self.reason = reason
        self.report_date = report_date


class FinancialDataValidationError(FinancialDataError, ValidationError):
    """财务数据验证异常"""
    
    def __init__(self, field_name: str, field_value: Any, reason: str = None):
        """
        初始化财务数据验证异常
        
        Args:
            field_name: 字段名称
            field_value: 字段值
            reason: 验证失败原因
        """
        if reason:
            message = f"财务数据字段 '{field_name}' 验证失败: {reason} (值: {field_value})"
        else:
            message = f"财务数据字段 '{field_name}' 验证失败 (值: {field_value})"
        
        suggestions = (
            "请检查财务数据的完整性和准确性。"
            "确保所有必需字段都有有效值，数值字段为数字类型"
        )
        
        super().__init__(
            message=message,
            error_code="FINANCIAL_DATA_VALIDATION_ERROR",
            details={
                "field_name": field_name,
                "field_value": field_value,
                "reason": reason
            },
            suggestions=suggestions
        )
        self.field_name = field_name
        self.field_value = field_value
        self.reason = reason


# 导入涨跌分布统计专用异常
try:
    from .price_distribution_errors import (
        PriceDistributionError,
        InvalidDistributionRangeError,
        InsufficientPriceDataError,
        DistributionCalculationError,
        MarketClassificationError,
        InvalidTradeDateError,
        StatisticsAggregationError,
        PriceDistributionValidationError,
        PriceDistributionServiceError
    )
    
    # 将涨跌分布异常添加到模块的公共接口
    __all__ = [
        'QuickStockError',
        'DataSourceError',
        'ValidationError',
        'RateLimitError',
        'NetworkError',
        'DatabaseError',
        'LimitUpStatsError',
        'InvalidTradeDateError',
        'InsufficientDataError',
        'LimitUpDatabaseError',
        'StockClassificationError',
        'LimitUpDetectionError',
        'ErrorHandler',
        'FinancialDataError',
        'ReportNotFoundError',
        'ForecastDataError',
        'FlashReportError',
        'FinancialDataValidationError',
        # 涨跌分布统计异常
        'PriceDistributionError',
        'InvalidDistributionRangeError',
        'InsufficientPriceDataError',
        'DistributionCalculationError',
        'MarketClassificationError',
        'StatisticsAggregationError',
        'PriceDistributionValidationError',
        'PriceDistributionServiceError'
    ]
    
except ImportError:
    # 如果涨跌分布异常模块不存在，继续使用基础异常
    __all__ = [
        'QuickStockError',
        'DataSourceError',
        'ValidationError',
        'RateLimitError',
        'NetworkError',
        'DatabaseError',
        'LimitUpStatsError',
        'InvalidTradeDateError',
        'InsufficientDataError',
        'LimitUpDatabaseError',
        'StockClassificationError',
        'LimitUpDetectionError',
        'ErrorHandler',
        'FinancialDataError',
        'ReportNotFoundError',
        'ForecastDataError',
        'FlashReportError',
        'FinancialDataValidationError'
    ]

