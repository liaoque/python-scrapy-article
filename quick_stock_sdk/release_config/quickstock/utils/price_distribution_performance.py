"""
价格分布统计性能优化器

集成现有的性能优化器，为价格分布统计提供专门的性能优化和监控功能
"""

import asyncio
import logging
import time
import gc
import psutil
import os
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime
from dataclasses import dataclass
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

from .performance_optimizations import (
    PerformanceOptimizer, 
    PerformanceConfig, 
    VectorizedOperations,
    ParallelProcessor,
    MemoryOptimizer
)
from .performance_monitor import PerformanceMonitor, get_performance_monitor
from ..models.price_distribution_models import (
    PriceDistributionRequest,
    PriceDistributionStats,
    DistributionRange
)
from ..core.price_distribution_errors import (
    PriceDistributionError,
    DistributionCalculationError,
    StatisticsAggregationError
)


@dataclass
class PriceDistributionPerformanceConfig:
    """价格分布性能配置"""
    # 基础性能配置
    enable_vectorization: bool = True
    enable_parallel_processing: bool = True
    enable_memory_optimization: bool = True
    enable_performance_monitoring: bool = True
    
    # 并行处理配置
    max_workers: int = None
    batch_size: int = 1000
    chunk_size: int = 500
    use_multiprocessing: bool = False
    
    # 内存优化配置
    memory_limit_mb: int = 2048
    enable_dataframe_optimization: bool = True
    enable_garbage_collection: bool = True
    gc_frequency: int = 10  # 每处理多少批次执行一次垃圾回收
    
    # 缓存配置
    enable_intermediate_caching: bool = True
    
    # 监控配置
    enable_detailed_metrics: bool = True
    metrics_history_size: int = 10000
    performance_report_interval: int = 100  # 每处理多少请求生成一次性能报告


