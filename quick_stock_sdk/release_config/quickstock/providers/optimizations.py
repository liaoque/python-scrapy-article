"""
数据提供者特定优化

为不同的数据提供者实现特定的优化策略
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime, timedelta
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum

from ..models import DataRequest, LimitUpStatsRequest
from .base import DataProvider


class OptimizationStrategy(Enum):
    """优化策略枚举"""
    BATCH_PROCESSING = "batch_processing"
    PARALLEL_REQUESTS = "parallel_requests"
    REQUEST_DEDUPLICATION = "request_deduplication"
    ADAPTIVE_TIMEOUT = "adaptive_timeout"
    CIRCUIT_BREAKER = "circuit_breaker"


@dataclass
class BatchConfig:
    """批处理配置"""
    batch_size: int = 100
    max_concurrent_batches: int = 3
    batch_delay: float = 0.1  # 批次间延迟（秒）
    enable_parallel_processing: bool = True
    timeout_per_batch: int = 30


@dataclass
class ProviderOptimizationConfig:
    """提供者优化配置"""
    provider_name: str
    enabled_strategies: List[OptimizationStrategy] = field(default_factory=list)
    batch_config: BatchConfig = field(default_factory=BatchConfig)
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: int = 30
    rate_limit_per_second: float = 5.0
    custom_params: Dict[str, Any] = field(default_factory=dict)


class ProviderOptimizer:
    """数据提供者优化器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化优化器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
        self._optimizations: Dict[str, ProviderOptimizationConfig] = {}
        self._rate_limiters: Dict[str, asyncio.Semaphore] = {}
        self._performance_stats: Dict[str, Dict[str, Any]] = {}
    
    def register_optimization(self, config: ProviderOptimizationConfig):
        """
        注册提供者优化配置
        
        Args:
            config: 优化配置
        """
        self._optimizations[config.provider_name] = config
        
        # 初始化速率限制器
        if config.rate_limit_per_second > 0:
            # 使用信号量实现简单的速率限制
            max_concurrent = max(1, int(config.rate_limit_per_second))
            self._rate_limiters[config.provider_name] = asyncio.Semaphore(max_concurrent)
        
        # 初始化性能统计
        self._performance_stats[config.provider_name] = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0,
            'batch_requests': 0,
            'last_request_time': None
        }
        
        self.logger.info(f"注册提供者优化配置: {config.provider_name}")
    
    async def optimize_stock_data_request(self, provider: DataProvider, 
                                        request: LimitUpStatsRequest) -> pd.DataFrame:
        """
        优化股票数据请求
        
        Args:
            provider: 数据提供者
            request: 涨停统计请求
            
        Returns:
            优化后获取的股票数据
        """
        provider_name = provider.get_provider_name()
        config = self._optimizations.get(provider_name)
        
        if not config:
            # 没有优化配置，使用默认方式
            return await self._default_stock_data_request(provider, request)
        
        # 应用优化策略
        return await self._apply_optimizations(provider, request, config)
    
    async def _apply_optimizations(self, provider: DataProvider, 
                                 request: LimitUpStatsRequest,
                                 config: ProviderOptimizationConfig) -> pd.DataFrame:
        """
        应用优化策略
        
        Args:
            provider: 数据提供者
            request: 请求
            config: 优化配置
            
        Returns:
            优化后的数据
        """
        provider_name = provider.get_provider_name()
        start_time = datetime.now()
        
        try:
            # 更新统计
            self._performance_stats[provider_name]['total_requests'] += 1
            self._performance_stats[provider_name]['last_request_time'] = start_time
            

            
            # 2. 应用速率限制
            rate_limiter = self._rate_limiters.get(provider_name)
            if rate_limiter:
                async with rate_limiter:
                    data = await self._execute_optimized_request(provider, request, config)
            else:
                data = await self._execute_optimized_request(provider, request, config)
            

            
            # 更新成功统计
            response_time = (datetime.now() - start_time).total_seconds()
            self._performance_stats[provider_name]['successful_requests'] += 1
            self._performance_stats[provider_name]['total_response_time'] += response_time
            
            self.logger.info(f"优化请求完成: {provider_name} - {request.trade_date}, "
                           f"响应时间: {response_time:.2f}s, 数据量: {len(data)}")
            
            return data
            
        except Exception as e:
            # 更新失败统计
            self._performance_stats[provider_name]['failed_requests'] += 1
            self.logger.error(f"优化请求失败: {provider_name} - {request.trade_date}, 错误: {e}")
            raise
    
    async def _execute_optimized_request(self, provider: DataProvider,
                                       request: LimitUpStatsRequest,
                                       config: ProviderOptimizationConfig) -> pd.DataFrame:
        """
        执行优化的请求
        
        Args:
            provider: 数据提供者
            request: 请求
            config: 优化配置
            
        Returns:
            数据结果
        """
        # 根据优化策略选择执行方式
        if OptimizationStrategy.BATCH_PROCESSING in config.enabled_strategies:
            return await self._batch_stock_data_request(provider, request, config)
        elif OptimizationStrategy.PARALLEL_REQUESTS in config.enabled_strategies:
            return await self._parallel_stock_data_request(provider, request, config)
        else:
            return await self._default_stock_data_request(provider, request)
    
    async def _batch_stock_data_request(self, provider: DataProvider,
                                      request: LimitUpStatsRequest,
                                      config: ProviderOptimizationConfig) -> pd.DataFrame:
        """
        批量股票数据请求
        
        Args:
            provider: 数据提供者
            request: 请求
            config: 优化配置
            
        Returns:
            批量获取的数据
        """
        provider_name = provider.get_provider_name()
        self._performance_stats[provider_name]['batch_requests'] += 1
        
        try:
            # 首先获取股票基础信息
            basic_data = await provider.get_stock_basic()
            if basic_data.empty:
                self.logger.warning(f"{provider_name}: 无法获取股票基础信息")
                return pd.DataFrame()
            
            stock_codes = basic_data['ts_code'].tolist()
            batch_config = config.batch_config
            
            self.logger.info(f"开始批量获取 {len(stock_codes)} 只股票的数据，"
                           f"批次大小: {batch_config.batch_size}")
            
            # 分批处理
            all_data = []
            semaphore = asyncio.Semaphore(batch_config.max_concurrent_batches)
            
            async def process_batch(batch_codes: List[str]) -> List[pd.DataFrame]:
                """处理单个批次"""
                async with semaphore:
                    batch_data = []
                    for code in batch_codes:
                        try:
                            stock_data = await asyncio.wait_for(
                                provider.get_stock_daily(
                                    ts_code=code,
                                    start_date=request.trade_date,
                                    end_date=request.trade_date
                                ),
                                timeout=batch_config.timeout_per_batch
                            )
                            if not stock_data.empty:
                                batch_data.append(stock_data)
                        except asyncio.TimeoutError:
                            self.logger.warning(f"获取股票 {code} 数据超时")
                        except Exception as e:
                            self.logger.debug(f"获取股票 {code} 数据失败: {e}")
                    
                    # 批次间延迟
                    if batch_config.batch_delay > 0:
                        await asyncio.sleep(batch_config.batch_delay)
                    
                    return batch_data
            
            # 创建批次任务
            tasks = []
            for i in range(0, len(stock_codes), batch_config.batch_size):
                batch_codes = stock_codes[i:i + batch_config.batch_size]
                tasks.append(process_batch(batch_codes))
            
            # 并发执行批次
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 收集所有数据
            for result in batch_results:
                if isinstance(result, Exception):
                    self.logger.error(f"批次处理失败: {result}")
                else:
                    all_data.extend(result)
            
            # 合并数据
            if all_data:
                combined_data = pd.concat(all_data, ignore_index=True)
                
                # 合并股票名称信息
                if 'name' in basic_data.columns:
                    combined_data = combined_data.merge(
                        basic_data[['ts_code', 'name']],
                        on='ts_code',
                        how='left'
                    )
                    combined_data['name'] = combined_data['name'].fillna('未知')
                else:
                    combined_data['name'] = '未知'
                
                self.logger.info(f"批量获取完成: {len(combined_data)} 条数据")
                return combined_data
            else:
                self.logger.warning("批量获取未获得任何数据")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"批量请求失败: {e}")
            raise
    
    async def _parallel_stock_data_request(self, provider: DataProvider,
                                         request: LimitUpStatsRequest,
                                         config: ProviderOptimizationConfig) -> pd.DataFrame:
        """
        并行股票数据请求
        
        Args:
            provider: 数据提供者
            request: 请求
            config: 优化配置
            
        Returns:
            并行获取的数据
        """
        try:
            # 并行获取股票日线数据和基础信息
            stock_task = provider.get_stock_daily(
                ts_code=None,
                start_date=request.trade_date,
                end_date=request.trade_date
            )
            
            basic_task = provider.get_stock_basic()
            
            # 使用超时控制
            stock_data, basic_data = await asyncio.wait_for(
                asyncio.gather(stock_task, basic_task, return_exceptions=True),
                timeout=config.timeout
            )
            
            # 处理异常结果
            if isinstance(stock_data, Exception):
                self.logger.error(f"获取股票数据失败: {stock_data}")
                stock_data = pd.DataFrame()
            
            if isinstance(basic_data, Exception):
                self.logger.warning(f"获取基础信息失败: {basic_data}")
                basic_data = pd.DataFrame()
            
            # 合并数据
            if not stock_data.empty and not basic_data.empty:
                merged_data = stock_data.merge(
                    basic_data[['ts_code', 'name']],
                    on='ts_code',
                    how='left'
                )
                merged_data['name'] = merged_data['name'].fillna('未知')
                return merged_data
            elif not stock_data.empty:
                stock_data['name'] = '未知'
                return stock_data
            else:
                return pd.DataFrame()
                
        except asyncio.TimeoutError:
            self.logger.error(f"并行请求超时: {config.timeout}s")
            return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"并行请求失败: {e}")
            raise
    
    async def _default_stock_data_request(self, provider: DataProvider,
                                        request: LimitUpStatsRequest) -> pd.DataFrame:
        """
        默认股票数据请求方式
        
        Args:
            provider: 数据提供者
            request: 请求
            
        Returns:
            股票数据
        """
        try:
            # 获取股票日线数据
            stock_data = await provider.get_stock_daily(
                ts_code=None,
                start_date=request.trade_date,
                end_date=request.trade_date
            )
            
            if stock_data.empty:
                return pd.DataFrame()
            
            # 获取股票基础信息
            try:
                basic_data = await provider.get_stock_basic()
                if not basic_data.empty and 'name' in basic_data.columns:
                    stock_data = stock_data.merge(
                        basic_data[['ts_code', 'name']],
                        on='ts_code',
                        how='left'
                    )
                    stock_data['name'] = stock_data['name'].fillna('未知')
                else:
                    stock_data['name'] = '未知'
            except Exception as e:
                self.logger.warning(f"获取基础信息失败，使用默认名称: {e}")
                stock_data['name'] = '未知'
            
            return stock_data
            
        except Exception as e:
            self.logger.error(f"默认请求失败: {e}")
            raise
    

    

    

    
    def get_optimization_stats(self, provider_name: str = None) -> Dict[str, Any]:
        """
        获取优化统计信息
        
        Args:
            provider_name: 提供者名称，None表示获取所有
            
        Returns:
            统计信息
        """
        if provider_name:
            stats = self._performance_stats.get(provider_name, {})
            config = self._optimizations.get(provider_name)
            
            result = stats.copy()
            if config:
                result['enabled_strategies'] = [s.value for s in config.enabled_strategies]
                result['batch_size'] = config.batch_config.batch_size
            
            # 计算派生指标
            if stats.get('successful_requests', 0) > 0:
                result['average_response_time'] = (
                    stats['total_response_time'] / stats['successful_requests']
                )
                result['success_rate'] = (
                    stats['successful_requests'] / stats['total_requests']
                )
            else:
                result['average_response_time'] = 0.0
                result['success_rate'] = 0.0
            
            return result
        else:
            return {
                name: self.get_optimization_stats(name)
                for name in self._performance_stats.keys()
            }
    
    def reset_stats(self, provider_name: str = None):
        """
        重置统计信息
        
        Args:
            provider_name: 提供者名称，None表示重置所有
        """
        if provider_name:
            if provider_name in self._performance_stats:
                self._performance_stats[provider_name] = {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'total_response_time': 0.0,
                    'batch_requests': 0,
                    'last_request_time': None
                }
        else:
            for name in self._performance_stats.keys():
                self.reset_stats(name)
    



