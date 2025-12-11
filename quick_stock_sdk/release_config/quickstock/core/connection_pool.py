"""
连接池管理器

提供HTTP连接池和会话管理功能，优化网络请求性能
"""

import asyncio
import aiohttp
import time
import logging
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from urllib.parse import urlparse

from .errors import NetworkError, RateLimitError

logger = logging.getLogger(__name__)


@dataclass
class ConnectionPoolConfig:
    """连接池配置"""
    # 连接池大小
    connector_limit: int = 100  # 总连接数限制
    connector_limit_per_host: int = 30  # 每个主机连接数限制
    
    # 超时配置
    total_timeout: int = 30  # 总超时时间
    connect_timeout: int = 10  # 连接超时时间
    read_timeout: int = 30  # 读取超时时间
    
    # 连接保持
    keepalive_timeout: int = 30  # 连接保持时间
    enable_cleanup_closed: bool = True  # 启用清理关闭的连接
    
    # 重试配置
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_factor: float = 2.0
    
    # 速率限制
    default_rate_limit: float = 10.0  # 默认每秒请求数
    rate_limit_window: int = 1  # 速率限制窗口（秒）


@dataclass
class RequestStats:
    """请求统计信息"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    retry_requests: int = 0
    total_response_time: float = 0.0
    
    def add_request(self, success: bool, response_time: float, retries: int = 0):
        """添加请求统计"""
        self.total_requests += 1
        self.total_response_time += response_time
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        if retries > 0:
            self.retry_requests += 1
    

    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def average_response_time(self) -> float:
        """平均响应时间"""
        if self.successful_requests == 0:
            return 0.0
        return self.total_response_time / self.successful_requests


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, rate_limit: float, window: int = 1):
        """
        初始化速率限制器
        
        Args:
            rate_limit: 每秒允许的请求数
            window: 时间窗口（秒）
        """
        self.rate_limit = rate_limit
        self.window = window
        self.requests = []
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """获取请求许可"""
        async with self._lock:
            current_time = time.time()
            
            # 清理过期的请求记录
            self.requests = [
                req_time for req_time in self.requests
                if current_time - req_time < self.window
            ]
            
            # 检查是否超过速率限制
            if len(self.requests) >= self.rate_limit:
                # 计算需要等待的时间
                oldest_request = min(self.requests)
                wait_time = self.window - (current_time - oldest_request)
                
                if wait_time > 0:
                    logger.debug(f"速率限制，等待 {wait_time:.2f} 秒")
                    await asyncio.sleep(wait_time)
                    current_time = time.time()
                    
                    # 重新清理过期记录
                    self.requests = [
                        req_time for req_time in self.requests
                        if current_time - req_time < self.window
                    ]
            
            # 记录当前请求
            self.requests.append(current_time)


class ConnectionPool:
    """HTTP连接池管理器"""
    
    def __init__(self, config: ConnectionPoolConfig):
        """
        初始化连接池
        
        Args:
            config: 连接池配置
        """
        self.config = config
        self._sessions: Dict[str, aiohttp.ClientSession] = {}
        self._rate_limiters: Dict[str, RateLimiter] = {}
        self._stats: Dict[str, RequestStats] = {}
        self._lock = asyncio.Lock()
        self._closed = False
    
    async def _create_session(self, host: str) -> aiohttp.ClientSession:
        """
        为指定主机创建会话
        
        Args:
            host: 主机名
            
        Returns:
            HTTP会话对象
        """
        # 创建连接器
        connector = aiohttp.TCPConnector(
            limit=self.config.connector_limit,
            limit_per_host=self.config.connector_limit_per_host,
            keepalive_timeout=self.config.keepalive_timeout,
            enable_cleanup_closed=self.config.enable_cleanup_closed,
            use_dns_cache=True,
            ttl_dns_cache=300,  # DNS缓存5分钟
        )
        
        # 创建超时配置
        timeout = aiohttp.ClientTimeout(
            total=self.config.total_timeout,
            connect=self.config.connect_timeout,
            sock_read=self.config.read_timeout
        )
        
        # 创建会话
        session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'QuickStock-SDK/1.0.0',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
        )
        
        return session
    
    async def get_session(self, url: str) -> aiohttp.ClientSession:
        """
        获取指定URL的会话
        
        Args:
            url: 请求URL
            
        Returns:
            HTTP会话对象
        """
        if self._closed:
            raise RuntimeError("连接池已关闭")
        
        # 解析主机名
        parsed = urlparse(url)
        host = f"{parsed.scheme}://{parsed.netloc}"
        
        async with self._lock:
            # 检查是否已存在会话
            if host not in self._sessions or self._sessions[host].closed:
                self._sessions[host] = await self._create_session(host)
                logger.debug(f"为主机 {host} 创建新会话")
            
            # 初始化速率限制器和统计信息
            if host not in self._rate_limiters:
                self._rate_limiters[host] = RateLimiter(self.config.default_rate_limit)
            
            if host not in self._stats:
                self._stats[host] = RequestStats()
            
            return self._sessions[host]
    
    async def get_rate_limiter(self, url: str) -> RateLimiter:
        """
        获取指定URL的速率限制器
        
        Args:
            url: 请求URL
            
        Returns:
            速率限制器
        """
        parsed = urlparse(url)
        host = f"{parsed.scheme}://{parsed.netloc}"
        
        async with self._lock:
            if host not in self._rate_limiters:
                self._rate_limiters[host] = RateLimiter(self.config.default_rate_limit)
            
            return self._rate_limiters[host]
    
    def set_rate_limit(self, url: str, rate_limit: float):
        """
        设置指定URL的速率限制
        
        Args:
            url: 请求URL
            rate_limit: 每秒请求数限制
        """
        parsed = urlparse(url)
        host = f"{parsed.scheme}://{parsed.netloc}"
        
        self._rate_limiters[host] = RateLimiter(rate_limit)
        logger.info(f"设置主机 {host} 速率限制为 {rate_limit} 请求/秒")
    
    @asynccontextmanager
    async def request(self, method: str, url: str, **kwargs):
        """
        发起HTTP请求的上下文管理器
        
        Args:
            method: HTTP方法
            url: 请求URL
            **kwargs: 其他请求参数
            
        Yields:
            HTTP响应对象
        """
        parsed = urlparse(url)
        host = f"{parsed.scheme}://{parsed.netloc}"
        
        # 获取会话和速率限制器
        session = await self.get_session(url)
        rate_limiter = await self.get_rate_limiter(url)
        
        # 应用速率限制
        await rate_limiter.acquire()
        
        start_time = time.time()
        retries = 0
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                async with session.request(method, url, **kwargs) as response:
                    response_time = time.time() - start_time
                    
                    # 记录统计信息
                    if host in self._stats:
                        self._stats[host].add_request(
                            success=response.status < 400,
                            response_time=response_time,
                            retries=retries
                        )
                    
                    yield response
                    return
                    
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                retries += 1
                
                if attempt < self.config.max_retries:
                    wait_time = self.config.retry_delay * (self.config.backoff_factor ** attempt)
                    logger.warning(f"请求失败，{wait_time:.1f}秒后重试 (第{attempt + 1}次): {e}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"重试{self.config.max_retries}次后仍然失败: {e}")
                    
                    # 记录失败统计
                    if host in self._stats:
                        response_time = time.time() - start_time
                        self._stats[host].add_request(
                            success=False,
                            response_time=response_time,
                            retries=retries
                        )
        
        # 抛出最后的异常
        if isinstance(last_exception, asyncio.TimeoutError):
            raise NetworkError("请求超时")
        elif isinstance(last_exception, aiohttp.ClientConnectorError):
            raise NetworkError(f"连接失败: {last_exception}")
        else:
            raise NetworkError(f"网络请求失败: {last_exception}")
    
    async def get(self, url: str, **kwargs):
        """发起GET请求"""
        async with self.request('GET', url, **kwargs) as response:
            return response
    
    async def post(self, url: str, **kwargs):
        """发起POST请求"""
        async with self.request('POST', url, **kwargs) as response:
            return response
    
    def get_stats(self, host: str = None) -> Dict[str, Any]:
        """
        获取统计信息
        
        Args:
            host: 指定主机，为None时返回所有主机统计
            
        Returns:
            统计信息字典
        """
        if host:
            parsed = urlparse(host) if '://' in host else urlparse(f'http://{host}')
            host_key = f"{parsed.scheme}://{parsed.netloc}"
            
            if host_key in self._stats:
                stats = self._stats[host_key]
                return {
                    'host': host_key,
                    'total_requests': stats.total_requests,
                    'successful_requests': stats.successful_requests,
                    'failed_requests': stats.failed_requests,
                    'retry_requests': stats.retry_requests,
                    'success_rate': stats.success_rate,
                    'average_response_time': stats.average_response_time
                }
            else:
                return {'host': host_key, 'no_data': True}
        else:
            # 返回所有主机的统计信息
            all_stats = {}
            for host_key, stats in self._stats.items():
                all_stats[host_key] = {
                    'total_requests': stats.total_requests,
                    'successful_requests': stats.successful_requests,
                    'failed_requests': stats.failed_requests,
                    'retry_requests': stats.retry_requests,
                    'success_rate': stats.success_rate,
                    'average_response_time': stats.average_response_time
                }
            
            return all_stats
    
    def get_active_connections(self) -> Dict[str, int]:
        """获取活跃连接数"""
        connections = {}
        for host, session in self._sessions.items():
            if not session.closed:
                connector = session.connector
                if hasattr(connector, '_conns'):
                    connections[host] = len(connector._conns)
                else:
                    connections[host] = 0
            else:
                connections[host] = 0
        
        return connections
    
    async def close(self):
        """关闭连接池"""
        if self._closed:
            return
        
        self._closed = True
        
        # 关闭所有会话
        close_tasks = []
        for host, session in self._sessions.items():
            if not session.closed:
                close_tasks.append(session.close())
                logger.debug(f"关闭主机 {host} 的会话")
        
        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)
        
        self._sessions.clear()
        self._rate_limiters.clear()
        
        logger.info("连接池已关闭")
    
    async def health_check(self) -> Dict[str, bool]:
        """健康检查"""
        health_status = {}
        
        for host, session in self._sessions.items():
            try:
                if session.closed:
                    health_status[host] = False
                else:
                    # 简单的连接测试
                    health_status[host] = True
            except Exception as e:
                logger.warning(f"主机 {host} 健康检查失败: {e}")
                health_status[host] = False
        
        return health_status
    
    def __del__(self):
        """析构函数"""
        if not self._closed and self._sessions:
            logger.warning("连接池未正确关闭，尝试清理资源")
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
            except RuntimeError:
                pass


class ConnectionPoolManager:
    """连接池管理器单例"""
    
    _instance: Optional['ConnectionPoolManager'] = None
    _lock = asyncio.Lock()
    
    def __new__(cls, config: ConnectionPoolConfig = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config: ConnectionPoolConfig = None):
        if not hasattr(self, '_initialized'):
            self.config = config or ConnectionPoolConfig()
            self.pool = ConnectionPool(self.config)
            self._initialized = True
    
    @classmethod
    async def get_instance(cls, config: ConnectionPoolConfig = None) -> 'ConnectionPoolManager':
        """获取连接池管理器实例"""
        async with cls._lock:
            if cls._instance is None:
                cls._instance = cls(config)
            return cls._instance
    
    async def request(self, method: str, url: str, **kwargs):
        """发起HTTP请求"""
        async with self.pool.request(method, url, **kwargs) as response:
            return response
    
    async def get(self, url: str, **kwargs):
        """发起GET请求"""
        return await self.pool.get(url, **kwargs)
    
    async def post(self, url: str, **kwargs):
        """发起POST请求"""
        return await self.pool.post(url, **kwargs)
    
    def set_rate_limit(self, url: str, rate_limit: float):
        """设置速率限制"""
        self.pool.set_rate_limit(url, rate_limit)
    
    def get_stats(self, host: str = None) -> Dict[str, Any]:
        """获取统计信息"""
        return self.pool.get_stats(host)
    
    def get_active_connections(self) -> Dict[str, int]:
        """获取活跃连接数"""
        return self.pool.get_active_connections()
    
    async def close(self):
        """关闭连接池"""
        await self.pool.close()
    
    async def health_check(self) -> Dict[str, bool]:
        """健康检查"""
        return await self.pool.health_check()