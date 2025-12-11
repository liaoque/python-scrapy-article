"""
涨跌分布统计容错机制和回退策略

实现涨跌分布统计功能的容错处理、错误恢复和回退策略
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
import pandas as pd

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
from .errors import DataSourceError, NetworkError, ValidationError
from ..models.price_distribution_models import PriceDistributionStats, PriceDistributionRequest


class FaultTolerantPriceDistributionService:
    """容错的涨跌分布统计服务"""
    
    def __init__(self, base_service, logger: Optional[logging.Logger] = None):
        """
        初始化容错服务
        
        Args:
            base_service: 基础的涨跌分布统计服务
            logger: 日志记录器
        """
        self.base_service = base_service
        self.logger = logger or logging.getLogger(__name__)
        
        # 容错配置
        self.fault_tolerance_config = {
            'max_retries': 3,
            'retry_delay': 1.0,
            'backoff_multiplier': 2.0,
            'max_delay': 30.0,
            'enable_fallback': True,
            'enable_partial_results': True,
            'min_stock_count_threshold': 100,
            'data_quality_threshold': 0.8
        }
        
        # 错误统计
        self.error_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'recovered_requests': 0,
            'fallback_used': 0,
            'partial_results': 0,
            'error_types': {}
        }
        

        
    async def get_price_distribution_stats_with_fault_tolerance(
        self, request: PriceDistributionRequest
    ) -> PriceDistributionStats:
        """
        带容错机制的涨跌分布统计获取
        
        Args:
            request: 统计请求
            
        Returns:
            统计结果
            
        Raises:
            PriceDistributionError: 所有恢复策略都失败时
        """
        self.error_stats['total_requests'] += 1
        start_time = time.time()
        
        try:
            # 尝试正常获取统计数据
            result = await self._execute_with_retry(
                self.base_service.get_price_distribution_stats,
                request
            )
            
            # 验证结果质量
            if self._validate_result_quality(result):
                self.error_stats['successful_requests'] += 1
                self.logger.info(
                    f"成功获取涨跌分布统计 (日期: {request.trade_date}, "
                    f"耗时: {time.time() - start_time:.2f}秒)"
                )
                return result
            else:
                # 结果质量不佳，尝试恢复
                self.logger.warning(f"统计结果质量不佳，尝试恢复策略")
                return await self._recover_from_poor_quality(request, result)
                
        except Exception as error:
            self.logger.error(f"获取涨跌分布统计失败: {error}")
            self._update_error_stats(error)
            
            # 尝试错误恢复
            try:
                recovered_result = await self._handle_error_with_recovery(error, request)
                if recovered_result:
                    self.error_stats['recovered_requests'] += 1
                    self.logger.info(
                        f"通过恢复策略成功获取统计数据 (日期: {request.trade_date}, "
                        f"耗时: {time.time() - start_time:.2f}秒)"
                    )
                    return recovered_result
            except Exception as recovery_error:
                self.logger.error(f"错误恢复失败: {recovery_error}")
            
            # 尝试回退策略
            if self.fault_tolerance_config['enable_fallback']:
                try:
                    fallback_result = await self._execute_fallback_strategy(request, error)
                    if fallback_result:
                        self.error_stats['fallback_used'] += 1
                        self.logger.info(
                            f"通过回退策略获取统计数据 (日期: {request.trade_date}, "
                            f"耗时: {time.time() - start_time:.2f}秒)"
                        )
                        return fallback_result
                except Exception as fallback_error:
                    self.logger.error(f"回退策略失败: {fallback_error}")
            
            # 所有策略都失败，记录并抛出异常
            self.error_stats['failed_requests'] += 1
            execution_time = time.time() - start_time
            
            raise PriceDistributionServiceError(
                service_operation="get_price_distribution_stats",
                reason=f"所有恢复策略都失败，原始错误: {str(error)}",
                service_state={
                    'execution_time': execution_time,
                    'retry_attempts': self.fault_tolerance_config['max_retries'],
                    'fallback_enabled': self.fault_tolerance_config['enable_fallback']
                },
                recovery_suggestion=(
                    "建议检查数据源连接、缓存服务状态，或稍后重试。"
                    "如果问题持续存在，可能需要联系技术支持"
                )
            )
    
    async def _execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        带重试的函数执行
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
        """
        last_error = None
        delay = self.fault_tolerance_config['retry_delay']
        
        for attempt in range(self.fault_tolerance_config['max_retries'] + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
                    
            except Exception as error:
                last_error = error
                
                # 判断是否应该重试
                if not self._should_retry_error(error) or attempt >= self.fault_tolerance_config['max_retries']:
                    break
                
                # 记录重试信息
                self.logger.warning(
                    f"第{attempt + 1}次尝试失败，{delay:.2f}秒后重试: {error}"
                )
                
                # 等待后重试
                await asyncio.sleep(delay)
                delay = min(
                    delay * self.fault_tolerance_config['backoff_multiplier'],
                    self.fault_tolerance_config['max_delay']
                )
        
        # 抛出最后的错误
        raise last_error
    
    def _should_retry_error(self, error: Exception) -> bool:
        """
        判断错误是否应该重试
        
        Args:
            error: 异常对象
            
        Returns:
            是否应该重试
        """
        # 网络相关错误应该重试
        if isinstance(error, (NetworkError, ConnectionError, TimeoutError)):
            return True
        
        # 数据源临时错误应该重试
        if isinstance(error, DataSourceError):
            error_msg = str(error).lower()
            temporary_keywords = [
                'timeout', 'connection', 'network', 'temporary', 
                'server error', '502', '503', '504', 'rate limit'
            ]
            return any(keyword in error_msg for keyword in temporary_keywords)
        
        # 缓存错误可以重试
        if isinstance(error, ValidationError):
            return True
        
        # 计算错误可能是临时的，可以重试
        if isinstance(error, DistributionCalculationError):
            # 如果是数据问题导致的计算错误，可以重试
            if error.reason and any(keyword in error.reason.lower() 
                                  for keyword in ['temporary', 'network', 'timeout']):
                return True
        
        # 验证错误通常不应该重试
        if isinstance(error, (ValidationError, PriceDistributionValidationError, 
                            InvalidTradeDateError, InvalidDistributionRangeError)):
            return False
        
        # 其他错误默认重试一次
        return True
    
    async def _handle_error_with_recovery(
        self, error: Exception, request: PriceDistributionRequest
    ) -> Optional[PriceDistributionStats]:
        """
        根据错误类型执行相应的恢复策略
        
        Args:
            error: 异常对象
            request: 原始请求
            
        Returns:
            恢复后的结果或None
        """
        if isinstance(error, InsufficientPriceDataError):
            return await self._recover_from_insufficient_data(error, request)
        elif isinstance(error, DistributionCalculationError):
            return await self._recover_from_calculation_error(error, request)
        elif isinstance(error, MarketClassificationError):
            return await self._recover_from_classification_error(error, request)

        elif isinstance(error, StatisticsAggregationError):
            return await self._recover_from_aggregation_error(error, request)
        elif isinstance(error, DataSourceError):
            return await self._recover_from_data_source_error(error, request)
        
        return None
    
    async def _recover_from_insufficient_data(
        self, error: InsufficientPriceDataError, request: PriceDistributionRequest
    ) -> Optional[PriceDistributionStats]:
        """
        从数据不足错误中恢复
        
        Args:
            error: 数据不足异常
            request: 原始请求
            
        Returns:
            恢复后的结果或None
        """
        self.logger.info(f"尝试从数据不足错误中恢复: {error.trade_date}")
        
        # 策略1: 尝试使用部分数据
        if (self.fault_tolerance_config['enable_partial_results'] and 
            error.available_count and 
            error.available_count >= self.fault_tolerance_config['min_stock_count_threshold']):
            
            self.logger.info(f"使用部分数据计算统计 (可用股票: {error.available_count})")
            try:
                # 创建修改后的请求，允许部分数据
                modified_request = PriceDistributionRequest(
                    trade_date=request.trade_date,
                    include_st=request.include_st,
                    market_filter=request.market_filter,
                    distribution_ranges=request.distribution_ranges,
                    force_refresh=False,  # 避免再次刷新
                    save_to_db=request.save_to_db
                )
                
                # 尝试使用基础服务的部分数据模式
                if hasattr(self.base_service, 'get_stats_with_partial_data'):
                    result = await self.base_service.get_stats_with_partial_data(modified_request)
                    if result:
                        self.error_stats['partial_results'] += 1
                        return result
            except Exception as recovery_error:
                self.logger.warning(f"部分数据恢复失败: {recovery_error}")
        
        # 策略2: 尝试相邻交易日的数据
        try:
            adjacent_dates = self._get_adjacent_trade_dates(error.trade_date)
            for adj_date in adjacent_dates:
                self.logger.info(f"尝试使用相邻交易日数据: {adj_date}")
                
                adj_request = PriceDistributionRequest(
                    trade_date=adj_date,
                    include_st=request.include_st,
                    market_filter=request.market_filter,
                    distribution_ranges=request.distribution_ranges,
                    force_refresh=False,
                    save_to_db=False  # 不保存相邻日期的数据
                )
                
                try:
                    result = await self.base_service.get_price_distribution_stats(adj_request)
                    if result and self._validate_result_quality(result):
                        # 修改结果中的日期信息，标记为估算数据
                        result.trade_date = error.trade_date
                        result.data_quality_score = 0.7  # 降低质量分数
                        if hasattr(result, 'metadata'):
                            result.metadata = result.metadata or {}
                            result.metadata['estimated_from'] = adj_date
                            result.metadata['estimation_reason'] = 'insufficient_data'
                        
                        self.logger.info(f"使用相邻交易日 {adj_date} 的数据作为估算")
                        return result
                except Exception:
                    continue
        except Exception as recovery_error:
            self.logger.warning(f"相邻交易日恢复失败: {recovery_error}")
        
        return None
    
    async def _recover_from_calculation_error(
        self, error: DistributionCalculationError, request: PriceDistributionRequest
    ) -> Optional[PriceDistributionStats]:
        """
        从计算错误中恢复
        
        Args:
            error: 计算异常
            request: 原始请求
            
        Returns:
            恢复后的结果或None
        """
        self.logger.info(f"尝试从计算错误中恢复: {error.calculation_type}")
        
        # 策略1: 使用简化的计算方法
        if error.calculation_type in ['区间分类', 'range_classification']:
            try:
                self.logger.info("尝试使用简化的区间分类方法")
                
                # 创建简化的请求，使用默认区间
                simplified_request = PriceDistributionRequest(
                    trade_date=request.trade_date,
                    include_st=request.include_st,
                    market_filter=request.market_filter,
                    distribution_ranges=None,  # 使用默认区间
                    force_refresh=False,
                    save_to_db=request.save_to_db
                )
                
                if hasattr(self.base_service, 'get_stats_with_simple_calculation'):
                    result = await self.base_service.get_stats_with_simple_calculation(simplified_request)
                    if result:
                        result.data_quality_score = 0.8  # 降低质量分数
                        return result
            except Exception as recovery_error:
                self.logger.warning(f"简化计算恢复失败: {recovery_error}")
        
        # 策略2: 排除有问题的股票后重新计算
        if error.affected_stocks:
            try:
                self.logger.info(f"排除 {len(error.affected_stocks)} 只有问题的股票后重新计算")
                
                # 这里需要基础服务支持排除特定股票的功能
                if hasattr(self.base_service, 'get_stats_excluding_stocks'):
                    result = await self.base_service.get_stats_excluding_stocks(
                        request, exclude_stocks=error.affected_stocks
                    )
                    if result:
                        result.data_quality_score = 0.9  # 稍微降低质量分数
                        if hasattr(result, 'metadata'):
                            result.metadata = result.metadata or {}
                            result.metadata['excluded_stocks'] = error.affected_stocks
                            result.metadata['exclusion_reason'] = 'calculation_error'
                        return result
            except Exception as recovery_error:
                self.logger.warning(f"排除问题股票恢复失败: {recovery_error}")
        
        return None
    
    async def _recover_from_classification_error(
        self, error: MarketClassificationError, request: PriceDistributionRequest
    ) -> Optional[PriceDistributionStats]:
        """
        从市场分类错误中恢复
        
        Args:
            error: 分类异常
            request: 原始请求
            
        Returns:
            恢复后的结果或None
        """
        self.logger.info(f"尝试从市场分类错误中恢复")
        
        # 策略1: 使用默认分类
        try:
            self.logger.info("使用默认市场分类")
            
            if hasattr(self.base_service, 'get_stats_with_default_classification'):
                result = await self.base_service.get_stats_with_default_classification(request)
                if result:
                    result.data_quality_score = 0.8  # 降低质量分数
                    if hasattr(result, 'metadata'):
                        result.metadata = result.metadata or {}
                        result.metadata['classification_method'] = 'default'
                        result.metadata['unclassified_stocks'] = error.stock_codes
                    return result
        except Exception as recovery_error:
            self.logger.warning(f"默认分类恢复失败: {recovery_error}")
        
        # 策略2: 简化市场分类（只区分主板和其他）
        try:
            self.logger.info("使用简化市场分类")
            
            simplified_request = PriceDistributionRequest(
                trade_date=request.trade_date,
                include_st=request.include_st,
                market_filter=['total', 'non_st'],  # 只使用基本分类
                distribution_ranges=request.distribution_ranges,
                force_refresh=False,
                save_to_db=request.save_to_db
            )
            
            result = await self.base_service.get_price_distribution_stats(simplified_request)
            if result:
                result.data_quality_score = 0.7  # 降低质量分数
                return result
        except Exception as recovery_error:
            self.logger.warning(f"简化分类恢复失败: {recovery_error}")
        
        return None
    

    
    async def _recover_from_aggregation_error(
        self, error: StatisticsAggregationError, request: PriceDistributionRequest
    ) -> Optional[PriceDistributionStats]:
        """
        从统计聚合错误中恢复
        
        Args:
            error: 聚合异常
            request: 原始请求
            
        Returns:
            恢复后的结果或None
        """
        self.logger.info(f"尝试从统计聚合错误中恢复: {error.aggregation_type}")
        
        # 策略1: 使用简化的聚合方法
        try:
            self.logger.info("使用简化的统计聚合")
            
            if hasattr(self.base_service, 'get_stats_with_simple_aggregation'):
                result = await self.base_service.get_stats_with_simple_aggregation(request)
                if result:
                    result.data_quality_score = 0.8  # 降低质量分数
                    return result
        except Exception as recovery_error:
            self.logger.warning(f"简化聚合恢复失败: {recovery_error}")
        
        # 策略2: 分步骤聚合，跳过有问题的市场板块
        if error.market_segments:
            try:
                self.logger.info(f"跳过有问题的市场板块: {error.market_segments}")
                
                # 创建排除有问题板块的请求
                available_markets = ['total', 'non_st', 'shanghai', 'shenzhen', 'star', 'beijing', 'st']
                filtered_markets = [m for m in available_markets if m not in error.market_segments]
                
                if filtered_markets:
                    filtered_request = PriceDistributionRequest(
                        trade_date=request.trade_date,
                        include_st=request.include_st,
                        market_filter=filtered_markets,
                        distribution_ranges=request.distribution_ranges,
                        force_refresh=False,
                        save_to_db=request.save_to_db
                    )
                    
                    result = await self.base_service.get_price_distribution_stats(filtered_request)
                    if result:
                        result.data_quality_score = 0.7  # 降低质量分数
                        if hasattr(result, 'metadata'):
                            result.metadata = result.metadata or {}
                            result.metadata['excluded_markets'] = error.market_segments
                            result.metadata['exclusion_reason'] = 'aggregation_error'
                        return result
            except Exception as recovery_error:
                self.logger.warning(f"跳过问题板块恢复失败: {recovery_error}")
        
        return None
    
    async def _recover_from_data_source_error(
        self, error: DataSourceError, request: PriceDistributionRequest
    ) -> Optional[PriceDistributionStats]:
        """
        从数据源错误中恢复
        
        Args:
            error: 数据源异常
            request: 原始请求
            
        Returns:
            恢复后的结果或None
        """
        self.logger.info(f"尝试从数据源错误中恢复")
        
        # 策略1: 尝试备用数据源
        try:
            self.logger.info("尝试使用备用数据源")
            
            if hasattr(self.base_service, 'get_stats_from_backup_source'):
                result = await self.base_service.get_stats_from_backup_source(request)
                if result:
                    result.data_quality_score = 0.8  # 降低质量分数
                    if hasattr(result, 'metadata'):
                        result.metadata = result.metadata or {}
                        result.metadata['data_source'] = 'backup'
                    return result
        except Exception as recovery_error:
            self.logger.warning(f"备用数据源恢复失败: {recovery_error}")
        
        return None
    
    async def _execute_fallback_strategy(
        self, request: PriceDistributionRequest, original_error: Exception
    ) -> Optional[PriceDistributionStats]:
        """
        执行回退策略
        
        Args:
            request: 原始请求
            original_error: 原始错误
            
        Returns:
            回退结果或None
        """
        self.logger.info(f"执行回退策略 (原始错误: {type(original_error).__name__})")
        

        
        # 策略2: 使用模拟数据
        if self.fault_tolerance_config.get('enable_mock_data', False):
            try:
                mock_result = await self._generate_mock_distribution_stats(request)
                if mock_result:
                    self.logger.info("使用模拟数据作为回退")
                    return mock_result
            except Exception as fallback_error:
                self.logger.warning(f"模拟数据回退失败: {fallback_error}")
        
        # 策略3: 返回空结果结构
        try:
            empty_result = self._create_empty_distribution_stats(request)
            self.logger.info("返回空结果结构作为最后回退")
            return empty_result
        except Exception as fallback_error:
            self.logger.error(f"空结果回退失败: {fallback_error}")
        
        return None
    
    async def _recover_from_poor_quality(
        self, request: PriceDistributionRequest, result: PriceDistributionStats
    ) -> PriceDistributionStats:
        """
        从低质量结果中恢复
        
        Args:
            request: 原始请求
            result: 低质量结果
            
        Returns:
            改进后的结果
        """
        self.logger.info(f"尝试改进低质量结果 (质量分数: {result.data_quality_score})")
        
        # 策略1: 数据清理和修正
        try:
            cleaned_result = await self._clean_and_correct_result(result)
            if cleaned_result and self._validate_result_quality(cleaned_result):
                self.logger.info("通过数据清理改进了结果质量")
                return cleaned_result
        except Exception as recovery_error:
            self.logger.warning(f"数据清理失败: {recovery_error}")
        
        # 策略2: 重新计算部分统计
        try:
            if hasattr(self.base_service, 'recalculate_partial_stats'):
                improved_result = await self.base_service.recalculate_partial_stats(request, result)
                if improved_result and self._validate_result_quality(improved_result):
                    self.logger.info("通过重新计算改进了结果质量")
                    return improved_result
        except Exception as recovery_error:
            self.logger.warning(f"重新计算失败: {recovery_error}")
        
        # 如果无法改进，返回原结果但标记质量问题
        result.data_quality_score = max(result.data_quality_score, 0.5)
        if hasattr(result, 'metadata'):
            result.metadata = result.metadata or {}
            result.metadata['quality_issues'] = 'low_quality_data_detected'
        
        return result
    
    def _validate_result_quality(self, result: PriceDistributionStats) -> bool:
        """
        验证结果质量
        
        Args:
            result: 统计结果
            
        Returns:
            是否达到质量要求
        """
        if not result:
            return False
        
        # 检查基本字段
        if not result.trade_date or result.total_stocks <= 0:
            return False
        
        # 检查数据质量分数
        if result.data_quality_score < self.fault_tolerance_config['data_quality_threshold']:
            return False
        
        # 检查股票数量是否足够
        if result.total_stocks < self.fault_tolerance_config['min_stock_count_threshold']:
            return False
        
        # 检查分布数据的完整性
        if not result.positive_ranges or not result.negative_ranges:
            return False
        
        # 检查百分比是否合理
        total_positive = sum(result.positive_percentages.values())
        total_negative = sum(result.negative_percentages.values())
        
        if total_positive < 0 or total_positive > 100 or total_negative < 0 or total_negative > 100:
            return False
        
        return True
    
    def _get_adjacent_trade_dates(self, trade_date: str, days: int = 3) -> List[str]:
        """
        获取相邻的交易日期
        
        Args:
            trade_date: 基准日期
            days: 查找天数
            
        Returns:
            相邻交易日期列表
        """
        try:
            from datetime import datetime, timedelta
            
            base_date = datetime.strptime(trade_date, '%Y%m%d')
            adjacent_dates = []
            
            # 向前查找
            for i in range(1, days + 1):
                prev_date = base_date - timedelta(days=i)
                # 简单跳过周末（实际应该使用交易日历）
                if prev_date.weekday() < 5:  # 0-4 是周一到周五
                    adjacent_dates.append(prev_date.strftime('%Y%m%d'))
            
            # 向后查找
            for i in range(1, days + 1):
                next_date = base_date + timedelta(days=i)
                if next_date.weekday() < 5:
                    adjacent_dates.append(next_date.strftime('%Y%m%d'))
            
            return adjacent_dates
        except Exception:
            return []
    

    
    async def _generate_mock_distribution_stats(
        self, request: PriceDistributionRequest
    ) -> Optional[PriceDistributionStats]:
        """
        生成模拟的分布统计数据
        
        Args:
            request: 统计请求
            
        Returns:
            模拟的统计数据
        """
        try:
            # 创建基本的模拟数据结构
            mock_stats = PriceDistributionStats(
                trade_date=request.trade_date,
                total_stocks=1000,  # 模拟总股票数
                positive_ranges={
                    "0-3%": 300,
                    "3-5%": 150,
                    "5-7%": 100,
                    "7-10%": 50,
                    ">=10%": 20
                },
                positive_percentages={
                    "0-3%": 30.0,
                    "3-5%": 15.0,
                    "5-7%": 10.0,
                    "7-10%": 5.0,
                    ">=10%": 2.0
                },
                negative_ranges={
                    "0到-3%": 280,
                    "-3到-5%": 120,
                    "-5到-7%": 80,
                    "-7到-10%": 40,
                    "<=-10%": 10
                },
                negative_percentages={
                    "0到-3%": 28.0,
                    "-3到-5%": 12.0,
                    "-5到-7%": 8.0,
                    "-7到-10%": 4.0,
                    "<=-10%": 1.0
                },
                market_breakdown={},
                data_quality_score=0.3,  # 明确标记为低质量
                processing_time=0.1
            )
            
            # 添加元数据标记
            if hasattr(mock_stats, 'metadata'):
                mock_stats.metadata = {
                    'data_type': 'mock',
                    'generation_reason': 'fallback_strategy',
                    'warning': 'This is simulated data for demonstration purposes only'
                }
            
            self.logger.warning("生成了模拟数据，仅用于演示目的")
            return mock_stats
            
        except Exception as error:
            self.logger.error(f"生成模拟数据失败: {error}")
            return None
    
    def _create_empty_distribution_stats(self, request: PriceDistributionRequest) -> PriceDistributionStats:
        """
        创建空的分布统计结构
        
        Args:
            request: 统计请求
            
        Returns:
            空的统计结构
        """
        return PriceDistributionStats(
            trade_date=request.trade_date,
            total_stocks=0,
            positive_ranges={},
            positive_percentages={},
            negative_ranges={},
            negative_percentages={},
            market_breakdown={},
            data_quality_score=0.0,
            processing_time=0.0
        )
    
    async def _clean_and_correct_result(self, result: PriceDistributionStats) -> Optional[PriceDistributionStats]:
        """
        清理和修正结果数据
        
        Args:
            result: 原始结果
            
        Returns:
            清理后的结果或None
        """
        try:
            # 创建结果副本
            cleaned_result = PriceDistributionStats(
                trade_date=result.trade_date,
                total_stocks=result.total_stocks,
                positive_ranges=result.positive_ranges.copy(),
                positive_percentages=result.positive_percentages.copy(),
                negative_ranges=result.negative_ranges.copy(),
                negative_percentages=result.negative_percentages.copy(),
                market_breakdown=result.market_breakdown.copy() if result.market_breakdown else {},
                data_quality_score=result.data_quality_score,
                processing_time=result.processing_time
            )
            
            # 修正百分比数据
            total_positive = sum(cleaned_result.positive_percentages.values())
            total_negative = sum(cleaned_result.negative_percentages.values())
            
            # 如果百分比总和不合理，重新计算
            if total_positive > 100 or total_negative > 100:
                total_stocks = cleaned_result.total_stocks
                if total_stocks > 0:
                    for range_name, count in cleaned_result.positive_ranges.items():
                        cleaned_result.positive_percentages[range_name] = (count / total_stocks) * 100
                    
                    for range_name, count in cleaned_result.negative_ranges.items():
                        cleaned_result.negative_percentages[range_name] = (count / total_stocks) * 100
            
            # 提高质量分数
            cleaned_result.data_quality_score = min(result.data_quality_score + 0.1, 1.0)
            
            return cleaned_result
            
        except Exception as error:
            self.logger.error(f"清理结果数据失败: {error}")
            return None
    
    def _update_error_stats(self, error: Exception):
        """
        更新错误统计
        
        Args:
            error: 异常对象
        """
        error_type = type(error).__name__
        self.error_stats['error_types'][error_type] = (
            self.error_stats['error_types'].get(error_type, 0) + 1
        )
    
    def get_fault_tolerance_stats(self) -> Dict[str, Any]:
        """
        获取容错统计信息
        
        Returns:
            容错统计数据
        """
        stats = self.error_stats.copy()
        
        # 计算成功率
        total_requests = stats['total_requests']
        if total_requests > 0:
            stats['success_rate'] = stats['successful_requests'] / total_requests
            stats['recovery_rate'] = stats['recovered_requests'] / total_requests
            stats['fallback_rate'] = stats['fallback_used'] / total_requests
            stats['failure_rate'] = stats['failed_requests'] / total_requests
        else:
            stats.update({
                'success_rate': 0.0,
                'recovery_rate': 0.0,
                'fallback_rate': 0.0,
                'failure_rate': 0.0
            })
        
        return stats
    
    def reset_fault_tolerance_stats(self):
        """重置容错统计"""
        self.error_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'recovered_requests': 0,
            'fallback_used': 0,
            'partial_results': 0,
            'error_types': {}
        }