class ProviderOptimizationManager:
    """提供者优化管理器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化优化管理器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.optimizer = ProviderOptimizer(logger)
        self._default_configs = self._create_default_configs()
    
    def _create_default_configs(self) -> Dict[str, ProviderOptimizationConfig]:
        """创建默认优化配置"""
        configs = {}
        
        # Baostock优化配置
        configs['baostock'] = ProviderOptimizationConfig(
            provider_name='baostock',
            enabled_strategies=[
                OptimizationStrategy.BATCH_PROCESSING,
                OptimizationStrategy.ADAPTIVE_TIMEOUT
            ],
            batch_config=BatchConfig(
                batch_size=50,
                max_concurrent_batches=2,
                batch_delay=0.2,
                timeout_per_batch=30
            ),
            rate_limit_per_second=2.0,
            timeout=60
        )
        
        # Eastmoney优化配置
        configs['eastmoney'] = ProviderOptimizationConfig(
            provider_name='eastmoney',
            enabled_strategies=[
                OptimizationStrategy.PARALLEL_REQUESTS,
                OptimizationStrategy.REQUEST_DEDUPLICATION
            ],
            batch_config=BatchConfig(
                batch_size=100,
                max_concurrent_batches=3,
                batch_delay=0.1,
                timeout_per_batch=20
            ),
            rate_limit_per_second=5.0,
            timeout=30
        )
        
        # Tonghuashun优化配置
        configs['tonghuashun'] = ProviderOptimizationConfig(
            provider_name='tonghuashun',
            enabled_strategies=[
                OptimizationStrategy.PARALLEL_REQUESTS
            ],
            batch_config=BatchConfig(
                batch_size=80,
                max_concurrent_batches=2,
                batch_delay=0.15,
                timeout_per_batch=25
            ),
            rate_limit_per_second=3.0,
            timeout=45
        )
        
        return configs
    
    def initialize_optimizations(self):
        """初始化所有优化配置"""
        for config in self._default_configs.values():
            self.optimizer.register_optimization(config)
        
        self.logger.info(f"初始化 {len(self._default_configs)} 个提供者优化配置")
    
    def get_optimizer(self) -> ProviderOptimizer:
        """获取优化器实例"""
        return self.optimizer
    
    def update_provider_config(self, provider_name: str, 
                             config_updates: Dict[str, Any]):
        """
        更新提供者配置
        
        Args:
            provider_name: 提供者名称
            config_updates: 配置更新
        """
        if provider_name in self._default_configs:
            config = self._default_configs[provider_name]
            
            # 更新配置
            for key, value in config_updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                elif hasattr(config.batch_config, key):
                    setattr(config.batch_config, key, value)
                else:
                    config.custom_params[key] = value
            
            # 重新注册配置
            self.optimizer.register_optimization(config)
            self.logger.info(f"更新提供者配置: {provider_name}")
        else:
            self.logger.warning(f"未知的提供者: {provider_name}")
    
    def get_provider_config(self, provider_name: str) -> Optional[ProviderOptimizationConfig]:
        """
        获取提供者配置
        
        Args:
            provider_name: 提供者名称
            
        Returns:
            配置对象或None
        """
        return self._default_configs.get(provider_name)
    
    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有优化统计信息"""
        return self.optimizer.get_optimization_stats()
    
    def reset_all_stats(self):
        """重置所有统计信息"""
        self.optimizer.reset_stats()
    
