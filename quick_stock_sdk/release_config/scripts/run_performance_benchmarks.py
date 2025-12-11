#!/usr/bin/env python3
"""
财务报告性能基准测试脚本

运行各种性能测试和基准测试，生成性能报告
"""

import asyncio
import time
import json
import sys
import os
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Any

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from quickstock.utils.performance_monitor import PerformanceMonitor, AdaptiveRateLimiter
from quickstock.utils.memory_optimizer import (
    MemoryMonitor, ChunkedDataProcessor, DataFrameOptimizer, 
    memory_efficient_processing
)


class PerformanceBenchmarkRunner:
    """性能基准测试运行器"""
    
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
        
    async def run_all_benchmarks(self) -> Dict[str, Any]:
        """运行所有基准测试"""
        print("开始运行财务报告性能基准测试...")
        print("=" * 60)
        
        # 1. 内存优化基准测试
        print("\n1. 运行内存优化基准测试...")
        self.results['memory_optimization'] = await self.benchmark_memory_optimization()
        
        # 2. 数据处理性能基准测试
        print("\n2. 运行数据处理性能基准测试...")
        self.results['data_processing'] = await self.benchmark_data_processing()
        
        # 3. 并发处理基准测试
        print("\n3. 运行并发处理基准测试...")
        self.results['concurrent_processing'] = await self.benchmark_concurrent_processing()
        

        
        # 5. 自适应速率限制基准测试
        print("\n5. 运行自适应速率限制基准测试...")
        self.results['rate_limiting'] = await self.benchmark_rate_limiting()
        
        # 6. 大数据集处理基准测试
        print("\n6. 运行大数据集处理基准测试...")
        self.results['large_dataset'] = await self.benchmark_large_dataset_processing()
        
        # 生成总结报告
        self.results['summary'] = self.generate_summary()
        
        print("\n" + "=" * 60)
        print("所有基准测试完成!")
        
        return self.results
    
    async def benchmark_memory_optimization(self) -> Dict[str, Any]:
        """内存优化基准测试"""
        results = {}
        
        # 测试不同大小的数据集
        dataset_sizes = [1000, 5000, 10000, 50000]
        
        for size in dataset_sizes:
            print(f"  测试数据集大小: {size:,} 行")
            
            # 创建测试数据
            df = pd.DataFrame({
                'int_small': np.random.randint(0, 100, size),
                'int_large': np.random.randint(0, 1000000, size),
                'float_data': np.random.random(size) * 1000,
                'category': np.random.choice(['A', 'B', 'C', 'D', 'E'], size),
                'text': [f'text_{i % 100}' for i in range(size)]
            })
            
            # 记录原始内存使用
            original_memory = df.memory_usage(deep=True).sum()
            
            # 执行优化
            start_time = time.time()
            optimized_df = DataFrameOptimizer.optimize_dtypes(df, aggressive=True)
            optimization_time = time.time() - start_time
            
            # 记录优化后内存使用
            optimized_memory = optimized_df.memory_usage(deep=True).sum()
            memory_reduction = (original_memory - optimized_memory) / original_memory
            
            results[f'size_{size}'] = {
                'original_memory_mb': round(original_memory / (1024 * 1024), 2),
                'optimized_memory_mb': round(optimized_memory / (1024 * 1024), 2),
                'memory_reduction_percent': round(memory_reduction * 100, 2),
                'optimization_time_seconds': round(optimization_time, 3),
                'throughput_rows_per_second': round(size / optimization_time, 0)
            }
            
            print(f"    内存减少: {memory_reduction:.1%}, 处理时间: {optimization_time:.3f}s")
        
        return results
    
    async def benchmark_data_processing(self) -> Dict[str, Any]:
        """数据处理性能基准测试"""
        results = {}
        
        # 测试分块处理
        chunk_sizes = [500, 1000, 2000, 5000]
        data_size = 20000
        
        # 创建大数据集
        large_df = pd.DataFrame({
            'value1': np.random.random(data_size),
            'value2': np.random.random(data_size),
            'category': np.random.choice(['A', 'B', 'C'], data_size)
        })
        
        def process_chunk(chunk):
            """示例处理函数：计算分组统计"""
            return chunk.groupby('category').agg({
                'value1': ['mean', 'sum'],
                'value2': ['mean', 'sum']
            }).reset_index()
        
        for chunk_size in chunk_sizes:
            print(f"  测试分块大小: {chunk_size:,}")
            
            processor = ChunkedDataProcessor(chunk_size=chunk_size, memory_limit_mb=100.0)
            
            start_time = time.time()
            result = processor.process_dataframe_chunks(large_df, process_chunk)
            processing_time = time.time() - start_time
            
            results[f'chunk_size_{chunk_size}'] = {
                'processing_time_seconds': round(processing_time, 3),
                'throughput_rows_per_second': round(data_size / processing_time, 0),
                'result_rows': len(result),
                'chunks_processed': (data_size + chunk_size - 1) // chunk_size
            }
            
            print(f"    处理时间: {processing_time:.3f}s, 吞吐量: {data_size/processing_time:.0f} 行/秒")
        
        return results
    
    async def benchmark_concurrent_processing(self) -> Dict[str, Any]:
        """并发处理基准测试"""
        results = {}
        
        # 测试不同并发级别
        concurrency_levels = [1, 5, 10, 20, 50]
        
        for concurrency in concurrency_levels:
            print(f"  测试并发级别: {concurrency}")
            
            monitor = PerformanceMonitor()
            
            async def simulate_task(task_id):
                async with monitor.measure_operation(f"task_{task_id}"):
                    # 模拟数据处理
                    await asyncio.sleep(0.1 + np.random.random() * 0.05)
                    
                    # 模拟偶尔的失败
                    if np.random.random() < 0.05:  # 5% 失败率
                        raise Exception("Simulated processing error")
            
            # 执行并发任务
            start_time = time.time()
            tasks = [simulate_task(i) for i in range(concurrency * 10)]  # 每个并发级别10个任务
            
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            # 分析结果
            successful_tasks = sum(1 for r in results_list if not isinstance(r, Exception))
            failed_tasks = len(results_list) - successful_tasks
            
            stats = monitor.get_performance_summary()
            
            results[f'concurrency_{concurrency}'] = {
                'total_time_seconds': round(total_time, 3),
                'successful_tasks': successful_tasks,
                'failed_tasks': failed_tasks,
                'success_rate': round(stats['success_rate'], 4),
                'average_response_time': round(stats['average_response_time'], 4),
                'throughput_tasks_per_second': round(len(tasks) / total_time, 2)
            }
            
            print(f"    成功率: {stats['success_rate']:.1%}, 平均响应时间: {stats['average_response_time']:.3f}s")
        
        return results
    

    
    async def benchmark_rate_limiting(self) -> Dict[str, Any]:
        """自适应速率限制基准测试"""
        results = {}
        
        # 测试不同的初始速率
        initial_rates = [1.0, 2.0, 5.0, 10.0]
        
        for rate in initial_rates:
            print(f"  测试初始速率: {rate} req/s")
            
            limiter = AdaptiveRateLimiter(initial_rate=rate, min_rate=0.5, max_rate=20.0)
            
            # 模拟请求序列
            request_count = 50
            start_time = time.time()
            
            for i in range(request_count):
                await limiter.acquire()
                
                # 模拟响应时间和成功率
                response_time = 0.1 + np.random.random() * 0.2
                success = np.random.random() > 0.1  # 90% 成功率
                error_type = None if success else "TestError"
                
                limiter.record_response(response_time, success, error_type)
            
            total_time = time.time() - start_time
            final_rate = limiter.current_rate
            
            stats = limiter.get_stats()
            
            results[f'initial_rate_{rate}'] = {
                'initial_rate': rate,
                'final_rate': round(final_rate, 2),
                'rate_adjustment': round((final_rate - rate) / rate * 100, 2),
                'total_time_seconds': round(total_time, 3),
                'actual_throughput': round(request_count / total_time, 2),
                'recent_success_rate': stats['recent_success_rate'],
                'recent_avg_response_time': stats['recent_avg_response_time']
            }
            
            print(f"    最终速率: {final_rate:.2f} req/s, 实际吞吐量: {request_count/total_time:.2f} req/s")
        
        return results
    
    async def benchmark_large_dataset_processing(self) -> Dict[str, Any]:
        """大数据集处理基准测试"""
        results = {}
        
        # 测试不同大小的数据集
        dataset_sizes = [10000, 50000, 100000, 500000]
        
        for size in dataset_sizes:
            print(f"  测试数据集大小: {size:,} 行")
            
            # 创建大数据集
            with memory_efficient_processing(f"创建{size:,}行数据集"):
                large_df = pd.DataFrame({
                    'ts_code': [f'00000{i%100:02d}.SZ' for i in range(size)],
                    'report_date': pd.date_range('2020-01-01', periods=size, freq='D').strftime('%Y%m%d'),
                    'total_revenue': np.random.random(size) * 1000000,
                    'net_profit': np.random.random(size) * 100000,
                    'total_assets': np.random.random(size) * 5000000,
                    'eps': np.random.random(size) * 10,
                    'roe': np.random.random(size) * 0.2
                })
            
            # 记录内存使用
            memory_monitor = MemoryMonitor()
            initial_memory = memory_monitor.get_memory_usage()
            
            # 测试数据处理性能
            start_time = time.time()
            
            with memory_efficient_processing(f"处理{size:,}行数据"):
                # 数据类型优化
                optimized_df = DataFrameOptimizer.optimize_dtypes(large_df)
                
                # 分组聚合操作
                summary = optimized_df.groupby('ts_code').agg({
                    'total_revenue': ['mean', 'sum', 'count'],
                    'net_profit': ['mean', 'sum'],
                    'eps': ['mean', 'std']
                })
            
            processing_time = time.time() - start_time
            final_memory = memory_monitor.get_memory_usage()
            
            # 计算内存使用
            memory_used = final_memory.process_mb - initial_memory.process_mb
            
            results[f'size_{size}'] = {
                'processing_time_seconds': round(processing_time, 3),
                'throughput_rows_per_second': round(size / processing_time, 0),
                'memory_used_mb': round(memory_used, 2),
                'memory_efficiency_mb_per_1k_rows': round(memory_used / (size / 1000), 3),
                'summary_rows': len(summary),
                'unique_stocks': optimized_df['ts_code'].nunique()
            }
            
            print(f"    处理时间: {processing_time:.3f}s, 内存使用: {memory_used:.1f}MB")
            
            # 清理内存
            del large_df, optimized_df, summary
            import gc
            gc.collect()
        
        return results
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成基准测试总结"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        summary = {
            'test_start_time': self.start_time.isoformat(),
            'test_end_time': end_time.isoformat(),
            'total_duration_seconds': round(total_duration, 2),
            'test_categories': len(self.results) - 1,  # 减去summary本身
            'key_findings': self.extract_key_findings()
        }
        
        return summary
    
    def extract_key_findings(self) -> Dict[str, str]:
        """提取关键发现"""
        findings = {}
        
        # 内存优化发现
        if 'memory_optimization' in self.results:
            memory_results = self.results['memory_optimization']
            max_reduction = max(
                result['memory_reduction_percent'] 
                for result in memory_results.values()
            )
            findings['memory_optimization'] = f"最大内存减少: {max_reduction:.1f}%"
        
        # 数据处理发现
        if 'data_processing' in self.results:
            processing_results = self.results['data_processing']
            best_throughput = max(
                result['throughput_rows_per_second']
                for result in processing_results.values()
            )
            findings['data_processing'] = f"最佳处理吞吐量: {best_throughput:,.0f} 行/秒"
        
        # 并发处理发现
        if 'concurrent_processing' in self.results:
            concurrent_results = self.results['concurrent_processing']
            best_concurrency = max(
                concurrent_results.keys(),
                key=lambda k: concurrent_results[k]['throughput_tasks_per_second']
            )
            best_throughput = concurrent_results[best_concurrency]['throughput_tasks_per_second']
            findings['concurrent_processing'] = f"最佳并发配置: {best_concurrency.split('_')[1]}, 吞吐量: {best_throughput:.1f} 任务/秒"
        
        return findings
    
    def save_results(self, output_file: str = None):
        """保存测试结果"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"performance_benchmark_results_{timestamp}.json"
        
        output_path = Path(__file__).parent.parent / "performance_reports" / output_file
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n基准测试结果已保存到: {output_path}")
        
        # 同时生成可读的文本报告
        text_file = output_path.with_suffix('.txt')
        self.generate_text_report(text_file)
        print(f"文本报告已保存到: {text_file}")
    
    def generate_text_report(self, output_file: Path):
        """生成文本格式的报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("财务报告性能基准测试报告\n")
            f.write("=" * 50 + "\n\n")
            
            # 测试概要
            summary = self.results.get('summary', {})
            f.write(f"测试开始时间: {summary.get('test_start_time', 'N/A')}\n")
            f.write(f"测试结束时间: {summary.get('test_end_time', 'N/A')}\n")
            f.write(f"总测试时间: {summary.get('total_duration_seconds', 0):.2f} 秒\n")
            f.write(f"测试类别数: {summary.get('test_categories', 0)}\n\n")
            
            # 关键发现
            f.write("关键发现:\n")
            f.write("-" * 20 + "\n")
            for category, finding in summary.get('key_findings', {}).items():
                f.write(f"• {category}: {finding}\n")
            f.write("\n")
            
            # 详细结果
            for category, results in self.results.items():
                if category == 'summary':
                    continue
                
                f.write(f"{category.replace('_', ' ').title()} 测试结果:\n")
                f.write("-" * 30 + "\n")
                
                if isinstance(results, dict):
                    for test_name, metrics in results.items():
                        f.write(f"  {test_name}:\n")
                        if isinstance(metrics, dict):
                            for metric, value in metrics.items():
                                f.write(f"    {metric}: {value}\n")
                        f.write("\n")
                f.write("\n")


async def main():
    """主函数"""
    runner = PerformanceBenchmarkRunner()
    
    try:
        # 运行所有基准测试
        results = await runner.run_all_benchmarks()
        
        # 保存结果
        runner.save_results()
        
        # 打印总结
        print("\n" + "=" * 60)
        print("基准测试总结:")
        print("-" * 30)
        
        summary = results.get('summary', {})
        print(f"总测试时间: {summary.get('total_duration_seconds', 0):.2f} 秒")
        print(f"测试类别: {summary.get('test_categories', 0)}")
        
        print("\n关键发现:")
        for category, finding in summary.get('key_findings', {}).items():
            print(f"• {category}: {finding}")
        
        print("\n基准测试完成! 🎉")
        
    except KeyboardInterrupt:
        print("\n基准测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n基准测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)