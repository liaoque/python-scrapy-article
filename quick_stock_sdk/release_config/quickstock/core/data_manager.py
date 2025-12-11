"""
数据管理器核心类

负责协调数据源、格式化等功能
"""

import asyncio
from typing import Optional, TYPE_CHECKING, List, Iterator, Callable, Dict, Any
import pandas as pd
import logging
import uuid
import gc

if TYPE_CHECKING:
    from ..config import Config

from .formatter import DataFormatter
from .errors import ErrorHandler
from .scheduler import RequestScheduler, TaskPriority
from ..providers.manager import DataSourceManager
from ..models import DataRequest, LimitUpStatsRequest
from ..utils.memory import (
    MemoryMonitor, GarbageCollectionOptimizer, DataFrameOptimizer,
    StreamProcessor, get_memory_monitor, get_gc_optimizer
)

logger = logging.getLogger(__name__)


class DataManager:
    """
    数据管理核心类
    负责协调数据源、格式化等功能
    """
    
    def __init__(self, config: 'Config'):
        """
        初始化数据管理器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.source_manager = DataSourceManager(config)
        self.formatter = DataFormatter(config)
        self.error_handler = ErrorHandler(config)
        
        # 初始化请求调度器
        self.scheduler = RequestScheduler(
            max_concurrent=config.max_concurrent_requests,
            max_queue_size=1000
        )
        self._scheduler_started = False
        
        # 初始化内存优化组件
        self.memory_monitor = get_memory_monitor()
        self.gc_optimizer = get_gc_optimizer()
        self.stream_processor = StreamProcessor(
            chunk_size=getattr(config, 'stream_chunk_size', 10000),
            memory_limit_mb=getattr(config, 'memory_limit_mb', 500.0)
        )
        
        # 注册内存状态回调
        self.memory_monitor.register_callback('warning', self._on_memory_warning)
        self.memory_monitor.register_callback('critical', self._on_memory_critical)
    
    async def get_data(self, request: DataRequest) -> pd.DataFrame:
        """
        获取数据的核心方法
        
        Args:
            request: 数据请求对象
            
        Returns:
            格式化后的数据
        """
        try:
            # 1. 验证请求参数
            if not self._validate_request(request):
                raise ValueError("请求参数验证失败")
            
            # 2. 检查是否为涨停统计请求，如果是则使用专门的处理逻辑
            if isinstance(request, LimitUpStatsRequest):
                return await self._handle_limit_up_stats_request(request)
            
            # 3. 从数据源获取数据
            raw_data = await self.source_manager.fetch_data(request)
            
            # 4. 格式化数据
            formatted_data = await self.formatter.format_data(raw_data, request.data_type)
            
            return formatted_data
            
        except Exception as e:
            # 使用错误处理器处理异常
            logger.error(f"数据获取失败: {e}")
            return await self.error_handler.handle_with_retry(
                self._get_data_without_cache, request
            )
    
    async def get_data_batch(self, requests: List[DataRequest]) -> List[pd.DataFrame]:
        """
        批量获取数据，支持并发处理和智能调度
        
        Args:
            requests: 数据请求列表
            
        Returns:
            数据结果列表
        """
        if not requests:
            return []
        
        # 使用信号量控制并发数量
        semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        
        async def get_single_data_with_semaphore(request: DataRequest, index: int) -> tuple:
            """带信号量控制的单个数据获取"""
            async with semaphore:
                try:
                    result = await self.get_data(request)
                    return index, result, None
                except Exception as e:
                    logger.error(f"批量请求第{index}个失败: {e}")
                    return index, pd.DataFrame(), e
        
        # 创建任务列表
        tasks = [
            get_single_data_with_semaphore(request, i) 
            for i, request in enumerate(requests)
        ]
        
        # 并发执行所有请求
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 按原始顺序整理结果
        processed_results = [None] * len(requests)
        failed_count = 0
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"批量请求任务异常: {result}")
                failed_count += 1
            else:
                index, data, error = result
                processed_results[index] = data
                if error:
                    failed_count += 1
        
        # 填充None值为空DataFrame
        for i in range(len(processed_results)):
            if processed_results[i] is None:
                processed_results[i] = pd.DataFrame()
        
        logger.info(f"批量请求完成: 总数{len(requests)}, 成功{len(requests) - failed_count}, 失败{failed_count}")
        
        return processed_results
    
    async def get_data_with_scheduler(self, request: DataRequest, 
                                    priority: TaskPriority = TaskPriority.NORMAL) -> pd.DataFrame:
        """
        使用调度器获取数据
        
        Args:
            request: 数据请求对象
            priority: 任务优先级
            
        Returns:
            格式化后的数据
        """
        # 确保调度器已启动
        if not self._scheduler_started:
            await self.scheduler.start()
            self._scheduler_started = True
        
        # 生成任务ID
        task_id = f"data_request_{uuid.uuid4().hex[:8]}"
        
        # 提交任务到调度器
        success = await self.scheduler.submit_task(
            task_id,
            self.get_data,
            request,  # positional argument
            priority=priority,
            max_retries=self.config.max_retries
        )
        
        if not success:
            logger.warning(f"任务提交失败: {task_id}")
            # 降级到直接执行
            return await self.get_data(request)
        
        # 等待任务完成
        try:
            result = await self.scheduler.wait_for_task(task_id, timeout=60.0)
            if result.success:
                return result.result
            else:
                logger.error(f"调度任务失败: {result.error}")
                raise result.error
        except asyncio.TimeoutError:
            logger.error(f"调度任务超时: {task_id}")
            # 降级到直接执行
            return await self.get_data(request)
    
    async def get_data_batch_scheduled(self, requests: List[DataRequest],
                                     priorities: List[TaskPriority] = None) -> List[pd.DataFrame]:
        """
        使用调度器批量获取数据
        
        Args:
            requests: 数据请求列表
            priorities: 优先级列表
            
        Returns:
            数据结果列表
        """
        if not requests:
            return []
        
        # 确保调度器已启动
        if not self._scheduler_started:
            await self.scheduler.start()
            self._scheduler_started = True
        
        # 设置默认优先级
        if priorities is None:
            priorities = [TaskPriority.NORMAL] * len(requests)
        
        if len(priorities) != len(requests):
            raise ValueError("优先级列表长度必须与请求列表长度相同")
        
        # 提交所有任务
        task_ids = []
        for i, (request, priority) in enumerate(zip(requests, priorities)):
            task_id = f"batch_request_{uuid.uuid4().hex[:8]}_{i}"
            
            success = await self.scheduler.submit_task(
                task_id,
                self.get_data,
                request,
                priority=priority,
                max_retries=self.config.max_retries
            )
            
            if success:
                task_ids.append(task_id)
            else:
                task_ids.append(None)  # 标记失败的任务
        
        # 等待所有任务完成
        results = []
        for i, task_id in enumerate(task_ids):
            if task_id is None:
                # 任务提交失败，降级到直接执行
                logger.warning(f"批量任务第{i}个提交失败，降级执行")
                try:
                    result = await self.get_data(requests[i])
                    results.append(result)
                except Exception as e:
                    logger.error(f"降级执行失败: {e}")
                    results.append(pd.DataFrame())
            else:
                try:
                    task_result = await self.scheduler.wait_for_task(task_id, timeout=60.0)
                    if task_result.success:
                        results.append(task_result.result)
                    else:
                        logger.error(f"批量任务第{i}个失败: {task_result.error}")
                        results.append(pd.DataFrame())
                except asyncio.TimeoutError:
                    logger.error(f"批量任务第{i}个超时")
                    results.append(pd.DataFrame())
        
        return results
    
    async def get_data_batch_with_priority(self, requests: List[DataRequest], 
                                         priorities: List[int] = None) -> List[pd.DataFrame]:
        """
        按优先级批量获取数据
        
        Args:
            requests: 数据请求列表
            priorities: 优先级列表（数字越小优先级越高）
            
        Returns:
            数据结果列表
        """
        if not requests:
            return []
        
        # 如果没有提供优先级，使用默认优先级
        if priorities is None:
            priorities = list(range(len(requests)))
        
        if len(priorities) != len(requests):
            raise ValueError("优先级列表长度必须与请求列表长度相同")
        
        # 按优先级排序
        sorted_items = sorted(
            zip(requests, priorities, range(len(requests))), 
            key=lambda x: x[1]
        )
        
        # 分批处理（高优先级先处理）
        batch_size = min(self.config.max_concurrent_requests, len(requests))
        results = [None] * len(requests)
        
        for i in range(0, len(sorted_items), batch_size):
            batch = sorted_items[i:i + batch_size]
            batch_requests = [item[0] for item in batch]
            batch_indices = [item[2] for item in batch]
            
            # 处理当前批次
            batch_results = await self.get_data_batch(batch_requests)
            
            # 将结果放回原始位置
            for j, original_index in enumerate(batch_indices):
                results[original_index] = batch_results[j]
        
        return results
    
    async def _get_data_without_cache(self, request: DataRequest) -> pd.DataFrame:
        """
        直接获取数据（用于错误重试）
        
        Args:
            request: 数据请求对象
            
        Returns:
            格式化后的数据
        """
        # 从数据源获取数据
        raw_data = await self.source_manager.fetch_data(request)
        
        # 格式化数据
        formatted_data = await self.formatter.format_data(raw_data, request.data_type)
        
        return formatted_data

    def _validate_request(self, request: DataRequest) -> bool:
        """
        验证请求参数
        
        Args:
            request: 数据请求对象
            
        Returns:
            验证是否通过
        """
        try:
            return request.validate()
        except Exception as e:
            # 记录验证错误
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"请求参数验证失败: {e}")
            return False
    

    async def refresh_data(self, request: DataRequest) -> pd.DataFrame:
        """
        强制刷新数据
        
        Args:
            request: 数据请求对象
            
        Returns:
            最新的数据
        """
        try:
            # 验证请求参数
            if not self._validate_request(request):
                raise ValueError("请求参数验证失败")
            
            # 直接从数据源获取数据
            raw_data = await self.source_manager.fetch_data(request)
            
            # 格式化数据
            formatted_data = await self.formatter.format_data(raw_data, request.data_type)
            
            return formatted_data
            
        except Exception as e:
            # 使用错误处理器处理异常
            return await self.error_handler.handle_with_retry(
                self._get_data_without_cache, request
            )
    
    def get_scheduler_stats(self) -> dict:
        """获取调度器统计信息"""
        if self._scheduler_started:
            return self.scheduler.get_stats()
        else:
            return {'scheduler_status': 'not_started'}
    
    def get_provider_stats(self) -> dict:
        """获取数据提供者统计信息"""
        if self._scheduler_started:
            return self.scheduler.get_provider_stats()
        else:
            return {}
    
    def _on_memory_warning(self, stats):
        """内存警告回调"""
        logger.warning(f"内存使用警告: 进程内存{stats.process_memory_mb:.1f}MB, "
                      f"系统内存使用率{stats.memory_percent:.1f}%")
        
        # 执行轻量级垃圾回收
        self.gc_optimizer.force_gc(0)
    
    def _on_memory_critical(self, stats):
        """内存临界回调"""
        logger.critical(f"内存使用临界: 进程内存{stats.process_memory_mb:.1f}MB, "
                       f"系统内存使用率{stats.memory_percent:.1f}%")
        
        # 执行完整垃圾回收
        self.gc_optimizer.force_gc()
    
    async def get_data_streaming(self, request: DataRequest, 
                               chunk_size: Optional[int] = None) -> Iterator[pd.DataFrame]:
        """
        流式获取数据，适用于大数据集
        
        Args:
            request: 数据请求对象
            chunk_size: 数据块大小，None使用默认值
            
        Yields:
            数据块
        """
        try:
            # 验证请求参数
            if not self._validate_request(request):
                raise ValueError("请求参数验证失败")
            
            # 从数据源获取数据
            raw_data = await self.source_manager.fetch_data(request)
            
            # 流式格式化和返回数据
            def format_processor(chunk):
                # 使用异步格式化器的同步版本
                return self.formatter.format_data_sync(chunk, request.data_type)
            
            for chunk in self.stream_processor.process_dataframe_chunks(
                raw_data, format_processor, optimize_memory=True
            ):
                yield chunk
            
        except Exception as e:
            logger.error(f"流式数据获取失败: {e}")
            raise
    
    async def get_data_with_memory_optimization(self, request: DataRequest) -> pd.DataFrame:
        """
        获取数据并进行内存优化
        
        Args:
            request: 数据请求对象
            
        Returns:
            内存优化后的数据
        """
        with self.memory_monitor.monitor_context():
            # 获取原始数据
            data = await self.get_data(request)
            
            # 优化数据类型
            if not data.empty:
                optimized_data = DataFrameOptimizer.optimize_dtypes(
                    data, 
                    aggressive=getattr(self.config, 'aggressive_memory_optimization', False)
                )
                return optimized_data
            
            return data
    
    async def get_data_batch_memory_efficient(self, requests: List[DataRequest]) -> List[pd.DataFrame]:
        """
        内存高效的批量数据获取
        
        Args:
            requests: 数据请求列表
            
        Returns:
            数据结果列表
        """
        if not requests:
            return []
        
        # 使用流式处理器进行批量处理
        def batch_processor(request_batch):
            # 创建异步任务
            async def process_batch():
                tasks = [self.get_data_with_memory_optimization(req) for req in request_batch]
                return await asyncio.gather(*tasks, return_exceptions=True)
            
            # 运行异步任务
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果在异步环境中，创建新的事件循环
                import threading
                import concurrent.futures
                
                def run_async():
                    new_loop = asyncio.new_event_loop()
                    try:
                        return new_loop.run_until_complete(process_batch())
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_async)
                    return future.result()
            else:
                return loop.run_until_complete(process_batch())
        
        # 流式批量处理
        all_results = []
        for batch_results in self.stream_processor.batch_process_requests(
            requests, batch_processor, 
            batch_size=getattr(self.config, 'memory_batch_size', 50)
        ):
            # 处理异常结果
            processed_results = []
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"批量请求失败: {result}")
                    processed_results.append(pd.DataFrame())
                else:
                    processed_results.append(result)
            
            all_results.extend(processed_results)
        
        return all_results
    
    def optimize_memory_usage(self):
        """优化内存使用"""
        logger.info("开始优化内存使用")
        
        # 执行垃圾回收
        collected = self.gc_optimizer.force_gc()
        
        # 获取内存统计
        stats = self.memory_monitor.get_memory_stats()
        
        logger.info(f"内存优化完成: 回收{collected}个对象, "
                   f"当前进程内存: {stats.process_memory_mb:.1f}MB")
        
        return stats
    
    def get_memory_stats(self) -> dict:
        """获取内存统计信息"""
        memory_stats = self.memory_monitor.get_memory_stats()
        gc_stats = self.gc_optimizer.get_gc_stats()
        
        return {
            'memory': {
                'process_memory_mb': memory_stats.process_memory_mb,
                'system_memory_percent': memory_stats.memory_percent,
                'available_memory_mb': memory_stats.available_memory_mb
            },
            'garbage_collection': gc_stats
        }
    
    async def _handle_limit_up_stats_request(self, request: LimitUpStatsRequest) -> pd.DataFrame:
        """
        处理涨停统计请求的专门逻辑
        
        Args:
            request: 涨停统计请求
            
        Returns:
            处理后的数据（实际上会通过LimitUpStatsService处理）
        """
        from ..services.limit_up_stats_service import LimitUpStatsService
        
        # 创建涨停统计服务实例
        limit_up_service = LimitUpStatsService(self, logger)
        
        try:
            # 获取涨停统计
            stats_result = await limit_up_service.get_daily_limit_up_stats(request)
            
            # 将统计结果转换为DataFrame格式以保持接口一致性
            stats_dict = stats_result.to_dict()
            
            # 创建包含统计信息的DataFrame
            stats_df = pd.DataFrame([{
                'trade_date': stats_dict['trade_date'],
                'total': stats_dict['total'],
                'non_st': stats_dict['non_st'],
                'shanghai': stats_dict['shanghai'],
                'shenzhen': stats_dict['shenzhen'],
                'star': stats_dict['star'],
                'beijing': stats_dict['beijing'],
                'st': stats_dict['st'],
                'limit_up_stocks': ','.join(stats_dict['limit_up_stocks']),
                'market_breakdown': str(stats_dict['market_breakdown']),
                'created_at': stats_dict['created_at'],
                'updated_at': stats_dict['updated_at']
            }])
            
            logger.info(f"涨停统计请求处理完成: {request.trade_date}, 总计: {stats_result.total}")
            return stats_df
            
        except Exception as e:
            logger.error(f"涨停统计请求处理失败: {e}")
            # 返回空DataFrame以保持接口一致性
            return pd.DataFrame()
    
    async def get_limit_up_stats_with_fallback(self, request: LimitUpStatsRequest) -> pd.DataFrame:
        """
        获取涨停统计数据，支持多数据源fallback
        
        Args:
            request: 涨停统计请求
            
        Returns:
            涨停统计数据
        """
        try:
            # 使用专门的处理逻辑
            result_df = await self._handle_limit_up_stats_request(request)
            
            return result_df
            
        except Exception as e:
            logger.error(f"涨停统计数据获取失败: {e}")
            # 使用错误处理器进行重试
            return await self.error_handler.handle_with_retry(
                self._handle_limit_up_stats_request, request
            )
    
    async def get_stock_data_with_coordination(self, trade_date: str, 
                                             timeout: int = 30) -> pd.DataFrame:
        """
        协调多个数据源获取股票日线数据
        
        Args:
            trade_date: 交易日期
            timeout: 超时时间
            
        Returns:
            股票日线数据
        """
        # 创建股票日线数据请求
        stock_request = DataRequest(
            data_type='stock_daily',
            start_date=trade_date,
            end_date=trade_date,
            extra_params={
                'fields': [
                    'ts_code', 'trade_date', 'open', 'high', 'low', 'close', 
                    'pre_close', 'change', 'pct_chg', 'vol', 'amount'
                ],
                'timeout': timeout
            }
        )
        
        # 创建股票基础信息请求
        basic_request = DataRequest(
            data_type='stock_basic',
            extra_params={
                'fields': ['ts_code', 'name'],
                'timeout': timeout
            }
        )
        
        try:
            # 并发获取股票日线数据和基础信息
            stock_data_task = self.get_data(stock_request)
            basic_data_task = self.get_data(basic_request)
            
            # 使用超时控制
            stock_data, basic_data = await asyncio.wait_for(
                asyncio.gather(stock_data_task, basic_data_task, return_exceptions=True),
                timeout=timeout
            )
            
            # 处理异常结果
            if isinstance(stock_data, Exception):
                logger.error(f"获取股票日线数据失败: {stock_data}")
                stock_data = pd.DataFrame()
            
            if isinstance(basic_data, Exception):
                logger.warning(f"获取股票基础信息失败: {basic_data}")
                basic_data = pd.DataFrame()
            
            # 合并数据
            if not stock_data.empty and not basic_data.empty:
                merged_data = stock_data.merge(
                    basic_data[['ts_code', 'name']], 
                    on='ts_code', 
                    how='left'
                )
                merged_data['name'] = merged_data['name'].fillna('未知')
            elif not stock_data.empty:
                merged_data = stock_data.copy()
                merged_data['name'] = '未知'
            else:
                merged_data = pd.DataFrame()
            
            logger.info(f"协调获取 {trade_date} 股票数据完成: {len(merged_data)} 只股票")
            return merged_data
            
        except asyncio.TimeoutError:
            logger.error(f"获取 {trade_date} 股票数据超时")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"协调获取股票数据失败: {e}")
            return pd.DataFrame()
    
    def get_data_source_priority(self, data_type: str) -> List[str]:
        """
        获取指定数据类型的数据源优先级
        
        Args:
            data_type: 数据类型
            
        Returns:
            数据源优先级列表
        """
        return self.source_manager._get_provider_priority(data_type)
    
    def get_data_source_health(self) -> Dict[str, Any]:
        """
        获取所有数据源的健康状态
        
        Returns:
            数据源健康状态字典
        """
        return {
            'provider_health': self.source_manager.get_provider_health(),
            'provider_stats': self.source_manager.get_provider_stats(),
            'coordination_stats': self.source_manager.get_coordination_stats()
        }
    
    async def test_data_source_connectivity(self) -> Dict[str, bool]:
        """
        测试所有数据源的连通性
        
        Returns:
            连通性测试结果
        """
        return await self.source_manager.health_check_all()
    
    def set_data_source_fallback_strategy(self, strategy: str):
        """
        设置数据源fallback策略
        
        Args:
            strategy: fallback策略名称
        """
        from ..providers.manager import FallbackStrategy
        
        try:
            fallback_strategy = FallbackStrategy(strategy)
            self.source_manager.set_fallback_strategy(fallback_strategy)
            logger.info(f"设置数据源fallback策略: {strategy}")
        except ValueError:
            logger.error(f"无效的fallback策略: {strategy}")
    
    def enable_circuit_breaker(self, threshold: float = 0.5, timeout: int = 300):
        """
        启用熔断器机制
        
        Args:
            threshold: 失败率阈值
            timeout: 熔断超时时间（秒）
        """
        self.source_manager.circuit_breaker_enabled = True
        self.source_manager.circuit_breaker_threshold = threshold
        self.source_manager.circuit_breaker_timeout = timeout
        logger.info(f"启用熔断器: 阈值={threshold}, 超时={timeout}s")
    
    def disable_circuit_breaker(self):
        """禁用熔断器机制"""
        self.source_manager.circuit_breaker_enabled = False
        logger.info("禁用熔断器")
    
    async def close(self):
        """关闭数据管理器"""
        if self._scheduler_started:
            await self.scheduler.stop()
            self._scheduler_started = False
        
        # 执行最终的内存清理
        self.optimize_memory_usage()
        
        # 关闭其他组件
        await self.source_manager.close()