class PriceDistributionVectorizedOperations:
    """价格分布向量化操作"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def vectorized_price_change_calculation(self, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        向量化价格变化计算
        
        Args:
            stock_data: 股票数据DataFrame
            
        Returns:
            包含价格变化的DataFrame
        """
        if stock_data.empty:
            return stock_data
        
        try:
            df = stock_data.copy()
            
            # 向量化计算涨跌幅
            if 'close' in df.columns and 'pre_close' in df.columns:
                # 避免除零错误
                valid_pre_close = df['pre_close'] != 0
                df.loc[valid_pre_close, 'pct_change'] = (
                    (df.loc[valid_pre_close, 'close'] - df.loc[valid_pre_close, 'pre_close']) / 
                    df.loc[valid_pre_close, 'pre_close'] * 100
                )
                df.loc[~valid_pre_close, 'pct_change'] = 0.0
            else:
                # 如果没有pre_close，尝试使用其他方法计算
                if 'pct_chg' in df.columns:
                    df['pct_change'] = df['pct_chg']
                else:
                    df['pct_change'] = 0.0
            
            # 向量化市场分类
            df['market'] = self._vectorized_market_classification(df.get('ts_code', df.index))
            
            # 向量化ST检测
            if 'name' in df.columns:
                df['is_st'] = self._vectorized_st_detection(df['name'])
            else:
                df['is_st'] = False
            
            self.logger.debug(f"向量化价格变化计算完成: {len(df)} 只股票")
            return df
            
        except Exception as e:
            self.logger.error(f"向量化价格变化计算失败: {e}")
            raise DistributionCalculationError(f"价格变化计算失败: {str(e)}")
    
    def vectorized_distribution_classification(self, pct_changes: pd.Series, 
                                             ranges: List[DistributionRange]) -> Dict[str, pd.Series]:
        """
        向量化分布分类
        
        Args:
            pct_changes: 涨跌幅Series
            ranges: 分布区间列表
            
        Returns:
            分类结果字典
        """
        try:
            classification_results = {}
            
            for range_def in ranges:
                if range_def.is_positive:
                    # 正区间
                    if range_def.max_value == float('inf'):
                        mask = pct_changes >= range_def.min_value
                    else:
                        mask = (pct_changes >= range_def.min_value) & (pct_changes < range_def.max_value)
                else:
                    # 负区间
                    if range_def.min_value == float('-inf'):
                        mask = pct_changes <= range_def.max_value
                    else:
                        mask = (pct_changes > range_def.min_value) & (pct_changes <= range_def.max_value)
                
                classification_results[range_def.name] = mask
            
            self.logger.debug(f"向量化分布分类完成: {len(ranges)} 个区间")
            return classification_results
            
        except Exception as e:
            self.logger.error(f"向量化分布分类失败: {e}")
            raise DistributionCalculationError(f"分布分类失败: {str(e)}")
    
    def vectorized_market_statistics(self, stock_data: pd.DataFrame, 
                                   classification_results: Dict[str, pd.Series]) -> Dict[str, Dict[str, Any]]:
        """
        向量化市场统计
        
        Args:
            stock_data: 股票数据
            classification_results: 分类结果
            
        Returns:
            市场统计结果
        """
        try:
            market_stats = {}
            
            # 获取所有市场类型
            markets = ['total', 'shanghai', 'shenzhen', 'star', 'beijing', 'st', 'non_st']
            
            for market in markets:
                if market == 'total':
                    market_mask = pd.Series(True, index=stock_data.index)
                elif market == 'st':
                    market_mask = stock_data.get('is_st', False)
                elif market == 'non_st':
                    market_mask = ~stock_data.get('is_st', True)
                else:
                    market_mask = stock_data.get('market', '') == market
                
                market_data = {}
                total_count = market_mask.sum()
                
                for range_name, range_mask in classification_results.items():
                    count = (market_mask & range_mask).sum()
                    percentage = (count / total_count * 100) if total_count > 0 else 0.0
                    
                    market_data[range_name] = {
                        'count': int(count),
                        'percentage': round(percentage, 2)
                    }
                
                market_data['total_stocks'] = int(total_count)
                market_stats[market] = market_data
            
            self.logger.debug(f"向量化市场统计完成: {len(markets)} 个市场")
            return market_stats
            
        except Exception as e:
            self.logger.error(f"向量化市场统计失败: {e}")
            raise StatisticsAggregationError(f"市场统计失败: {str(e)}")
    
    def _vectorized_market_classification(self, ts_codes: pd.Series) -> pd.Series:
        """向量化市场分类"""
        if ts_codes.empty:
            return pd.Series(dtype=str)
        
        # 提取股票代码的数字部分
        code_numbers = ts_codes.astype(str).str.extract(r'^(\d{6})')[0]
        
        # 向量化市场分类
        conditions = [
            code_numbers.str.startswith('688'),  # 科创板
            code_numbers.str.startswith(('60', '68')),  # 上海主板
            code_numbers.str.startswith(('00', '30')),  # 深圳主板
            code_numbers.str.startswith(('8', '4')),    # 北证
        ]
        
        choices = ['star', 'shanghai', 'shenzhen', 'beijing']
        
        return pd.Series(np.select(conditions, choices, default='unknown'), index=ts_codes.index)
    
    def _vectorized_st_detection(self, stock_names: pd.Series) -> pd.Series:
        """向量化ST检测"""
        if stock_names.empty:
            return pd.Series(dtype=bool)
        
        # 向量化ST模式匹配
        st_pattern = r'(\*ST|ST|退市|暂停)'
        return stock_names.astype(str).str.contains(st_pattern, case=False, na=False)


