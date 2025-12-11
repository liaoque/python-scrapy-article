"""
内存优化工具

提供大数据集的内存高效处理功能
"""

import gc
import psutil
import logging
from typing import Iterator, List, Dict, Any, Optional, Callable, Union
import pandas as pd
import numpy as np
from contextlib import contextmanager
from dataclasses import dataclass
import threading
import time


@dataclass
class MemoryUsage:
    """内存使用情况"""
    total_mb: float
    available_mb: float
    used_mb: float
    percent: float
    process_mb: float
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total_mb': round(self.total_mb, 2),
            'available_mb': round(self.available_mb, 2),
            'used_mb': round(self.used_mb, 2),
            'percent': round(self.percent, 2),
            'process_mb': round(self.process_mb, 2)
        }


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
        self.logger = logging.getLogger(__name__)
        self._process = psutil.Process()
    
    def get_memory_usage(self) -> MemoryUsage:
        """获取当前内存使用情况"""
        # 系统内存信息
        memory = psutil.virtual_memory()
        
        # 进程内存信息
        process_memory = self._process.memory_info()
        
        return MemoryUsage(
            total_mb=memory.total / (1024 * 1024),
            available_mb=memory.available / (1024 * 1024),
            used_mb=memory.used / (1024 * 1024),
            percent=memory.percent,
            process_mb=process_memory.rss / (1024 * 1024)
        )
    
    def check_memory_pressure(self) -> Optional[str]:
        """
        检查内存压力
        
        Returns:
            内存压力级别：None（正常）、'warning'（警告）、'critical'（临界）
        """
        usage = self.get_memory_usage()
        
        if usage.percent >= self.critical_threshold:
            return 'critical'
        elif usage.percent >= self.warning_threshold:
            return 'warning'
        else:
            return None
    
    def log_memory_usage(self, operation: str = ""):
        """记录内存使用情况"""
        usage = self.get_memory_usage()
        pressure = self.check_memory_pressure()
        
        log_msg = f"内存使用情况{f' ({operation})' if operation else ''}: " \
                 f"系统 {usage.percent:.1f}% ({usage.used_mb:.1f}MB/{usage.total_mb:.1f}MB), " \
                 f"进程 {usage.process_mb:.1f}MB"
        
        if pressure == 'critical':
            self.logger.error(f"[CRITICAL] {log_msg}")
        elif pressure == 'warning':
            self.logger.warning(f"[WARNING] {log_msg}")
        else:
            self.logger.debug(log_msg)


@contextmanager
def memory_efficient_processing(operation_name: str = "", 
                              force_gc: bool = True,
                              log_usage: bool = True):
    """
    内存高效处理的上下文管理器
    
    Args:
        operation_name: 操作名称
        force_gc: 是否强制垃圾回收
        log_usage: 是否记录内存使用情况
    """
    monitor = MemoryMonitor()
    
    if log_usage:
        monitor.log_memory_usage(f"{operation_name} - 开始")
    
    try:
        yield monitor
    finally:
        if force_gc:
            gc.collect()
        
        if log_usage:
            monitor.log_memory_usage(f"{operation_name} - 结束")


