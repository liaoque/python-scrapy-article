"""
内存优化工具模块

提供内存监控、垃圾回收优化和数据流式处理功能
"""

import gc
import sys
import psutil
import pandas as pd
import numpy as np
from typing import Iterator, List, Optional, Dict, Any, Union, Callable
from dataclasses import dataclass
import logging
import threading
import time
from contextlib import contextmanager
import weakref

logger = logging.getLogger(__name__)


@dataclass
class MemoryStats:
    """内存统计信息"""
    total_memory_mb: float
    available_memory_mb: float
    used_memory_mb: float
    memory_percent: float
    process_memory_mb: float
    process_memory_percent: float


class MemoryMonitor:
    """内存监控器"""
    
    def __init__(self, warning_threshold: float = 80.0, critical_threshold: float = 90.0):
        """
        初始化内存监控器
        
        Args:
            warning_threshold: 内存使用警告阈值（百分比）
            critical_threshold: 内存使用临界阈值（百分比）
        """
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self._process = psutil.Process()
        self._callbacks = {
            'warning': [],
            'critical': [],
            'normal': []
        }
    
    def get_memory_stats(self) -> MemoryStats:
        """获取当前内存统计信息"""
        try:
            # 系统内存信息
            memory = psutil.virtual_memory()
            
            # 进程内存信息
            process_memory = self._process.memory_info()
            
            return MemoryStats(
                total_memory_mb=memory.total / (1024 * 1024),
                available_memory_mb=memory.available / (1024 * 1024),
                used_memory_mb=memory.used / (1024 * 1024),
                memory_percent=memory.percent,
                process_memory_mb=process_memory.rss / (1024 * 1024),
                process_memory_percent=(process_memory.rss / memory.total) * 100
            )
        except Exception as e:
            logger.error(f"获取内存统计失败: {e}")
            return MemoryStats(0, 0, 0, 0, 0, 0)
    
    def check_memory_status(self) -> str:
        """
        检查内存状态
        
        Returns:
            内存状态: 'normal', 'warning', 'critical'
        """
        stats = self.get_memory_stats()
        
        if stats.memory_percent >= self.critical_threshold:
            return 'critical'
        elif stats.memory_percent >= self.warning_threshold:
            return 'warning'
        else:
            return 'normal'
    
    def register_callback(self, status: str, callback: Callable[[MemoryStats], None]):
        """
        注册内存状态回调函数
        
        Args:
            status: 状态类型 ('normal', 'warning', 'critical')
            callback: 回调函数
        """
        if status in self._callbacks:
            self._callbacks[status].append(callback)
    
    def trigger_callbacks(self, status: str, stats: MemoryStats):
        """触发状态回调"""
        for callback in self._callbacks.get(status, []):
            try:
                callback(stats)
            except Exception as e:
                logger.error(f"内存状态回调执行失败: {e}")
    
    @contextmanager
    def monitor_context(self, log_stats: bool = True):
        """
        内存监控上下文管理器
        
        Args:
            log_stats: 是否记录内存统计
        """
        start_stats = self.get_memory_stats()
        start_status = self.check_memory_status()
        
        if log_stats:
            logger.info(f"内存监控开始 - 进程内存: {start_stats.process_memory_mb:.1f}MB, "
                       f"系统内存使用率: {start_stats.memory_percent:.1f}%")
        
        try:
            yield start_stats
        finally:
            end_stats = self.get_memory_stats()
            end_status = self.check_memory_status()
            
            memory_diff = end_stats.process_memory_mb - start_stats.process_memory_mb
            
            if log_stats:
                logger.info(f"内存监控结束 - 进程内存: {end_stats.process_memory_mb:.1f}MB "
                           f"({memory_diff:+.1f}MB), 系统内存使用率: {end_stats.memory_percent:.1f}%")
            
            # 触发状态回调
            if end_status != start_status:
                self.trigger_callbacks(end_status, end_stats)


