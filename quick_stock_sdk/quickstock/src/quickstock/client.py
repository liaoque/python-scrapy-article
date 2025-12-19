"""
SDK客户端类

提供简洁易用的接口，用于获取股票、指数和基金数据
"""

import asyncio
from typing import Any, Optional
import pandas as pd
from .sources.baostock import BaostockSource
from .errors import (ValidationError, NetworkError, 
                     DataSourceError, DataNotFoundError)


class QuickStockClient:
    """
    QuickStock SDK客户端类
    
    提供同步和异步两种方式的API接口，用于获取各种金融数据
    默认使用Baostock作为数据源
    """
    
    def __init__(self):
        """
        初始化客户端
        """
        # 固定使用Baostock数据源
        self.baostock = BaostockSource()
    
    def _run_async(self, coro) -> Any:
        """
        在同步方法中运行异步协程
        
        Args:
            coro: 异步协程对象
            
        Returns:
            协程执行结果
        """
        return asyncio.run(coro)
    
    # ------------------------股票数据相关方法------------------------
    
    def stock_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取股票基础信息（同步方法）
        
        Returns:
            包含股票基础信息的DataFrame
        """
        return self._run_async(self.baostock.get_stock_basic(**kwargs))
    
    async def astock_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取股票基础信息（异步方法）
        
        Returns:
            包含股票基础信息的DataFrame
        """
        return await self.baostock.get_stock_basic(**kwargs)
    
    def stock_daily(self, code: str, start_date: Optional[str] = None, 
                   end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票日线数据（同步方法）
        
        Args:
            code: 股票代码
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票日线数据的DataFrame
        """
        return self._run_async(self.baostock.get_stock_daily(
            code, start_date, end_date, **kwargs
        ))
    
    async def astock_daily(self, code: str, start_date: Optional[str] = None, 
                          end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票日线数据（异步方法）
        
        Args:
            code: 股票代码
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票日线数据的DataFrame
        """
        return await self.baostock.get_stock_daily(
            code, start_date, end_date, **kwargs
        )
    
    def stock_minute(self, code: str, start_date: Optional[str] = None, 
                    end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票分钟线数据（同步方法）
        
        Args:
            code: 股票代码
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票分钟线数据的DataFrame
        """
        return self._run_async(self.baostock.get_stock_minute(
            code, start_date, end_date, **kwargs
        ))
    
    async def astock_minute(self, code: str, start_date: Optional[str] = None, 
                           end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票分钟线数据（异步方法）
        
        Args:
            code: 股票代码
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票分钟线数据的DataFrame
        """
        return await self.baostock.get_stock_minute(
            code, start_date, end_date, **kwargs
        )
    
    def stock_weekly(self, code: str, start_date: Optional[str] = None, 
                    end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票周线数据（同步方法）
        
        Args:
            code: 股票代码
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票周线数据的DataFrame
        """
        return self._run_async(self.baostock.get_stock_weekly(
            code, start_date, end_date, **kwargs
        ))
    
    async def astock_weekly(self, code: str, start_date: Optional[str] = None, 
                           end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票周线数据（异步方法）
        
        Args:
            code: 股票代码
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票周线数据的DataFrame
        """
        return await self.baostock.get_stock_weekly(
            code, start_date, end_date, **kwargs
        )
    
    def stock_monthly(self, code: str, start_date: Optional[str] = None, 
                     end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票月线数据（同步方法）
        
        Args:
            code: 股票代码
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票月线数据的DataFrame
        """
        return self._run_async(self.baostock.get_stock_monthly(
            code, start_date, end_date, **kwargs
        ))
    
    async def astock_monthly(self, code: str, start_date: Optional[str] = None, 
                            end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票月线数据（异步方法）
        
        Args:
            code: 股票代码
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票月线数据的DataFrame
        """
        return await self.baostock.get_stock_monthly(
            code, start_date, end_date, **kwargs
        )
    
    # ------------------------指数数据相关方法------------------------
    
    def all_stock(self, **kwargs) -> pd.DataFrame:
        """
        获取所有证券信息（同步方法）
        
        Returns:
            包含所有证券信息的DataFrame
        """
        return self._run_async(self.baostock.query_all_stock(**kwargs))
    
    async def aall_stock(self, **kwargs) -> pd.DataFrame:
        """
        获取所有证券信息（异步方法）
        
        Returns:
            包含所有证券信息的DataFrame
        """
        return await self.baostock.query_all_stock(**kwargs)
    
    def index_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取指数基础信息（同步方法）
        
        Returns:
            包含指数基础信息的DataFrame
        """
        return self._run_async(self.baostock.get_index_basic(**kwargs))
    
    async def aindex_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取指数基础信息（异步方法）
        
        Returns:
            包含指数基础信息的DataFrame
        """
        return await self.baostock.get_index_basic(**kwargs)
    
    def index_daily(self, code: str, start_date: Optional[str] = None, 
                   end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数日线数据（同步方法）
        
        Args:
            code: 指数代码
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含指数日线数据的DataFrame
        """
        return self._run_async(self.baostock.get_index_daily(
            code, start_date, end_date, **kwargs
        ))
    
    async def aindex_daily(self, code: str, start_date: Optional[str] = None, 
                          end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数日线数据（异步方法）
        
        Args:
            code: 指数代码
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含指数日线数据的DataFrame
        """
        return await self.baostock.get_index_daily(
            code, start_date, end_date, **kwargs
        )
    
    def index_minute(self, code: str, start_date: Optional[str] = None, 
                    end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数分钟线数据（同步方法）
        
        Args:
            code: 指数代码
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含指数分钟线数据的DataFrame
        """
        return self._run_async(self.baostock.get_index_minute(
            code, start_date, end_date, **kwargs
        ))
    
    async def aindex_minute(self, code: str, start_date: Optional[str] = None, 
                           end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数分钟线数据（异步方法）
        
        Args:
            code: 指数代码
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含指数分钟线数据的DataFrame
        """
        return await self.baostock.get_index_minute(
            code, start_date, end_date, **kwargs
        )
    
    # ------------------------基金数据相关方法------------------------
    
    def fund_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取基金基础信息（同步方法）
        
        Returns:
            包含基金基础信息的DataFrame
        """
        return self._run_async(self.baostock.get_fund_basic(**kwargs))
    
    async def afund_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取基金基础信息（异步方法）
        
        Returns:
            包含基金基础信息的DataFrame
        """
        return await self.baostock.get_fund_basic(**kwargs)
    
    def fund_daily(self, code: str, start_date: Optional[str] = None, 
                  end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取基金日线数据（同步方法）
        
        Args:
            code: 基金代码
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含基金日线数据的DataFrame
        """
        return self._run_async(self.baostock.get_fund_daily(
            code, start_date, end_date, **kwargs
        ))
    
    async def afund_daily(self, code: str, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取基金日线数据（异步方法）
        
        Args:
            code: 基金代码
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含基金日线数据的DataFrame
        """
        return await self.baostock.get_fund_daily(
            code, start_date, end_date, **kwargs
        )