class ChunkedDataProcessor:
    """分块数据处理器"""
    
    def __init__(self, chunk_size: int = 1000, memory_limit_mb: float = 500.0):
        """
        初始化分块数据处理器
        
        Args:
            chunk_size: 每块的大小
            memory_limit_mb: 内存限制（MB）
        """
        self.chunk_size = chunk_size
        self.memory_limit_mb = memory_limit_mb
        self.monitor = MemoryMonitor()
        self.logger = logging.getLogger(__name__)
    
    def process_dataframe_chunks(self, 
                               df: pd.DataFrame,
                               processor: Callable[[pd.DataFrame], pd.DataFrame],
                               **kwargs) -> pd.DataFrame:
        """
        分块处理DataFrame
        
        Args:
            df: 要处理的DataFrame
            processor: 处理函数
            **kwargs: 传递给处理函数的额外参数
            
        Returns:
            处理后的DataFrame
        """
        if df.empty:
            return df
        
        # 检查是否需要分块处理
        df_memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        
        if df_memory_mb <= self.memory_limit_mb:
            # 数据量小，直接处理
            with memory_efficient_processing(f"处理DataFrame ({len(df)}行)"):
                return processor(df, **kwargs)
        
        # 数据量大，分块处理
        self.logger.info(f"数据量较大 ({df_memory_mb:.1f}MB)，开始分块处理，块大小: {self.chunk_size}")
        
        results = []
        total_chunks = (len(df) + self.chunk_size - 1) // self.chunk_size
        
        for i, chunk in enumerate(self._chunk_dataframe(df, self.chunk_size)):
            with memory_efficient_processing(f"处理块 {i+1}/{total_chunks}"):
                # 检查内存压力
                pressure = self.monitor.check_memory_pressure()
                if pressure == 'critical':
                    self.logger.warning("内存压力过大，强制垃圾回收")
                    gc.collect()
                
                # 处理当前块
                processed_chunk = processor(chunk, **kwargs)
                results.append(processed_chunk)
                
                # 清理临时变量
                del chunk
        
        # 合并结果
        with memory_efficient_processing("合并处理结果"):
            if results:
                final_result = pd.concat(results, ignore_index=True)
                # 清理中间结果
                del results
                gc.collect()
                return final_result
            else:
                return pd.DataFrame()
    
    def _chunk_dataframe(self, df: pd.DataFrame, chunk_size: int) -> Iterator[pd.DataFrame]:
        """将DataFrame分块"""
        for i in range(0, len(df), chunk_size):
            yield df.iloc[i:i + chunk_size].copy()
    
    def process_list_chunks(self,
                          data_list: List[Any],
                          processor: Callable[[List[Any]], List[Any]],
                          **kwargs) -> List[Any]:
        """
        分块处理列表数据
        
        Args:
            data_list: 要处理的列表
            processor: 处理函数
            **kwargs: 传递给处理函数的额外参数
            
        Returns:
            处理后的列表
        """
        if not data_list:
            return data_list
        
        if len(data_list) <= self.chunk_size:
            # 数据量小，直接处理
            with memory_efficient_processing(f"处理列表 ({len(data_list)}项)"):
                return processor(data_list, **kwargs)
        
        # 数据量大，分块处理
        self.logger.info(f"列表数据量较大 ({len(data_list)}项)，开始分块处理")
        
        results = []
        total_chunks = (len(data_list) + self.chunk_size - 1) // self.chunk_size
        
        for i in range(0, len(data_list), self.chunk_size):
            chunk = data_list[i:i + self.chunk_size]
            
            with memory_efficient_processing(f"处理块 {i//self.chunk_size + 1}/{total_chunks}"):
                # 检查内存压力
                pressure = self.monitor.check_memory_pressure()
                if pressure == 'critical':
                    self.logger.warning("内存压力过大，强制垃圾回收")
                    gc.collect()
                
                # 处理当前块
                processed_chunk = processor(chunk, **kwargs)
                results.extend(processed_chunk)
        
        return results


