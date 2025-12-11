"""
数据源管理器

负责管理和协调多个数据提供者
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, TYPE_CHECKING, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import pandas as pd

if TYPE_CHECKING:
    from ..config import Config

from ..models import DataRequest, LimitUpStatsRequest
from .base import DataProvider
from .optimizations import ProviderOptimizationManager


class FallbackStrategy(Enum):
    """Fallback策略枚举"""
    PRIORITY_ORDER = "priority_order"  # 按优先级顺序
    PERFORMANCE_BASED = "performance_based"  # 基于性能
    ROUND_ROBIN = "round_robin"  # 轮询
    FASTEST_FIRST = "fastest_first"  # 最快优先


class LoadBalanceStrategy(Enum):
    """负载均衡策略枚举"""
    NONE = "none"  # 不使用负载均衡
    ROUND_ROBIN = "round_robin"  # 轮询
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"  # 加权轮询
    LEAST_CONNECTIONS = "least_connections"  # 最少连接
    PERFORMANCE_BASED = "performance_based"  # 基于性能


@dataclass
class ProviderHealth:
    """数据提供者健康状态"""
    name: str
    is_healthy: bool = True
    last_check: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    response_time: float = 0.0
    success_rate: float = 1.0
    total_requests: int = 0
    failed_requests: int = 0


@dataclass
class ProviderStats:
    """数据提供者统计信息"""
    name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    active_connections: int = 0  # 当前活跃连接数
    weight: float = 1.0  # 权重（用于加权轮询）
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests
    
    @property
    def average_response_time(self) -> float:
        """平均响应时间"""
        if self.successful_requests == 0:
            return 0.0
        return self.total_response_time / self.successful_requests
    
    @property
    def load_score(self) -> float:
        """负载评分（越低越好）"""
        # 综合考虑活跃连接数、响应时间和成功率
        connection_factor = self.active_connections * 0.4
        response_factor = self.average_response_time * 0.4
        success_factor = (1 - self.success_rate) * 0.2
        return connection_factor + response_factor + success_factor


class DataSourceManager:
    """数据源管理器"""
    
    def __init__(self, config: 'Config'):
        """
        初始化数据源管理器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.providers: Dict[str, DataProvider] = {}
        self.provider_health: Dict[str, ProviderHealth] = {}
        self.provider_stats: Dict[str, ProviderStats] = {}
        self.logger = logging.getLogger(__name__)
        
        # 协调机制配置
        self.fallback_strategy = FallbackStrategy.PRIORITY_ORDER
        self.load_balance_strategy = LoadBalanceStrategy.NONE
        self.circuit_breaker_enabled = True
        self.circuit_breaker_threshold = 0.5  # 失败率阈值
        self.circuit_breaker_timeout = 300  # 熔断超时时间（秒）
        
        # 轮询计数器
        self._round_robin_counters: Dict[str, int] = {}
        
        # 事件回调
        self._event_callbacks: Dict[str, List[Callable]] = {
            'provider_failed': [],
            'provider_recovered': [],
            'fallback_triggered': [],
            'circuit_breaker_opened': [],
            'circuit_breaker_closed': []
        }
        
        # 初始化优化管理器
        self.optimization_manager = ProviderOptimizationManager(self.logger)
        self.optimization_manager.initialize_optimizations()
        
        # 初始化数据提供者
        self._initialize_providers()
    
    def _initialize_providers(self):
        """初始化数据提供者"""
        # 根据配置启用相应的数据提供者
        if self.config.enable_baostock:
            try:
                from .baostock import BaostockProvider
                self.register_provider('baostock', BaostockProvider(self.config))
            except ImportError as e:
                self.logger.warning(f"无法导入BaostockProvider: {e}")
        
        if self.config.enable_eastmoney:
            try:
                from .eastmoney import EastmoneyProvider
                self.register_provider('eastmoney', EastmoneyProvider(self.config))
            except ImportError as e:
                self.logger.warning(f"无法导入EastmoneyProvider: {e}")
        
        if self.config.enable_tonghuashun:
            try:
                from .tonghuashun import TonghuashunProvider
                self.register_provider('tonghuashun', TonghuashunProvider(self.config))
            except ImportError as e:
                self.logger.warning(f"无法导入TonghuashunProvider: {e}")
        
        # 如果有tushare token，启用tushare提供者
        if self.config.tushare_token:
            try:
                # TODO: 实现TushareProvider
                # from .tushare import TushareProvider
                # self.register_provider('tushare', TushareProvider(self.config))
                pass
            except ImportError as e:
                self.logger.warning(f"无法导入TushareProvider: {e}")
    
    async def fetch_data(self, request: DataRequest) -> pd.DataFrame:
        """
        从数据源获取数据
        支持多数据源fallback机制
        
        Args:
            request: 数据请求对象
            
        Returns:
            获取的数据
        """
        # 验证请求
        request.validate()
        
        # 使用协调机制获取数据
        return await self._fetch_with_coordination(request)
    
    async def _fetch_from_provider(self, provider: DataProvider, request: DataRequest) -> pd.DataFrame:
        """
        从指定提供者获取数据
        
        Args:
            provider: 数据提供者
            request: 数据请求
            
        Returns:
            获取的数据
        """
        # 根据数据类型调用相应的方法
        if request.data_type == 'stock_basic':
            return await provider.get_stock_basic(**request.extra_params)
        elif request.data_type == 'stock_daily':
            return await provider.get_stock_daily(
                request.ts_code, request.start_date, request.end_date
            )
        elif request.data_type == 'stock_minute':
            return await provider.get_stock_minute(
                request.ts_code, request.freq, request.start_date, request.end_date
            )
        elif request.data_type == 'index_basic':
            return await provider.get_index_basic(**request.extra_params)
        elif request.data_type == 'index_daily':
            return await provider.get_index_daily(
                request.ts_code, request.start_date, request.end_date
            )
        elif request.data_type == 'fund_basic':
            return await provider.get_fund_basic(**request.extra_params)
        elif request.data_type == 'fund_nav':
            return await provider.get_fund_nav(
                request.ts_code, request.start_date, request.end_date
            )
        elif request.data_type == 'trade_cal':
            return await provider.get_trade_cal(request.start_date, request.end_date)
        elif request.data_type == 'limit_up_stats':
            # 涨停统计请求需要特殊处理，因为它需要组合多个数据源
            return await self._fetch_limit_up_stats_data(provider, request)
        else:
            # 对于未实现的数据类型，抛出异常
            from ..core.errors import DataSourceError
            raise DataSourceError(f"不支持的数据类型: {request.data_type}")
    
    def _get_provider_priority(self, data_type: str) -> List[str]:
        """
        获取指定数据类型的数据源优先级列表
        
        Args:
            data_type: 数据类型
            
        Returns:
            按优先级排序的数据源名称列表
        """
        # 从配置获取优先级列表
        priority_list = self.config.get_data_source_priority(data_type)
        
        # 过滤出实际可用的数据源
        available_providers = []
        for provider_name in priority_list:
            if provider_name in self.providers:
                available_providers.append(provider_name)
        
        # 如果配置中没有指定优先级，使用默认策略
        if not available_providers:
            available_providers = list(self.providers.keys())
        
        return available_providers
    
    async def _is_provider_healthy(self, provider_name: str) -> bool:
        """
        检查数据提供者是否健康
        
        Args:
            provider_name: 提供者名称
            
        Returns:
            是否健康
        """
        if provider_name not in self.provider_health:
            # 首次检查，初始化健康状态
            self.provider_health[provider_name] = ProviderHealth(provider_name)
        
        health = self.provider_health[provider_name]
        
        # 如果最近检查过且状态良好，直接返回
        if (health.last_check and 
            datetime.now() - health.last_check < timedelta(minutes=5) and
            health.is_healthy):
            return True
        
        # 执行健康检查
        try:
            provider = self.providers[provider_name]
            is_healthy = await provider.health_check()
            
            # 更新健康状态
            health.is_healthy = is_healthy
            health.last_check = datetime.now()
            
            if is_healthy:
                health.error_count = 0
                health.last_error = None
            
            return is_healthy
            
        except Exception as e:
            # 健康检查失败
            health.is_healthy = False
            health.last_check = datetime.now()
            health.error_count += 1
            health.last_error = str(e)
            
            self.logger.warning(f"数据源{provider_name}健康检查失败: {e}")
            return False
    
    def _record_success(self, provider_name: str, response_time: float):
        """
        记录成功请求统计
        
        Args:
            provider_name: 提供者名称
            response_time: 响应时间
        """
        if provider_name not in self.provider_stats:
            self.provider_stats[provider_name] = ProviderStats(provider_name)
        
        stats = self.provider_stats[provider_name]
        stats.total_requests += 1
        stats.successful_requests += 1
        stats.total_response_time += response_time
        stats.last_request_time = datetime.now()
        
        # 更新健康状态
        if provider_name in self.provider_health:
            health = self.provider_health[provider_name]
            health.response_time = response_time
            health.success_rate = stats.success_rate
            health.total_requests = stats.total_requests
            health.failed_requests = stats.failed_requests
    
    def _record_failure(self, provider_name: str, error_msg: str, response_time: float):
        """
        记录失败请求统计
        
        Args:
            provider_name: 提供者名称
            error_msg: 错误信息
            response_time: 响应时间
        """
        if provider_name not in self.provider_stats:
            self.provider_stats[provider_name] = ProviderStats(provider_name)
        
        stats = self.provider_stats[provider_name]
        stats.total_requests += 1
        stats.failed_requests += 1
        stats.last_request_time = datetime.now()
        
        # 更新健康状态
        if provider_name not in self.provider_health:
            self.provider_health[provider_name] = ProviderHealth(provider_name)
        
        health = self.provider_health[provider_name]
        health.error_count += 1
        health.last_error = error_msg
        health.success_rate = stats.success_rate
        health.total_requests = stats.total_requests
        health.failed_requests = stats.failed_requests
        
        # 如果错误率过高，标记为不健康
        if stats.success_rate < 0.5 and stats.total_requests >= 5:
            health.is_healthy = False
    
    def get_preferred_provider(self, data_type: str) -> Optional[str]:
        """
        获取指定数据类型的首选数据源
        
        Args:
            data_type: 数据类型
            
        Returns:
            首选数据源名称
        """
        priority_list = self._get_provider_priority(data_type)
        
        # 返回第一个可用的数据源
        for provider_name in priority_list:
            if provider_name in self.providers:
                return provider_name
        
        return None
    
    def register_provider(self, name: str, provider: DataProvider):
        """
        注册数据提供者
        
        Args:
            name: 提供者名称
            provider: 提供者实例
        """
        self.providers[name] = provider
        
        # 初始化统计信息
        if name not in self.provider_stats:
            self.provider_stats[name] = ProviderStats(name)
        
        if name not in self.provider_health:
            self.provider_health[name] = ProviderHealth(name)
        
        self.logger.info(f"注册数据提供者: {name}")
    
    def unregister_provider(self, name: str):
        """
        注销数据提供者
        
        Args:
            name: 提供者名称
        """
        if name in self.providers:
            del self.providers[name]
            self.logger.info(f"注销数据提供者: {name}")
        
        # 清理统计信息
        if name in self.provider_stats:
            del self.provider_stats[name]
        
        if name in self.provider_health:
            del self.provider_health[name]
    
    def get_provider(self, name: str) -> Optional[DataProvider]:
        """
        获取数据提供者
        
        Args:
            name: 提供者名称
            
        Returns:
            提供者实例
        """
        return self.providers.get(name)
    
    def list_providers(self) -> List[str]:
        """
        获取所有已注册的数据提供者名称
        
        Returns:
            提供者名称列表
        """
        return list(self.providers.keys())
    
    def get_provider_stats(self, name: str = None) -> Dict[str, ProviderStats]:
        """
        获取数据提供者统计信息
        
        Args:
            name: 提供者名称，如果为None则返回所有提供者的统计
            
        Returns:
            统计信息字典
        """
        if name:
            return {name: self.provider_stats.get(name)} if name in self.provider_stats else {}
        else:
            return self.provider_stats.copy()
    
    def get_provider_health(self, name: str = None) -> Dict[str, ProviderHealth]:
        """
        获取数据提供者健康状态
        
        Args:
            name: 提供者名称，如果为None则返回所有提供者的健康状态
            
        Returns:
            健康状态字典
        """
        if name:
            return {name: self.provider_health.get(name)} if name in self.provider_health else {}
        else:
            return self.provider_health.copy()
    
    async def health_check_all(self) -> Dict[str, bool]:
        """
        对所有数据提供者执行健康检查
        
        Returns:
            健康检查结果字典
        """
        results = {}
        
        # 并发执行健康检查
        tasks = []
        for name in self.providers.keys():
            tasks.append(self._is_provider_healthy(name))
        
        if tasks:
            health_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, name in enumerate(self.providers.keys()):
                result = health_results[i]
                if isinstance(result, Exception):
                    results[name] = False
                    self.logger.error(f"健康检查异常 {name}: {result}")
                else:
                    results[name] = result
        
        return results
    
    def reset_stats(self, provider_name: str = None):
        """
        重置统计信息
        
        Args:
            provider_name: 提供者名称，如果为None则重置所有提供者的统计
        """
        if provider_name:
            if provider_name in self.provider_stats:
                self.provider_stats[provider_name] = ProviderStats(provider_name)
            if provider_name in self.provider_health:
                self.provider_health[provider_name] = ProviderHealth(provider_name)
        else:
            # 重置所有统计
            for name in self.providers.keys():
                self.provider_stats[name] = ProviderStats(name)
                self.provider_health[name] = ProviderHealth(name)
        
        self.logger.info(f"重置统计信息: {provider_name or '所有提供者'}")
    
    def get_best_provider(self, data_type: str) -> Optional[str]:
        """
        根据性能统计获取最佳数据提供者
        
        Args:
            data_type: 数据类型
            
        Returns:
            最佳提供者名称
        """
        priority_list = self._get_provider_priority(data_type)
        
        best_provider = None
        best_score = -1
        
        for provider_name in priority_list:
            if provider_name not in self.provider_stats:
                continue
            
            stats = self.provider_stats[provider_name]
            health = self.provider_health.get(provider_name)
            
            # 如果提供者不健康，跳过
            if health and not health.is_healthy:
                continue
            
            # 计算综合评分（成功率 * 0.7 + 响应时间权重 * 0.3）
            success_weight = 0.7
            speed_weight = 0.3
            
            # 成功率评分
            success_score = stats.success_rate
            
            # 响应时间评分（响应时间越短评分越高）
            avg_response_time = stats.average_response_time
            if avg_response_time > 0:
                # 假设5秒以内为满分，超过5秒按比例递减
                speed_score = max(0, 1 - (avg_response_time - 1) / 4)
            else:
                speed_score = 1.0
            
            # 综合评分
            total_score = success_score * success_weight + speed_score * speed_weight
            
            if total_score > best_score:
                best_score = total_score
                best_provider = provider_name
        
        return best_provider
    
    def set_fallback_strategy(self, strategy: FallbackStrategy):
        """
        设置fallback策略
        
        Args:
            strategy: fallback策略
        """
        self.fallback_strategy = strategy
        self.logger.info(f"设置fallback策略为: {strategy.value}")
    
    def set_load_balance_strategy(self, strategy: LoadBalanceStrategy):
        """
        设置负载均衡策略
        
        Args:
            strategy: 负载均衡策略
        """
        self.load_balance_strategy = strategy
        self.logger.info(f"设置负载均衡策略为: {strategy.value}")
    
    def _get_provider_by_strategy(self, data_type: str, available_providers: List[str]) -> Optional[str]:
        """
        根据策略选择数据提供者
        
        Args:
            data_type: 数据类型
            available_providers: 可用提供者列表
            
        Returns:
            选中的提供者名称
        """
        if not available_providers:
            return None
        
        if self.load_balance_strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._round_robin_select(data_type, available_providers)
        elif self.load_balance_strategy == LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(available_providers)
        elif self.load_balance_strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(available_providers)
        elif self.load_balance_strategy == LoadBalanceStrategy.PERFORMANCE_BASED:
            return self._performance_based_select(available_providers)
        else:
            # 默认返回第一个可用的
            return available_providers[0]
    
    def _round_robin_select(self, data_type: str, providers: List[str]) -> str:
        """轮询选择"""
        if data_type not in self._round_robin_counters:
            self._round_robin_counters[data_type] = 0
        
        index = self._round_robin_counters[data_type] % len(providers)
        self._round_robin_counters[data_type] += 1
        
        return providers[index]
    
    def _weighted_round_robin_select(self, providers: List[str]) -> str:
        """加权轮询选择"""
        # 计算总权重
        total_weight = sum(
            self.provider_stats[name].weight 
            for name in providers 
            if name in self.provider_stats
        )
        
        if total_weight == 0:
            return providers[0]
        
        # 随机选择
        import random
        rand_weight = random.uniform(0, total_weight)
        current_weight = 0
        
        for provider_name in providers:
            if provider_name in self.provider_stats:
                current_weight += self.provider_stats[provider_name].weight
                if current_weight >= rand_weight:
                    return provider_name
        
        return providers[0]
    
    def _least_connections_select(self, providers: List[str]) -> str:
        """最少连接选择"""
        min_connections = float('inf')
        selected_provider = providers[0]
        
        for provider_name in providers:
            if provider_name in self.provider_stats:
                connections = self.provider_stats[provider_name].active_connections
                if connections < min_connections:
                    min_connections = connections
                    selected_provider = provider_name
        
        return selected_provider
    
    def _performance_based_select(self, providers: List[str]) -> str:
        """基于性能选择"""
        best_score = float('inf')
        selected_provider = providers[0]
        
        for provider_name in providers:
            if provider_name in self.provider_stats:
                score = self.provider_stats[provider_name].load_score
                if score < best_score:
                    best_score = score
                    selected_provider = provider_name
        
        return selected_provider
    
    def _is_circuit_breaker_open(self, provider_name: str) -> bool:
        """
        检查熔断器是否开启
        
        Args:
            provider_name: 提供者名称
            
        Returns:
            熔断器是否开启
        """
        if not self.circuit_breaker_enabled:
            return False
        
        if provider_name not in self.provider_stats:
            return False
        
        stats = self.provider_stats[provider_name]
        health = self.provider_health.get(provider_name)
        
        # 检查失败率是否超过阈值
        if (stats.total_requests >= 5 and 
            stats.success_rate < self.circuit_breaker_threshold):
            
            # 检查是否在熔断超时期内
            if health and health.last_check:
                time_since_last_check = (datetime.now() - health.last_check).total_seconds()
                if time_since_last_check < self.circuit_breaker_timeout:
                    return True
        
        return False
    
    def _trigger_event(self, event_name: str, **kwargs):
        """
        触发事件回调
        
        Args:
            event_name: 事件名称
            **kwargs: 事件参数
        """
        if event_name in self._event_callbacks:
            for callback in self._event_callbacks[event_name]:
                try:
                    callback(**kwargs)
                except Exception as e:
                    self.logger.error(f"事件回调执行失败 {event_name}: {e}")
    
    def add_event_callback(self, event_name: str, callback: Callable):
        """
        添加事件回调
        
        Args:
            event_name: 事件名称
            callback: 回调函数
        """
        if event_name in self._event_callbacks:
            self._event_callbacks[event_name].append(callback)
        else:
            self.logger.warning(f"未知的事件类型: {event_name}")
    
    def remove_event_callback(self, event_name: str, callback: Callable):
        """
        移除事件回调
        
        Args:
            event_name: 事件名称
            callback: 回调函数
        """
        if event_name in self._event_callbacks:
            try:
                self._event_callbacks[event_name].remove(callback)
            except ValueError:
                pass
    
    async def _fetch_with_coordination(self, request: DataRequest) -> pd.DataFrame:
        """
        使用协调机制获取数据
        
        Args:
            request: 数据请求
            
        Returns:
            获取的数据
        """
        from ..core.errors import DataSourceError
        
        # 获取可用的数据源
        priority_list = self._get_provider_priority(request.data_type)
        available_providers = []
        
        for provider_name in priority_list:
            if (provider_name in self.providers and 
                await self._is_provider_healthy(provider_name) and
                not self._is_circuit_breaker_open(provider_name)):
                available_providers.append(provider_name)
        
        if not available_providers:
            # 所有提供者都不可用，尝试使用熔断器开启的提供者
            self.logger.warning("所有首选提供者不可用，尝试使用熔断器开启的提供者")
            for provider_name in priority_list:
                if provider_name in self.providers:
                    available_providers.append(provider_name)
        
        if not available_providers:
            raise DataSourceError(f"没有可用的数据源获取{request.data_type}数据")
        
        # 根据fallback策略排序提供者
        if self.fallback_strategy == FallbackStrategy.PERFORMANCE_BASED:
            available_providers.sort(
                key=lambda x: self.provider_stats.get(x, ProviderStats(x)).load_score
            )
        elif self.fallback_strategy == FallbackStrategy.FASTEST_FIRST:
            available_providers.sort(
                key=lambda x: self.provider_stats.get(x, ProviderStats(x)).average_response_time
            )
        
        last_error = None
        
        # 根据负载均衡策略选择提供者顺序
        if self.load_balance_strategy != LoadBalanceStrategy.NONE:
            # 对于负载均衡，我们只选择一个提供者尝试
            selected_provider = self._get_provider_by_strategy(
                request.data_type, available_providers
            )
            if selected_provider:
                # 先尝试选中的提供者，如果失败再fallback到其他提供者
                available_providers = [selected_provider] + [
                    p for p in available_providers if p != selected_provider
                ]
        
        # 尝试从提供者获取数据
        for provider_name in available_providers:
            
            provider = self.providers[provider_name]
            
            try:
                # 增加活跃连接数
                if provider_name in self.provider_stats:
                    self.provider_stats[provider_name].active_connections += 1
                
                start_time = time.time()
                data = await self._fetch_from_provider(provider, request)
                response_time = time.time() - start_time
                
                # 记录成功
                self._record_success(provider_name, response_time)
                
                # 检查提供者是否恢复
                if provider_name in self.provider_health:
                    health = self.provider_health[provider_name]
                    if not health.is_healthy:
                        health.is_healthy = True
                        self._trigger_event('provider_recovered', provider_name=provider_name)
                
                self.logger.info(f"成功从{provider_name}获取数据，响应时间: {response_time:.2f}s")
                return data
                
            except Exception as e:
                response_time = time.time() - start_time
                self._record_failure(provider_name, str(e), response_time)
                
                # 触发失败事件
                self._trigger_event('provider_failed', 
                                  provider_name=provider_name, 
                                  error=str(e))
                
                # 检查是否需要开启熔断器
                if self._is_circuit_breaker_open(provider_name):
                    self._trigger_event('circuit_breaker_opened', 
                                      provider_name=provider_name)
                
                self.logger.warning(f"从{provider_name}获取数据失败: {e}")
                last_error = e
                
                # 触发fallback事件
                self._trigger_event('fallback_triggered',
                                  from_provider=provider_name,
                                  data_type=request.data_type)
                
            finally:
                # 减少活跃连接数
                if provider_name in self.provider_stats:
                    self.provider_stats[provider_name].active_connections = max(
                        0, self.provider_stats[provider_name].active_connections - 1
                    )
        
        # 所有提供者都失败
        error_msg = f"无法从任何数据源获取{request.data_type}数据"
        if last_error:
            error_msg += f"，最后一个错误: {last_error}"
        
        raise DataSourceError(error_msg)
    
    def get_coordination_stats(self) -> Dict[str, Any]:
        """
        获取协调机制统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'fallback_strategy': self.fallback_strategy.value,
            'load_balance_strategy': self.load_balance_strategy.value,
            'circuit_breaker_enabled': self.circuit_breaker_enabled,
            'circuit_breaker_threshold': self.circuit_breaker_threshold,
            'circuit_breaker_timeout': self.circuit_breaker_timeout,
            'round_robin_counters': self._round_robin_counters.copy(),
            'total_providers': len(self.providers),
            'healthy_providers': sum(
                1 for health in self.provider_health.values() 
                if health.is_healthy
            ),
            'circuit_breaker_open_providers': [
                name for name in self.providers.keys()
                if self._is_circuit_breaker_open(name)
            ]
        }
    
    async def test_provider(self, provider_name: str, data_type: str = 'stock_basic') -> bool:
        """
        测试指定数据提供者
        
        Args:
            provider_name: 提供者名称
            data_type: 测试的数据类型
            
        Returns:
            测试是否成功
        """
        if provider_name not in self.providers:
            return False
        
        try:
            # 创建测试请求
            test_request = DataRequest(
                data_type=data_type,
                extra_params={'limit': 1}  # 只获取少量数据进行测试
            )
            
            provider = self.providers[provider_name]
            data = await self._fetch_from_provider(provider, test_request)
            
            # 检查返回的数据是否有效
            return isinstance(data, pd.DataFrame) and not data.empty
            
        except Exception as e:
            self.logger.warning(f"测试数据提供者{provider_name}失败: {e}")
            return False
    
    async def _fetch_limit_up_stats_data(self, provider: DataProvider, request: DataRequest) -> pd.DataFrame:
        """
        获取涨停统计所需的股票数据（使用优化策略）
        
        Args:
            provider: 数据提供者
            request: 数据请求
            
        Returns:
            股票日线数据
        """
        # 如果是LimitUpStatsRequest，使用优化策略
        if isinstance(request, LimitUpStatsRequest):
            optimizer = self.optimization_manager.get_optimizer()
            return await optimizer.optimize_stock_data_request(provider, request)
        
        # 非LimitUpStatsRequest，使用传统方式
        trade_date = request.start_date or request.end_date
        
        if not trade_date:
            from ..core.errors import DataSourceError
            raise DataSourceError("涨停统计请求缺少交易日期")
        
        try:
            # 获取股票日线数据
            stock_data = await provider.get_stock_daily(
                ts_code=None,  # 获取所有股票
                start_date=trade_date,
                end_date=trade_date
            )
            
            # 如果股票数据为空，尝试使用不同的参数
            if stock_data.empty:
                # 尝试使用extra_params中的参数
                extra_params = request.extra_params.copy()
                extra_params.update({
                    'trade_date': trade_date,
                    'fields': [
                        'ts_code', 'trade_date', 'open', 'high', 'low', 'close', 
                        'pre_close', 'change', 'pct_chg', 'vol', 'amount'
                    ]
                })
                
                # 尝试通过stock_basic获取所有股票代码，然后批量获取数据
                try:
                    basic_data = await provider.get_stock_basic()
                    if not basic_data.empty and 'ts_code' in basic_data.columns:
                        # 分批获取股票数据以避免请求过大
                        stock_codes = basic_data['ts_code'].tolist()
                        batch_size = 100  # 每批处理100只股票
                        
                        all_stock_data = []
                        for i in range(0, len(stock_codes), batch_size):
                            batch_codes = stock_codes[i:i + batch_size]
                            for code in batch_codes:
                                try:
                                    single_stock_data = await provider.get_stock_daily(
                                        ts_code=code,
                                        start_date=trade_date,
                                        end_date=trade_date
                                    )
                                    if not single_stock_data.empty:
                                        all_stock_data.append(single_stock_data)
                                except Exception as e:
                                    self.logger.debug(f"获取股票 {code} 数据失败: {e}")
                                    continue
                            
                            # 避免请求过于频繁
                            await asyncio.sleep(0.1)
                        
                        if all_stock_data:
                            stock_data = pd.concat(all_stock_data, ignore_index=True)
                
                except Exception as e:
                    self.logger.warning(f"批量获取股票数据失败: {e}")
            
            self.logger.info(f"从 {provider.__class__.__name__} 获取到 {len(stock_data)} 只股票的 {trade_date} 数据")
            return stock_data
            
        except Exception as e:
            self.logger.error(f"从 {provider.__class__.__name__} 获取涨停统计数据失败: {e}")
            raise
    
    async def get_stock_data_with_fallback(self, trade_date: str, 
                                         timeout: int = 30) -> pd.DataFrame:
        """
        使用fallback机制获取股票数据
        
        Args:
            trade_date: 交易日期
            timeout: 超时时间
            
        Returns:
            股票数据
        """
        from ..models import LimitUpStatsRequest
        
        # 创建涨停统计请求
        request = LimitUpStatsRequest(
            trade_date=trade_date,
            extra_params={'timeout': timeout}
        )
        
        try:
            # 使用协调机制获取数据
            return await self._fetch_with_coordination(request)
        except Exception as e:
            self.logger.error(f"获取股票数据失败: {e}")
            return pd.DataFrame()
    
    def get_provider_capabilities(self, provider_name: str) -> Dict[str, bool]:
        """
        获取数据提供者的能力信息
        
        Args:
            provider_name: 提供者名称
            
        Returns:
            能力信息字典
        """
        if provider_name not in self.providers:
            return {}
        
        provider = self.providers[provider_name]
        capabilities = {}
        
        # 检查各种数据类型的支持情况
        data_types = [
            'stock_basic', 'stock_daily', 'stock_minute',
            'index_basic', 'index_daily',
            'fund_basic', 'fund_nav',
            'trade_cal'
        ]
        
        for data_type in data_types:
            method_name = f"get_{data_type.replace('_', '_')}"
            capabilities[data_type] = hasattr(provider, method_name)
        
        # 特殊检查涨停统计支持（需要stock_daily和stock_basic）
        capabilities['limit_up_stats'] = (
            capabilities.get('stock_daily', False) and 
            capabilities.get('stock_basic', False)
        )
        
        return capabilities
    
    def get_best_provider_for_limit_up_stats(self) -> Optional[str]:
        """
        获取最适合涨停统计的数据提供者
        
        Returns:
            最佳提供者名称
        """
        # 获取支持涨停统计的提供者
        suitable_providers = []
        
        for provider_name in self.providers.keys():
            capabilities = self.get_provider_capabilities(provider_name)
            if capabilities.get('limit_up_stats', False):
                # 检查健康状态
                health = self.provider_health.get(provider_name)
                if health and health.is_healthy:
                    suitable_providers.append(provider_name)
        
        if not suitable_providers:
            return None
        
        # 根据性能选择最佳提供者
        best_provider = None
        best_score = -1
        
        for provider_name in suitable_providers:
            stats = self.provider_stats.get(provider_name)
            if stats:
                # 综合评分：成功率 * 0.6 + 响应时间权重 * 0.4
                success_score = stats.success_rate
                speed_score = max(0, 1 - (stats.average_response_time - 1) / 4) if stats.average_response_time > 0 else 1.0
                total_score = success_score * 0.6 + speed_score * 0.4
                
                if total_score > best_score:
                    best_score = total_score
                    best_provider = provider_name
        
        return best_provider or suitable_providers[0]
    
    async def test_limit_up_stats_capability(self, provider_name: str) -> bool:
        """
        测试数据提供者的涨停统计能力
        
        Args:
            provider_name: 提供者名称
            
        Returns:
            是否支持涨停统计
        """
        if provider_name not in self.providers:
            return False
        
        try:
            from datetime import datetime, timedelta
            
            # 使用最近的交易日进行测试
            test_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
            
            # 创建测试请求
            from ..models import LimitUpStatsRequest
            test_request = LimitUpStatsRequest(trade_date=test_date)
            
            # 尝试获取少量数据
            provider = self.providers[provider_name]
            test_data = await self._fetch_limit_up_stats_data(provider, test_request)
            
            # 检查数据是否有效
            return isinstance(test_data, pd.DataFrame) and len(test_data) > 0
            
        except Exception as e:
            self.logger.warning(f"测试 {provider_name} 涨停统计能力失败: {e}")
            return False
    
    def add_provider_optimization(self, provider_name: str, optimization_config: Dict[str, Any]):
        """
        为特定提供者添加优化配置
        
        Args:
            provider_name: 提供者名称
            optimization_config: 优化配置
        """
        if provider_name not in self.provider_stats:
            self.provider_stats[provider_name] = ProviderStats(provider_name)
        
        stats = self.provider_stats[provider_name]
        
        # 应用优化配置
        if 'weight' in optimization_config:
            stats.weight = optimization_config['weight']
        
        if 'batch_size' in optimization_config:
            # 存储批处理大小配置
            if not hasattr(stats, 'optimization_config'):
                stats.optimization_config = {}
            stats.optimization_config['batch_size'] = optimization_config['batch_size']
        
        if 'timeout' in optimization_config:
            if not hasattr(stats, 'optimization_config'):
                stats.optimization_config = {}
            stats.optimization_config['timeout'] = optimization_config['timeout']
        
        self.logger.info(f"为 {provider_name} 应用优化配置: {optimization_config}")
    
    async def close_all(self):
        """关闭所有数据提供者连接"""
        for provider_name, provider in self.providers.items():
            try:
                if hasattr(provider, 'close'):
                    await provider.close()
                self.logger.debug(f"已关闭数据提供者: {provider_name}")
            except Exception as e:
                self.logger.error(f"关闭数据提供者 {provider_name} 失败: {e}")
    
    def get_optimization_manager(self) -> ProviderOptimizationManager:
        """获取优化管理器"""
        return self.optimization_manager
    
    def get_optimization_stats(self, provider_name: str = None) -> Dict[str, Any]:
        """
        获取优化统计信息
        
        Args:
            provider_name: 提供者名称
            
        Returns:
            优化统计信息
        """
        return self.optimization_manager.get_all_stats() if provider_name is None else \
               self.optimization_manager.optimizer.get_optimization_stats(provider_name)
    
    def update_provider_optimization(self, provider_name: str, config_updates: Dict[str, Any]):
        """
        更新提供者优化配置
        
        Args:
            provider_name: 提供者名称
            config_updates: 配置更新
        """
        self.optimization_manager.update_provider_config(provider_name, config_updates)
        self.logger.info(f"更新提供者优化配置: {provider_name}")
    
    def enable_provider_optimization(self, provider_name: str, strategies: List[str]):
        """
        启用提供者优化策略
        
        Args:
            provider_name: 提供者名称
            strategies: 优化策略列表
        """
        from .optimizations import OptimizationStrategy
        
        strategy_enums = []
        for strategy in strategies:
            try:
                strategy_enums.append(OptimizationStrategy(strategy))
            except ValueError:
                self.logger.warning(f"未知的优化策略: {strategy}")
        
        if strategy_enums:
            self.optimization_manager.update_provider_config(
                provider_name, 
                {'enabled_strategies': strategy_enums}
            )
    
    def disable_provider_optimization(self, provider_name: str):
        """
        禁用提供者优化
        
        Args:
            provider_name: 提供者名称
        """
        self.optimization_manager.update_provider_config(
            provider_name, 
            {'enabled_strategies': []}
        )
    
    def reset_optimization_stats(self, provider_name: str = None):
        """
        重置优化统计信息
        
        Args:
            provider_name: 提供者名称，None表示重置所有
        """
        if provider_name:
            self.optimization_manager.optimizer.reset_stats(provider_name)
        else:
            self.optimization_manager.reset_all_stats()
    

    async def benchmark_provider_performance(self, provider_name: str, 
                                           test_date: str = None) -> Dict[str, Any]:
        """
        基准测试提供者性能
        
        Args:
            provider_name: 提供者名称
            test_date: 测试日期
            
        Returns:
            性能基准测试结果
        """
        if provider_name not in self.providers:
            return {'error': f'提供者 {provider_name} 不存在'}
        
        if not test_date:
            from datetime import datetime, timedelta
            test_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        
        provider = self.providers[provider_name]
        optimizer = self.optimization_manager.get_optimizer()
        
        # 测试不同的优化策略
        test_results = {}
        
        # 1. 测试默认方式
        start_time = datetime.now()
        try:
            default_request = LimitUpStatsRequest(trade_date=test_date)
            default_data = await optimizer._default_stock_data_request(provider, default_request)
            default_time = (datetime.now() - start_time).total_seconds()
            test_results['default'] = {
                'response_time': default_time,
                'data_count': len(default_data),
                'success': True
            }
        except Exception as e:
            test_results['default'] = {
                'response_time': (datetime.now() - start_time).total_seconds(),
                'data_count': 0,
                'success': False,
                'error': str(e)
            }
        
        # 2. 测试优化方式
        config = self.optimization_manager.get_provider_config(provider_name)
        if config:
            start_time = datetime.now()
            try:
                optimized_request = LimitUpStatsRequest(trade_date=test_date)
                optimized_data = await optimizer.optimize_stock_data_request(provider, optimized_request)
                optimized_time = (datetime.now() - start_time).total_seconds()
                test_results['optimized'] = {
                    'response_time': optimized_time,
                    'data_count': len(optimized_data),
                    'success': True,
                    'strategies': [s.value for s in config.enabled_strategies]
                }
            except Exception as e:
                test_results['optimized'] = {
                    'response_time': (datetime.now() - start_time).total_seconds(),
                    'data_count': 0,
                    'success': False,
                    'error': str(e),
                    'strategies': [s.value for s in config.enabled_strategies]
                }
        
        # 计算性能提升
        if (test_results.get('default', {}).get('success') and 
            test_results.get('optimized', {}).get('success')):
            
            default_time = test_results['default']['response_time']
            optimized_time = test_results['optimized']['response_time']
            
            if default_time > 0:
                improvement = ((default_time - optimized_time) / default_time) * 100
                test_results['performance_improvement'] = {
                    'time_saved_seconds': default_time - optimized_time,
                    'improvement_percentage': improvement
                }
        
        test_results['test_date'] = test_date
        test_results['provider_name'] = provider_name
        test_results['timestamp'] = datetime.now().isoformat()
        
        return test_results
    
    async def close(self):
        """关闭数据源管理器"""
        await self.close_all()
        self.logger.info("数据源管理器已关闭")