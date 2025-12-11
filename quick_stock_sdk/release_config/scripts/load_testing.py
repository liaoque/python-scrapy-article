#!/usr/bin/env python3
"""
负载测试脚本

测试QuickStock系统在各种负载条件下的行为和性能
包括轻负载、中等负载、重负载和并发负载测试
"""

import sys
import time
import asyncio
import threading
import concurrent.futures
import json
import logging
import psutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from quickstock.client import QuickStockClient
from quickstock.config import Config
from quickstock.utils.performance_monitor import get_performance_monitor
from quickstock.utils.memory_optimizer import memory_efficient_processing


class LoadTester:
    """负载测试器"""
    
    def __init__(self, output_dir: str = None):
        """
        初始化负载测试器
        
        Args:
            output_dir: 输出目录路径
        """
        self.project_root = project_root
        self.output_dir = Path(output_dir) if output_dir else self.project_root / "load_test_reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置日志
        self._setup_logging()
        
        # 初始化客户端
        self.config = Config.load_default()
        self.client = QuickStockClient(self.config)
        
        # 性能监控
        self.performance_monitor = get_performance_monitor()
        
        # 测试数据
        self.test_stocks = [
            '000001.SZ', '000002.SZ', '000858.SZ', '000876.SZ', '002415.SZ',
            '600000.SH', '600036.SH', '600519.SH', '600887.SH', '601318.SH'
        ]
        
        self.test_date_ranges = [
            ('20231201', '20231231'),
            ('20230901', '20230930'),
            ('20230601', '20230630'),
            ('20230301', '20230331'),
            ('20221201', '20221231')
        ]
        
        # 测试结果
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self._get_system_info(),
            'test_scenarios': {},
            'performance_metrics': {},
            'summary': {
                'total_scenarios': 0,
                'passed_scenarios': 0,
                'failed_scenarios': 0,
                'overall_success_rate': 0.0
            }
        }
    
    def _setup_logging(self):
        """设置日志配置"""
        log_file = self.output_dir / f"load_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"负载测试器初始化完成，日志文件: {log_file}")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'disk_total': psutil.disk_usage('/').total if sys.platform != 'win32' else psutil.disk_usage('C:').total,
            'python_version': sys.version,
            'platform': sys.platform
        }
    
    async def run_all_load_tests(self) -> Dict[str, Any]:
        """
        运行所有负载测试场景
        
        Returns:
            测试结果字典
        """
        self.logger.info("开始负载测试")
        
        try:
            # 1. 轻负载测试
            self.logger.info("执行轻负载测试...")
            light_load_results = await self._run_light_load_test()
            self.test_results['test_scenarios']['light_load'] = light_load_results
            
            # 2. 中等负载测试
            self.logger.info("执行中等负载测试...")
            medium_load_results = await self._run_medium_load_test()
            self.test_results['test_scenarios']['medium_load'] = medium_load_results
            
            # 3. 重负载测试
            self.logger.info("执行重负载测试...")
            heavy_load_results = await self._run_heavy_load_test()
            self.test_results['test_scenarios']['heavy_load'] = heavy_load_results
            
            # 4. 并发负载测试
            self.logger.info("执行并发负载测试...")
            concurrent_load_results = await self._run_concurrent_load_test()
            self.test_results['test_scenarios']['concurrent_load'] = concurrent_load_results
            
            # 5. 持续负载测试
            self.logger.info("执行持续负载测试...")
            sustained_load_results = await self._run_sustained_load_test()
            self.test_results['test_scenarios']['sustained_load'] = sustained_load_results
            
            # 6. 峰值负载测试
            self.logger.info("执行峰值负载测试...")
            peak_load_results = await self._run_peak_load_test()
            self.test_results['test_scenarios']['peak_load'] = peak_load_results
            
            # 7. 收集性能指标
            self.test_results['performance_metrics'] = self._collect_performance_metrics()
            
            # 8. 计算汇总统计
            self._calculate_summary_statistics()
            
            # 9. 生成测试报告
            self._generate_load_test_report()
            
            self.logger.info(f"负载测试完成，总体成功率: {self.test_results['summary']['overall_success_rate']:.2%}")
            
            return self.test_results
            
        except Exception as e:
            self.logger.error(f"负载测试失败: {e}")
            raise
    
    async def _run_light_load_test(self) -> Dict[str, Any]:
        """轻负载测试：单个请求，低频率"""
        scenario_name = "轻负载测试"
        self.logger.info(f"开始{scenario_name}")
        
        start_time = time.time()
        results = {
            'scenario_name': scenario_name,
            'description': '单个股票查询，低频率请求',
            'test_parameters': {
                'request_count': 20,
                'concurrent_users': 1,
                'request_interval': 1.0  # 1秒间隔
            },
            'results': {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'response_times': [],
                'error_details': []
            },
            'performance_metrics': {},
            'success': False
        }
        
        try:
            request_count = results['test_parameters']['request_count']
            request_interval = results['test_parameters']['request_interval']
            
            for i in range(request_count):
                request_start = time.time()
                
                try:
                    # 单个股票财务报告查询
                    stock_code = self.test_stocks[i % len(self.test_stocks)]
                    start_date, end_date = self.test_date_ranges[i % len(self.test_date_ranges)]
                    
                    financial_data = self.client.get_financial_reports(
                        ts_code=stock_code,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    request_end = time.time()
                    response_time = request_end - request_start
                    
                    results['results']['response_times'].append(response_time)
                    results['results']['successful_requests'] += 1
                    
                    self.logger.debug(f"请求 {i+1}/{request_count} 成功，响应时间: {response_time:.2f}s")
                    
                except Exception as e:
                    request_end = time.time()
                    response_time = request_end - request_start
                    
                    results['results']['response_times'].append(response_time)
                    results['results']['failed_requests'] += 1
                    results['results']['error_details'].append({
                        'request_index': i,
                        'error': str(e),
                        'response_time': response_time
                    })
                    
                    self.logger.warning(f"请求 {i+1}/{request_count} 失败: {e}")
                
                results['results']['total_requests'] += 1
                
                # 请求间隔
                if i < request_count - 1:
                    await asyncio.sleep(request_interval)
            
            # 计算性能指标
            response_times = results['results']['response_times']
            if response_times:
                results['performance_metrics'] = {
                    'avg_response_time': statistics.mean(response_times),
                    'min_response_time': min(response_times),
                    'max_response_time': max(response_times),
                    'median_response_time': statistics.median(response_times),
                    'p95_response_time': self._calculate_percentile(response_times, 95),
                    'success_rate': results['results']['successful_requests'] / results['results']['total_requests']
                }
            
            # 判断测试是否成功
            success_rate = results['performance_metrics'].get('success_rate', 0)
            avg_response_time = results['performance_metrics'].get('avg_response_time', 999)
            
            results['success'] = success_rate >= 0.95 and avg_response_time <= 5.0
            
            end_time = time.time()
            results['total_duration'] = end_time - start_time
            
            self.logger.info(f"{scenario_name}完成: 成功率 {success_rate:.2%}, 平均响应时间 {avg_response_time:.2f}s")
            
            return results
            
        except Exception as e:
            self.logger.error(f"{scenario_name}执行失败: {e}")
            results['error'] = str(e)
            return results
    
    async def _run_medium_load_test(self) -> Dict[str, Any]:
        """中等负载测试：批量请求，中等频率"""
        scenario_name = "中等负载测试"
        self.logger.info(f"开始{scenario_name}")
        
        start_time = time.time()
        results = {
            'scenario_name': scenario_name,
            'description': '批量股票查询，中等频率请求',
            'test_parameters': {
                'request_count': 50,
                'batch_size': 3,
                'concurrent_users': 2,
                'request_interval': 0.5
            },
            'results': {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'response_times': [],
                'error_details': []
            },
            'performance_metrics': {},
            'success': False
        }
        
        try:
            request_count = results['test_parameters']['request_count']
            batch_size = results['test_parameters']['batch_size']
            request_interval = results['test_parameters']['request_interval']
            
            for i in range(request_count):
                request_start = time.time()
                
                try:
                    # 批量股票查询
                    stock_codes = self.test_stocks[:batch_size]
                    start_date, end_date = self.test_date_ranges[i % len(self.test_date_ranges)]
                    
                    batch_data = self.client.get_batch_financial_data(
                        stock_codes=stock_codes,
                        data_types=['financial_reports'],
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    request_end = time.time()
                    response_time = request_end - request_start
                    
                    results['results']['response_times'].append(response_time)
                    
                    # 检查批量请求是否成功
                    if batch_data and batch_data.get('success_count', 0) > 0:
                        results['results']['successful_requests'] += 1
                    else:
                        results['results']['failed_requests'] += 1
                    
                    self.logger.debug(f"批量请求 {i+1}/{request_count} 完成，响应时间: {response_time:.2f}s")
                    
                except Exception as e:
                    request_end = time.time()
                    response_time = request_end - request_start
                    
                    results['results']['response_times'].append(response_time)
                    results['results']['failed_requests'] += 1
                    results['results']['error_details'].append({
                        'request_index': i,
                        'error': str(e),
                        'response_time': response_time
                    })
                    
                    self.logger.warning(f"批量请求 {i+1}/{request_count} 失败: {e}")
                
                results['results']['total_requests'] += 1
                
                # 请求间隔
                if i < request_count - 1:
                    await asyncio.sleep(request_interval)
            
            # 计算性能指标
            response_times = results['results']['response_times']
            if response_times:
                results['performance_metrics'] = {
                    'avg_response_time': statistics.mean(response_times),
                    'min_response_time': min(response_times),
                    'max_response_time': max(response_times),
                    'median_response_time': statistics.median(response_times),
                    'p95_response_time': self._calculate_percentile(response_times, 95),
                    'success_rate': results['results']['successful_requests'] / results['results']['total_requests']
                }
            
            # 判断测试是否成功
            success_rate = results['performance_metrics'].get('success_rate', 0)
            avg_response_time = results['performance_metrics'].get('avg_response_time', 999)
            
            results['success'] = success_rate >= 0.90 and avg_response_time <= 8.0
            
            end_time = time.time()
            results['total_duration'] = end_time - start_time
            
            self.logger.info(f"{scenario_name}完成: 成功率 {success_rate:.2%}, 平均响应时间 {avg_response_time:.2f}s")
            
            return results
            
        except Exception as e:
            self.logger.error(f"{scenario_name}执行失败: {e}")
            results['error'] = str(e)
            return results
    
    async def _run_heavy_load_test(self) -> Dict[str, Any]:
        """重负载测试：大批量请求，高频率"""
        scenario_name = "重负载测试"
        self.logger.info(f"开始{scenario_name}")
        
        start_time = time.time()
        results = {
            'scenario_name': scenario_name,
            'description': '大批量股票查询，高频率请求',
            'test_parameters': {
                'request_count': 100,
                'batch_size': 5,
                'concurrent_users': 3,
                'request_interval': 0.1
            },
            'results': {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'response_times': [],
                'error_details': []
            },
            'performance_metrics': {},
            'success': False
        }
        
        try:
            request_count = results['test_parameters']['request_count']
            batch_size = results['test_parameters']['batch_size']
            request_interval = results['test_parameters']['request_interval']
            
            for i in range(request_count):
                request_start = time.time()
                
                try:
                    # 大批量股票查询，包含多种数据类型
                    stock_codes = self.test_stocks[:batch_size]
                    start_date, end_date = self.test_date_ranges[i % len(self.test_date_ranges)]
                    
                    batch_data = self.client.get_batch_financial_data(
                        stock_codes=stock_codes,
                        data_types=['financial_reports', 'earnings_forecast', 'flash_reports'],
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    request_end = time.time()
                    response_time = request_end - request_start
                    
                    results['results']['response_times'].append(response_time)
                    
                    # 检查批量请求是否成功
                    if batch_data and batch_data.get('success_count', 0) > 0:
                        results['results']['successful_requests'] += 1
                    else:
                        results['results']['failed_requests'] += 1
                    
                    if i % 10 == 0:
                        self.logger.debug(f"重负载请求 {i+1}/{request_count} 完成，响应时间: {response_time:.2f}s")
                    
                except Exception as e:
                    request_end = time.time()
                    response_time = request_end - request_start
                    
                    results['results']['response_times'].append(response_time)
                    results['results']['failed_requests'] += 1
                    results['results']['error_details'].append({
                        'request_index': i,
                        'error': str(e),
                        'response_time': response_time
                    })
                    
                    if i % 10 == 0:
                        self.logger.warning(f"重负载请求 {i+1}/{request_count} 失败: {e}")
                
                results['results']['total_requests'] += 1
                
                # 请求间隔
                if i < request_count - 1:
                    await asyncio.sleep(request_interval)
            
            # 计算性能指标
            response_times = results['results']['response_times']
            if response_times:
                results['performance_metrics'] = {
                    'avg_response_time': statistics.mean(response_times),
                    'min_response_time': min(response_times),
                    'max_response_time': max(response_times),
                    'median_response_time': statistics.median(response_times),
                    'p95_response_time': self._calculate_percentile(response_times, 95),
                    'success_rate': results['results']['successful_requests'] / results['results']['total_requests']
                }
            
            # 判断测试是否成功（重负载下标准稍微放宽）
            success_rate = results['performance_metrics'].get('success_rate', 0)
            avg_response_time = results['performance_metrics'].get('avg_response_time', 999)
            
            results['success'] = success_rate >= 0.85 and avg_response_time <= 15.0
            
            end_time = time.time()
            results['total_duration'] = end_time - start_time
            
            self.logger.info(f"{scenario_name}完成: 成功率 {success_rate:.2%}, 平均响应时间 {avg_response_time:.2f}s")
            
            return results
            
        except Exception as e:
            self.logger.error(f"{scenario_name}执行失败: {e}")
            results['error'] = str(e)
            return results
    
    async def _run_concurrent_load_test(self) -> Dict[str, Any]:
        """并发负载测试：多线程并发请求"""
        scenario_name = "并发负载测试"
        self.logger.info(f"开始{scenario_name}")
        
        start_time = time.time()
        results = {
            'scenario_name': scenario_name,
            'description': '多线程并发请求测试',
            'test_parameters': {
                'total_requests': 60,
                'concurrent_threads': 6,
                'requests_per_thread': 10
            },
            'results': {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'response_times': [],
                'error_details': []
            },
            'performance_metrics': {},
            'success': False
        }
        
        try:
            concurrent_threads = results['test_parameters']['concurrent_threads']
            requests_per_thread = results['test_parameters']['requests_per_thread']
            
            # 线程安全的结果收集
            results_lock = threading.Lock()
            
            def worker_thread(thread_id: int):
                """工作线程函数"""
                thread_results = {
                    'successful': 0,
                    'failed': 0,
                    'response_times': [],
                    'errors': []
                }
                
                for i in range(requests_per_thread):
                    request_start = time.time()
                    
                    try:
                        # 创建线程专用的客户端实例
                        thread_client = QuickStockClient(self.config)
                        
                        stock_code = self.test_stocks[(thread_id * requests_per_thread + i) % len(self.test_stocks)]
                        start_date, end_date = self.test_date_ranges[i % len(self.test_date_ranges)]
                        
                        financial_data = thread_client.get_financial_reports(
                            ts_code=stock_code,
                            start_date=start_date,
                            end_date=end_date
                        )
                        
                        request_end = time.time()
                        response_time = request_end - request_start
                        
                        thread_results['response_times'].append(response_time)
                        thread_results['successful'] += 1
                        
                    except Exception as e:
                        request_end = time.time()
                        response_time = request_end - request_start
                        
                        thread_results['response_times'].append(response_time)
                        thread_results['failed'] += 1
                        thread_results['errors'].append({
                            'thread_id': thread_id,
                            'request_index': i,
                            'error': str(e),
                            'response_time': response_time
                        })
                
                # 合并结果到主结果中
                with results_lock:
                    results['results']['total_requests'] += requests_per_thread
                    results['results']['successful_requests'] += thread_results['successful']
                    results['results']['failed_requests'] += thread_results['failed']
                    results['results']['response_times'].extend(thread_results['response_times'])
                    results['results']['error_details'].extend(thread_results['errors'])
            
            # 启动并发线程
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_threads) as executor:
                futures = [executor.submit(worker_thread, i) for i in range(concurrent_threads)]
                concurrent.futures.wait(futures)
            
            # 计算性能指标
            response_times = results['results']['response_times']
            if response_times:
                results['performance_metrics'] = {
                    'avg_response_time': statistics.mean(response_times),
                    'min_response_time': min(response_times),
                    'max_response_time': max(response_times),
                    'median_response_time': statistics.median(response_times),
                    'p95_response_time': self._calculate_percentile(response_times, 95),
                    'success_rate': results['results']['successful_requests'] / results['results']['total_requests']
                }
            
            # 判断测试是否成功
            success_rate = results['performance_metrics'].get('success_rate', 0)
            avg_response_time = results['performance_metrics'].get('avg_response_time', 999)
            
            results['success'] = success_rate >= 0.80 and avg_response_time <= 20.0
            
            end_time = time.time()
            results['total_duration'] = end_time - start_time
            
            self.logger.info(f"{scenario_name}完成: 成功率 {success_rate:.2%}, 平均响应时间 {avg_response_time:.2f}s")
            
            return results
            
        except Exception as e:
            self.logger.error(f"{scenario_name}执行失败: {e}")
            results['error'] = str(e)
            return results
    
    async def _run_sustained_load_test(self) -> Dict[str, Any]:
        """持续负载测试：长时间持续请求"""
        scenario_name = "持续负载测试"
        self.logger.info(f"开始{scenario_name}")
        
        start_time = time.time()
        results = {
            'scenario_name': scenario_name,
            'description': '长时间持续负载测试',
            'test_parameters': {
                'duration_minutes': 5,  # 5分钟持续测试
                'requests_per_minute': 12,
                'request_interval': 5.0
            },
            'results': {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'response_times': [],
                'error_details': []
            },
            'performance_metrics': {},
            'success': False
        }
        
        try:
            duration_minutes = results['test_parameters']['duration_minutes']
            request_interval = results['test_parameters']['request_interval']
            end_time = start_time + (duration_minutes * 60)
            
            request_count = 0
            
            while time.time() < end_time:
                request_start = time.time()
                
                try:
                    stock_code = self.test_stocks[request_count % len(self.test_stocks)]
                    start_date, end_date = self.test_date_ranges[request_count % len(self.test_date_ranges)]
                    
                    financial_data = self.client.get_financial_reports(
                        ts_code=stock_code,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    request_end = time.time()
                    response_time = request_end - request_start
                    
                    results['results']['response_times'].append(response_time)
                    results['results']['successful_requests'] += 1
                    
                    if request_count % 10 == 0:
                        self.logger.debug(f"持续负载请求 {request_count+1} 成功，响应时间: {response_time:.2f}s")
                    
                except Exception as e:
                    request_end = time.time()
                    response_time = request_end - request_start
                    
                    results['results']['response_times'].append(response_time)
                    results['results']['failed_requests'] += 1
                    results['results']['error_details'].append({
                        'request_index': request_count,
                        'error': str(e),
                        'response_time': response_time,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    if request_count % 10 == 0:
                        self.logger.warning(f"持续负载请求 {request_count+1} 失败: {e}")
                
                results['results']['total_requests'] += 1
                request_count += 1
                
                # 等待下一个请求
                await asyncio.sleep(request_interval)
            
            # 计算性能指标
            response_times = results['results']['response_times']
            if response_times:
                results['performance_metrics'] = {
                    'avg_response_time': statistics.mean(response_times),
                    'min_response_time': min(response_times),
                    'max_response_time': max(response_times),
                    'median_response_time': statistics.median(response_times),
                    'p95_response_time': self._calculate_percentile(response_times, 95),
                    'success_rate': results['results']['successful_requests'] / results['results']['total_requests'],
                    'requests_per_minute': results['results']['total_requests'] / duration_minutes
                }
            
            # 判断测试是否成功
            success_rate = results['performance_metrics'].get('success_rate', 0)
            avg_response_time = results['performance_metrics'].get('avg_response_time', 999)
            
            results['success'] = success_rate >= 0.90 and avg_response_time <= 10.0
            
            actual_end_time = time.time()
            results['total_duration'] = actual_end_time - start_time
            
            self.logger.info(f"{scenario_name}完成: 成功率 {success_rate:.2%}, 平均响应时间 {avg_response_time:.2f}s")
            
            return results
            
        except Exception as e:
            self.logger.error(f"{scenario_name}执行失败: {e}")
            results['error'] = str(e)
            return results
    
    async def _run_peak_load_test(self) -> Dict[str, Any]:
        """峰值负载测试：短时间内大量请求"""
        scenario_name = "峰值负载测试"
        self.logger.info(f"开始{scenario_name}")
        
        start_time = time.time()
        results = {
            'scenario_name': scenario_name,
            'description': '短时间内大量并发请求',
            'test_parameters': {
                'burst_requests': 30,
                'burst_duration': 10,  # 10秒内完成
                'concurrent_threads': 10
            },
            'results': {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'response_times': [],
                'error_details': []
            },
            'performance_metrics': {},
            'success': False
        }
        
        try:
            burst_requests = results['test_parameters']['burst_requests']
            concurrent_threads = results['test_parameters']['concurrent_threads']
            
            # 线程安全的结果收集
            results_lock = threading.Lock()
            
            def burst_worker(requests_to_make: int):
                """峰值负载工作函数"""
                worker_results = {
                    'successful': 0,
                    'failed': 0,
                    'response_times': [],
                    'errors': []
                }
                
                for i in range(requests_to_make):
                    request_start = time.time()
                    
                    try:
                        # 创建工作线程专用的客户端
                        worker_client = QuickStockClient(self.config)
                        
                        stock_code = self.test_stocks[i % len(self.test_stocks)]
                        start_date, end_date = self.test_date_ranges[0]  # 使用固定日期范围
                        
                        financial_data = worker_client.get_financial_reports(
                            ts_code=stock_code,
                            start_date=start_date,
                            end_date=end_date
                        )
                        
                        request_end = time.time()
                        response_time = request_end - request_start
                        
                        worker_results['response_times'].append(response_time)
                        worker_results['successful'] += 1
                        
                    except Exception as e:
                        request_end = time.time()
                        response_time = request_end - request_start
                        
                        worker_results['response_times'].append(response_time)
                        worker_results['failed'] += 1
                        worker_results['errors'].append({
                            'request_index': i,
                            'error': str(e),
                            'response_time': response_time
                        })
                
                # 合并结果
                with results_lock:
                    results['results']['total_requests'] += requests_to_make
                    results['results']['successful_requests'] += worker_results['successful']
                    results['results']['failed_requests'] += worker_results['failed']
                    results['results']['response_times'].extend(worker_results['response_times'])
                    results['results']['error_details'].extend(worker_results['errors'])
            
            # 计算每个线程的请求数
            requests_per_thread = burst_requests // concurrent_threads
            remaining_requests = burst_requests % concurrent_threads
            
            # 启动峰值负载
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_threads) as executor:
                futures = []
                
                for i in range(concurrent_threads):
                    thread_requests = requests_per_thread
                    if i < remaining_requests:
                        thread_requests += 1
                    
                    futures.append(executor.submit(burst_worker, thread_requests))
                
                # 等待所有线程完成
                concurrent.futures.wait(futures)
            
            # 计算性能指标
            response_times = results['results']['response_times']
            if response_times:
                results['performance_metrics'] = {
                    'avg_response_time': statistics.mean(response_times),
                    'min_response_time': min(response_times),
                    'max_response_time': max(response_times),
                    'median_response_time': statistics.median(response_times),
                    'p95_response_time': self._calculate_percentile(response_times, 95),
                    'success_rate': results['results']['successful_requests'] / results['results']['total_requests']
                }
            
            # 判断测试是否成功（峰值负载标准更宽松）
            success_rate = results['performance_metrics'].get('success_rate', 0)
            avg_response_time = results['performance_metrics'].get('avg_response_time', 999)
            
            results['success'] = success_rate >= 0.70 and avg_response_time <= 30.0
            
            end_time = time.time()
            results['total_duration'] = end_time - start_time
            
            self.logger.info(f"{scenario_name}完成: 成功率 {success_rate:.2%}, 平均响应时间 {avg_response_time:.2f}s")
            
            return results
            
        except Exception as e:
            self.logger.error(f"{scenario_name}执行失败: {e}")
            results['error'] = str(e)
            return results
    
    def _calculate_percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100.0) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            weight = index - lower_index
            return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight
    
    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """收集性能指标"""
        try:
            # 从性能监控器获取指标
            performance_summary = self.performance_monitor.get_performance_summary()
            
            # 收集系统资源使用情况
            system_metrics = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_available': psutil.virtual_memory().available,
                'disk_usage_percent': (
                    psutil.disk_usage('/').percent if sys.platform != 'win32' 
                    else psutil.disk_usage('C:').percent
                ),
                'network_io': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
            }
            
            # 收集客户端统计信息
            client_stats = {
                'cache_stats': self.client.get_cache_stats(),
                'memory_stats': self.client.get_memory_stats(),
                'provider_stats': self.client.get_provider_stats()
            }
            
            return {
                'performance_summary': performance_summary,
                'system_metrics': system_metrics,
                'client_stats': client_stats,
                'collection_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"性能指标收集失败: {e}")
            return {}
    
    def _calculate_summary_statistics(self):
        """计算汇总统计"""
        summary = self.test_results['summary']
        
        for scenario_name, scenario_results in self.test_results['test_scenarios'].items():
            if isinstance(scenario_results, dict):
                summary['total_scenarios'] += 1
                
                if scenario_results.get('success', False):
                    summary['passed_scenarios'] += 1
                else:
                    summary['failed_scenarios'] += 1
        
        # 计算总体成功率
        if summary['total_scenarios'] > 0:
            summary['overall_success_rate'] = summary['passed_scenarios'] / summary['total_scenarios']
    
    def _generate_load_test_report(self):
        """生成负载测试报告"""
        # 生成JSON报告
        json_report_path = self.output_dir / f"load_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        # 生成文本摘要报告
        text_report_path = self.output_dir / f"load_test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self._generate_text_load_report(text_report_path)
        
        self.logger.info(f"负载测试报告已生成:")
        self.logger.info(f"  JSON报告: {json_report_path}")
        self.logger.info(f"  文本摘要: {text_report_path}")
    
    def _generate_text_load_report(self, output_path: Path):
        """生成文本格式的负载测试报告"""
        summary = self.test_results['summary']
        
        content = f"""
QuickStock 负载测试报告
{'='*60}

测试时间: {self.test_results['timestamp']}

系统信息:
  CPU核心数: {self.test_results['system_info']['cpu_count']}
  内存总量: {self.test_results['system_info']['memory_total'] / (1024**3):.2f} GB
  Python版本: {self.test_results['system_info']['python_version']}
  平台: {self.test_results['system_info']['platform']}

总体统计:
  总测试场景: {summary['total_scenarios']}
  通过场景: {summary['passed_scenarios']}
  失败场景: {summary['failed_scenarios']}
  总体成功率: {summary['overall_success_rate']:.2%}

测试场景详情:
{'-'*60}
"""
        
        # 添加各测试场景的详细结果
        for scenario_name, scenario_results in self.test_results['test_scenarios'].items():
            if isinstance(scenario_results, dict):
                content += f"""
{scenario_results.get('scenario_name', scenario_name)}:
  描述: {scenario_results.get('description', 'N/A')}
  状态: {'通过' if scenario_results.get('success', False) else '失败'}
  总请求数: {scenario_results.get('results', {}).get('total_requests', 0)}
  成功请求: {scenario_results.get('results', {}).get('successful_requests', 0)}
  失败请求: {scenario_results.get('results', {}).get('failed_requests', 0)}
  执行时间: {scenario_results.get('total_duration', 0):.2f} 秒
"""
                
                # 添加性能指标
                perf_metrics = scenario_results.get('performance_metrics', {})
                if perf_metrics:
                    content += f"""  性能指标:
    成功率: {perf_metrics.get('success_rate', 0):.2%}
    平均响应时间: {perf_metrics.get('avg_response_time', 0):.2f} 秒
    最小响应时间: {perf_metrics.get('min_response_time', 0):.2f} 秒
    最大响应时间: {perf_metrics.get('max_response_time', 0):.2f} 秒
    95%响应时间: {perf_metrics.get('p95_response_time', 0):.2f} 秒
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='QuickStock 负载测试')
    parser.add_argument('--output-dir', help='输出目录路径')
    
    args = parser.parse_args()
    
    # 创建负载测试器
    tester = LoadTester(output_dir=args.output_dir)
    
    try:
        # 运行负载测试
        results = await tester.run_all_load_tests()
        
        # 输出结果摘要
        summary = results['summary']
        print(f"\n{'='*60}")
        print("负载测试完成!")
        print(f"总测试场景: {summary['total_scenarios']}")
        print(f"通过场景: {summary['passed_scenarios']}")
        print(f"失败场景: {summary['failed_scenarios']}")
        print(f"总体成功率: {summary['overall_success_rate']:.2%}")
        print(f"{'='*60}")
        
        # 根据成功率设置退出码
        exit_code = 0 if summary['overall_success_rate'] >= 0.80 else 1
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"负载测试失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())