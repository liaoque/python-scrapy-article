"""
性能基准测试工具

提供涨停统计系统的性能基准测试和监控功能
"""

import time
import asyncio
import logging
import statistics
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import psutil
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..models import LimitUpStatsRequest, StockDailyData
from .performance_optimizations import PerformanceOptimizer, PerformanceConfig


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    test_name: str
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    std_time: float
    throughput: float  # 每秒处理量
    memory_usage_mb: float
    cpu_usage_percent: float
    success_rate: float
    iterations: int
    data_size: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'test_name': self.test_name,
            'total_time': self.total_time,
            'avg_time': self.avg_time,
            'min_time': self.min_time,
            'max_time': self.max_time,
            'std_time': self.std_time,
            'throughput': self.throughput,
            'memory_usage_mb': self.memory_usage_mb,
            'cpu_usage_percent': self.cpu_usage_percent,
            'success_rate': self.success_rate,
            'iterations': self.iterations,
            'data_size': self.data_size,
            'timestamp': self.timestamp
        }


@dataclass
class BenchmarkConfig:
    """基准测试配置"""
    iterations: int = 10
    warmup_iterations: int = 3
    data_sizes: List[int] = field(default_factory=lambda: [100, 500, 1000, 5000])
    concurrent_levels: List[int] = field(default_factory=lambda: [1, 5, 10, 20])
    enable_memory_monitoring: bool = True
    enable_cpu_monitoring: bool = True
    output_file: Optional[str] = None
    detailed_logging: bool = True


