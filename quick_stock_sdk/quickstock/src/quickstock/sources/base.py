"""
数据源抽象基类

定义所有数据源必须实现的接口方法，确保不同数据源之间的一致性
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import pandas as pd


class BaseSource(ABC):
    """
    数据源抽象基类
    所有具体数据源实现都必须继承此类并实现所有抽象方法
    """
    
    def __init__(self, name: str):
        """
        初始化数据源
        
        Args:
            name: 数据源名称
        """
        self.name = name
    
    # 股票基础数据
    @abstractmethod
    async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取股票基础信息
        
        Returns:
            包含股票基础信息的DataFrame
        """
        pass
    
    # 股票日线数据
    @abstractmethod
    async def get_stock_daily(self, codes: List[str], start_date: Optional[str] = None, 
                            end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票日线数据
        
        Args:
            codes: 股票代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票日线数据的DataFrame
        """
        pass
    
    # 股票分钟线数据
    @abstractmethod
    async def get_stock_minute(self, codes: List[str], start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票分钟线数据
        
        Args:
            codes: 股票代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票分钟线数据的DataFrame
        """
        pass
    
    # 股票周线数据
    @abstractmethod
    async def get_stock_weekly(self, codes: List[str], start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票周线数据
        
        Args:
            codes: 股票代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票周线数据的DataFrame
        """
        pass
    
    # 股票月线数据
    @abstractmethod
    async def get_stock_monthly(self, codes: List[str], start_date: Optional[str] = None, 
                               end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票月线数据
        
        Args:
            codes: 股票代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票月线数据的DataFrame
        """
        pass
    
    # 指数基础数据
    @abstractmethod
    async def get_index_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取指数基础信息
        
        Returns:
            包含指数基础信息的DataFrame
        """
        pass
    
    # 指数日线数据
    @abstractmethod
    async def get_index_daily(self, codes: List[str], start_date: Optional[str] = None, 
                            end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数日线数据
        
        Args:
            codes: 指数代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含指数日线数据的DataFrame
        """
        pass
    
    # 指数分钟线数据
    @abstractmethod
    async def get_index_minute(self, codes: List[str], start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数分钟线数据
        
        Args:
            codes: 指数代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含指数分钟线数据的DataFrame
        """
        pass
    
    # 指数周线数据
    @abstractmethod
    async def get_index_weekly(self, codes: List[str], start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数周线数据
        
        Args:
            codes: 指数代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含指数周线数据的DataFrame
        """
        pass
    
    # 指数月线数据
    @abstractmethod
    async def get_index_monthly(self, codes: List[str], start_date: Optional[str] = None, 
                               end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数月线数据
        
        Args:
            codes: 指数代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含指数月线数据的DataFrame
        """
        pass
    
    # 基金基础数据
    @abstractmethod
    async def get_fund_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取基金基础信息
        
        Returns:
            包含基金基础信息的DataFrame
        """
        pass
    
    # 基金日线数据
    @abstractmethod
    async def get_fund_daily(self, codes: List[str], start_date: Optional[str] = None, 
                            end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取基金日线数据
        
        Args:
            codes: 基金代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含基金日线数据的DataFrame
        """
        pass
    
    # 基金分钟线数据
    @abstractmethod
    async def get_fund_minute(self, codes: List[str], start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取基金分钟线数据
        
        Args:
            codes: 基金代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含基金分钟线数据的DataFrame
        """
        pass
    
    # 基金周线数据
    @abstractmethod
    async def get_fund_weekly(self, codes: List[str], start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取基金周线数据
        
        Args:
            codes: 基金代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含基金周线数据的DataFrame
        """
        pass
    
    # 基金月线数据
    @abstractmethod
    async def get_fund_monthly(self, codes: List[str], start_date: Optional[str] = None, 
                               end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取基金月线数据
        
        Args:
            codes: 基金代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含基金月线数据的DataFrame
        """
        pass
    
    # 交易日查询
    @abstractmethod
    async def query_trade_dates(self, start_date: Optional[str] = None, 
                               end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        查询交易日数据
        
        Args:
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含交易日数据的DataFrame
        """
        pass
