"""
涨跌分布统计服务

作为核心业务服务，集成现有的 DataManager 和 StockClassifier，
实时获取股票数据并进行市场分类，提供完整的统计分析流程
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd

from ..core.data_manager import DataManager
from ..core.errors import ValidationError, DataSourceError
from ..core.price_distribution_errors import (
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
from ..core.price_distribution_fault_tolerance import FaultTolerantPriceDistributionService
from ..models import DataRequest
from ..models.price_distribution_models import (
    PriceDistributionRequest, 
    PriceDistributionStats, 
    DistributionRange
)
from ..utils.stock_classifier import StockCodeClassifier, ClassificationResult
from ..utils.price_distribution_analyzer import PriceDistributionAnalyzer
from ..utils.price_distribution_performance import (
    PriceDistributionPerformanceOptimizer,
    PriceDistributionPerformanceConfig
)
from ..utils.performance_monitor import get_performance_monitor


# 使用新的异常类，保持向后兼容
PriceDistributionStatsError = PriceDistributionServiceError
InsufficientDataError = InsufficientPriceDataError


class PriceDistributionStatsService:
    """
    涨跌分布统计服务
    
    作为核心业务服务，集成现有的 DataManager 和 StockClassifier，
    实时获取股票数据并进行市场分类，提供完整的统计分析流程
    """
    
    def __init__(self, data_manager: DataManager, logger: Optional[logging.Logger] = None):
        """
        初始化涨跌分布统计服务
        
        Args:
            data_manager: 数据管理器
            logger: 日志记录器
        """
        self.data_manager = data_manager
        self.logger = logger or logging.getLogger(__name__)
        
        # 初始化组件
        self.stock_classifier = StockCodeClassifier(enable_fallback=True, logger=self.logger)
        
        # 服务配置
        self.config = {
            'min_stock_count': getattr(data_manager.config, 'min_stock_count_for_distribution', 100),
            'max_processing_time': getattr(data_manager.config, 'max_distribution_processing_time', 60),
            'enable_fallback_classification': getattr(data_manager.config, 'enable_fallback_classification', True),
            'parallel_processing': getattr(data_manager.config, 'parallel_processing_enabled', True)
        }
        
        # 性能统计
        self._performance_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_processing_time': 0.0,
            'total_processing_time': 0.0
        }
        
        # 初始化性能优化器
        performance_config = PriceDistributionPerformanceConfig(
            enable_vectorization=getattr(data_manager.config, 'enable_vectorization', True),
            enable_parallel_processing=getattr(data_manager.config, 'enable_parallel_processing', True),
            enable_memory_optimization=getattr(data_manager.config, 'enable_memory_optimization', True),
            enable_performance_monitoring=getattr(data_manager.config, 'enable_performance_monitoring', True),
            max_workers=getattr(data_manager.config, 'max_workers', None),
            batch_size=getattr(data_manager.config, 'batch_size', 1000),
            chunk_size=getattr(data_manager.config, 'chunk_size', 500),
            use_multiprocessing=getattr(data_manager.config, 'use_multiprocessing', False),
            memory_limit_mb=getattr(data_manager.config, 'memory_limit_mb', 2048),
            enable_dataframe_optimization=getattr(data_manager.config, 'enable_dataframe_optimization', True),
            enable_garbage_collection=getattr(data_manager.config, 'enable_garbage_collection', True),
            gc_frequency=getattr(data_manager.config, 'gc_frequency', 10),
            enable_intermediate_caching=getattr(data_manager.config, 'enable_intermediate_caching', True),
            enable_detailed_metrics=getattr(data_manager.config, 'enable_detailed_metrics', True),
            metrics_history_size=getattr(data_manager.config, 'metrics_history_size', 10000),
            performance_report_interval=getattr(data_manager.config, 'performance_report_interval', 100)
        )
        
        self.performance_optimizer = PriceDistributionPerformanceOptimizer(
            performance_config, self.logger
        )
        
        # 性能监控器
        self.performance_monitor = get_performance_monitor() if performance_config.enable_performance_monitoring else None
        
        # 初始化分析器，传入性能优化器
        self.analyzer = PriceDistributionAnalyzer(
            performance_optimizer=self.performance_optimizer,
            logger=self.logger
        )
        
        # 初始化容错服务包装器
        self._fault_tolerant_service = None
        if getattr(data_manager.config, 'enable_fault_tolerance', True):
            self._fault_tolerant_service = FaultTolerantPriceDistributionService(
                base_service=self,
                logger=self.logger
            )
    
    async def get_price_distribution_stats_with_fault_tolerance(self, request: PriceDistributionRequest) -> PriceDistributionStats:
        """
        获取涨跌分布统计（带容错机制）
        
        Args:
            request: 分布统计请求
            
        Returns:
            涨跌分布统计结果
            
        Raises:
            PriceDistributionServiceError: 所有恢复策略都失败时
        """
        if self._fault_tolerant_service:
            return await self._fault_tolerant_service.get_price_distribution_stats_with_fault_tolerance(request)
        else:
            return await self.get_price_distribution_stats(request)
    
    async def get_price_distribution_stats(self, request: PriceDistributionRequest) -> PriceDistributionStats:
        """
        获取涨跌分布统计
        
        Args:
            request: 分布统计请求
            
        Returns:
            涨跌分布统计结果
            
        Raises:
            PriceDistributionStatsError: 统计过程中发生错误
        """
        start_time = time.time()
        self._performance_stats['total_requests'] += 1
        
        try:
            # 1. 验证和处理请求参数
            validated_request = self._validate_and_process_request(request)
            
            # 2. 获取股票数据
            self.logger.info(f"Fetching stock data for {validated_request.trade_date}")
            stock_data = await self._fetch_stock_data(validated_request.trade_date)
            
            # 3. 验证数据充足性
            self._validate_data_sufficiency(stock_data, validated_request.trade_date)
            
            # 4. 按市场分类股票
            self.logger.info(f"Classifying {len(stock_data)} stocks by market")
            classified_data = await self._classify_stocks_by_market(stock_data)
            
            # 5. 执行完整的分布分析（使用性能优化）
            self.logger.info(f"Performing distribution analysis for {validated_request.trade_date}")
            if self.performance_optimizer:
                stats = await self.analyzer.analyze_complete_distribution_with_performance_optimization(
                    validated_request, stock_data, classified_data
                )
            else:
                stats = await self.analyzer.analyze_complete_distribution(
                    validated_request, stock_data, classified_data
                )
            
            # 6. 更新性能统计
            processing_time = time.time() - start_time
            self._update_performance_stats(processing_time, success=True)
            
            self.logger.info(f"Distribution stats completed for {validated_request.trade_date} in {processing_time:.3f}s")
            return stats
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_performance_stats(processing_time, success=False)
            
            if isinstance(e, (PriceDistributionStatsError, ValidationError)):
                raise
            else:
                raise PriceDistributionStatsError(
                    f"Failed to get distribution stats for {request.trade_date}: {str(e)}",
                    {
                        'trade_date': request.trade_date,
                        'processing_time': processing_time,
                        'error_type': type(e).__name__
                    }
                )
    
    async def _fetch_stock_data(self, trade_date: str) -> pd.DataFrame:
        """
        实时获取股票数据
        
        Args:
            trade_date: 交易日期
            
        Returns:
            股票数据DataFrame
            
        Raises:
            DataSourceError: 数据获取失败
        """
        try:
            # 使用数据管理器的协调获取方法
            stock_data = await self.data_manager.get_stock_data_with_coordination(
                trade_date, timeout=30
            )
            
            if stock_data.empty:
                raise DataSourceError(f"No stock data available for {trade_date}")
            
            # 验证必需列
            required_columns = ['ts_code', 'pct_chg']
            missing_columns = [col for col in required_columns if col not in stock_data.columns]
            if missing_columns:
                raise DataSourceError(f"Missing required columns in stock data: {missing_columns}")
            
            # 数据清洗
            stock_data = self._clean_stock_data(stock_data)
            
            self.logger.info(f"Fetched {len(stock_data)} stocks for {trade_date}")
            return stock_data
            
        except Exception as e:
            if isinstance(e, DataSourceError):
                raise
            else:
                raise DataSourceError(f"Failed to fetch stock data for {trade_date}: {str(e)}")
    
    async def _classify_stocks_by_market(self, stock_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        按市场分类股票
        
        Args:
            stock_data: 股票数据
            
        Returns:
            按市场分类的股票数据字典
            
        Raises:
            MarketClassificationError: 市场分类失败
        """
        try:
            # 执行分类
            classified_data = {}
            failed_stocks = []
            
            # 准备股票信息列表
            stocks_info = []
            for _, row in stock_data.iterrows():
                stocks_info.append({
                    'ts_code': row['ts_code'],
                    'name': row.get('name', '')
                })
            
            # 批量分类
            classification_results = self.stock_classifier.batch_classify(stocks_info)
            
            # 创建分类映射
            classification_map = {}
            for result in classification_results:
                if result.confidence > 0:
                    classification_map[result.ts_code] = {
                        'market': result.market,
                        'is_st': result.is_st,
                        'confidence': result.confidence
                    }
                else:
                    failed_stocks.append(result.ts_code)
            
            # 如果失败的股票太多，抛出异常
            if len(failed_stocks) > len(stock_data) * 0.1:  # 超过10%失败
                raise MarketClassificationError(
                    f"Too many stocks failed classification: {len(failed_stocks)}/{len(stock_data)}",
                    failed_stocks
                )
            
            # 按市场分组数据
            market_groups = {
                'total': stock_data.copy(),
                'shanghai': pd.DataFrame(),
                'shenzhen': pd.DataFrame(),
                'star': pd.DataFrame(),
                'beijing': pd.DataFrame(),
                'st': pd.DataFrame(),
                'non_st': pd.DataFrame()
            }
            
            # 分类股票数据
            for _, row in stock_data.iterrows():
                ts_code = row['ts_code']
                
                if ts_code in classification_map:
                    classification = classification_map[ts_code]
                    market = classification['market']
                    is_st = classification['is_st']
                    
                    # 添加到对应市场
                    if market in market_groups:
                        market_groups[market] = pd.concat([market_groups[market], row.to_frame().T], ignore_index=True)
                    
                    # 添加到ST/非ST分组
                    if is_st:
                        market_groups['st'] = pd.concat([market_groups['st'], row.to_frame().T], ignore_index=True)
                    else:
                        market_groups['non_st'] = pd.concat([market_groups['non_st'], row.to_frame().T], ignore_index=True)
            
            # 移除空的市场组
            classified_data = {k: v for k, v in market_groups.items() if not v.empty}
            
            self.logger.info(f"Market classification completed: {len(classified_data)} markets, "
                           f"{len(failed_stocks)} failed stocks")
            
            return classified_data
            
        except Exception as e:
            if isinstance(e, MarketClassificationError):
                raise
            else:
                raise MarketClassificationError(f"Market classification failed: {str(e)}")
    
    def _validate_and_process_request(self, request: PriceDistributionRequest) -> PriceDistributionRequest:
        """
        验证和处理请求参数
        
        Args:
            request: 原始请求
            
        Returns:
            验证后的请求
            
        Raises:
            ValidationError: 参数验证失败
        """
        try:
            # 使用请求对象的内置验证
            request.validate()
            
            # 额外的业务逻辑验证
            if request.timeout > self.config['max_processing_time']:
                self.logger.warning(f"Request timeout {request.timeout}s exceeds max processing time "
                                  f"{self.config['max_processing_time']}s, adjusting")
                request.timeout = self.config['max_processing_time']
            
            return request
            
        except Exception as e:
            raise ValidationError(f"Request validation failed: {str(e)}")
    
    def _validate_data_sufficiency(self, stock_data: pd.DataFrame, trade_date: str):
        """
        验证数据充足性
        
        Args:
            stock_data: 股票数据
            trade_date: 交易日期
            
        Raises:
            InsufficientDataError: 数据不足
        """
        if stock_data.empty:
            raise InsufficientDataError(trade_date, 0, self.config['min_stock_count'])
        
        # 检查有效涨跌幅数据
        valid_pct_chg = stock_data['pct_chg'].notna().sum()
        if valid_pct_chg < self.config['min_stock_count']:
            raise InsufficientDataError(trade_date, valid_pct_chg, self.config['min_stock_count'])
    
    def _clean_stock_data(self, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        清洗股票数据
        
        Args:
            stock_data: 原始股票数据
            
        Returns:
            清洗后的股票数据
        """
        # 创建副本避免修改原数据
        cleaned_data = stock_data.copy()
        
        # 移除涨跌幅为空的记录
        cleaned_data = cleaned_data.dropna(subset=['pct_chg'])
        
        # 移除异常的涨跌幅数据（超过±50%的可能是数据错误）
        cleaned_data = cleaned_data[
            (cleaned_data['pct_chg'] >= -50) & 
            (cleaned_data['pct_chg'] <= 50)
        ]
        
        # 确保股票名称列存在
        if 'name' not in cleaned_data.columns:
            cleaned_data['name'] = '未知'
        
        # 填充空的股票名称
        cleaned_data['name'] = cleaned_data['name'].fillna('未知')
        
        return cleaned_data
    
    def _update_performance_stats(self, processing_time: float, success: bool = True):
        """
        更新性能统计
        
        Args:
            processing_time: 处理时间
            success: 是否成功
        """
        if success:
            self._performance_stats['successful_requests'] += 1
        else:
            self._performance_stats['failed_requests'] += 1
        
        self._performance_stats['total_processing_time'] += processing_time
        if self._performance_stats['total_requests'] > 0:
            self._performance_stats['average_processing_time'] = (
                self._performance_stats['total_processing_time'] / 
                self._performance_stats['total_requests']
            )
    
    # ========== 容错恢复方法 ==========
    
    async def get_stats_with_partial_data(self, request: PriceDistributionRequest) -> Optional[PriceDistributionStats]:
        """
        使用部分数据计算统计（容错恢复方法）
        
        Args:
            request: 统计请求
            
        Returns:
            基于部分数据的统计结果
        """
        try:
            # 降低最小股票数量要求
            original_min_count = self.config['min_stock_count']
            self.config['min_stock_count'] = max(50, original_min_count // 2)
            
            try:
                result = await self.get_price_distribution_stats(request)
                if result:
                    result.data_quality_score = min(result.data_quality_score, 0.7)
                return result
            finally:
                # 恢复原始配置
                self.config['min_stock_count'] = original_min_count
                
        except Exception as e:
            self.logger.warning(f"Partial data recovery failed: {e}")
            return None
    
    async def get_stats_with_simple_calculation(self, request: PriceDistributionRequest) -> Optional[PriceDistributionStats]:
        """
        使用简化计算方法（容错恢复方法）
        
        Args:
            request: 统计请求
            
        Returns:
            简化计算的统计结果
        """
        try:
            # 使用默认区间，跳过复杂的自定义区间
            simplified_request = PriceDistributionRequest(
                trade_date=request.trade_date,
                include_st=request.include_st,
                market_filter=['total', 'non_st'],  # 只使用基本分类
                distribution_ranges=None,  # 使用默认区间
                force_refresh=request.force_refresh,
                save_to_db=False  # 不保存简化结果
            )
            
            result = await self.get_price_distribution_stats(simplified_request)
            if result:
                result.data_quality_score = min(result.data_quality_score, 0.8)
            return result
            
        except Exception as e:
            self.logger.warning(f"Simple calculation recovery failed: {e}")
            return None
    
    async def get_stats_excluding_stocks(self, request: PriceDistributionRequest, 
                                       exclude_stocks: List[str]) -> Optional[PriceDistributionStats]:
        """
        排除特定股票后计算统计（容错恢复方法）
        
        Args:
            request: 统计请求
            exclude_stocks: 要排除的股票代码列表
            
        Returns:
            排除问题股票后的统计结果
        """
        try:
            # 获取股票数据
            stock_data = await self._fetch_stock_data(request.trade_date)
            
            # 排除问题股票
            filtered_data = stock_data[~stock_data['ts_code'].isin(exclude_stocks)]
            
            if len(filtered_data) < self.config['min_stock_count']:
                self.logger.warning(f"Too few stocks after exclusion: {len(filtered_data)}")
                return None
            
            # 验证数据充足性
            self._validate_data_sufficiency(filtered_data, request.trade_date)
            
            # 按市场分类
            classified_data = await self._classify_stocks_by_market(filtered_data)
            
            # 执行分析
            stats = await self.analyzer.analyze_complete_distribution(
                request, filtered_data, classified_data
            )
            
            if stats:
                stats.data_quality_score = min(stats.data_quality_score, 0.9)
                # 添加元数据
                if hasattr(stats, 'metadata'):
                    stats.metadata = stats.metadata or {}
                    stats.metadata['excluded_stocks'] = exclude_stocks
                    stats.metadata['exclusion_reason'] = 'error_recovery'
            
            return stats
            
        except Exception as e:
            self.logger.warning(f"Exclude stocks recovery failed: {e}")
            return None
    
    async def get_stats_with_default_classification(self, request: PriceDistributionRequest) -> Optional[PriceDistributionStats]:
        """
        使用默认分类计算统计（容错恢复方法）
        
        Args:
            request: 统计请求
            
        Returns:
            使用默认分类的统计结果
        """
        try:
            # 获取股票数据
            stock_data = await self._fetch_stock_data(request.trade_date)
            
            # 使用简单的默认分类
            default_classified_data = {
                'total': stock_data.copy(),
                'non_st': stock_data[~stock_data['ts_code'].str.contains('ST', na=False)].copy()
            }
            
            # 执行分析
            stats = await self.analyzer.analyze_complete_distribution(
                request, stock_data, default_classified_data
            )
            
            if stats:
                stats.data_quality_score = min(stats.data_quality_score, 0.8)
                # 添加元数据
                if hasattr(stats, 'metadata'):
                    stats.metadata = stats.metadata or {}
                    stats.metadata['classification_method'] = 'default'
            
            return stats
            
        except Exception as e:
            self.logger.warning(f"Default classification recovery failed: {e}")
            return None
    

    
    async def get_stats_with_simple_aggregation(self, request: PriceDistributionRequest) -> Optional[PriceDistributionStats]:
        """
        使用简化聚合计算统计（容错恢复方法）
        
        Args:
            request: 统计请求
            
        Returns:
            简化聚合的统计结果
        """
        try:
            # 只使用基本的市场分类
            simplified_request = PriceDistributionRequest(
                trade_date=request.trade_date,
                include_st=request.include_st,
                market_filter=['total'],  # 只计算总体统计
                distribution_ranges=request.distribution_ranges,
                force_refresh=request.force_refresh,
                save_to_db=False
            )
            
            result = await self.get_price_distribution_stats(simplified_request)
            if result:
                result.data_quality_score = min(result.data_quality_score, 0.8)
            return result
            
        except Exception as e:
            self.logger.warning(f"Simple aggregation recovery failed: {e}")
            return None
    
    async def get_stats_from_backup_source(self, request: PriceDistributionRequest) -> Optional[PriceDistributionStats]:
        """
        从备用数据源获取统计（容错恢复方法）
        
        Args:
            request: 统计请求
            
        Returns:
            备用数据源的统计结果
        """
        try:
            # 尝试使用数据管理器的备用数据源
            if hasattr(self.data_manager, 'get_stock_data_from_backup'):
                backup_data = await self.data_manager.get_stock_data_from_backup(request.trade_date)
                
                if backup_data is not None and not backup_data.empty:
                    # 清洗备用数据
                    cleaned_data = self._clean_stock_data(backup_data)
                    
                    # 验证数据充足性
                    self._validate_data_sufficiency(cleaned_data, request.trade_date)
                    
                    # 使用默认分类
                    default_classified_data = {
                        'total': cleaned_data.copy(),
                        'non_st': cleaned_data[~cleaned_data['ts_code'].str.contains('ST', na=False)].copy()
                    }
                    
                    # 执行分析
                    stats = await self.analyzer.analyze_complete_distribution(
                        request, cleaned_data, default_classified_data
                    )
                    
                    if stats:
                        stats.data_quality_score = min(stats.data_quality_score, 0.8)
                        # 添加元数据
                        if hasattr(stats, 'metadata'):
                            stats.metadata = stats.metadata or {}
                            stats.metadata['data_source'] = 'backup'
                    
                    return stats
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Backup source recovery failed: {e}")
            return None
    
    async def recalculate_partial_stats(self, request: PriceDistributionRequest, 
                                      original_stats: PriceDistributionStats) -> Optional[PriceDistributionStats]:
        """
        重新计算部分统计以改进质量（容错恢复方法）
        
        Args:
            request: 统计请求
            original_stats: 原始统计结果
            
        Returns:
            改进后的统计结果
        """
        try:
            # 如果原始结果的股票数量太少，尝试重新获取数据
            if original_stats.total_stocks < self.config['min_stock_count']:
                return await self.get_stats_with_partial_data(request)
            
            # 如果只是质量分数低，尝试重新计算百分比
            if original_stats.data_quality_score < 0.8:
                # 重新计算百分比确保一致性
                total_positive = sum(original_stats.positive_ranges.values())
                total_negative = sum(original_stats.negative_ranges.values())
                total_stocks = original_stats.total_stocks
                
                if total_stocks > 0:
                    # 重新计算百分比
                    for range_name, count in original_stats.positive_ranges.items():
                        original_stats.positive_percentages[range_name] = (count / total_stocks) * 100
                    
                    for range_name, count in original_stats.negative_ranges.items():
                        original_stats.negative_percentages[range_name] = (count / total_stocks) * 100
                    
                    # 提高质量分数
                    original_stats.data_quality_score = min(original_stats.data_quality_score + 0.1, 1.0)
            
            return original_stats
            
        except Exception as e:
            self.logger.warning(f"Partial recalculation failed: {e}")
            return original_stats
    
    def get_fault_tolerance_stats(self) -> Dict[str, Any]:
        """
        获取容错统计信息
        
        Returns:
            容错统计数据
        """
        if self._fault_tolerant_service:
            return self._fault_tolerant_service.get_fault_tolerance_stats()
        else:
            return {
                'fault_tolerance_enabled': False,
                'message': 'Fault tolerance is disabled'
            }
    
    def reset_fault_tolerance_stats(self):
        """重置容错统计"""
        if self._fault_tolerant_service:
            self._fault_tolerant_service.reset_fault_tolerance_stats()
    
    # ========== 服务管理接口 ==========
    
    def get_service_stats(self) -> Dict[str, Any]:
        """
        获取服务统计信息
        
        Returns:
            服务统计信息
        """
        return {
            'performance': self._performance_stats.copy(),
            'analyzer': self.analyzer.get_performance_stats(),
            'classifier': {
                'market_rules': len(self.stock_classifier.get_market_rules()),
                'st_patterns': len(self.stock_classifier.get_st_patterns()),
                'fallback_enabled': self.stock_classifier.enable_fallback
            },
            'config': self.config.copy(),
            'data_manager': {
                'memory_stats': self.data_manager.get_memory_stats(),
                'provider_health': self.data_manager.get_data_source_health()
            }
        }
    
    def reset_performance_stats(self):
        """重置性能统计"""
        self._performance_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_processing_time': 0.0,
            'total_processing_time': 0.0
        }
        
        self.analyzer.reset_performance_stats()
        self.logger.info("Performance statistics reset")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康检查结果
        """
        health_result = {
            'service': 'PriceDistributionStatsService',
            'status': 'healthy',
            'timestamp': time.time(),
            'checks': {},
            'issues': []
        }
        
        try:
            # 检查数据管理器
            data_manager_health = self.data_manager.get_data_source_health()
            health_result['checks']['data_manager'] = {
                'status': 'healthy' if data_manager_health else 'unhealthy',
                'details': data_manager_health
            }
            
            # 检查股票分类器
            classifier_validation = self.stock_classifier.validate_classification_rules()
            health_result['checks']['stock_classifier'] = {
                'status': 'healthy' if classifier_validation['is_valid'] else 'unhealthy',
                'details': classifier_validation
            }
            
            if not classifier_validation['is_valid']:
                health_result['issues'].extend(classifier_validation['issues'])
            
            # 检查分析器
            health_result['checks']['analyzer'] = {
                'status': 'healthy',
                'details': self.analyzer.get_performance_stats()
            }
            
            # 综合状态判断
            unhealthy_checks = [
                check for check in health_result['checks'].values() 
                if check['status'] != 'healthy'
            ]
            
            if unhealthy_checks:
                health_result['status'] = 'unhealthy'
                health_result['issues'].append(f"{len(unhealthy_checks)} components are unhealthy")
            
        except Exception as e:
            health_result['status'] = 'error'
            health_result['issues'].append(f"Health check failed: {str(e)}")
        
        return health_result
    
    async def validate_service_configuration(self) -> Dict[str, Any]:
        """
        验证服务配置
        
        Returns:
            配置验证结果
        """
        validation_result = {
            'is_valid': True,
            'issues': [],
            'warnings': [],
            'config_checks': {}
        }
        
        try:
            # 检查配置参数
            config_checks = {
                'min_stock_count': self.config['min_stock_count'] > 0,
                'max_processing_time': self.config['max_processing_time'] > 0,
                'parallel_processing': isinstance(self.config['parallel_processing'], bool)
            }
            
            validation_result['config_checks'] = config_checks
            
            # 检查失败的配置
            failed_checks = [k for k, v in config_checks.items() if not v]
            if failed_checks:
                validation_result['is_valid'] = False
                validation_result['issues'].extend([f"Invalid config: {check}" for check in failed_checks])
            
            # 检查数据管理器配置
            if not hasattr(self.data_manager, 'config'):
                validation_result['issues'].append("DataManager missing config")
                validation_result['is_valid'] = False
            
            # 性能警告
            if self.config['max_processing_time'] > 300:  # 5分钟
                validation_result['warnings'].append("Max processing time is very high (>5min)")
            
            if self.config['min_stock_count'] < 50:
                validation_result['warnings'].append("Min stock count is very low (<50)")
            
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['issues'].append(f"Configuration validation failed: {str(e)}")
        
        return validation_result
    
    def get_performance_optimization_stats(self) -> Dict[str, Any]:
        """
        获取性能优化统计信息
        
        Returns:
            性能优化统计字典
        """
        stats = {
            'service_stats': self._performance_stats.copy(),
            'performance_optimizer_available': self.performance_optimizer is not None,
            'performance_monitor_available': self.performance_monitor is not None
        }
        
        # 添加性能优化器统计
        if self.performance_optimizer:
            stats['optimizer_stats'] = self.performance_optimizer.get_performance_stats()
        
        # 添加性能监控器统计
        if self.performance_monitor:
            stats['monitor_stats'] = self.performance_monitor.get_performance_summary()
        
        # 添加分析器统计
        stats['analyzer_stats'] = self.analyzer.get_performance_optimization_stats()
        
        return stats
    
    def configure_performance_optimization(self, config_updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        配置性能优化参数
        
        Args:
            config_updates: 配置更新字典
            
        Returns:
            配置结果
        """
        result = {
            'success': True,
            'updated_configs': [],
            'errors': []
        }
        
        try:
            if self.performance_optimizer:
                # 更新性能优化器配置
                current_config = self.performance_optimizer.config
                
                for key, value in config_updates.items():
                    if hasattr(current_config, key):
                        old_value = getattr(current_config, key)
                        setattr(current_config, key, value)
                        result['updated_configs'].append({
                            'parameter': key,
                            'old_value': old_value,
                            'new_value': value
                        })
                        self.logger.info(f"Updated performance config {key}: {old_value} -> {value}")
                    else:
                        result['errors'].append(f"Unknown configuration parameter: {key}")
            
            else:
                result['success'] = False
                result['errors'].append("Performance optimizer not available")
        
        except Exception as e:
            result['success'] = False
            result['errors'].append(f"Configuration update failed: {str(e)}")
            self.logger.error(f"Performance configuration update failed: {e}")
        
        return result
    
    async def benchmark_performance(self, test_data_size: int = 1000, 
                                  iterations: int = 3) -> Dict[str, Any]:
        """
        性能基准测试
        
        Args:
            test_data_size: 测试数据大小
            iterations: 测试迭代次数
            
        Returns:
            基准测试结果
        """
        import numpy as np
        
        benchmark_result = {
            'test_config': {
                'data_size': test_data_size,
                'iterations': iterations,
                'timestamp': time.time()
            },
            'results': {
                'with_optimization': [],
                'without_optimization': []
            },
            'summary': {}
        }
        
        try:
            # 生成测试数据
            test_data = pd.DataFrame({
                'ts_code': [f'{i:06d}.SZ' for i in range(test_data_size)],
                'name': [f'股票{i}' for i in range(test_data_size)],
                'close': np.random.uniform(5, 100, test_data_size),
                'pre_close': np.random.uniform(5, 100, test_data_size),
                'pct_chg': np.random.uniform(-10, 10, test_data_size)
            })
            
            ranges = self.analyzer.default_ranges
            
            # 测试优化版本
            if self.performance_optimizer:
                for i in range(iterations):
                    start_time = time.time()
                    await self.analyzer.analyze_distribution_with_performance_optimization(
                        test_data, ranges, f"benchmark_optimized_{i}"
                    )
                    processing_time = time.time() - start_time
                    benchmark_result['results']['with_optimization'].append(processing_time)
            
            # 测试标准版本（临时禁用优化器）
            original_optimizer = self.analyzer.performance_optimizer
            self.analyzer.performance_optimizer = None
            
            try:
                for i in range(iterations):
                    start_time = time.time()
                    await self.analyzer.analyze_distribution(test_data, ranges)
                    processing_time = time.time() - start_time
                    benchmark_result['results']['without_optimization'].append(processing_time)
            finally:
                # 恢复优化器
                self.analyzer.performance_optimizer = original_optimizer
            
            # 计算统计摘要
            if benchmark_result['results']['with_optimization']:
                optimized_times = benchmark_result['results']['with_optimization']
                benchmark_result['summary']['optimized'] = {
                    'mean': np.mean(optimized_times),
                    'std': np.std(optimized_times),
                    'min': np.min(optimized_times),
                    'max': np.max(optimized_times)
                }
            
            if benchmark_result['results']['without_optimization']:
                standard_times = benchmark_result['results']['without_optimization']
                benchmark_result['summary']['standard'] = {
                    'mean': np.mean(standard_times),
                    'std': np.std(standard_times),
                    'min': np.min(standard_times),
                    'max': np.max(standard_times)
                }
                
                # 计算性能提升
                if benchmark_result['results']['with_optimization']:
                    optimized_mean = benchmark_result['summary']['optimized']['mean']
                    standard_mean = benchmark_result['summary']['standard']['mean']
                    
                    speedup = standard_mean / optimized_mean if optimized_mean > 0 else 0
                    improvement_pct = (standard_mean - optimized_mean) / standard_mean * 100 if standard_mean > 0 else 0
                    
                    benchmark_result['summary']['performance_improvement'] = {
                        'speedup_factor': speedup,
                        'improvement_percentage': improvement_pct,
                        'time_saved_seconds': standard_mean - optimized_mean
                    }
            
            self.logger.info(f"Performance benchmark completed: {benchmark_result['summary']}")
            
        except Exception as e:
            benchmark_result['error'] = str(e)
            self.logger.error(f"Performance benchmark failed: {e}")
        
        return benchmark_result
    
    def enable_performance_monitoring(self, enable: bool = True) -> Dict[str, Any]:
        """
        启用或禁用性能监控
        
        Args:
            enable: 是否启用
            
        Returns:
            操作结果
        """
        result = {
            'success': True,
            'previous_state': self.performance_monitor is not None,
            'new_state': enable,
            'message': ''
        }
        
        try:
            if enable and not self.performance_monitor:
                self.performance_monitor = get_performance_monitor()
                result['message'] = 'Performance monitoring enabled'
                self.logger.info("Performance monitoring enabled")
                
            elif not enable and self.performance_monitor:
                if hasattr(self.performance_monitor, 'close'):
                    self.performance_monitor.close()
                self.performance_monitor = None
                result['message'] = 'Performance monitoring disabled'
                self.logger.info("Performance monitoring disabled")
                
            else:
                result['message'] = f'Performance monitoring already {"enabled" if enable else "disabled"}'
        
        except Exception as e:
            result['success'] = False
            result['message'] = f'Failed to {"enable" if enable else "disable"} performance monitoring: {str(e)}'
            self.logger.error(result['message'])
        
        return result
    
    async def get_memory_usage_stats(self) -> Dict[str, Any]:
        """
        获取内存使用统计
        
        Returns:
            内存使用统计字典
        """
        stats = {
            'service_memory': {},
            'optimizer_memory': {},
            'system_memory': {}
        }
        
        try:
            # 获取系统内存信息
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            stats['system_memory'] = {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'percent': process.memory_percent()
            }
            
            # 获取优化器内存信息
            if self.performance_optimizer:
                stats['optimizer_memory'] = self.performance_optimizer.memory_optimizer.get_memory_usage()
            
            # 获取缓存内存信息
        except Exception as e:
            stats['error'] = str(e)
            self.logger.warning(f"Failed to get memory usage stats: {e}")
        
        return stats


# 便利函数

async def create_price_distribution_service(data_manager: DataManager, 
                                          logger: Optional[logging.Logger] = None) -> PriceDistributionStatsService:
    """
    创建涨跌分布统计服务实例
    
    Args:
        data_manager: 数据管理器
        logger: 日志记录器
        
    Returns:
        服务实例
    """
    service = PriceDistributionStatsService(data_manager, logger)
    
    # 执行健康检查
    health_result = await service.health_check()
    if health_result['status'] != 'healthy':
        logger.warning(f"Service health check issues: {health_result['issues']}")
    
    return service


async def get_distribution_stats_with_fallback(service: PriceDistributionStatsService,
                                             trade_date: str,
                                             **kwargs) -> Optional[PriceDistributionStats]:
    """
    获取分布统计数据，支持fallback策略
    
    Args:
        service: 服务实例
        trade_date: 交易日期
        **kwargs: 其他参数
        
    Returns:
        统计数据或None
    """
    try:
        request = PriceDistributionRequest(trade_date=trade_date, **kwargs)
        return await service.get_price_distribution_stats(request)
    except Exception as e:
        service.logger.error(f"Failed to get distribution stats with fallback: {e}")
        return None


        
        benchmark_result = {
            'test_config': {
                'data_size': test_data_size,
                'iterations': iterations,
                'timestamp': time.time()
            },
            'results': {
                'with_optimization': [],
                'without_optimization': []
            },
            'summary': {}
        }
        
        try:
            # 生成测试数据
            test_data = pd.DataFrame({
                'ts_code': [f'{i:06d}.SZ' for i in range(test_data_size)],
                'name': [f'股票{i}' for i in range(test_data_size)],
                'close': np.random.uniform(5, 100, test_data_size),
                'pre_close': np.random.uniform(5, 100, test_data_size),
                'pct_chg': np.random.uniform(-10, 10, test_data_size)
            })
            
            ranges = self.analyzer.default_ranges
            
            # 测试优化版本
            if self.performance_optimizer:
                for i in range(iterations):
                    start_time = time.time()
                    await self.analyzer.analyze_distribution_with_performance_optimization(
                        test_data, ranges, f"benchmark_optimized_{i}"
                    )
                    processing_time = time.time() - start_time
                    benchmark_result['results']['with_optimization'].append(processing_time)
            
            # 测试标准版本（临时禁用优化器）
            original_optimizer = self.analyzer.performance_optimizer
            self.analyzer.performance_optimizer = None
            
            try:
                for i in range(iterations):
                    start_time = time.time()
                    await self.analyzer.analyze_distribution(test_data, ranges)
                    processing_time = time.time() - start_time
                    benchmark_result['results']['without_optimization'].append(processing_time)
            finally:
                # 恢复优化器
                self.analyzer.performance_optimizer = original_optimizer
            
            # 计算统计摘要
            if benchmark_result['results']['with_optimization']:
                optimized_times = benchmark_result['results']['with_optimization']
                benchmark_result['summary']['optimized'] = {
                    'mean': np.mean(optimized_times),
                    'std': np.std(optimized_times),
                    'min': np.min(optimized_times),
                    'max': np.max(optimized_times)
                }
            
            if benchmark_result['results']['without_optimization']:
                standard_times = benchmark_result['results']['without_optimization']
                benchmark_result['summary']['standard'] = {
                    'mean': np.mean(standard_times),
                    'std': np.std(standard_times),
                    'min': np.min(standard_times),
                    'max': np.max(standard_times)
                }
                
                # 计算性能提升
                if benchmark_result['results']['with_optimization']:
                    optimized_mean = benchmark_result['summary']['optimized']['mean']
                    standard_mean = benchmark_result['summary']['standard']['mean']
                    
                    speedup = standard_mean / optimized_mean if optimized_mean > 0 else 0
                    improvement_pct = (standard_mean - optimized_mean) / standard_mean * 100 if standard_mean > 0 else 0
                    
                    benchmark_result['summary']['performance_improvement'] = {
                        'speedup_factor': speedup,
                        'improvement_percentage': improvement_pct,
                        'time_saved_seconds': standard_mean - optimized_mean
                    }
            
            self.logger.info(f"Performance benchmark completed: {benchmark_result['summary']}")
            
        except Exception as e:
            benchmark_result['error'] = str(e)
            self.logger.error(f"Performance benchmark failed: {e}")
        
        return benchmark_result
    
    def enable_performance_monitoring(self, enable: bool = True) -> Dict[str, Any]:
        """
        启用或禁用性能监控
        
        Args:
            enable: 是否启用
            
        Returns:
            操作结果
        """
        result = {
            'success': True,
            'previous_state': self.performance_monitor is not None,
            'new_state': enable,
            'message': ''
        }
        
        try:
            if enable and not self.performance_monitor:
                self.performance_monitor = get_performance_monitor()
                result['message'] = 'Performance monitoring enabled'
                self.logger.info("Performance monitoring enabled")
                
            elif not enable and self.performance_monitor:
                if hasattr(self.performance_monitor, 'close'):
                    self.performance_monitor.close()
                self.performance_monitor = None
                result['message'] = 'Performance monitoring disabled'
                self.logger.info("Performance monitoring disabled")
                
            else:
                result['message'] = f'Performance monitoring already {"enabled" if enable else "disabled"}'
        
        except Exception as e:
            result['success'] = False
            result['message'] = f'Failed to {"enable" if enable else "disable"} performance monitoring: {str(e)}'
            self.logger.error(result['message'])
        
        return result
    
    async def get_memory_usage_stats(self) -> Dict[str, Any]:
        """
        获取内存使用统计
        
        Returns:
            内存使用统计字典
        """
        stats = {
            'service_memory': {},
            'optimizer_memory': {},
            'system_memory': {}
        }
        
        try:
            # 获取系统内存信息
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            stats['system_memory'] = {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'percent': process.memory_percent()
            }
            
            # 获取优化器内存信息
            if self.performance_optimizer:
                stats['optimizer_memory'] = self.performance_optimizer.memory_optimizer.get_memory_usage()
            
            # 获取缓存内存信息
        except Exception as e:
            stats['error'] = str(e)
            self.logger.warning(f"Failed to get memory usage stats: {e}")
        
        return stats