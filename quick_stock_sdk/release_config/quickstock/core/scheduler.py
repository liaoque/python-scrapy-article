"""
并发请求调度器

提供智能的请求调度和负载均衡功能
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import heapq

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """任务优先级"""
    URGENT = 1      # 紧急任务
    HIGH = 2        # 高优先级
    NORMAL = 3      # 普通优先级
    LOW = 4         # 低优先级
    BACKGROUND = 5  # 后台任务


@dataclass
class ScheduledTask:
    """调度任务"""
    id: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: float = field(default_factory=time.time)
    max_retries: int = 3
    retry_count: int = 0
    delay: float = 0.0  # 延迟执行时间（秒）
    
    def __lt__(self, other):
        """用于优先队列排序"""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.created_at < other.created_at


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    success: bool
    result: Any = None
    error: Exception = None
    execution_time: float = 0.0
    retry_count: int = 0


class RequestScheduler:
    """并发请求调度器"""
    
    def __init__(self, max_concurrent: int = 10, max_queue_size: int = 1000):
        """
        初始化调度器
        
        Args:
            max_concurrent: 最大并发数
            max_queue_size: 最大队列大小
        """
        self.max_concurrent = max_concurrent
        self.max_queue_size = max_queue_size
        
        # 任务队列（优先队列）
        self._task_queue: List[ScheduledTask] = []
        self._delayed_tasks: List[Tuple[float, ScheduledTask]] = []  # (执行时间, 任务)
        
        # 运行状态
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._completed_tasks: Dict[str, TaskResult] = {}
        self._failed_tasks: Dict[str, TaskResult] = {}
        
        # 控制信号量
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._queue_lock = asyncio.Lock()
        self._running = False
        self._scheduler_task: Optional[asyncio.Task] = None
        
        # 统计信息
        self._stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'retried_tasks': 0,
            'queue_full_rejections': 0,
            'average_execution_time': 0.0,
            'peak_concurrent_tasks': 0
        }
        
        # 负载均衡
        self._provider_load: Dict[str, int] = defaultdict(int)  # 每个提供者的当前负载
        self._provider_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'last_request_time': 0.0
        })
    
    async def start(self):
        """启动调度器"""
        if self._running:
            return
        
        self._running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info(f"请求调度器已启动，最大并发数: {self.max_concurrent}")
    
    async def stop(self):
        """停止调度器"""
        if not self._running:
            return
        
        self._running = False
        
        # 等待调度器任务完成
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        
        # 取消所有运行中的任务
        if self._running_tasks:
            for task in self._running_tasks.values():
                task.cancel()
            
            # 等待所有任务完成或取消
            await asyncio.gather(*self._running_tasks.values(), return_exceptions=True)
        
        logger.info("请求调度器已停止")
    
    async def submit_task(self, task_id: str, func: Callable, *args, 
                         priority: TaskPriority = TaskPriority.NORMAL,
                         max_retries: int = 3, delay: float = 0.0, **kwargs) -> bool:
        """
        提交任务到调度器
        
        Args:
            task_id: 任务ID
            func: 要执行的函数
            *args: 函数参数
            priority: 任务优先级
            max_retries: 最大重试次数
            delay: 延迟执行时间（秒）
            **kwargs: 函数关键字参数
            
        Returns:
            是否成功提交
        """
        async with self._queue_lock:
            # 检查队列是否已满
            total_queued = len(self._task_queue) + len(self._delayed_tasks)
            if total_queued >= self.max_queue_size:
                self._stats['queue_full_rejections'] += 1
                logger.warning(f"任务队列已满，拒绝任务: {task_id}")
                return False
            
            # 创建任务
            task = ScheduledTask(
                id=task_id,
                func=func,
                args=args,
                kwargs=kwargs,
                priority=priority,
                max_retries=max_retries,
                delay=delay
            )
            
            # 根据延迟时间决定放入哪个队列
            if delay > 0:
                execute_time = time.time() + delay
                heapq.heappush(self._delayed_tasks, (execute_time, task))
                logger.debug(f"任务 {task_id} 已加入延迟队列，{delay}秒后执行")
            else:
                heapq.heappush(self._task_queue, task)
                logger.debug(f"任务 {task_id} 已加入执行队列")
            
            self._stats['total_tasks'] += 1
            return True
    
    async def get_task_result(self, task_id: str, timeout: float = None) -> Optional[TaskResult]:
        """
        获取任务结果
        
        Args:
            task_id: 任务ID
            timeout: 超时时间（秒）
            
        Returns:
            任务结果，如果任务未完成则返回None
        """
        start_time = time.time()
        
        while True:
            # 检查已完成的任务
            if task_id in self._completed_tasks:
                return self._completed_tasks[task_id]
            
            # 检查失败的任务
            if task_id in self._failed_tasks:
                return self._failed_tasks[task_id]
            
            # 检查超时
            if timeout and (time.time() - start_time) > timeout:
                logger.warning(f"等待任务结果超时: {task_id}")
                return None
            
            # 短暂等待
            await asyncio.sleep(0.1)
    
    async def wait_for_task(self, task_id: str, timeout: float = None) -> TaskResult:
        """
        等待任务完成
        
        Args:
            task_id: 任务ID
            timeout: 超时时间（秒）
            
        Returns:
            任务结果
            
        Raises:
            asyncio.TimeoutError: 等待超时
            RuntimeError: 任务不存在
        """
        result = await self.get_task_result(task_id, timeout)
        if result is None:
            if timeout:
                raise asyncio.TimeoutError(f"等待任务 {task_id} 超时")
            else:
                raise RuntimeError(f"任务 {task_id} 不存在")
        
        return result
    
    async def _scheduler_loop(self):
        """调度器主循环"""
        while self._running:
            try:
                # 处理延迟任务
                await self._process_delayed_tasks()
                
                # 处理普通任务
                await self._process_regular_tasks()
                
                # 清理完成的任务
                await self._cleanup_completed_tasks()
                
                # 更新统计信息
                self._update_stats()
                
                # 短暂休息
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"调度器循环异常: {e}")
                await asyncio.sleep(1.0)
    
    async def _process_delayed_tasks(self):
        """处理延迟任务"""
        current_time = time.time()
        
        async with self._queue_lock:
            # 将到期的延迟任务移到普通队列
            while self._delayed_tasks:
                execute_time, task = self._delayed_tasks[0]
                if execute_time <= current_time:
                    heapq.heappop(self._delayed_tasks)
                    heapq.heappush(self._task_queue, task)
                    logger.debug(f"延迟任务 {task.id} 已移入执行队列")
                else:
                    break
    
    async def _process_regular_tasks(self):
        """处理普通任务"""
        # 检查是否有可用的执行槽位
        if len(self._running_tasks) >= self.max_concurrent:
            return
        
        async with self._queue_lock:
            # 获取下一个任务
            if not self._task_queue:
                return
            
            task = heapq.heappop(self._task_queue)
        
        # 执行任务
        asyncio_task = asyncio.create_task(self._execute_task(task))
        self._running_tasks[task.id] = asyncio_task
        
        # 更新峰值并发数
        current_concurrent = len(self._running_tasks)
        if current_concurrent > self._stats['peak_concurrent_tasks']:
            self._stats['peak_concurrent_tasks'] = current_concurrent
    
    async def _execute_task(self, task: ScheduledTask):
        """
        执行单个任务
        
        Args:
            task: 要执行的任务
        """
        start_time = time.time()
        
        try:
            async with self._semaphore:
                # 执行任务函数
                if asyncio.iscoroutinefunction(task.func):
                    result = await task.func(*task.args, **task.kwargs)
                else:
                    result = task.func(*task.args, **task.kwargs)
                
                execution_time = time.time() - start_time
                
                # 记录成功结果
                task_result = TaskResult(
                    task_id=task.id,
                    success=True,
                    result=result,
                    execution_time=execution_time,
                    retry_count=task.retry_count
                )
                
                self._completed_tasks[task.id] = task_result
                self._stats['completed_tasks'] += 1
                
                logger.debug(f"任务 {task.id} 执行成功，耗时 {execution_time:.2f}秒")
                
        except Exception as e:
            execution_time = time.time() - start_time
            
            # 检查是否需要重试
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                self._stats['retried_tasks'] += 1
                
                # 计算重试延迟（指数退避）
                retry_delay = min(2.0 ** task.retry_count, 60.0)
                
                logger.warning(f"任务 {task.id} 执行失败，{retry_delay}秒后重试 (第{task.retry_count}次): {e}")
                
                # 重新加入延迟队列
                async with self._queue_lock:
                    execute_time = time.time() + retry_delay
                    heapq.heappush(self._delayed_tasks, (execute_time, task))
            else:
                # 记录失败结果
                task_result = TaskResult(
                    task_id=task.id,
                    success=False,
                    error=e,
                    execution_time=execution_time,
                    retry_count=task.retry_count
                )
                
                self._failed_tasks[task.id] = task_result
                self._stats['failed_tasks'] += 1
                
                logger.error(f"任务 {task.id} 最终执行失败: {e}")
        
        finally:
            # 从运行任务列表中移除
            self._running_tasks.pop(task.id, None)
    
    async def _cleanup_completed_tasks(self):
        """清理完成的任务（保留最近的结果）"""
        max_results = 1000  # 最多保留1000个结果
        
        # 清理完成的任务
        if len(self._completed_tasks) > max_results:
            # 按时间排序，保留最新的
            sorted_tasks = sorted(
                self._completed_tasks.items(),
                key=lambda x: x[1].task_id,  # 简单按ID排序
                reverse=True
            )
            
            # 保留最新的结果
            self._completed_tasks = dict(sorted_tasks[:max_results])
        
        # 清理失败的任务
        if len(self._failed_tasks) > max_results:
            sorted_tasks = sorted(
                self._failed_tasks.items(),
                key=lambda x: x[1].task_id,
                reverse=True
            )
            
            self._failed_tasks = dict(sorted_tasks[:max_results])
    
    def _update_stats(self):
        """更新统计信息"""
        # 计算平均执行时间
        if self._completed_tasks:
            total_time = sum(result.execution_time for result in self._completed_tasks.values())
            self._stats['average_execution_time'] = total_time / len(self._completed_tasks)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取调度器统计信息"""
        return {
            **self._stats,
            'current_queue_size': len(self._task_queue),
            'delayed_tasks_count': len(self._delayed_tasks),
            'running_tasks_count': len(self._running_tasks),
            'completed_tasks_count': len(self._completed_tasks),
            'failed_tasks_count': len(self._failed_tasks),
            'queue_utilization': len(self._task_queue) / self.max_queue_size,
            'concurrent_utilization': len(self._running_tasks) / self.max_concurrent
        }
    
    def get_provider_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取数据提供者统计信息"""
        return dict(self._provider_stats)
    
    def update_provider_stats(self, provider: str, success: bool, response_time: float):
        """
        更新数据提供者统计信息
        
        Args:
            provider: 提供者名称
            success: 是否成功
            response_time: 响应时间
        """
        stats = self._provider_stats[provider]
        stats['total_requests'] += 1
        stats['last_request_time'] = time.time()
        
        if success:
            stats['successful_requests'] += 1
        else:
            stats['failed_requests'] += 1
        
        # 更新平均响应时间
        if stats['total_requests'] == 1:
            stats['average_response_time'] = response_time
        else:
            # 使用移动平均
            alpha = 0.1  # 平滑因子
            stats['average_response_time'] = (
                alpha * response_time + 
                (1 - alpha) * stats['average_response_time']
            )
    
    def get_best_provider(self, providers: List[str]) -> Optional[str]:
        """
        根据统计信息选择最佳数据提供者
        
        Args:
            providers: 可用的提供者列表
            
        Returns:
            最佳提供者名称
        """
        if not providers:
            return None
        
        if len(providers) == 1:
            return providers[0]
        
        # 计算每个提供者的得分
        scores = {}
        for provider in providers:
            stats = self._provider_stats.get(provider, {})
            
            # 基础得分
            score = 100.0
            
            # 成功率权重 (40%)
            total_requests = stats.get('total_requests', 0)
            if total_requests > 0:
                success_rate = stats.get('successful_requests', 0) / total_requests
                score += success_rate * 40
            
            # 响应时间权重 (30%) - 响应时间越短得分越高
            avg_response_time = stats.get('average_response_time', 1.0)
            if avg_response_time > 0:
                time_score = max(0, 30 - avg_response_time * 10)  # 假设1秒以内为满分
                score += time_score
            
            # 当前负载权重 (20%) - 负载越低得分越高
            current_load = self._provider_load.get(provider, 0)
            load_score = max(0, 20 - current_load * 2)
            score += load_score
            
            # 最近使用时间权重 (10%) - 避免长时间不使用的提供者
            last_request_time = stats.get('last_request_time', 0)
            if last_request_time > 0:
                time_since_last = time.time() - last_request_time
                if time_since_last < 300:  # 5分钟内
                    score += 10
                elif time_since_last < 3600:  # 1小时内
                    score += 5
            
            scores[provider] = score
        
        # 返回得分最高的提供者
        best_provider = max(scores.items(), key=lambda x: x[1])[0]
        logger.debug(f"选择最佳提供者: {best_provider}, 得分: {scores}")
        
        return best_provider
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.stop()