class PriceDistributionParallelProcessor:
    """价格分布并行处理器"""
    
    def __init__(self, config: PriceDistributionPerformanceConfig, 
                 logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # 确定工作进程数
        if config.max_workers is None:
            self.max_workers = min(multiprocessing.cpu_count(), 8)
        else:
            self.max_workers = config.max_workers
        
        self.vectorized_ops = PriceDistributionVectorizedOperations(logger)
    
    async def parallel_distribution_analysis(self, stock_data: pd.DataFrame, 
                                           ranges: List[DistributionRange]) -> Dict[str, Any]:
        """
        并行分布分析
        
        Args:
            stock_data: 股票数据
            ranges: 分布区间
            
        Returns:
            分析结果
        """
        if stock_data.empty:
            return {}
        
        try:
            # 如果数据量小，直接使用向量化处理
            if len(stock_data) <= self.config.batch_size:
                return await self._single_thread_analysis(stock_data, ranges)
            
            # 大数据集使用并行处理
            chunks = self._split_dataframe(stock_data, self.config.chunk_size)
            
            if self.config.use_multiprocessing and len(chunks) > 1:
                results = await self._process_chunks_multiprocessing(chunks, ranges)
            else:
                results = await self._process_chunks_threading(chunks, ranges)
            
            # 合并结果
            merged_result = self._merge_analysis_results(results)
            
            self.logger.info(f"并行分布分析完成: {len(chunks)} 个块, {len(stock_data)} 只股票")
            return merged_result
            
        except Exception as e:
            self.logger.error(f"并行分布分析失败: {e}")
            # 回退到单线程处理
            return await self._single_thread_analysis(stock_data, ranges)
    
    async def _single_thread_analysis(self, stock_data: pd.DataFrame, 
                                    ranges: List[DistributionRange]) -> Dict[str, Any]:
        """单线程分析"""
        # 计算价格变化
        processed_data = self.vectorized_ops.vectorized_price_change_calculation(stock_data)
        
        # 分类
        classification_results = self.vectorized_ops.vectorized_distribution_classification(
            processed_data['pct_change'], ranges
        )
        
        # 统计
        market_stats = self.vectorized_ops.vectorized_market_statistics(
            processed_data, classification_results
        )
        
        return market_stats
    
    def _split_dataframe(self, df: pd.DataFrame, chunk_size: int) -> List[pd.DataFrame]:
        """将DataFrame分割成块"""
        chunks = []
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i + chunk_size].copy()
            chunks.append(chunk)
        return chunks
    
    async def _process_chunks_threading(self, chunks: List[pd.DataFrame], 
                                      ranges: List[DistributionRange]) -> List[Dict[str, Any]]:
        """使用线程池处理数据块"""
        loop = asyncio.get_event_loop()
        
        def process_chunk(chunk):
            return asyncio.run(self._single_thread_analysis(chunk, ranges))
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            tasks = [
                loop.run_in_executor(executor, process_chunk, chunk)
                for chunk in chunks
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤异常结果
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.warning(f"块 {i} 处理失败: {result}")
                else:
                    valid_results.append(result)
            
            return valid_results
    
    async def _process_chunks_multiprocessing(self, chunks: List[pd.DataFrame], 
                                            ranges: List[DistributionRange]) -> List[Dict[str, Any]]:
        """使用进程池处理数据块"""
        loop = asyncio.get_event_loop()
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            tasks = [
                loop.run_in_executor(executor, _process_distribution_chunk, chunk, ranges)
                for chunk in chunks
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤异常结果
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.warning(f"块 {i} 处理失败: {result}")
                else:
                    valid_results.append(result)
            
            return valid_results
    
    def _merge_analysis_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """合并分析结果"""
        if not results:
            return {}
        
        merged = {}
        
        # 获取所有市场类型
        all_markets = set()
        for result in results:
            all_markets.update(result.keys())
        
        for market in all_markets:
            merged[market] = {'total_stocks': 0}
            
            # 获取所有区间名称
            all_ranges = set()
            for result in results:
                if market in result:
                    for range_name in result[market]:
                        if range_name != 'total_stocks':
                            all_ranges.add(range_name)
            
            # 合并每个区间的统计
            for range_name in all_ranges:
                total_count = 0
                for result in results:
                    if market in result and range_name in result[market]:
                        total_count += result[market][range_name]['count']
                
                merged[market][range_name] = {'count': total_count}
            
            # 计算总股票数和百分比
            total_stocks = sum(
                result[market]['total_stocks'] 
                for result in results 
                if market in result
            )
            merged[market]['total_stocks'] = total_stocks
            
            # 重新计算百分比
            for range_name in all_ranges:
                count = merged[market][range_name]['count']
                percentage = (count / total_stocks * 100) if total_stocks > 0 else 0.0
                merged[market][range_name]['percentage'] = round(percentage, 2)
        
        return merged


class PriceDistributionMemoryOptimizer:
    """价格分布内存优化器"""
    
    def __init__(self, config: PriceDistributionPerformanceConfig, 
                 logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.process = psutil.Process(os.getpid())
        self.gc_counter = 0
    
    def optimize_stock_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """优化股票数据DataFrame"""
        if df.empty:
            return df
        
        try:
            optimized_df = df.copy()
            
            # 优化数值列
            numeric_columns = ['open', 'high', 'low', 'close', 'pre_close', 'volume', 'amount']
            for col in numeric_columns:
                if col in optimized_df.columns:
                    optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='float')
            
            # 优化字符串列
            string_columns = ['ts_code', 'name', 'market']
            for col in string_columns:
                if col in optimized_df.columns and optimized_df[col].dtype == 'object':
                    try:
                        optimized_df[col] = optimized_df[col].astype('category')
                    except:
                        pass
            
            # 优化布尔列
            bool_columns = ['is_st']
            for col in bool_columns:
                if col in optimized_df.columns:
                    optimized_df[col] = optimized_df[col].astype('bool')
            
            # 计算内存节省
            original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
            optimized_memory = optimized_df.memory_usage(deep=True).sum() / 1024 / 1024
            memory_saved = original_memory - optimized_memory
            
            if memory_saved > 0:
                self.logger.debug(f"DataFrame内存优化: 节省 {memory_saved:.2f}MB")
            
            return optimized_df
            
        except Exception as e:
            self.logger.warning(f"DataFrame内存优化失败: {e}")
            return df
    
    def check_and_cleanup_memory(self):
        """检查并清理内存"""
        self.gc_counter += 1
        
        if self.config.enable_garbage_collection and self.gc_counter % self.config.gc_frequency == 0:
            memory_before = self.get_memory_usage()['rss_mb']
            gc.collect()
            memory_after = self.get_memory_usage()['rss_mb']
            
            memory_freed = memory_before - memory_after
            if memory_freed > 0:
                self.logger.debug(f"垃圾回收释放内存: {memory_freed:.2f}MB")
    
    def get_memory_usage(self) -> Dict[str, float]:
        """获取当前内存使用情况"""
        memory_info = self.process.memory_info()
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': self.process.memory_percent()
        }
    
    def check_memory_limit(self) -> bool:
        """检查是否超过内存限制"""
        current_memory = self.get_memory_usage()['rss_mb']
        return current_memory > self.config.memory_limit_mb


class PriceDistributionPerformanceOptimizer:
    """价格分布性能优化器主类"""
    
    def __init__(self, config: PriceDistributionPerformanceConfig = None, 
                 logger: Optional[logging.Logger] = None):
        """
        初始化价格分布性能优化器
        
        Args:
            config: 性能配置
            logger: 日志记录器
        """
        self.config = config or PriceDistributionPerformanceConfig()
        self.logger = logger or logging.getLogger(__name__)
        
        # 初始化子组件
        self.vectorized_ops = PriceDistributionVectorizedOperations(logger)
        self.parallel_processor = PriceDistributionParallelProcessor(self.config, logger)
        self.memory_optimizer = PriceDistributionMemoryOptimizer(self.config, logger)
        
        # 性能监控器
        self.performance_monitor = get_performance_monitor() if self.config.enable_performance_monitoring else None
        
        # 性能统计
        self.performance_stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0,
            'memory_optimizations': 0,
            'parallel_operations': 0,
            'vectorized_operations': 0
        }
        
        self.logger.info(f"价格分布性能优化器初始化完成: "
                        f"向量化={self.config.enable_vectorization}, "
                        f"并行处理={self.config.enable_parallel_processing}, "
                        f"内存优化={self.config.enable_memory_optimization}")
    
    async def optimize_distribution_analysis(self, stock_data: pd.DataFrame, 
                                           ranges: List[DistributionRange],
                                           operation_name: str = "distribution_analysis") -> Dict[str, Any]:
        """
        优化分布分析处理
        
        Args:
            stock_data: 股票数据
            ranges: 分布区间
            operation_name: 操作名称
            
        Returns:
            优化处理后的分析结果
        """
        if stock_data.empty:
            return {}
        
        start_time = time.time()
        self.performance_stats['total_operations'] += 1
        
        try:
            # 性能监控
            if self.performance_monitor:
                async with self.performance_monitor.measure_operation(
                    operation_name, data_size=len(stock_data)
                ):
                    result = await self._perform_optimized_analysis(stock_data, ranges)
            else:
                result = await self._perform_optimized_analysis(stock_data, ranges)
            
            # 更新成功统计
            processing_time = time.time() - start_time
            self.performance_stats['successful_operations'] += 1
            self.performance_stats['total_processing_time'] += processing_time
            self.performance_stats['average_processing_time'] = (
                self.performance_stats['total_processing_time'] / 
                self.performance_stats['successful_operations']
            )
            
            self.logger.info(f"优化分布分析完成: "
                           f"处理 {len(stock_data)} 只股票, "
                           f"耗时 {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.performance_stats['failed_operations'] += 1
            self.performance_stats['total_processing_time'] += processing_time
            
            self.logger.error(f"优化分布分析失败: {e}")
            raise
        finally:
            # 内存清理
            self.memory_optimizer.check_and_cleanup_memory()
    
    async def _perform_optimized_analysis(self, stock_data: pd.DataFrame, 
                                        ranges: List[DistributionRange]) -> Dict[str, Any]:
        """执行优化的分析"""
        # 1. 内存优化
        if self.config.enable_memory_optimization:
            stock_data = self.memory_optimizer.optimize_stock_dataframe(stock_data)
            self.performance_stats['memory_optimizations'] += 1
        
        # 2. 选择处理策略
        if (self.config.enable_parallel_processing and 
            len(stock_data) > self.config.batch_size):
            # 大数据集使用并行处理
            result = await self.parallel_processor.parallel_distribution_analysis(stock_data, ranges)
            self.performance_stats['parallel_operations'] += 1
        elif self.config.enable_vectorization:
            # 中等数据集使用向量化处理
            result = await self._vectorized_analysis(stock_data, ranges)
            self.performance_stats['vectorized_operations'] += 1
        else:
            # 基本处理
            result = await self._basic_analysis(stock_data, ranges)
        
        return result
    
    async def _vectorized_analysis(self, stock_data: pd.DataFrame, 
                                 ranges: List[DistributionRange]) -> Dict[str, Any]:
        """向量化分析"""
        # 计算价格变化
        processed_data = self.vectorized_ops.vectorized_price_change_calculation(stock_data)
        
        # 分类
        classification_results = self.vectorized_ops.vectorized_distribution_classification(
            processed_data['pct_change'], ranges
        )
        
        # 统计
        market_stats = self.vectorized_ops.vectorized_market_statistics(
            processed_data, classification_results
        )
        
        return market_stats
    
    async def _basic_analysis(self, stock_data: pd.DataFrame, 
                            ranges: List[DistributionRange]) -> Dict[str, Any]:
        """基本分析（回退方案）"""
        # 这里实现基本的分析逻辑作为回退方案
        return {}
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        memory_usage = self.memory_optimizer.get_memory_usage()
        
        stats = {
            'config': {
                'vectorization_enabled': self.config.enable_vectorization,
                'parallel_processing_enabled': self.config.enable_parallel_processing,
                'memory_optimization_enabled': self.config.enable_memory_optimization,
                'performance_monitoring_enabled': self.config.enable_performance_monitoring,
                'max_workers': self.parallel_processor.max_workers,
                'batch_size': self.config.batch_size,
                'memory_limit_mb': self.config.memory_limit_mb
            },
            'performance_stats': self.performance_stats.copy(),
            'memory_usage': memory_usage,
            'cpu_count': multiprocessing.cpu_count()
        }
        
        # 添加性能监控器统计
        if self.performance_monitor:
            stats['monitor_stats'] = self.performance_monitor.get_performance_summary()
        
        return stats
    
    def reset_performance_stats(self):
        """重置性能统计"""
        self.performance_stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0,
            'memory_optimizations': 0,
            'parallel_operations': 0,
            'vectorized_operations': 0
        }
        
        if self.performance_monitor:
            self.performance_monitor.reset_stats()


def _process_distribution_chunk(chunk: pd.DataFrame, ranges: List[DistributionRange]) -> Dict[str, Any]:
    """
    多进程工作函数
    
    Args:
        chunk: 数据块
        ranges: 分布区间
        
    Returns:
        处理后的分析结果
    """
    # 在子进程中创建向量化操作实例
    vectorized_ops = PriceDistributionVectorizedOperations()
    
    # 计算价格变化
    processed_data = vectorized_ops.vectorized_price_change_calculation(chunk)
    
    # 分类
    classification_results = vectorized_ops.vectorized_distribution_classification(
        processed_data['pct_change'], ranges
    )
    
    # 统计
    market_stats = vectorized_ops.vectorized_market_statistics(
        processed_data, classification_results
    )
    
    return market_stats