class GarbageCollectionOptimizer:
    """垃圾回收优化器"""
    
    def __init__(self):
        self._gc_stats = {
            'collections': 0,
            'objects_collected': 0,
            'time_spent': 0.0
        }
    
    def optimize_gc_thresholds(self, generation0: int = 2000, 
                              generation1: int = 20, generation2: int = 20):
        """
        优化垃圾回收阈值
        
        Args:
            generation0: 第0代垃圾回收阈值
            generation1: 第1代垃圾回收阈值  
            generation2: 第2代垃圾回收阈值
        """
        old_thresholds = gc.get_threshold()
        gc.set_threshold(generation0, generation1, generation2)
        
        logger.info(f"垃圾回收阈值已优化: {old_thresholds} -> {gc.get_threshold()}")
    
    def force_gc(self, generation: Optional[int] = None) -> int:
        """
        强制执行垃圾回收
        
        Args:
            generation: 指定回收的代数，None表示全部
            
        Returns:
            回收的对象数量
        """
        start_time = time.time()
        
        if generation is not None:
            collected = gc.collect(generation)
        else:
            collected = gc.collect()
        
        elapsed_time = time.time() - start_time
        
        self._gc_stats['collections'] += 1
        self._gc_stats['objects_collected'] += collected
        self._gc_stats['time_spent'] += elapsed_time
        
        logger.debug(f"垃圾回收完成: 回收{collected}个对象, 耗时{elapsed_time:.3f}秒")
        
        return collected
    
    def get_gc_stats(self) -> Dict[str, Any]:
        """获取垃圾回收统计信息"""
        return {
            **self._gc_stats,
            'gc_counts': gc.get_count(),
            'gc_threshold': gc.get_threshold(),
            'gc_stats': gc.get_stats()
        }
    
    @contextmanager
    def gc_disabled(self):
        """临时禁用垃圾回收的上下文管理器"""
        was_enabled = gc.isenabled()
        gc.disable()
        try:
            yield
        finally:
            if was_enabled:
                gc.enable()


class DataFrameOptimizer:
    """DataFrame内存优化器"""
    
    @staticmethod
    def optimize_dtypes(df: pd.DataFrame, aggressive: bool = False) -> pd.DataFrame:
        """
        优化DataFrame的数据类型以减少内存使用
        
        Args:
            df: 要优化的DataFrame
            aggressive: 是否使用激进优化（可能损失精度）
            
        Returns:
            优化后的DataFrame
        """
        if df.empty:
            return df
        
        original_memory = df.memory_usage(deep=True).sum()
        optimized_df = df.copy()
        
        for col in optimized_df.columns:
            col_type = optimized_df[col].dtype
            
            # 优化整数类型
            if col_type in ['int64', 'int32', 'int16', 'int8']:
                c_min = optimized_df[col].min()
                c_max = optimized_df[col].max()
                
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    optimized_df[col] = optimized_df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    optimized_df[col] = optimized_df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    optimized_df[col] = optimized_df[col].astype(np.int32)
            
            # 优化浮点数类型
            elif col_type in ['float64', 'float32']:
                if aggressive:
                    # 激进模式：尝试转换为float32
                    optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='float')
                else:
                    # 保守模式：只在不损失精度的情况下转换
                    c_min = optimized_df[col].min()
                    c_max = optimized_df[col].max()
                    
                    if (c_min > np.finfo(np.float32).min and 
                        c_max < np.finfo(np.float32).max):
                        optimized_df[col] = optimized_df[col].astype(np.float32)
            
            # 优化对象类型（字符串）
            elif col_type == 'object':
                # 尝试转换为category类型
                num_unique_values = len(optimized_df[col].unique())
                num_total_values = len(optimized_df[col])
                
                # 如果唯一值比例小于50%，转换为category
                if num_unique_values / num_total_values < 0.5:
                    optimized_df[col] = optimized_df[col].astype('category')
        
        optimized_memory = optimized_df.memory_usage(deep=True).sum()
        memory_reduction = (original_memory - optimized_memory) / original_memory * 100
        
        logger.info(f"DataFrame内存优化完成: {original_memory / 1024 / 1024:.1f}MB -> "
                   f"{optimized_memory / 1024 / 1024:.1f}MB (减少{memory_reduction:.1f}%)")
        
        return optimized_df
    
    @staticmethod
    def get_memory_usage(df: pd.DataFrame) -> Dict[str, Any]:
        """获取DataFrame的内存使用详情"""
        if df.empty:
            return {'total_mb': 0, 'columns': {}}
        
        memory_usage = df.memory_usage(deep=True)
        total_memory = memory_usage.sum()
        
        column_usage = {}
        for col in df.columns:
            col_memory = memory_usage[col]
            column_usage[col] = {
                'memory_mb': col_memory / 1024 / 1024,
                'dtype': str(df[col].dtype),
                'null_count': df[col].isnull().sum(),
                'unique_count': df[col].nunique()
            }
        
        return {
            'total_mb': total_memory / 1024 / 1024,
            'index_mb': memory_usage['Index'] / 1024 / 1024,
            'columns': column_usage
        }


