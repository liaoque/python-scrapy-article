"""
涨停统计验证工具

提供涨停统计功能的各种验证和回退机制
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd

from ..core.errors import (
    InvalidTradeDateError,
    InsufficientDataError,
    StockClassificationError,
    LimitUpDetectionError
)


logger = logging.getLogger(__name__)


class TradeDateValidator:
    """交易日期验证器"""
    
    # 支持的日期格式
    DATE_FORMATS = [
        "%Y-%m-%d",
        "%Y%m%d",
        "%Y/%m/%d"
    ]
    
    # 已知的非交易日（节假日等）
    KNOWN_HOLIDAYS = {
        # 2024年节假日示例
        "2024-01-01",  # 元旦
        "2024-02-10", "2024-02-11", "2024-02-12", "2024-02-13", 
        "2024-02-14", "2024-02-15", "2024-02-16", "2024-02-17",  # 春节
        "2024-04-04", "2024-04-05", "2024-04-06",  # 清明节
        "2024-05-01", "2024-05-02", "2024-05-03",  # 劳动节
        "2024-06-10",  # 端午节
        "2024-09-15", "2024-09-16", "2024-09-17",  # 中秋节
        "2024-10-01", "2024-10-02", "2024-10-03", "2024-10-04",
        "2024-10-05", "2024-10-06", "2024-10-07",  # 国庆节
    }
    
    @classmethod
    def validate_date_format(cls, date_str: str) -> datetime:
        """
        验证并解析日期格式
        
        Args:
            date_str: 日期字符串
            
        Returns:
            解析后的datetime对象
            
        Raises:
            InvalidTradeDateError: 日期格式无效
        """
        if not date_str or not isinstance(date_str, str):
            raise InvalidTradeDateError(str(date_str), "日期不能为空")
        
        # 尝试各种日期格式
        for date_format in cls.DATE_FORMATS:
            try:
                parsed_date = datetime.strptime(date_str.strip(), date_format)
                return parsed_date
            except ValueError:
                continue
        
        # 所有格式都失败
        supported_formats = ", ".join(cls.DATE_FORMATS)
        raise InvalidTradeDateError(
            date_str, 
            f"不支持的日期格式，支持的格式: {supported_formats}"
        )
    
    @classmethod
    def validate_trade_date(cls, date_str: str) -> str:
        """
        验证交易日期
        
        Args:
            date_str: 日期字符串
            
        Returns:
            标准化的日期字符串 (YYYY-MM-DD)
            
        Raises:
            InvalidTradeDateError: 无效的交易日期
        """
        # 验证格式
        parsed_date = cls.validate_date_format(date_str)
        
        # 检查是否为未来日期
        today = datetime.now().date()
        if parsed_date.date() > today:
            raise InvalidTradeDateError(date_str, "不能查询未来日期的数据")
        
        # 检查是否过于久远（超过10年）
        ten_years_ago = today - timedelta(days=365 * 10)
        if parsed_date.date() < ten_years_ago:
            raise InvalidTradeDateError(date_str, "日期过于久远，可能没有数据")
        
        # 标准化日期格式
        normalized_date = parsed_date.strftime("%Y-%m-%d")
        
        # 检查是否为周末
        if parsed_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            logger.warning(f"日期 {normalized_date} 是周末，可能不是交易日")
        
        # 检查是否为已知节假日
        if normalized_date in cls.KNOWN_HOLIDAYS:
            logger.warning(f"日期 {normalized_date} 是已知节假日，可能不是交易日")
        
        return normalized_date
    
    @classmethod
    def is_likely_trading_day(cls, date_str: str) -> bool:
        """
        判断是否可能是交易日
        
        Args:
            date_str: 日期字符串
            
        Returns:
            是否可能是交易日
        """
        try:
            parsed_date = cls.validate_date_format(date_str)
            normalized_date = parsed_date.strftime("%Y-%m-%d")
            
            # 周末不是交易日
            if parsed_date.weekday() >= 5:
                return False
            
            # 已知节假日不是交易日
            if normalized_date in cls.KNOWN_HOLIDAYS:
                return False
            
            return True
        except InvalidTradeDateError:
            return False


class DataValidator:
    """数据验证器"""
    
    @staticmethod
    def validate_stock_data(stock_data: pd.DataFrame, date: str, 
                          min_stocks: int = 100) -> Tuple[bool, str]:
        """
        验证股票数据的完整性
        
        Args:
            stock_data: 股票数据DataFrame
            date: 交易日期
            min_stocks: 最少股票数量
            
        Returns:
            (是否有效, 错误信息)
        """
        if stock_data is None or stock_data.empty:
            return False, f"日期 {date} 没有股票数据"
        
        # 检查数据量
        if len(stock_data) < min_stocks:
            return False, f"股票数据量不足，当前: {len(stock_data)}, 最少需要: {min_stocks}"
        
        # 检查必要字段
        required_columns = ['ts_code', 'open', 'close', 'high', 'low']
        missing_columns = [col for col in required_columns if col not in stock_data.columns]
        if missing_columns:
            return False, f"缺少必要字段: {missing_columns}"
        
        # 检查数据质量
        null_counts = stock_data[required_columns].isnull().sum()
        if null_counts.any():
            problematic_columns = null_counts[null_counts > 0].to_dict()
            return False, f"存在空值字段: {problematic_columns}"
        
        # 检查价格数据的合理性
        price_columns = ['open', 'close', 'high', 'low']
        for col in price_columns:
            if (stock_data[col] <= 0).any():
                invalid_count = (stock_data[col] <= 0).sum()
                return False, f"存在无效价格数据 ({col}): {invalid_count} 条记录"
        
        # 检查价格逻辑（最高价应该 >= 最低价）
        invalid_price_logic = stock_data['high'] < stock_data['low']
        if invalid_price_logic.any():
            invalid_count = invalid_price_logic.sum()
            return False, f"存在价格逻辑错误（最高价 < 最低价）: {invalid_count} 条记录"
        
        return True, "数据验证通过"
    
    @staticmethod
    def validate_price_data(stock_code: str, price_data: Dict[str, float]) -> bool:
        """
        验证单只股票的价格数据
        
        Args:
            stock_code: 股票代码
            price_data: 价格数据字典
            
        Returns:
            是否有效
            
        Raises:
            LimitUpDetectionError: 价格数据无效
        """
        required_fields = ['open', 'close', 'high']
        
        # 检查必要字段
        for field in required_fields:
            if field not in price_data:
                raise LimitUpDetectionError(
                    stock_code, 
                    f"缺少必要的价格字段: {field}",
                    price_data
                )
            
            value = price_data[field]
            if value is None or pd.isna(value):
                raise LimitUpDetectionError(
                    stock_code,
                    f"价格字段 {field} 为空",
                    price_data
                )
            
            if not isinstance(value, (int, float)) or value <= 0:
                raise LimitUpDetectionError(
                    stock_code,
                    f"价格字段 {field} 无效: {value}",
                    price_data
                )
        
        # 检查价格逻辑
        if price_data['high'] < max(price_data['open'], price_data['close']):
            raise LimitUpDetectionError(
                stock_code,
                "最高价不能低于开盘价或收盘价",
                price_data
            )
        
        return True


class FallbackManager:
    """回退机制管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化回退管理器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
    
    def handle_insufficient_data(self, date: str, available_data: pd.DataFrame,
                                min_required: int = 100) -> pd.DataFrame:
        """
        处理数据不足的情况
        
        Args:
            date: 交易日期
            available_data: 可用数据
            min_required: 最少需要的数据量
            
        Returns:
            处理后的数据
            
        Raises:
            InsufficientDataError: 数据不足且无法回退
        """
        if available_data is None or available_data.empty:
            raise InsufficientDataError(date, "股票数据", 0, min_required)
        
        data_count = len(available_data)
        
        # 如果数据量严重不足（少于最少要求的50%），抛出异常
        if data_count < min_required * 0.5:
            raise InsufficientDataError(
                date, 
                "股票数据", 
                data_count, 
                min_required
            )
        
        # 如果数据量不足但可以接受，记录警告并继续
        if data_count < min_required:
            self.logger.warning(
                f"日期 {date} 的数据量不足（{data_count}/{min_required}），"
                f"将使用可用数据继续计算"
            )
        
        return available_data
    
    def handle_classification_error(self, stock_code: str, 
                                  error: StockClassificationError) -> str:
        """
        处理股票分类错误
        
        Args:
            stock_code: 股票代码
            error: 分类错误
            
        Returns:
            回退分类结果
        """
        self.logger.warning(f"股票 {stock_code} 分类失败: {error}, 使用默认分类")
        
        # 基于股票代码的简单回退逻辑
        if stock_code.endswith('.SH'):
            if stock_code.startswith('688'):
                return 'star'
            else:
                return 'shanghai'
        elif stock_code.endswith('.SZ'):
            return 'shenzhen'
        elif stock_code.endswith('.BJ'):
            return 'beijing'
        else:
            # 完全未知的代码，使用默认分类
            return 'unknown'
    
    def handle_detection_error(self, stock_code: str, 
                             error: LimitUpDetectionError) -> bool:
        """
        处理涨停检测错误
        
        Args:
            stock_code: 股票代码
            error: 检测错误
            
        Returns:
            回退检测结果（保守估计为False）
        """
        self.logger.warning(f"股票 {stock_code} 涨停检测失败: {error}, 假设未涨停")
        return False
    
    def create_partial_results(self, date: str, successful_data: Dict[str, Any],
                             failed_stocks: List[str]) -> Dict[str, Any]:
        """
        创建部分结果
        
        Args:
            date: 交易日期
            successful_data: 成功处理的数据
            failed_stocks: 失败的股票列表
            
        Returns:
            部分结果字典
        """
        results = successful_data.copy()
        
        # 添加警告信息
        results['warnings'] = {
            'partial_data': True,
            'failed_stocks_count': len(failed_stocks),
            'failed_stocks': failed_stocks[:10],  # 只显示前10个失败的股票
            'message': f"部分股票处理失败，结果可能不完整"
        }
        
        self.logger.warning(
            f"日期 {date} 的涨停统计存在 {len(failed_stocks)} 只股票处理失败，"
            f"返回部分结果"
        )
        
        return results
    
    def get_graceful_degradation_strategy(self, error: Exception) -> Dict[str, Any]:
        """
        获取优雅降级策略
        
        Args:
            error: 发生的错误
            
        Returns:
            降级策略配置
        """
        if isinstance(error, InvalidTradeDateError):
            return {
                'strategy': 'reject',
                'message': '日期验证失败，无法降级',
                'suggestions': error.suggestions
            }
        
        elif isinstance(error, InsufficientDataError):
            return {
                'strategy': 'partial_results',
                'message': '数据不足，返回可用数据的统计结果',
                'min_data_threshold': 0.3  # 至少需要30%的数据
            }
        
        elif isinstance(error, StockClassificationError):
            return {
                'strategy': 'default_classification',
                'message': '使用默认分类策略',
                'default_market': 'unknown'
            }
        
        elif isinstance(error, LimitUpDetectionError):
            return {
                'strategy': 'conservative_detection',
                'message': '使用保守的涨停检测策略',
                'assume_not_limit_up': True
            }
        
        else:
            return {
                'strategy': 'fail_fast',
                'message': '未知错误，快速失败',
                'retry_suggested': True
            }