class DataFrameOptimizer:
    """DataFrame优化器"""
    
    @staticmethod
    def optimize_dtypes(df: pd.DataFrame, 
                       aggressive: bool = False,
                       categorical_threshold: int = 50) -> pd.DataFrame:
        """
        优化DataFrame的数据类型以减少内存使用
        
        Args:
            df: 要优化的DataFrame
            aggressive: 是否使用激进优化
            categorical_threshold: 字符串转分类变量的阈值
            
        Returns:
            优化后的DataFrame
        """
        if df.empty:
            return df
        
        logger = logging.getLogger(__name__)
        original_memory = df.memory_usage(deep=True).sum()
        
        optimized_df = df.copy()
        
        for col in optimized_df.columns:
            col_type = optimized_df[col].dtype
            
            # 优化数值类型
            if pd.api.types.is_numeric_dtype(col_type):
                optimized_df[col] = DataFrameOptimizer._optimize_numeric_column(
                    optimized_df[col], aggressive
                )
            
            # 优化字符串类型
            elif pd.api.types.is_object_dtype(col_type):
                optimized_df[col] = DataFrameOptimizer._optimize_object_column(
                    optimized_df[col], categorical_threshold
                )
        
        # 计算优化效果
        optimized_memory = optimized_df.memory_usage(deep=True).sum()
        memory_reduction = (original_memory - optimized_memory) / original_memory * 100
        
        logger.info(f"DataFrame内存优化完成: "
                   f"{original_memory / (1024*1024):.1f}MB -> "
                   f"{optimized_memory / (1024*1024):.1f}MB "
                   f"(减少 {memory_reduction:.1f}%)")
        
        return optimized_df
    
    @staticmethod
    def _optimize_numeric_column(series: pd.Series, aggressive: bool = False) -> pd.Series:
        """优化数值列"""
        if series.dtype == 'object':
            return series
        
        # 检查是否有缺失值
        has_na = series.isna().any()
        
        if pd.api.types.is_integer_dtype(series):
            # 整数类型优化
            min_val = series.min()
            max_val = series.max()
            
            if has_na:
                # 有缺失值，使用nullable integer types
                if min_val >= 0:
                    if max_val < 255:
                        return series.astype('UInt8')
                    elif max_val < 65535:
                        return series.astype('UInt16')
                    elif max_val < 4294967295:
                        return series.astype('UInt32')
                    else:
                        return series.astype('UInt64')
                else:
                    if min_val >= -128 and max_val <= 127:
                        return series.astype('Int8')
                    elif min_val >= -32768 and max_val <= 32767:
                        return series.astype('Int16')
                    elif min_val >= -2147483648 and max_val <= 2147483647:
                        return series.astype('Int32')
                    else:
                        return series.astype('Int64')
            else:
                # 无缺失值，使用标准integer types
                if min_val >= 0:
                    if max_val < 255:
                        return series.astype('uint8')
                    elif max_val < 65535:
                        return series.astype('uint16')
                    elif max_val < 4294967295:
                        return series.astype('uint32')
                    else:
                        return series.astype('uint64')
                else:
                    if min_val >= -128 and max_val <= 127:
                        return series.astype('int8')
                    elif min_val >= -32768 and max_val <= 32767:
                        return series.astype('int16')
                    elif min_val >= -2147483648 and max_val <= 2147483647:
                        return series.astype('int32')
                    else:
                        return series.astype('int64')
        
        elif pd.api.types.is_float_dtype(series):
            # 浮点类型优化
            if aggressive:
                # 激进模式：尝试转换为float32
                if series.dtype == 'float64':
                    # 检查是否可以安全转换为float32
                    converted = series.astype('float32')
                    if np.allclose(series.dropna(), converted.dropna(), equal_nan=True):
                        return converted
            
            # 保持原类型或转换为float32
            if series.dtype == 'float64' and not aggressive:
                return series  # 保持精度
            else:
                return series.astype('float32')
        
        return series
    
    @staticmethod
    def _optimize_object_column(series: pd.Series, categorical_threshold: int = 50) -> pd.Series:
        """优化对象列"""
        if series.dtype != 'object':
            return series
        
        # 检查唯一值数量
        unique_count = series.nunique()
        total_count = len(series)
        
        # 如果唯一值较少，转换为分类变量
        if unique_count < categorical_threshold and unique_count / total_count < 0.5:
            return series.astype('category')
        
        # 尝试转换为字符串类型（pandas 1.0+）
        try:
            return series.astype('string')
        except:
            return series
    
    @staticmethod
    def reduce_memory_usage(df: pd.DataFrame, 
                          drop_duplicates: bool = False,
                          fill_na: bool = False) -> pd.DataFrame:
        """
        减少DataFrame内存使用的综合方法
        
        Args:
            df: 要优化的DataFrame
            drop_duplicates: 是否删除重复行
            fill_na: 是否填充缺失值
            
        Returns:
            优化后的DataFrame
        """
        if df.empty:
            return df
        
        logger = logging.getLogger(__name__)
        original_memory = df.memory_usage(deep=True).sum()
        
        # 1. 优化数据类型
        optimized_df = DataFrameOptimizer.optimize_dtypes(df, aggressive=True)
        
        # 2. 删除重复行
        if drop_duplicates:
            before_dedup = len(optimized_df)
            optimized_df = optimized_df.drop_duplicates()
            after_dedup = len(optimized_df)
            if before_dedup != after_dedup:
                logger.info(f"删除重复行: {before_dedup} -> {after_dedup}")
        
        # 3. 处理缺失值
        if fill_na:
            for col in optimized_df.columns:
                if optimized_df[col].isna().any():
                    if pd.api.types.is_numeric_dtype(optimized_df[col]):
                        optimized_df[col] = optimized_df[col].fillna(0)
                    else:
                        optimized_df[col] = optimized_df[col].fillna('')
        
        # 4. 重置索引以释放内存
        optimized_df = optimized_df.reset_index(drop=True)
        
        # 计算最终优化效果
        final_memory = optimized_df.memory_usage(deep=True).sum()
        total_reduction = (original_memory - final_memory) / original_memory * 100
        
        logger.info(f"DataFrame综合优化完成: "
                   f"{original_memory / (1024*1024):.1f}MB -> "
                   f"{final_memory / (1024*1024):.1f}MB "
                   f"(总共减少 {total_reduction:.1f}%)")
        
        return optimized_df


# 全局内存监控器
_global_memory_monitor: Optional[MemoryMonitor] = None


def get_memory_monitor() -> MemoryMonitor:
    """获取全局内存监控器"""
    global _global_memory_monitor
    if _global_memory_monitor is None:
        _global_memory_monitor = MemoryMonitor()
    return _global_memory_monitor