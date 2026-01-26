"""
SDK客户端类

提供简洁易用的接口，用于获取股票、指数和基金数据
"""

import asyncio
from typing import Any, Optional, List
import pandas as pd
from .sources.baostock import BaostockSource
from .sources.tonghuashun import TongHuaShunSource


class QuickStockClient:
    """
    QuickStock SDK客户端类
    
    提供同步和异步两种方式的API接口，用于获取各种金融数据
    默认使用Baostock作为数据源，同时支持同花顺数据源获取板块数据
    """
    
    def __init__(self):
        """
        初始化客户端
        """
        # 固定使用Baostock数据源
        self.baostock = BaostockSource()
        # 同花顺数据源，用于获取板块数据
        self.tonghuashun = TongHuaShunSource()
    
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
    
    def stock_daily(self, codes: List[str], start_date: Optional[str] = None, 
                   end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票日线数据（同步方法）
        
        Args:
            codes: 股票代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票日线数据的DataFrame，字段包括：
            - trade_date: 交易所行情日期
            - code: 证券代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - preclose: 前收盘价
            - volume: 成交量（股）
            - amount: 成交额（元）
            - adjustflag: 复权状态(1:后复权, 2:前复权, 3:不复权)
            - turn: 换手率(%)
            - tradestatus: 交易状态(1:正常, 0:停牌)
            - pctChg: 涨跌幅(%)
            - isST: 是否ST股(1:是, 0:否)
            - peTTM: 滚动市盈率
            - pbMRQ: 市净率
            - psTTM: 滚动市销率
            - pcfNcfTTM: 滚动市现率
        """
        return self._run_async(self.baostock.get_stock_daily(
            codes, start_date, end_date, **kwargs
        ))
    
    async def astock_daily(self, codes: List[str], start_date: Optional[str] = None, 
                          end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票日线数据（异步方法）
        
        Args:
            codes: 股票代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票日线数据的DataFrame，字段包括：
            - trade_date: 交易所行情日期
            - code: 证券代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - preclose: 前收盘价
            - volume: 成交量（股）
            - amount: 成交额（元）
            - adjustflag: 复权状态(1:后复权, 2:前复权, 3:不复权)
            - turn: 换手率(%)
            - tradestatus: 交易状态(1:正常, 0:停牌)
            - pctChg: 涨跌幅(%)
            - isST: 是否ST股(1:是, 0:否)
            - peTTM: 滚动市盈率
            - pbMRQ: 市净率
            - psTTM: 滚动市销率
            - pcfNcfTTM: 滚动市现率
        """
        return await self.baostock.get_stock_daily(
            codes, start_date, end_date, **kwargs
        )
    
    def stock_minute(self, codes: List[str], start_date: Optional[str] = None, 
                    end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票分钟线数据（同步方法）
        
        Args:
            codes: 股票代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            **kwargs:
                frequency: 分钟线频率，支持5/15/30/60，默认5分钟
                
        Returns:
            包含股票分钟线数据的DataFrame，字段包括：
            - trade_date: 交易所行情日期
            - time: 交易所行情时间
            - code: 证券代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量（股）
            - amount: 成交额（元）
            - adjustflag: 复权状态
        """
        return self._run_async(self.baostock.get_stock_minute(
            codes, start_date, end_date, **kwargs
        ))
    
    async def astock_minute(self, codes: List[str], start_date: Optional[str] = None, 
                           end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票分钟线数据（异步方法）
        
        Args:
            codes: 股票代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            **kwargs:
                frequency: 分钟线频率，支持5/15/30/60，默认5分钟
                
        Returns:
            包含股票分钟线数据的DataFrame，字段包括：
            - trade_date: 交易所行情日期
            - time: 交易所行情时间
            - code: 证券代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量（股）
            - amount: 成交额（元）
            - adjustflag: 复权状态
        """
        return await self.baostock.get_stock_minute(
            codes, start_date, end_date, **kwargs
        )
    
    def stock_weekly(self, codes: List[str], start_date: Optional[str] = None, 
                    end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票周线数据（同步方法）
        
        Args:
            codes: 股票代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票周线数据的DataFrame，字段包括：
            - trade_date: 交易所行情日期
            - code: 证券代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量（股）
            - amount: 成交额（元）
            - adjustflag: 复权状态(1:后复权, 2:前复权, 3:不复权)
            - turn: 换手率(%)
            - pctChg: 涨跌幅(%)
        """
        return self._run_async(self.baostock.get_stock_weekly(
            codes, start_date, end_date, **kwargs
        ))
    
    async def astock_weekly(self, codes: List[str], start_date: Optional[str] = None, 
                           end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票周线数据（异步方法）
        
        Args:
            codes: 股票代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票周线数据的DataFrame，字段包括：
            - trade_date: 交易所行情日期
            - code: 证券代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量（股）
            - amount: 成交额（元）
            - adjustflag: 复权状态(1:后复权, 2:前复权, 3:不复权)
            - turn: 换手率(%)
            - pctChg: 涨跌幅(%)
        """
        return await self.baostock.get_stock_weekly(
            codes, start_date, end_date, **kwargs
        )
    
    def stock_monthly(self, codes: List[str], start_date: Optional[str] = None, 
                     end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票月线数据（同步方法）
        
        Args:
            codes: 股票代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票月线数据的DataFrame，字段包括：
            - trade_date: 交易所行情日期
            - code: 证券代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量（股）
            - amount: 成交额（元）
            - adjustflag: 复权状态(1:后复权, 2:前复权, 3:不复权)
            - turn: 换手率(%)
            - pctChg: 涨跌幅(%)
        """
        return self._run_async(self.baostock.get_stock_monthly(
            codes, start_date, end_date, **kwargs
        ))
    
    async def astock_monthly(self, codes: List[str], start_date: Optional[str] = None, 
                            end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票月线数据（异步方法）
        
        Args:
            codes: 股票代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含股票月线数据的DataFrame，字段包括：
            - trade_date: 交易所行情日期
            - code: 证券代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量（股）
            - amount: 成交额（元）
            - adjustflag: 复权状态(1:后复权, 2:前复权, 3:不复权)
            - turn: 换手率(%)
            - pctChg: 涨跌幅(%)
        """
        return await self.baostock.get_stock_monthly(
            codes, start_date, end_date, **kwargs
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
    
    def index_daily(self, codes: List[str], start_date: Optional[str] = None, 
                   end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数日线数据（同步方法）
        
        Args:
            codes: 指数代码列表，如['sh.000001', 'sz.399001']
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含指数日线数据的DataFrame，字段包括：
            - trade_date: 交易所行情日期
            - code: 证券代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - preclose: 昨日收盘价
            - volume: 成交量（股）
            - amount: 成交额（元）
            - pctChg: 涨跌幅(%)
        """
        return self._run_async(self.baostock.get_index_daily(
            codes, start_date, end_date, **kwargs
        ))
    
    async def aindex_daily(self, codes: List[str], start_date: Optional[str] = None, 
                          end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数日线数据（异步方法）
        
        Args:
            codes: 指数代码列表，如['sh.000001', 'sz.399001']
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含指数日线数据的DataFrame，字段包括：
            - trade_date: 交易所行情日期
            - code: 证券代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - preclose: 昨日收盘价
            - volume: 成交量（股）
            - amount: 成交额（元）
            - pctChg: 涨跌幅(%)
        """
        return await self.baostock.get_index_daily(
            codes, start_date, end_date, **kwargs
        )
    
    def index_minute(self, codes: List[str], start_date: Optional[str] = None, 
                    end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数分钟线数据（同步方法）
        
        Args:
            codes: 指数代码列表，如['sh.000001', 'sz.399001']
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            **kwargs:
                frequency: 分钟线频率，支持5/15/30/60，默认5分钟
                
        Returns:
            包含指数分钟线数据的DataFrame，字段包括：
            - trade_date: 交易所行情日期
            - time: 交易所行情时间
            - code: 证券代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量（股）
            - amount: 成交额（元）
            - adjustflag: 复权状态
        """
        return self._run_async(self.baostock.get_index_minute(
            codes, start_date, end_date, **kwargs
        ))
    
    async def aindex_minute(self, codes: List[str], start_date: Optional[str] = None, 
                           end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数分钟线数据（异步方法）
        
        Args:
            codes: 指数代码列表，如['sh.000001', 'sz.399001']
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            **kwargs:
                frequency: 分钟线频率，支持5/15/30/60，默认5分钟
                
        Returns:
            包含指数分钟线数据的DataFrame，字段包括：
            - trade_date: 交易所行情日期
            - time: 交易所行情时间
            - code: 证券代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量（股）
            - amount: 成交额（元）
            - adjustflag: 复权状态
        """
        return await self.baostock.get_index_minute(
            codes, start_date, end_date, **kwargs
        )
    
    def index_weekly(self, codes: List[str], start_date: Optional[str] = None, 
                    end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数周线数据（同步方法）
        
        Args:
            codes: 指数代码列表，如['sh.000001', 'sz.399001']
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含指数周线数据的DataFrame，字段包括：
            - trade_date: 交易所行情日期
            - code: 证券代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - preclose: 昨日收盘价
            - volume: 成交量（股）
            - amount: 成交额（元）
            - pctChg: 涨跌幅(%)
        """
        return self._run_async(self.baostock.get_index_weekly(
            codes, start_date, end_date, **kwargs
        ))
    
    async def aindex_weekly(self, codes: List[str], start_date: Optional[str] = None, 
                           end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数周线数据（异步方法）
        
        Args:
            codes: 指数代码列表，如['sh.000001', 'sz.399001']
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含指数周线数据的DataFrame，字段包括：
            - trade_date: 交易所行情日期
            - code: 证券代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - preclose: 昨日收盘价
            - volume: 成交量（股）
            - amount: 成交额（元）
            - pctChg: 涨跌幅(%)
        """
        return await self.baostock.get_index_weekly(
            codes, start_date, end_date, **kwargs
        )
    

    
    def index_monthly(self, codes: List[str], start_date: Optional[str] = None, 
                     end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数月线数据（同步方法）
        
        Args:
            codes: 指数代码列表，如['sh.000001', 'sz.399001']
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含指数月线数据的DataFrame，字段包括：
            - trade_date: 交易所行情日期
            - code: 证券代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - preclose: 昨日收盘价
            - volume: 成交量（股）
            - amount: 成交额（元）
            - pctChg: 涨跌幅(%)
        """
        return self._run_async(self.baostock.get_index_monthly(
            codes, start_date, end_date, **kwargs
        ))
    
    async def aindex_monthly(self, codes: List[str], start_date: Optional[str] = None, 
                            end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数月线数据（异步方法）
        
        Args:
            codes: 指数代码列表，如['sh.000001', 'sz.399001']
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含指数月线数据的DataFrame，字段包括：
            - trade_date: 交易所行情日期
            - code: 证券代码
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - preclose: 昨日收盘价
            - volume: 成交量（股）
            - amount: 成交额（元）
            - pctChg: 涨跌幅(%)
        """
        return await self.baostock.get_index_monthly(
            codes, start_date, end_date, **kwargs
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
    
    def fund_daily(self, codes: List[str], start_date: Optional[str] = None, 
                  end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取基金日线数据（同步方法）
        
        Args:
            codes: 基金代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含基金日线数据的DataFrame
        """
        return self._run_async(self.baostock.get_fund_daily(
            codes, start_date, end_date, **kwargs
        ))
    
    async def afund_daily(self, codes: List[str], start_date: Optional[str] = None, 
                         end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取基金日线数据（异步方法）
        
        Args:
            codes: 基金代码列表
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含基金日线数据的DataFrame
        """
        return await self.baostock.get_fund_daily(
            codes, start_date, end_date, **kwargs
        )
    
    # ------------------------辅助数据相关方法------------------------
    
    def query_trade_dates(self, start_date: Optional[str] = None, 
                          end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        查询交易日数据（同步方法）
        
        Args:
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含交易日数据的DataFrame
        """
        return self._run_async(self.baostock.query_trade_dates(
            start_date, end_date, **kwargs
        ))
    
    async def aquery_trade_dates(self, start_date: Optional[str] = None, 
                               end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        查询交易日数据（异步方法）
        
        Args:
            start_date: 开始日期，格式如'2024-01-01'
            end_date: 结束日期，格式如'2024-01-31'
            
        Returns:
            包含交易日数据的DataFrame
        """
        return await self.baostock.query_trade_dates(
            start_date, end_date, **kwargs
        )
    
    # ------------------------同花顺板块数据相关方法------------------------
    
    def concept_list(self) -> pd.DataFrame:
        """
        获取所有概念板块列表（同步方法）
        
        Returns:
            包含概念板块信息的DataFrame，字段包括：
            - code: 板块代码
            - name: 板块名称
            - cid: 板块ID
        """
        return self._run_async(self.tonghuashun.get_concept_list())
    
    async def aconcept_list(self) -> pd.DataFrame:
        """
        获取所有概念板块列表（异步方法）
        
        Returns:
            包含概念板块信息的DataFrame，字段包括：
            - code: 板块代码
            - name: 板块名称
            - cid: 板块ID
        """
        return await self.tonghuashun.get_concept_list()
    
    def concept_stocks(self, concept_code: str) -> pd.DataFrame:
        """
        获取指定概念板块的成分股（同步方法）
        
        Args:
            concept_code: 概念板块代码，如'885943'
            
        Returns:
            包含成分股信息的DataFrame，字段包括：
            - code: 股票代码
            - cid: 概念板块ID
        """
        return self._run_async(self.tonghuashun.get_concept_stocks(concept_code))
    
    async def aconcept_stocks(self, concept_code: str) -> pd.DataFrame:
        """
        获取指定概念板块的成分股（异步方法）
        
        Args:
            concept_code: 概念板块代码，如'885943'
            
        Returns:
            包含成分股信息的DataFrame，字段包括：
            - code: 股票代码
            - cid: 概念板块ID
        """
        return await self.tonghuashun.get_concept_stocks(concept_code)
    
    def board_daily(self, board_code: str, start_date: Optional[str] = None, 
                   end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块日线数据（同步方法）
        
        Args:
            board_code: 板块代码，如'885943'或'bk_885943'
            start_date: 开始日期，格式如'2024-01-01'（暂未使用）
            end_date: 结束日期，格式如'2024-01-31'（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块日线数据的DataFrame，字段包括：
            - date_at: 日期
            - start: 开盘价
            - end: 收盘价
            - max: 最高价
            - min: 最低价
            - count: 成交量
            - amount: 成交额
            - amplitude: 振幅
            - range: 涨跌幅
            - range_amount: 涨跌额
            - turnover_rate: 换手率
        """
        return self._run_async(self.tonghuashun.get_board_daily(
            board_code, start_date, end_date, **kwargs
        ))
    
    async def aboard_daily(self, board_code: str, start_date: Optional[str] = None, 
                          end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块日线数据（异步方法）
        
        Args:
            board_code: 板块代码，如'885943'或'bk_885943'
            start_date: 开始日期，格式如'2024-01-01'（暂未使用）
            end_date: 结束日期，格式如'2024-01-31'（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块日线数据的DataFrame
        """
        return await self.tonghuashun.get_board_daily(
            board_code, start_date, end_date, **kwargs
        )
    
    def board_weekly(self, board_code: str, start_date: Optional[str] = None, 
                    end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块周线数据（同步方法）
        
        Args:
            board_code: 板块代码，如'885943'或'bk_885943'
            start_date: 开始日期，格式如'2024-01-01'（暂未使用）
            end_date: 结束日期，格式如'2024-01-31'（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块周线数据的DataFrame
        """
        return self._run_async(self.tonghuashun.get_board_weekly(
            board_code, start_date, end_date, **kwargs
        ))
    
    async def aboard_weekly(self, board_code: str, start_date: Optional[str] = None, 
                           end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块周线数据（异步方法）
        
        Args:
            board_code: 板块代码，如'885943'或'bk_885943'
            start_date: 开始日期，格式如'2024-01-01'（暂未使用）
            end_date: 结束日期，格式如'2024-01-31'（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块周线数据的DataFrame
        """
        return await self.tonghuashun.get_board_weekly(
            board_code, start_date, end_date, **kwargs
        )
    
    def board_monthly(self, board_code: str, start_date: Optional[str] = None, 
                     end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块月线数据（同步方法）
        
        Args:
            board_code: 板块代码，如'885943'或'bk_885943'
            start_date: 开始日期，格式如'2024-01-01'（暂未使用）
            end_date: 结束日期，格式如'2024-01-31'（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块月线数据的DataFrame
        """
        return self._run_async(self.tonghuashun.get_board_monthly(
            board_code, start_date, end_date, **kwargs
        ))
    
    async def aboard_monthly(self, board_code: str, start_date: Optional[str] = None, 
                            end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块月线数据（异步方法）
        
        Args:
            board_code: 板块代码，如'885943'或'bk_885943'
            start_date: 开始日期，格式如'2024-01-01'（暂未使用）
            end_date: 结束日期，格式如'2024-01-31'（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块月线数据的DataFrame
        """
        return await self.tonghuashun.get_board_monthly(
            board_code, start_date, end_date, **kwargs
        )
    
    def board_minute(self, board_code: str, start_date: Optional[str] = None, 
                    end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块分钟线数据（同步方法，1分钟）
        
        Args:
            board_code: 板块代码，如'885943'或'bk_885943'
            start_date: 开始日期，格式如'2024-01-01'（暂未使用）
            end_date: 结束日期，格式如'2024-01-31'（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块分钟线数据的DataFrame
        """
        return self._run_async(self.tonghuashun.get_board_minute(
            board_code, start_date, end_date, **kwargs
        ))
    
    async def aboard_minute(self, board_code: str, start_date: Optional[str] = None, 
                           end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块分钟线数据（异步方法，1分钟）
        
        Args:
            board_code: 板块代码，如'885943'或'bk_885943'
            start_date: 开始日期，格式如'2024-01-01'（暂未使用）
            end_date: 结束日期，格式如'2024-01-31'（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块分钟线数据的DataFrame
        """
        return await self.tonghuashun.get_board_minute(
            board_code, start_date, end_date, **kwargs
        )
    
    def board_minute30(self, board_code: str, start_date: Optional[str] = None, 
                      end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块30分钟线数据（同步方法）
        
        Args:
            board_code: 板块代码，如'885943'或'bk_885943'
            start_date: 开始日期，格式如'2024-01-01'（暂未使用）
            end_date: 结束日期，格式如'2024-01-31'（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块30分钟线数据的DataFrame
        """
        return self._run_async(self.tonghuashun.get_board_minute30(
            board_code, start_date, end_date, **kwargs
        ))
    
    async def aboard_minute30(self, board_code: str, start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块30分钟线数据（异步方法）
        
        Args:
            board_code: 板块代码，如'885943'或'bk_885943'
            start_date: 开始日期，格式如'2024-01-01'（暂未使用）
            end_date: 结束日期，格式如'2024-01-31'（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块30分钟线数据的DataFrame
        """
        return await self.tonghuashun.get_board_minute30(
            board_code, start_date, end_date, **kwargs
        )
    
    def board_minute60(self, board_code: str, start_date: Optional[str] = None, 
                      end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块60分钟线数据（同步方法）
        
        Args:
            board_code: 板块代码，如'885943'或'bk_885943'
            start_date: 开始日期，格式如'2024-01-01'（暂未使用）
            end_date: 结束日期，格式如'2024-01-31'（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块60分钟线数据的DataFrame
        """
        return self._run_async(self.tonghuashun.get_board_minute60(
            board_code, start_date, end_date, **kwargs
        ))
    
    async def aboard_minute60(self, board_code: str, start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块60分钟线数据（异步方法）
        
        Args:
            board_code: 板块代码，如'885943'或'bk_885943'
            start_date: 开始日期，格式如'2024-01-01'（暂未使用）
            end_date: 结束日期，格式如'2024-01-31'（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块60分钟线数据的DataFrame
        """
        return await self.tonghuashun.get_board_minute60(
            board_code, start_date, end_date, **kwargs
        )