class ValidationUtils:
    """验证工具类"""
    
    @staticmethod
    def sanitize_stock_code(stock_code: str) -> str:
        """
        清理和标准化股票代码
        
        Args:
            stock_code: 原始股票代码
            
        Returns:
            清理后的股票代码
        """
        if not stock_code:
            return ""
        
        # 移除空白字符
        code = stock_code.strip().upper()
        
        # 移除特殊字符（除了点号）
        code = re.sub(r'[^\w.]', '', code)
        
        return code
    
    @staticmethod
    def validate_market_filter(market_filter: Optional[List[str]]) -> List[str]:
        """
        验证市场过滤器
        
        Args:
            market_filter: 市场过滤器列表
            
        Returns:
            验证后的市场过滤器
        """
        if not market_filter:
            return []
        
        valid_markets = {'shanghai', 'shenzhen', 'star', 'beijing', 'unknown'}
        validated_filter = []
        
        for market in market_filter:
            if isinstance(market, str) and market.lower() in valid_markets:
                validated_filter.append(market.lower())
            else:
                logger.warning(f"无效的市场过滤器: {market}")
        
        return validated_filter
    
    @staticmethod
    def validate_statistics_consistency(stats: Dict[str, int]) -> bool:
        """
        验证统计数据的一致性
        
        Args:
            stats: 统计数据字典
            
        Returns:
            是否一致
        """
        required_keys = ['total', 'non_st', 'st', 'shanghai', 'shenzhen', 'star', 'beijing']
        
        # 检查必要字段
        for key in required_keys:
            if key not in stats:
                logger.error(f"统计数据缺少字段: {key}")
                return False
            
            if not isinstance(stats[key], int) or stats[key] < 0:
                logger.error(f"统计数据字段 {key} 无效: {stats[key]}")
                return False
        
        # 检查数据一致性
        calculated_total = stats['shanghai'] + stats['shenzhen'] + stats['star'] + stats['beijing']
        if calculated_total != stats['total']:
            logger.error(
                f"统计数据不一致: 各市场总和 {calculated_total} != 总计 {stats['total']}"
            )
            return False
        
        calculated_non_st_total = stats['non_st'] + stats['st']
        if calculated_non_st_total != stats['total']:
            logger.error(
                f"统计数据不一致: 非ST + ST {calculated_non_st_total} != 总计 {stats['total']}"
            )
            return False
        
        return True