class StreamProcessor:
    """数据流式处理器"""
    
    def __init__(self, chunk_size: int = 10000, memory_limit_mb: float = 500.0):
        """
        初始化流式处理器
        
        Args:
            chunk_size: 每个数据块的大小
            memory_limit_mb: 内存使用限制（MB）
        """
        self.chunk_size = chunk_size
        self.memory_limit_mb = memory_limit_mb
        self.memory_monitor = MemoryMonitor()
        self.gc_optimizer = GarbageCollectionOptimizer()
    
    def process_dataframe_chunks(self, df: pd.DataFrame, 
                               processor_func: Callable[[pd.DataFrame], pd.DataFrame],
                               optimize_memory: bool = True) -> Iterator[pd.DataFrame]:
        """
        分块处理DataFrame
        
        Args:
            df: 要处理的DataFrame
            processor_func: 处理函数
            optimize_memory: 是否优化内存使用
            
        Yields:
            处理后的数据块
        """
        total_rows = len(df)
        processed_rows = 0
        
        logger.info(f"开始流式处理DataFrame: 总行数{total_rows}, 块大小{self.chunk_size}")
        
        for start_idx in range(0, total_rows, self.chunk_size):
            end_idx = min(start_idx + self.chunk_size, total_rows)
            chunk = df.iloc[start_idx:end_idx].copy()
            
            # 检查内存使用
            memory_stats = self.memory_monitor.get_memory_stats()
            if memory_stats.process_memory_mb > self.memory_limit_mb:
                logger.warning(f"内存使用超限({memory_stats.process_memory_mb:.1f}MB), 执行垃圾回收")
                self.gc_optimizer.force_gc()
            
            # 优化数据类型
            if optimize_memory:
                chunk = DataFrameOptimizer.optimize_dtypes(chunk)
            
            # 处理数据块
            try:
                processed_chunk = processor_func(chunk)
                yield processed_chunk
                
                processed_rows += len(chunk)
                progress = (processed_rows / total_rows) * 100
                
                logger.debug(f"处理进度: {processed_rows}/{total_rows} ({progress:.1f}%)")
                
            except Exception as e:
                logger.error(f"处理数据块失败 (行{start_idx}-{end_idx}): {e}")
                continue
            
            # 清理临时变量
            del chunk
            if 'processed_chunk' in locals():
                del processed_chunk
    
    def batch_process_requests(self, requests: List[Any],
                             processor_func: Callable[[List[Any]], List[Any]],
                             batch_size: Optional[int] = None) -> Iterator[List[Any]]:
        """
        批量处理请求
        
        Args:
            requests: 请求列表
            processor_func: 批处理函数
            batch_size: 批处理大小，None使用默认chunk_size
            
        Yields:
            处理后的结果批次
        """
        if batch_size is None:
            batch_size = self.chunk_size
        
        total_requests = len(requests)
        processed_requests = 0
        
        logger.info(f"开始批量处理请求: 总数{total_requests}, 批大小{batch_size}")
        
        for start_idx in range(0, total_requests, batch_size):
            end_idx = min(start_idx + batch_size, total_requests)
            batch = requests[start_idx:end_idx]
            
            # 检查内存使用
            memory_stats = self.memory_monitor.get_memory_stats()
            if memory_stats.process_memory_mb > self.memory_limit_mb:
                logger.warning(f"内存使用超限({memory_stats.process_memory_mb:.1f}MB), 执行垃圾回收")
                self.gc_optimizer.force_gc()
            
            # 处理批次
            try:
                processed_batch = processor_func(batch)
                yield processed_batch
                
                processed_requests += len(batch)
                progress = (processed_requests / total_requests) * 100
                
                logger.debug(f"处理进度: {processed_requests}/{total_requests} ({progress:.1f}%)")
                
            except Exception as e:
                logger.error(f"处理请求批次失败 (索引{start_idx}-{end_idx}): {e}")
                continue
            
            # 清理临时变量
            del batch
            if 'processed_batch' in locals():
                del processed_batch
    
    def get_stats(self) -> Dict[str, Any]:
        """获取数据处理统计信息"""
        return {
            'chunk_size': self.chunk_size,
            'memory_limit_mb': self.memory_limit_mb
        }




    


# 全局内存监控实例
_global_memory_monitor = None
_global_gc_optimizer = None


def get_memory_monitor() -> MemoryMonitor:
    """获取全局内存监控器实例"""
    global _global_memory_monitor
    if _global_memory_monitor is None:
        _global_memory_monitor = MemoryMonitor()
    return _global_memory_monitor


def get_gc_optimizer() -> GarbageCollectionOptimizer:
    """获取全局垃圾回收优化器实例"""
    global _global_gc_optimizer
    if _global_gc_optimizer is None:
        _global_gc_optimizer = GarbageCollectionOptimizer()
    return _global_gc_optimizer


def optimize_memory_usage():
    """优化全局内存使用"""
    gc_optimizer = get_gc_optimizer()
    
    # 优化垃圾回收阈值
    gc_optimizer.optimize_gc_thresholds()
    
    # 执行垃圾回收
    collected = gc_optimizer.force_gc()
    
    # 获取内存统计
    memory_monitor = get_memory_monitor()
    stats = memory_monitor.get_memory_stats()
    
    logger.info(f"内存优化完成: 回收{collected}个对象, "
               f"当前进程内存: {stats.process_memory_mb:.1f}MB")
    
    return stats