class PerformanceBenchmark:
    """性能基准测试器"""
    
    def __init__(self, config: BenchmarkConfig = None, logger: Optional[logging.Logger] = None):
        """
        初始化性能基准测试器
        
        Args:
            config: 基准测试配置
            logger: 日志记录器
        """
        self.config = config or BenchmarkConfig()
        self.logger = logger or logging.getLogger(__name__)
        self.process = psutil.Process(os.getpid())
        self.results: List[BenchmarkResult] = []
        
        # 创建性能优化器实例
        self.optimizer = PerformanceOptimizer()
        
        self.logger.info("性能基准测试器初始化完成")
    
    def generate_test_data(self, size: int, trade_date: str = '20241015') -> pd.DataFrame:
        """
        生成测试数据
        
        Args:
            size: 数据大小
            trade_date: 交易日期
            
        Returns:
            测试数据DataFrame
        """
        stock_data = []
        
        for i in range(size):
            # 生成不同市场的股票代码
            if i % 4 == 0:  # 上海主板
                ts_code = f'60{i:04d}.SH'
            elif i % 4 == 1:  # 深圳主板
                ts_code = f'00{i:04d}.SZ'
            elif i % 4 == 2:  # 科创板
                ts_code = f'688{i:03d}.SH'
            else:  # 北证
                ts_code = f'43{i:04d}.BJ'
            
            # 模拟价格数据
            base_price = 10.0 + (i % 100) * 0.1
            
            # 30%的股票涨停
            if i % 3 == 0:
                close_price = base_price * 1.10  # 10%涨停
                high_price = close_price
                pct_chg = 10.0
            else:
                # 非涨停股票
                close_price = base_price * (1 + (i % 10 - 5) * 0.01)
                high_price = close_price * 1.02
                pct_chg = (close_price - base_price) / base_price * 100
            
            stock_data.append({
                'ts_code': ts_code,
                'trade_date': trade_date,
                'open': base_price,
                'high': high_price,
                'low': base_price * 0.98,
                'close': close_price,
                'pre_close': base_price,
                'change': close_price - base_price,
                'pct_chg': pct_chg,
                'vol': (i % 1000 + 1) * 1000,
                'amount': close_price * (i % 1000 + 1) * 1000,
                'name': f'股票{i:04d}' if i % 20 != 0 else f'ST股票{i:04d}'
            })
        
        return pd.DataFrame(stock_data)
    
    async def benchmark_limit_up_detection(self) -> List[BenchmarkResult]:
        """
        涨停检测性能基准测试
        
        Returns:
            基准测试结果列表
        """
        self.logger.info("开始涨停检测性能基准测试")
        results = []
        
        for data_size in self.config.data_sizes:
            self.logger.info(f"测试数据大小: {data_size}")
            
            # 生成测试数据
            test_data = self.generate_test_data(data_size)
            
            # 预热
            for _ in range(self.config.warmup_iterations):
                await self.optimizer.optimize_limit_up_detection(test_data.copy())
            
            # 正式测试
            times = []
            memory_usages = []
            cpu_usages = []
            success_count = 0
            
            for i in range(self.config.iterations):
                # 监控开始状态
                start_memory = self.process.memory_info().rss / 1024 / 1024
                start_cpu = self.process.cpu_percent()
                
                # 执行测试
                start_time = time.time()
                try:
                    result = await self.optimizer.optimize_limit_up_detection(test_data.copy())
                    elapsed_time = time.time() - start_time
                    times.append(elapsed_time)
                    success_count += 1
                    
                    # 验证结果
                    if not isinstance(result, pd.DataFrame):
                        self.logger.warning(f"测试 {i+1} 返回结果类型异常")
                    
                except Exception as e:
                    elapsed_time = time.time() - start_time
                    times.append(elapsed_time)
                    self.logger.error(f"测试 {i+1} 失败: {e}")
                
                # 监控结束状态
                end_memory = self.process.memory_info().rss / 1024 / 1024
                end_cpu = self.process.cpu_percent()
                
                memory_usages.append(end_memory - start_memory)
                cpu_usages.append(end_cpu)
                
                if self.config.detailed_logging:
                    self.logger.debug(f"测试 {i+1}: {elapsed_time:.3f}s, "
                                    f"内存: {end_memory - start_memory:+.2f}MB")
            
            # 计算统计指标
            if times:
                result = BenchmarkResult(
                    test_name=f'limit_up_detection_{data_size}',
                    total_time=sum(times),
                    avg_time=statistics.mean(times),
                    min_time=min(times),
                    max_time=max(times),
                    std_time=statistics.stdev(times) if len(times) > 1 else 0,
                    throughput=data_size / statistics.mean(times),
                    memory_usage_mb=statistics.mean(memory_usages) if memory_usages else 0,
                    cpu_usage_percent=statistics.mean(cpu_usages) if cpu_usages else 0,
                    success_rate=success_count / self.config.iterations,
                    iterations=self.config.iterations,
                    data_size=data_size
                )
                
                results.append(result)
                self.results.append(result)
                
                self.logger.info(f"数据大小 {data_size} 测试完成: "
                               f"平均时间 {result.avg_time:.3f}s, "
                               f"吞吐量 {result.throughput:.1f} 股票/秒")
        
        return results
    
    async def benchmark_concurrent_processing(self) -> List[BenchmarkResult]:
        """
        并发处理性能基准测试
        
        Returns:
            基准测试结果列表
        """
        self.logger.info("开始并发处理性能基准测试")
        results = []
        
        # 使用中等大小的数据集进行并发测试
        test_data_size = 1000
        test_data = self.generate_test_data(test_data_size)
        
        for concurrent_level in self.config.concurrent_levels:
            self.logger.info(f"测试并发级别: {concurrent_level}")
            
            # 预热
            for _ in range(self.config.warmup_iterations):
                tasks = [
                    self.optimizer.optimize_limit_up_detection(test_data.copy())
                    for _ in range(min(concurrent_level, 3))
                ]
                await asyncio.gather(*tasks)
            
            # 正式测试
            times = []
            memory_usages = []
            cpu_usages = []
            success_count = 0
            
            for i in range(self.config.iterations):
                # 监控开始状态
                start_memory = self.process.memory_info().rss / 1024 / 1024
                start_cpu = self.process.cpu_percent()
                
                # 执行并发测试
                start_time = time.time()
                try:
                    tasks = [
                        self.optimizer.optimize_limit_up_detection(test_data.copy())
                        for _ in range(concurrent_level)
                    ]
                    results_batch = await asyncio.gather(*tasks, return_exceptions=True)
                    elapsed_time = time.time() - start_time
                    times.append(elapsed_time)
                    
                    # 检查成功率
                    successful_tasks = sum(1 for r in results_batch if not isinstance(r, Exception))
                    if successful_tasks == concurrent_level:
                        success_count += 1
                    
                except Exception as e:
                    elapsed_time = time.time() - start_time
                    times.append(elapsed_time)
                    self.logger.error(f"并发测试 {i+1} 失败: {e}")
                
                # 监控结束状态
                end_memory = self.process.memory_info().rss / 1024 / 1024
                end_cpu = self.process.cpu_percent()
                
                memory_usages.append(end_memory - start_memory)
                cpu_usages.append(end_cpu)
                
                if self.config.detailed_logging:
                    self.logger.debug(f"并发测试 {i+1}: {elapsed_time:.3f}s, "
                                    f"并发数 {concurrent_level}")
            
            # 计算统计指标
            if times:
                result = BenchmarkResult(
                    test_name=f'concurrent_processing_{concurrent_level}',
                    total_time=sum(times),
                    avg_time=statistics.mean(times),
                    min_time=min(times),
                    max_time=max(times),
                    std_time=statistics.stdev(times) if len(times) > 1 else 0,
                    throughput=(test_data_size * concurrent_level) / statistics.mean(times),
                    memory_usage_mb=statistics.mean(memory_usages) if memory_usages else 0,
                    cpu_usage_percent=statistics.mean(cpu_usages) if cpu_usages else 0,
                    success_rate=success_count / self.config.iterations,
                    iterations=self.config.iterations,
                    data_size=test_data_size * concurrent_level
                )
                
                results.append(result)
                self.results.append(result)
                
                self.logger.info(f"并发级别 {concurrent_level} 测试完成: "
                               f"平均时间 {result.avg_time:.3f}s, "
                               f"吞吐量 {result.throughput:.1f} 股票/秒")
        
        return results
    
    def benchmark_memory_optimization(self) -> List[BenchmarkResult]:
        """
        内存优化性能基准测试
        
        Returns:
            基准测试结果列表
        """
        self.logger.info("开始内存优化性能基准测试")
        results = []
        
        for data_size in self.config.data_sizes:
            self.logger.info(f"测试内存优化，数据大小: {data_size}")
            
            # 生成测试数据
            test_data = self.generate_test_data(data_size)
            
            # 测试未优化的内存使用
            times_unoptimized = []
            memory_unoptimized = []
            
            for i in range(self.config.iterations):
                start_memory = self.process.memory_info().rss / 1024 / 1024
                start_time = time.time()
                
                # 不使用内存优化
                data_copy = test_data.copy()
                # 模拟处理
                _ = data_copy.memory_usage(deep=True).sum()
                
                elapsed_time = time.time() - start_time
                end_memory = self.process.memory_info().rss / 1024 / 1024
                
                times_unoptimized.append(elapsed_time)
                memory_unoptimized.append(end_memory - start_memory)
                
                del data_copy
            
            # 测试优化后的内存使用
            times_optimized = []
            memory_optimized = []
            
            for i in range(self.config.iterations):
                start_memory = self.process.memory_info().rss / 1024 / 1024
                start_time = time.time()
                
                # 使用内存优化
                data_copy = test_data.copy()
                optimized_data = self.optimizer.memory_optimizer.optimize_dataframe_memory(data_copy)
                _ = optimized_data.memory_usage(deep=True).sum()
                
                elapsed_time = time.time() - start_time
                end_memory = self.process.memory_info().rss / 1024 / 1024
                
                times_optimized.append(elapsed_time)
                memory_optimized.append(end_memory - start_memory)
                
                del data_copy, optimized_data
            
            # 计算优化效果
            if times_unoptimized and times_optimized:
                avg_memory_unoptimized = statistics.mean(memory_unoptimized)
                avg_memory_optimized = statistics.mean(memory_optimized)
                memory_saved = avg_memory_unoptimized - avg_memory_optimized
                
                result = BenchmarkResult(
                    test_name=f'memory_optimization_{data_size}',
                    total_time=sum(times_optimized),
                    avg_time=statistics.mean(times_optimized),
                    min_time=min(times_optimized),
                    max_time=max(times_optimized),
                    std_time=statistics.stdev(times_optimized) if len(times_optimized) > 1 else 0,
                    throughput=data_size / statistics.mean(times_optimized),
                    memory_usage_mb=memory_saved,  # 使用节省的内存作为指标
                    cpu_usage_percent=0,  # 内存优化测试不关注CPU
                    success_rate=1.0,
                    iterations=self.config.iterations,
                    data_size=data_size
                )
                
                results.append(result)
                self.results.append(result)
                
                self.logger.info(f"内存优化测试完成，数据大小 {data_size}: "
                               f"节省内存 {memory_saved:.2f}MB")
        
        return results
    
    async def run_full_benchmark_suite(self) -> Dict[str, List[BenchmarkResult]]:
        """
        运行完整的基准测试套件
        
        Returns:
            基准测试结果字典
        """
        self.logger.info("开始运行完整基准测试套件")
        start_time = datetime.now()
        
        suite_results = {}
        
        try:
            # 1. 涨停检测性能测试
            self.logger.info("=" * 50)
            self.logger.info("1. 涨停检测性能测试")
            suite_results['limit_up_detection'] = await self.benchmark_limit_up_detection()
            
            # 2. 并发处理性能测试
            self.logger.info("=" * 50)
            self.logger.info("2. 并发处理性能测试")
            suite_results['concurrent_processing'] = await self.benchmark_concurrent_processing()
            
            # 3. 内存优化性能测试
            self.logger.info("=" * 50)
            self.logger.info("3. 内存优化性能测试")
            suite_results['memory_optimization'] = self.benchmark_memory_optimization()
            
            # 生成测试报告
            total_time = (datetime.now() - start_time).total_seconds()
            self.logger.info("=" * 50)
            self.logger.info(f"基准测试套件完成，总耗时: {total_time:.2f}秒")
            
            # 保存结果
            if self.config.output_file:
                self.save_results(self.config.output_file)
            
            return suite_results
            
        except Exception as e:
            self.logger.error(f"基准测试套件执行失败: {e}")
            raise
    
    def save_results(self, filename: str):
        """
        保存测试结果到文件
        
        Args:
            filename: 输出文件名
        """
        try:
            results_data = {
                'benchmark_config': {
                    'iterations': self.config.iterations,
                    'warmup_iterations': self.config.warmup_iterations,
                    'data_sizes': self.config.data_sizes,
                    'concurrent_levels': self.config.concurrent_levels
                },
                'system_info': {
                    'cpu_count': psutil.cpu_count(),
                    'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
                    'python_version': os.sys.version,
                    'platform': os.name
                },
                'results': [result.to_dict() for result in self.results],
                'timestamp': datetime.now().isoformat()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"基准测试结果已保存到: {filename}")
            
        except Exception as e:
            self.logger.error(f"保存测试结果失败: {e}")
    
    def generate_performance_report(self) -> str:
        """
        生成性能报告
        
        Returns:
            性能报告内容
        """
        if not self.results:
            return "没有可用的测试结果"
        
        report_lines = []
        report_lines.append("涨停统计系统性能基准测试报告")
        report_lines.append("=" * 60)
        report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # 系统信息
        report_lines.append("系统信息:")
        report_lines.append(f"  CPU核心数: {psutil.cpu_count()}")
        report_lines.append(f"  总内存: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.1f} GB")
        report_lines.append("")
        
        # 按测试类型分组结果
        test_groups = {}
        for result in self.results:
            test_type = result.test_name.split('_')[0] + '_' + result.test_name.split('_')[1]
            if test_type not in test_groups:
                test_groups[test_type] = []
            test_groups[test_type].append(result)
        
        # 生成各测试类型的报告
        for test_type, results in test_groups.items():
            report_lines.append(f"{test_type.replace('_', ' ').title()} 测试结果:")
            report_lines.append("-" * 40)
            
            for result in results:
                report_lines.append(f"  数据大小/并发级别: {result.data_size}")
                report_lines.append(f"    平均响应时间: {result.avg_time:.3f} 秒")
                report_lines.append(f"    吞吐量: {result.throughput:.1f} 项/秒")
                report_lines.append(f"    内存使用: {result.memory_usage_mb:.2f} MB")
                report_lines.append(f"    成功率: {result.success_rate:.2%}")
                report_lines.append("")
            
            # 计算该测试类型的总体统计
            avg_times = [r.avg_time for r in results]
            throughputs = [r.throughput for r in results]
            
            if avg_times:
                report_lines.append(f"  总体统计:")
                report_lines.append(f"    最快平均时间: {min(avg_times):.3f} 秒")
                report_lines.append(f"    最慢平均时间: {max(avg_times):.3f} 秒")
                report_lines.append(f"    最高吞吐量: {max(throughputs):.1f} 项/秒")
                report_lines.append("")
        
        # 性能建议
        report_lines.append("性能建议:")
        report_lines.append("-" * 20)
        
        # 分析结果并给出建议
        limit_up_results = [r for r in self.results if 'limit_up_detection' in r.test_name]
        if limit_up_results:
            avg_throughput = statistics.mean([r.throughput for r in limit_up_results])
            if avg_throughput < 1000:
                report_lines.append("- 涨停检测吞吐量较低，建议启用并行处理")
            
            max_memory = max([r.memory_usage_mb for r in limit_up_results])
            if max_memory > 500:
                report_lines.append("- 内存使用较高，建议启用内存优化")
        
        concurrent_results = [r for r in self.results if 'concurrent_processing' in r.test_name]
        if concurrent_results:
            best_concurrent = max(concurrent_results, key=lambda x: x.throughput)
            report_lines.append(f"- 最佳并发级别: {best_concurrent.data_size // 1000}")
        
        return "\n".join(report_lines)


