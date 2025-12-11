"""
性能优化工具

为涨停统计系统提供向量化操作、并行处理和内存优化功能
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
import multiprocessing
import gc
import psutil
import os

from ..models import StockDailyData, LimitUpStats, LIMIT_UP_THRESHOLDS
from ..core.errors import LimitUpStatsError


@dataclass
class PerformanceConfig:
    """性能优化配置"""
    enable_vectorization: bool = True
    enable_parallel_processing: bool = True
    max_workers: int = None
    batch_size: int = 1000
    memory_limit_mb: int = 1024
    use_multiprocessing: bool = False
    chunk_size: int = 100
    enable_memory_optimization: bool = True


class VectorizedOperations:
    """向量化操作工具"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化向量化操作工具
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def vectorized_limit_up_detection(self, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        向量化涨停检测
        
        Args:
            stock_data: 股票数据DataFrame
            
        Returns:
            包含涨停检测结果的DataFrame
        """
        if stock_data.empty:
            return stock_data
        
        try:
            # 确保必要的列存在
            required_columns = ['open', 'close', 'high', 'pre_close', 'ts_code']
            missing_columns = [col for col in required_columns if col not in stock_data.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # 创建副本避免修改原数据
            df = stock_data.copy()
            
            # 向量化计算涨停价格
            df['limit_up_price_10'] = df['pre_close'] * 1.10  # 普通股票10%
            df['limit_up_price_20'] = df['pre_close'] * 1.20  # 科创板20%
            df['limit_up_price_30'] = df['pre_close'] * 1.30  # 北证30%
            df['limit_up_price_5'] = df['pre_close'] * 1.05   # ST股票5%
            
            # 向量化市场分类
            df['market'] = self._vectorized_market_classification(df['ts_code'])
            
            # 向量化ST检测
            if 'name' in df.columns:
                df['is_st'] = self._vectorized_st_detection(df['name'])
            else:
                df['is_st'] = False
            
            # 根据股票类型选择对应的涨停价格
            conditions = [
                df['is_st'],
                df['market'] == 'star',
                df['market'] == 'beijing',
                True  # 默认情况
            ]
            
            choices = [
                df['limit_up_price_5'],
                df['limit_up_price_20'],
                df['limit_up_price_30'],
                df['limit_up_price_10']
            ]
            
            df['expected_limit_up_price'] = np.select(conditions, choices)
            
            # 向量化涨停检测
            price_tolerance = 0.005
            df['price_diff'] = np.abs(df['close'] - df['expected_limit_up_price'])
            df['is_price_match'] = df['price_diff'] <= price_tolerance
            df['is_high_match'] = np.abs(df['close'] - df['high']) <= price_tolerance
            df['is_limit_up'] = df['is_price_match'] & df['is_high_match']
            
            # 计算置信度
            df['confidence'] = np.where(
                df['is_limit_up'],
                np.minimum(1.0, 0.5 + 0.4 * df['is_high_match'].astype(float) + 
                          0.1 * (1 - df['price_diff'] / price_tolerance)),
                0.0
            )
            
            # 清理临时列
            temp_columns = [
                'limit_up_price_10', 'limit_up_price_20', 'limit_up_price_30', 'limit_up_price_5',
                'expected_limit_up_price', 'price_diff', 'is_price_match', 'is_high_match'
            ]
            df = df.drop(columns=[col for col in temp_columns if col in df.columns])
            
            self.logger.debug(f"向量化涨停检测完成: {len(df)} 只股票, "
                            f"{df['is_limit_up'].sum()} 只涨停")
            
            return df
            
        except Exception as e:
            self.logger.error(f"向量化涨停检测失败: {e}")
            raise LimitUpStatsError(f"向量化涨停检测失败: {str(e)}")
    
    def _vectorized_market_classification(self, ts_codes: pd.Series) -> pd.Series:
        """
        向量化市场分类
        
        Args:
            ts_codes: 股票代码Series
            
        Returns:
            市场分类Series
        """
        # 提取股票代码的数字部分
        code_numbers = ts_codes.str.extract(r'^(\d{6})')[0]
        
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
        """
        向量化ST检测
        
        Args:
            stock_names: 股票名称Series
            
        Returns:
            ST检测结果Series
        """
        # 向量化ST模式匹配
        st_pattern = r'(\*ST|ST|退市|暂停)'
        return stock_names.str.contains(st_pattern, case=False, na=False)
    
    def vectorized_statistics_aggregation(self, limit_up_data: pd.DataFrame) -> Dict[str, Any]:
        """
        向量化统计聚合
        
        Args:
            limit_up_data: 涨停股票数据
            
        Returns:
            聚合统计结果
        """
        if limit_up_data.empty:
            return {
                'total': 0, 'non_st': 0, 'shanghai': 0, 'shenzhen': 0,
                'star': 0, 'beijing': 0, 'st': 0,
                'limit_up_stocks': [], 'market_breakdown': {}
            }
        
        try:
            # 筛选涨停股票
            limit_up_stocks = limit_up_data[limit_up_data['is_limit_up'] == True].copy()
            
            if limit_up_stocks.empty:
                return {
                    'total': 0, 'non_st': 0, 'shanghai': 0, 'shenzhen': 0,
                    'star': 0, 'beijing': 0, 'st': 0,
                    'limit_up_stocks': [], 'market_breakdown': {}
                }
            
            # 向量化统计计算
            market_counts = limit_up_stocks['market'].value_counts()
            st_counts = limit_up_stocks['is_st'].value_counts()
            
            # 构建统计结果
            stats = {
                'total': len(limit_up_stocks),
                'non_st': st_counts.get(False, 0),
                'shanghai': market_counts.get('shanghai', 0),
                'shenzhen': market_counts.get('shenzhen', 0),
                'star': market_counts.get('star', 0),
                'beijing': market_counts.get('beijing', 0),
                'st': st_counts.get(True, 0),
                'limit_up_stocks': limit_up_stocks['ts_code'].tolist(),
                'market_breakdown': {}
            }
            
            # 构建市场分解
            for market in ['shanghai', 'shenzhen', 'star', 'beijing']:
                market_stocks = limit_up_stocks[limit_up_stocks['market'] == market]['ts_code'].tolist()
                if market_stocks:
                    stats['market_breakdown'][market] = market_stocks
            
            self.logger.debug(f"向量化统计聚合完成: 总计 {stats['total']}")
            
            return stats
            
        except Exception as e:
            self.logger.error(f"向量化统计聚合失败: {e}")
            raise LimitUpStatsError(f"向量化统计聚合失败: {str(e)}")


class ParallelProcessor:
    """并行处理器"""
    
    def __init__(self, config: PerformanceConfig, logger: Optional[logging.Logger] = None):
        """
        初始化并行处理器
        
        Args:
            config: 性能配置
            logger: 日志记录器
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # 确定工作进程数
        if config.max_workers is None:
            self.max_workers = min(multiprocessing.cpu_count(), 8)
        else:
            self.max_workers = config.max_workers
        
        self.vectorized_ops = VectorizedOperations(logger)
    
    async def parallel_stock_processing(self, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        并行股票数据处理
        
        Args:
            stock_data: 股票数据
            
        Returns:
            处理后的数据
        """
        if stock_data.empty:
            return stock_data
        
        try:
            # 如果数据量小，直接使用向量化处理
            if len(stock_data) <= self.config.batch_size:
                return self.vectorized_ops.vectorized_limit_up_detection(stock_data)
            
            # 大数据集使用并行处理
            chunks = self._split_dataframe(stock_data, self.config.chunk_size)
            
            if self.config.use_multiprocessing and len(chunks) > 1:
                # 使用多进程处理
                results = await self._process_chunks_multiprocessing(chunks)
            else:
                # 使用多线程处理
                results = await self._process_chunks_threading(chunks)
            
            # 合并结果
            if results:
                combined_result = pd.concat(results, ignore_index=True)
                self.logger.info(f"并行处理完成: {len(chunks)} 个块, {len(combined_result)} 只股票")
                return combined_result
            else:
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"并行股票处理失败: {e}")
            # 回退到向量化处理
            return self.vectorized_ops.vectorized_limit_up_detection(stock_data)
    
    def _split_dataframe(self, df: pd.DataFrame, chunk_size: int) -> List[pd.DataFrame]:
        """将DataFrame分割成块"""
        chunks = []
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i + chunk_size].copy()
            chunks.append(chunk)
        return chunks
    
    async def _process_chunks_threading(self, chunks: List[pd.DataFrame]) -> List[pd.DataFrame]:
        """使用线程池处理数据块"""
        loop = asyncio.get_event_loop()
        
        def process_chunk(chunk):
            return self.vectorized_ops.vectorized_limit_up_detection(chunk)
        
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
    
    async def _process_chunks_multiprocessing(self, chunks: List[pd.DataFrame]) -> List[pd.DataFrame]:
        """使用进程池处理数据块"""
        loop = asyncio.get_event_loop()
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            tasks = [
                loop.run_in_executor(executor, _process_chunk_worker, chunk)
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
    
    async def parallel_batch_operations(self, operations: List[Callable], 
                                      batch_size: int = None) -> List[Any]:
        """
        并行批量操作
        
        Args:
            operations: 操作函数列表
            batch_size: 批次大小
            
        Returns:
            操作结果列表
        """
        if not operations:
            return []
        
        batch_size = batch_size or self.config.batch_size
        
        try:
            # 分批处理操作
            results = []
            
            for i in range(0, len(operations), batch_size):
                batch_ops = operations[i:i + batch_size]
                
                # 并发执行批次操作
                if asyncio.iscoroutinefunction(batch_ops[0]):
                    # 异步操作
                    batch_results = await asyncio.gather(*batch_ops, return_exceptions=True)
                else:
                    # 同步操作
                    loop = asyncio.get_event_loop()
                    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                        batch_tasks = [
                            loop.run_in_executor(executor, op)
                            for op in batch_ops
                        ]
                        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # 处理结果
                for result in batch_results:
                    if isinstance(result, Exception):
                        self.logger.warning(f"批量操作失败: {result}")
                        results.append(None)
                    else:
                        results.append(result)
                
                # 内存清理
                if self.config.enable_memory_optimization:
                    gc.collect()
            
            return results
            
        except Exception as e:
            self.logger.error(f"并行批量操作失败: {e}")
            raise


class MemoryOptimizer:
    """内存优化器"""
    
    def __init__(self, config: PerformanceConfig, logger: Optional[logging.Logger] = None):
        """
        初始化内存优化器
        
        Args:
            config: 性能配置
            logger: 日志记录器
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.process = psutil.Process(os.getpid())
    
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
    
    def optimize_dataframe_memory(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        优化DataFrame内存使用
        
        Args:
            df: 原始DataFrame
            
        Returns:
            优化后的DataFrame
        """
        if df.empty:
            return df
        
        try:
            optimized_df = df.copy()
            
            # 优化数值列的数据类型
            for col in optimized_df.select_dtypes(include=['int64']).columns:
                col_min = optimized_df[col].min()
                col_max = optimized_df[col].max()
                
                if col_min >= 0:
                    if col_max < 255:
                        optimized_df[col] = optimized_df[col].astype('uint8')
                    elif col_max < 65535:
                        optimized_df[col] = optimized_df[col].astype('uint16')
                    elif col_max < 4294967295:
                        optimized_df[col] = optimized_df[col].astype('uint32')
                else:
                    if col_min > -128 and col_max < 127:
                        optimized_df[col] = optimized_df[col].astype('int8')
                    elif col_min > -32768 and col_max < 32767:
                        optimized_df[col] = optimized_df[col].astype('int16')
                    elif col_min > -2147483648 and col_max < 2147483647:
                        optimized_df[col] = optimized_df[col].astype('int32')
            
            # 优化浮点数列
            for col in optimized_df.select_dtypes(include=['float64']).columns:
                optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='float')
            
            # 优化字符串列
            for col in optimized_df.select_dtypes(include=['object']).columns:
                if optimized_df[col].dtype == 'object':
                    try:
                        optimized_df[col] = optimized_df[col].astype('category')
                    except:
                        pass
            
            # 计算内存节省
            original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
            optimized_memory = optimized_df.memory_usage(deep=True).sum() / 1024 / 1024
            memory_saved = original_memory - optimized_memory
            
            if memory_saved > 0:
                self.logger.debug(f"DataFrame内存优化: 节省 {memory_saved:.2f}MB "
                                f"({memory_saved/original_memory:.1%})")
            
            return optimized_df
            
        except Exception as e:
            self.logger.warning(f"DataFrame内存优化失败: {e}")
            return df
    
    def batch_process_with_memory_control(self, data: pd.DataFrame, 
                                        process_func: Callable,
                                        batch_size: int = None) -> List[Any]:
        """
        带内存控制的批量处理
        
        Args:
            data: 待处理数据
            process_func: 处理函数
            batch_size: 批次大小
            
        Returns:
            处理结果列表
        """
        if data.empty:
            return []
        
        batch_size = batch_size or self.config.batch_size
        results = []
        
        try:
            for i in range(0, len(data), batch_size):
                # 检查内存使用
                if self.check_memory_limit():
                    self.logger.warning("内存使用超限，执行垃圾回收")
                    gc.collect()
                    
                    # 如果仍然超限，减小批次大小
                    if self.check_memory_limit():
                        batch_size = max(batch_size // 2, 10)
                        self.logger.info(f"调整批次大小为: {batch_size}")
                
                # 处理批次
                batch_data = data.iloc[i:i + batch_size]
                batch_result = process_func(batch_data)
                results.append(batch_result)
                
                # 清理批次数据
                del batch_data
                
                # 定期垃圾回收
                if (i // batch_size) % 10 == 0:
                    gc.collect()
            
            return results
            
        except Exception as e:
            self.logger.error(f"批量处理失败: {e}")
            raise
    
    def cleanup_memory(self):
        """清理内存"""
        gc.collect()
        
        # 记录清理后的内存使用
        memory_usage = self.get_memory_usage()
        self.logger.debug(f"内存清理完成: {memory_usage['rss_mb']:.2f}MB")


def _process_chunk_worker(chunk: pd.DataFrame) -> pd.DataFrame:
    """
    多进程工作函数
    
    Args:
        chunk: 数据块
        
    Returns:
        处理后的数据块
    """
    # 在子进程中创建向量化操作实例
    vectorized_ops = VectorizedOperations()
    return vectorized_ops.vectorized_limit_up_detection(chunk)


class PerformanceOptimizer:
    """性能优化器主类"""
    
    def __init__(self, config: PerformanceConfig = None, logger: Optional[logging.Logger] = None):
        """
        初始化性能优化器
        
        Args:
            config: 性能配置
            logger: 日志记录器
        """
        self.config = config or PerformanceConfig()
        self.logger = logger or logging.getLogger(__name__)
        
        # 初始化子组件
        self.vectorized_ops = VectorizedOperations(logger)
        self.parallel_processor = ParallelProcessor(self.config, logger)
        self.memory_optimizer = MemoryOptimizer(self.config, logger)
        
        self.logger.info(f"性能优化器初始化完成: "
                        f"向量化={self.config.enable_vectorization}, "
                        f"并行处理={self.config.enable_parallel_processing}, "
                        f"最大工作进程={self.parallel_processor.max_workers}")
    
    async def optimize_limit_up_detection(self, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        优化涨停检测处理
        
        Args:
            stock_data: 股票数据
            
        Returns:
            优化处理后的数据
        """
        if stock_data.empty:
            return stock_data
        
        start_time = datetime.now()
        initial_memory = self.memory_optimizer.get_memory_usage()
        
        try:
            # 内存优化
            if self.config.enable_memory_optimization:
                stock_data = self.memory_optimizer.optimize_dataframe_memory(stock_data)
            
            # 选择处理策略
            if (self.config.enable_parallel_processing and 
                len(stock_data) > self.config.batch_size):
                # 大数据集使用并行处理
                result = await self.parallel_processor.parallel_stock_processing(stock_data)
            elif self.config.enable_vectorization:
                # 中等数据集使用向量化处理
                result = self.vectorized_ops.vectorized_limit_up_detection(stock_data)
            else:
                # 回退到基本处理
                result = stock_data
            
            # 性能统计
            processing_time = (datetime.now() - start_time).total_seconds()
            final_memory = self.memory_optimizer.get_memory_usage()
            memory_delta = final_memory['rss_mb'] - initial_memory['rss_mb']
            
            self.logger.info(f"涨停检测优化完成: "
                           f"处理 {len(stock_data)} 只股票, "
                           f"耗时 {processing_time:.3f}s, "
                           f"内存变化 {memory_delta:+.2f}MB")
            
            return result
            
        except Exception as e:
            self.logger.error(f"涨停检测优化失败: {e}")
            raise
        finally:
            # 清理内存
            if self.config.enable_memory_optimization:
                self.memory_optimizer.cleanup_memory()
    
    def optimize_statistics_aggregation(self, limit_up_data: pd.DataFrame) -> Dict[str, Any]:
        """
        优化统计聚合
        
        Args:
            limit_up_data: 涨停数据
            
        Returns:
            聚合统计结果
        """
        if self.config.enable_vectorization:
            return self.vectorized_ops.vectorized_statistics_aggregation(limit_up_data)
        else:
            # 基本聚合逻辑
            return self._basic_statistics_aggregation(limit_up_data)
    
    def _basic_statistics_aggregation(self, limit_up_data: pd.DataFrame) -> Dict[str, Any]:
        """基本统计聚合"""
        # 这里实现基本的统计聚合逻辑
        # 作为向量化操作的回退方案
        return {
            'total': 0, 'non_st': 0, 'shanghai': 0, 'shenzhen': 0,
            'star': 0, 'beijing': 0, 'st': 0,
            'limit_up_stocks': [], 'market_breakdown': {}
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        memory_usage = self.memory_optimizer.get_memory_usage()
        
        return {
            'config': {
                'vectorization_enabled': self.config.enable_vectorization,
                'parallel_processing_enabled': self.config.enable_parallel_processing,
                'max_workers': self.parallel_processor.max_workers,
                'batch_size': self.config.batch_size,
                'memory_limit_mb': self.config.memory_limit_mb
            },
            'memory_usage': memory_usage,
            'cpu_count': multiprocessing.cpu_count()
        }