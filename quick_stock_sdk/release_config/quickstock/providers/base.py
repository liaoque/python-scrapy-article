"""
数据提供者基类

定义数据提供者的抽象接口
"""

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING
import pandas as pd
import asyncio
import logging

if TYPE_CHECKING:
    from ..config import Config
    from ..core.connection_pool import ConnectionPoolManager


class RateLimit:
    """速率限制信息"""
    
    def __init__(self, requests_per_second: float = 1.0, 
                 requests_per_minute: int = 60,
                 requests_per_hour: int = 3600):
        """
        初始化速率限制
        
        Args:
            requests_per_second: 每秒请求数
            requests_per_minute: 每分钟请求数
            requests_per_hour: 每小时请求数
        """
        self.requests_per_second = requests_per_second
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour


class DataProvider(ABC):
    """数据提供者抽象基类"""
    
    def __init__(self, config: 'Config'):
        """
        初始化数据提供者
        
        Args:
            config: 配置对象
        """
        self.config = config
        self._connection_pool: Optional['ConnectionPoolManager'] = None
        self._semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取股票基础信息
        
        Args:
            **kwargs: 查询参数
            
        Returns:
            股票基础信息DataFrame
        """
        pass
        
    @abstractmethod
    async def get_stock_daily(self, ts_code: str, start_date: str, 
                             end_date: str) -> pd.DataFrame:
        """
        获取股票日线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            股票日线数据DataFrame
        """
        pass
        
    @abstractmethod
    async def get_trade_cal(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取交易日历
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            交易日历DataFrame
        """
        pass
    
    async def get_stock_minute(self, ts_code: str, freq: str = '1min',
                              start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取股票分钟数据（可选实现）
        
        Args:
            ts_code: 股票代码
            freq: 频率 (1min, 5min, 15min, 30min, 60min)
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            股票分钟数据DataFrame
        """
        # 默认实现：不支持分钟数据
        raise NotImplementedError(f"{self.get_provider_name()}不支持分钟数据获取")
    
    async def get_index_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取指数基础信息（可选实现）
        
        Args:
            **kwargs: 查询参数
            
        Returns:
            指数基础信息DataFrame
        """
        # 默认实现：不支持指数数据
        raise NotImplementedError(f"{self.get_provider_name()}不支持指数基础信息获取")
    
    async def get_index_daily(self, ts_code: str, start_date: str,
                             end_date: str) -> pd.DataFrame:
        """
        获取指数日线数据（可选实现）
        
        Args:
            ts_code: 指数代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            指数日线数据DataFrame
        """
        # 默认实现：不支持指数数据
        raise NotImplementedError(f"{self.get_provider_name()}不支持指数日线数据获取")
    
    async def get_fund_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取基金基础信息（可选实现）
        
        Args:
            **kwargs: 查询参数
            
        Returns:
            基金基础信息DataFrame
        """
        # 默认实现：不支持基金数据
        raise NotImplementedError(f"{self.get_provider_name()}不支持基金基础信息获取")
    
    async def get_fund_nav(self, ts_code: str, start_date: str,
                          end_date: str) -> pd.DataFrame:
        """
        获取基金净值数据（可选实现）
        
        Args:
            ts_code: 基金代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            基金净值数据DataFrame
        """
        # 默认实现：不支持基金数据
        raise NotImplementedError(f"{self.get_provider_name()}不支持基金净值数据获取")
        
    def is_available(self) -> bool:
        """
        检查数据源是否可用
        
        Returns:
            是否可用
        """
        # TODO: 实现可用性检查逻辑
        return True
        
    def get_rate_limit(self) -> RateLimit:
        """
        获取速率限制信息
        
        Returns:
            速率限制对象
        """
        # TODO: 返回具体的速率限制信息
        return RateLimit()
    
    def get_provider_name(self) -> str:
        """
        获取提供者名称
        
        Returns:
            提供者名称
        """
        return self.__class__.__name__.lower().replace('provider', '')
    
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            是否健康
        """
        # TODO: 实现健康检查逻辑
        return self.is_available()
    
    async def get_connection_pool(self) -> 'ConnectionPoolManager':
        """
        获取连接池管理器
        
        Returns:
            连接池管理器实例
        """
        if self._connection_pool is None:
            from ..core.connection_pool import ConnectionPoolManager, ConnectionPoolConfig
            
            # 创建连接池配置
            pool_config = ConnectionPoolConfig(
                connector_limit=self.config.connection_pool_size,
                connector_limit_per_host=self.config.connection_pool_per_host,
                total_timeout=self.config.request_timeout,
                keepalive_timeout=self.config.connection_keepalive_timeout,
                enable_cleanup_closed=self.config.connection_cleanup_enabled,
                max_retries=self.config.max_retries,
                retry_delay=self.config.retry_delay
            )
            
            self._connection_pool = await ConnectionPoolManager.get_instance(pool_config)
        
        return self._connection_pool
    
    async def make_request(self, method: str, url: str, **kwargs):
        """
        发起HTTP请求（使用连接池和并发控制）
        
        Args:
            method: HTTP方法
            url: 请求URL
            **kwargs: 其他请求参数
            
        Returns:
            HTTP响应对象
        """
        async with self._semaphore:  # 控制并发数量
            pool = await self.get_connection_pool()
            async with pool.pool.request(method, url, **kwargs) as response:
                return response
    
    def convert_input_code(self, code: str) -> str:
        """
        将输入代码转换为数据源所需格式
        
        Args:
            code: 输入的股票代码
            
        Returns:
            数据源所需格式的代码
            
        Note:
            子类应该重写此方法以实现特定的代码转换逻辑
        """
        # 默认实现：不进行转换
        return code
    
    def convert_output_code(self, code: str) -> str:
        """
        将数据源返回的代码转换为标准格式
        
        Args:
            code: 数据源格式的代码
            
        Returns:
            标准格式的代码
            
        Note:
            子类应该重写此方法以实现特定的代码转换逻辑
        """
        # 默认实现：不进行转换
        return code
    
    def get_required_format(self) -> str:
        """
        获取数据源要求的代码格式
        
        Returns:
            格式名称
            
        Note:
            子类应该重写此方法以返回具体的格式名称
        """
        return "unknown"
    
    def validate_code_format(self, code: str) -> bool:
        """
        验证代码格式是否符合数据源要求
        
        Args:
            code: 股票代码
            
        Returns:
            是否符合格式要求
        """
        try:
            # 尝试转换代码，如果成功则认为格式正确
            self.convert_input_code(code)
            return True
        except Exception:
            return False
    
    def validate_data_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        验证和修正数据返回格式
        
        Args:
            df: 原始数据DataFrame
            
        Returns:
            格式修正后的DataFrame
        """
        if df.empty:
            return df
        
        # 检查并修正股票代码格式
        if 'ts_code' in df.columns:
            try:
                # 安全地转换代码格式
                df['ts_code'] = df['ts_code'].apply(self._safe_convert_output_code)
                self.logger.debug(f"成功验证并修正{len(df)}条数据的代码格式")
            except Exception as e:
                self.logger.warning(f"批量代码格式修正失败，尝试逐行处理: {e}")
                # 逐行处理，跳过无法转换的行
                valid_rows = []
                for idx, row in df.iterrows():
                    try:
                        row['ts_code'] = self._safe_convert_output_code(row['ts_code'])
                        valid_rows.append(row)
                    except Exception as row_error:
                        self.logger.warning(f"跳过无效代码行: {row.get('ts_code', 'N/A')}, 错误: {row_error}")
                        continue
                df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame()
        
        return df
    
    def _safe_convert_output_code(self, code: str) -> str:
        """
        安全地转换输出代码格式
        
        Args:
            code: 股票代码
            
        Returns:
            标准格式的代码
        """
        if not code or not isinstance(code, str):
            return code
        
        # 检查是否已经是标准格式 (XXXXXX.SH 或 XXXXXX.SZ)
        import re
        if re.match(r'^[0-9]{6}\.(SH|SZ)$', code.upper()):
            # 已经是标准格式，直接返回（确保大写）
            return code.upper()
        
        # 不是标准格式，尝试转换
        try:
            return self.convert_output_code(code)
        except Exception:
            # 转换失败，返回原始代码
            self.logger.debug(f"无法转换代码格式: {code}，保持原样")
            return code
    
    def check_data_consistency(self, df: pd.DataFrame, expected_code: str = None) -> bool:
        """
        检查数据一致性
        
        Args:
            df: 数据DataFrame
            expected_code: 期望的股票代码（标准格式）
            
        Returns:
            数据是否一致
        """
        if df.empty:
            return True
        
        # 检查代码一致性
        if expected_code and 'ts_code' in df.columns:
            try:
                # 标准化期望代码
                from ..utils.code_converter import StockCodeConverter
                standard_expected = StockCodeConverter.normalize_code(expected_code)
                
                # 检查所有行的代码是否与期望一致
                unique_codes = df['ts_code'].unique()
                if len(unique_codes) != 1 or unique_codes[0] != standard_expected:
                    self.logger.warning(f"数据代码不一致: 期望 {standard_expected}, 实际 {unique_codes}")
                    return False
                    
            except Exception as e:
                self.logger.error(f"代码一致性检查失败: {e}")
                return False
        
        # 检查必要字段
        required_fields = ['ts_code']
        missing_fields = [field for field in required_fields if field not in df.columns]
        if missing_fields:
            self.logger.warning(f"数据缺少必要字段: {missing_fields}")
            return False
        
        return True
    
    async def close(self):
        """
        关闭数据提供者，清理资源
        """
        if self._connection_pool:
            await self._connection_pool.close()
            self._connection_pool = None