class ContinuousPerformanceMonitor:
    """持续性能监控器"""
    
    def __init__(self, monitor_interval: int = 60, logger: Optional[logging.Logger] = None):
        """
        初始化持续性能监控器
        
        Args:
            monitor_interval: 监控间隔（秒）
            logger: 日志记录器
        """
        self.monitor_interval = monitor_interval
        self.logger = logger or logging.getLogger(__name__)
        self.process = psutil.Process(os.getpid())
        self.monitoring = False
        self.performance_data = []
    
    async def start_monitoring(self):
        """开始性能监控"""
        self.monitoring = True
        self.logger.info(f"开始持续性能监控，间隔: {self.monitor_interval}秒")
        
        while self.monitoring:
            try:
                # 收集性能数据
                performance_snapshot = {
                    'timestamp': datetime.now().isoformat(),
                    'memory_rss_mb': self.process.memory_info().rss / 1024 / 1024,
                    'memory_vms_mb': self.process.memory_info().vms / 1024 / 1024,
                    'memory_percent': self.process.memory_percent(),
                    'cpu_percent': self.process.cpu_percent(),
                    'num_threads': self.process.num_threads(),
                    'open_files': len(self.process.open_files()),
                    'connections': len(self.process.connections())
                }
                
                self.performance_data.append(performance_snapshot)
                
                # 保持最近1000个数据点
                if len(self.performance_data) > 1000:
                    self.performance_data = self.performance_data[-1000:]
                
                # 检查异常情况
                self._check_performance_alerts(performance_snapshot)
                
                await asyncio.sleep(self.monitor_interval)
                
            except Exception as e:
                self.logger.error(f"性能监控错误: {e}")
                await asyncio.sleep(self.monitor_interval)
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.monitoring = False
        self.logger.info("停止持续性能监控")
    
    def _check_performance_alerts(self, snapshot: Dict[str, Any]):
        """检查性能告警"""
        # 内存使用告警
        if snapshot['memory_percent'] > 80:
            self.logger.warning(f"内存使用率过高: {snapshot['memory_percent']:.1f}%")
        
        # CPU使用告警
        if snapshot['cpu_percent'] > 90:
            self.logger.warning(f"CPU使用率过高: {snapshot['cpu_percent']:.1f}%")
        
        # 线程数告警
        if snapshot['num_threads'] > 50:
            self.logger.warning(f"线程数过多: {snapshot['num_threads']}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.performance_data:
            return {}
        
        # 计算统计指标
        memory_values = [d['memory_rss_mb'] for d in self.performance_data]
        cpu_values = [d['cpu_percent'] for d in self.performance_data]
        
        return {
            'monitoring_duration_minutes': len(self.performance_data) * self.monitor_interval / 60,
            'data_points': len(self.performance_data),
            'memory_stats': {
                'avg_mb': statistics.mean(memory_values),
                'max_mb': max(memory_values),
                'min_mb': min(memory_values),
                'std_mb': statistics.stdev(memory_values) if len(memory_values) > 1 else 0
            },
            'cpu_stats': {
                'avg_percent': statistics.mean(cpu_values),
                'max_percent': max(cpu_values),
                'min_percent': min(cpu_values),
                'std_percent': statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0
            },
            'latest_snapshot': self.performance_data[-1] if self.performance_data else None
        }