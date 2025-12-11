"""
性能监控工具

提供API响应时间监控、缓存命中率统计和自适应速率限制功能
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from collections import deque, defaultdict
from dataclasses import dataclass, field
import statistics
import threading
from contextlib import asynccontextmanager


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    operation: str
    start_time: float
    end_time: float
    duration: float
    success: bool
    error_type: Optional[str] = None
    data_size: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'operation': self.operation,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'success': self.success,
            'error_type': self.error_type,
            'data_size': self.data_size,
            'timestamp': datetime.fromtimestamp(self.start_time).isoformat()
        }


@dataclass
class ApiUsageStats:
    """API使用统计"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    rate_limit_hits: int = 0
    last_request_time: Optional[datetime] = None
    
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
    

    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': round(self.success_rate, 4),
            'average_response_time': round(self.average_response_time, 4),
            'min_response_time': self.min_response_time if self.min_response_time != float('inf') else 0,
            'max_response_time': self.max_response_time,
            'rate_limit_hits': self.rate_limit_hits,
            'last_request_time': self.last_request_time.isoformat() if self.last_request_time else None
        }


class AdaptiveRateLimiter:
    """自适应速率限制器"""
    
    def __init__(self, initial_rate: float = 2.0, min_rate: float = 0.5, max_rate: float = 10.0):
        """
        初始化自适应速率限制器
        
        Args:
            initial_rate: 初始请求速率（请求/秒）
            min_rate: 最小请求速率
            max_rate: 最大请求速率
        """
        self.current_rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.last_request_time = 0.0
        self.recent_response_times = deque(maxlen=50)  # 保留最近50次响应时间
        self.recent_errors = deque(maxlen=20)  # 保留最近20次错误
        self._lock = threading.RLock()
        
        # 自适应参数
        self.success_rate_threshold = 0.95  # 成功率阈值
        self.response_time_threshold = 5.0  # 响应时间阈值（秒）
        self.adjustment_factor = 0.1  # 调整因子
        
    async def acquire(self) -> None:
        """获取请求许可，实现速率限制"""
        with self._lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            # 计算需要等待的时间
            min_interval = 1.0 / self.current_rate
            if time_since_last < min_interval:
                wait_time = min_interval - time_since_last
                await asyncio.sleep(wait_time)
            
            self.last_request_time = time.time()
    
    def record_response(self, response_time: float, success: bool, error_type: Optional[str] = None):
        """记录响应结果，用于自适应调整"""
        with self._lock:
            self.recent_response_times.append(response_time)
            self.recent_errors.append((success, error_type, time.time()))
            
            # 触发自适应调整
            self._adjust_rate()
    
    def _adjust_rate(self):
        """根据最近的响应情况调整速率"""
        if len(self.recent_response_times) < 10:
            return  # 数据不足，不调整
        
        # 计算最近的成功率
        recent_successes = sum(1 for success, _, _ in self.recent_errors if success)
        success_rate = recent_successes / len(self.recent_errors) if self.recent_errors else 1.0
        
        # 计算平均响应时间
        avg_response_time = statistics.mean(self.recent_response_times)
        
        # 检查是否有速率限制错误
        rate_limit_errors = sum(1 for _, error_type, _ in self.recent_errors 
                               if error_type and 'rate' in error_type.lower())
        
        old_rate = self.current_rate
        
        # 调整逻辑
        if rate_limit_errors > 0:
            # 如果有速率限制错误，降低速率
            self.current_rate *= (1 - self.adjustment_factor * 2)
        elif success_rate < self.success_rate_threshold:
            # 成功率低，降低速率
            self.current_rate *= (1 - self.adjustment_factor)
        elif avg_response_time > self.response_time_threshold:
            # 响应时间过长，降低速率
            self.current_rate *= (1 - self.adjustment_factor * 0.5)
        elif success_rate > 0.98 and avg_response_time < 2.0:
            # 表现良好，可以适当提高速率
            self.current_rate *= (1 + self.adjustment_factor * 0.5)
        
        # 确保速率在合理范围内
        self.current_rate = max(self.min_rate, min(self.max_rate, self.current_rate))
        
        # 记录调整日志
        if abs(old_rate - self.current_rate) > 0.01:
            logging.getLogger(__name__).debug(
                f"速率调整: {old_rate:.2f} -> {self.current_rate:.2f} "
                f"(成功率: {success_rate:.2f}, 平均响应时间: {avg_response_time:.2f}s)"
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取速率限制器统计信息"""
        with self._lock:
            recent_successes = sum(1 for success, _, _ in self.recent_errors if success)
            success_rate = recent_successes / len(self.recent_errors) if self.recent_errors else 1.0
            avg_response_time = statistics.mean(self.recent_response_times) if self.recent_response_times else 0.0
            
            return {
                'current_rate': round(self.current_rate, 2),
                'min_rate': self.min_rate,
                'max_rate': self.max_rate,
                'recent_success_rate': round(success_rate, 4),
                'recent_avg_response_time': round(avg_response_time, 4),
                'recent_samples': len(self.recent_response_times)
            }


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, max_metrics_history: int = 10000):
        """
        初始化性能监控器
        
        Args:
            max_metrics_history: 最大指标历史记录数
        """
        self.max_metrics_history = max_metrics_history
        self.metrics_history: deque = deque(maxlen=max_metrics_history)
        self.operation_stats: Dict[str, ApiUsageStats] = defaultdict(ApiUsageStats)
        self.rate_limiter = AdaptiveRateLimiter()
        self._lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        
        # 启动清理任务
        self._cleanup_task = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """启动定期清理任务"""
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(3600)  # 每小时清理一次
                    self._cleanup_old_metrics()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"清理任务异常: {e}")
        
        try:
            loop = asyncio.get_event_loop()
            self._cleanup_task = loop.create_task(cleanup_loop())
        except RuntimeError:
            # 如果没有运行的事件循环，跳过清理任务
            pass
    
    def _cleanup_old_metrics(self):
        """清理旧的指标数据"""
        with self._lock:
            # 清理超过24小时的指标
            cutoff_time = time.time() - 86400  # 24小时
            
            # 清理历史指标
            while self.metrics_history and self.metrics_history[0].start_time < cutoff_time:
                self.metrics_history.popleft()
            
            self.logger.debug(f"清理旧指标，当前历史记录数: {len(self.metrics_history)}")
    
    @asynccontextmanager
    async def measure_operation(self, operation: str, data_size: Optional[int] = None):
        """
        测量操作性能的上下文管理器
        
        Args:
            operation: 操作名称
            data_size: 数据大小（可选）
        """
        # 应用速率限制
        await self.rate_limiter.acquire()
        
        start_time = time.time()
        success = False
        error_type = None
        
        try:
            yield self
            success = True
        except Exception as e:
            error_type = type(e).__name__
            raise
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            # 记录指标
            metrics = PerformanceMetrics(
                operation=operation,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                success=success,
                error_type=error_type,
                data_size=data_size
            )
            
            self.record_metrics(metrics)
            
            # 更新速率限制器
            self.rate_limiter.record_response(duration, success, error_type)
    
    def record_metrics(self, metrics: PerformanceMetrics):
        """记录性能指标"""
        with self._lock:
            # 添加到历史记录
            self.metrics_history.append(metrics)
            
            # 更新操作统计
            stats = self.operation_stats[metrics.operation]
            stats.total_requests += 1
            stats.last_request_time = datetime.fromtimestamp(metrics.start_time)
            
            if metrics.success:
                stats.successful_requests += 1
                stats.total_response_time += metrics.duration
                stats.min_response_time = min(stats.min_response_time, metrics.duration)
                stats.max_response_time = max(stats.max_response_time, metrics.duration)
            else:
                stats.failed_requests += 1
                if metrics.error_type and 'rate' in metrics.error_type.lower():
                    stats.rate_limit_hits += 1
    

    
    def get_operation_stats(self, operation: str = None) -> Dict[str, Any]:
        """
        获取操作统计信息
        
        Args:
            operation: 操作名称，None表示获取所有操作
            
        Returns:
            统计信息字典
        """
        with self._lock:
            if operation:
                if operation in self.operation_stats:
                    return {operation: self.operation_stats[operation].to_dict()}
                else:
                    return {}
            else:
                return {op: stats.to_dict() for op, stats in self.operation_stats.items()}
    
    def get_recent_metrics(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """
        获取最近的性能指标
        
        Args:
            minutes: 时间范围（分钟）
            
        Returns:
            指标列表
        """
        with self._lock:
            cutoff_time = time.time() - (minutes * 60)
            recent_metrics = [
                metrics.to_dict() 
                for metrics in self.metrics_history 
                if metrics.start_time >= cutoff_time
            ]
            return recent_metrics
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        with self._lock:
            total_operations = len(self.metrics_history)
            if total_operations == 0:
                return {
                    'total_operations': 0,
                    'success_rate': 0.0,
                    'average_response_time': 0.0,
                    'rate_limiter_stats': self.rate_limiter.get_stats()
                }
            
            successful_operations = sum(1 for m in self.metrics_history if m.success)
            total_response_time = sum(m.duration for m in self.metrics_history if m.success)
            
            return {
                'total_operations': total_operations,
                'successful_operations': successful_operations,
                'failed_operations': total_operations - successful_operations,
                'success_rate': round(successful_operations / total_operations, 4),
                'average_response_time': round(total_response_time / successful_operations, 4) if successful_operations > 0 else 0.0,
                'rate_limiter_stats': self.rate_limiter.get_stats(),
                'operation_breakdown': self.get_operation_stats()
            }
    
    def reset_stats(self):
        """重置所有统计信息"""
        with self._lock:
            self.metrics_history.clear()
            self.operation_stats.clear()
            self.rate_limiter = AdaptiveRateLimiter()
    
    def close(self):
        """关闭监控器，清理资源"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()


# 全局性能监控器实例
_global_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """获取全局性能监控器实例"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


def reset_performance_monitor():
    """重置全局性能监控器"""
    global _global_monitor
    if _global_monitor:
        _global_monitor.close()
    _global_monitor = PerformanceMonitor()