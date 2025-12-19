"""
Baostock数据源实现

基于Baostock API的数据源实现，提供股票、指数和基金数据的获取功能
"""

from typing import Optional, Dict, Any
import pandas as pd
from datetime import datetime, timedelta
from ..errors import (DataSourceError, ValidationError, 
                     NetworkError, DataNotFoundError)
from .base import BaseSource
import baostock as bs


class BaostockSource(BaseSource):
    """
    Baostock数据源实现类
    实现BaseSource中定义的所有抽象方法
    """
    
    def __init__(self, name: str = "baostock"):
        """
        初始化Baostock数据源
        
        Args:
            name: 数据源名称
        """
        super().__init__(name)
    
    async def _connect(self):
        """
        连接到Baostock API
        
        Raises:
            NetworkError: 网络连接失败时抛出
        """
        try:
            # 调用Baostock登录API
            lg = bs.login()
            if lg.error_code != '0':
                raise NetworkError(f"Baostock登录失败: {lg.error_msg}")
        except Exception as e:
            if isinstance(e, NetworkError):
                raise
            raise NetworkError(f"连接Baostock API失败: {e}")
    
    async def _disconnect(self):
        """
        断开与Baostock API的连接
        """
        try:
            bs.logout()
        except Exception:
            # 忽略登出时的异常，避免影响主流程
            pass
    
    async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取股票基础信息
        
        Returns:
            包含股票基础信息的DataFrame
        """
        # 调用query_all_stock获取所有证券数据，然后过滤出股票
        all_stocks = await self.query_all_stock(**kwargs)
        # 过滤出证券类型为股票的数据
        stock_data = all_stocks[all_stocks['security_type'] == 'stock']
        
        # 保留需要的列并重新命名
        stock_data = stock_data[[
            'code', 'name', 'market', 'listing_date'
        ]].rename(columns={
            'listing_date': 'list_date'
        })
        
        # 添加缺失的industry列
        stock_data['industry'] = ''
        
        return stock_data
    
    async def get_stock_daily(self, code: str, start_date: Optional[str] = None, 
                            end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票日线数据
        
        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            包含股票日线数据的DataFrame
        """
        await self._connect()
        try:
            # 验证参数
            if not code:
                raise ValidationError("股票代码不能为空")
            
            # 设置默认日期范围
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            # 调用Baostock API获取日线数据
            fields = "date,code,open,high,low,close,volume"
            rs = bs.query_history_k_data_plus(
                code=code,
                fields=fields,
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="3"  # 不复权
            )
            
            if rs.error_code != '0':
                raise DataSourceError(f"获取股票日线数据失败: {rs.error_msg}")
            
            # 处理结果
            result_list = []
            while rs.next():
                result_list.append(rs.get_row_data())
            
            if not result_list:
                return pd.DataFrame()
            
            df = pd.DataFrame(result_list, columns=rs.fields)
            
            # 重命名列以匹配SDK规范
            df = df.rename(columns={
                'date': 'trade_date',
                'code': 'code',
                'volume': 'vol'
            })
            
            # 保留需要的列
            df = df[['code', 'trade_date', 'open', 'high', 'low', 'close', 'vol']]
            
            return df
        except ValidationError:
            raise
        except Exception as e:
            if isinstance(e, DataSourceError):
                raise
            raise DataSourceError(f"获取股票日线数据失败: {e}")
        finally:
            await self._disconnect()
    
    async def get_stock_minute(self, code: str, start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票分钟线数据
        
        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs:
                frequency: 分钟线频率，支持5/15/30/60，默认5分钟
                
        Returns:
            包含股票分钟线数据的DataFrame
        """
        await self._connect()
        try:
            # 验证参数
            if not code:
                raise ValidationError("股票代码不能为空")
            
            # 设置默认日期
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = end_date
            
            # 获取分钟线频率参数
            frequency = kwargs.get('frequency', '5')
            if frequency not in ['5', '15', '30', '60']:
                raise ValidationError(f"不支持的分钟线频率: {frequency}")
            
            # 调用Baostock API获取分钟线数据
            fields = "date,code,open,high,low,close,volume"
            rs = bs.query_history_k_data_plus(
                code=code,
                fields=fields,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                adjustflag="3"  # 不复权
            )
            
            if rs.error_code != '0':
                raise DataSourceError(f"获取股票分钟线数据失败: {rs.error_msg}")
            
            # 处理结果
            result_list = []
            while rs.next():
                result_list.append(rs.get_row_data())
            
            if not result_list:
                return pd.DataFrame()
            
            df = pd.DataFrame(result_list, columns=rs.fields)
            
            # 重命名列以匹配SDK规范
            df = df.rename(columns={
                'date': 'datetime',
                'code': 'code',
                'volume': 'vol'
            })
            
            # 保留需要的列
            df = df[['code', 'datetime', 'open', 'high', 'low', 'close', 'vol']]
            
            return df
        except ValidationError:
            raise
        except Exception as e:
            if isinstance(e, DataSourceError):
                raise
            raise DataSourceError(f"获取股票分钟线数据失败: {e}")
        finally:
            await self._disconnect()
    
    async def get_stock_weekly(self, code: str, start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票周线数据
        
        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            包含股票周线数据的DataFrame
        """
        await self._connect()
        try:
            # 验证参数
            if not code:
                raise ValidationError("股票代码不能为空")
            
            # 设置默认日期范围
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            
            # 调用Baostock API获取周线数据
            fields = "date,code,open,high,low,close,volume"
            rs = bs.query_history_k_data_plus(
                code=code,
                fields=fields,
                start_date=start_date,
                end_date=end_date,
                frequency="w",
                adjustflag="3"  # 不复权
            )
            
            if rs.error_code != '0':
                raise DataSourceError(f"获取股票周线数据失败: {rs.error_msg}")
            
            # 处理结果
            result_list = []
            while rs.next():
                result_list.append(rs.get_row_data())
            
            if not result_list:
                return pd.DataFrame()
            
            df = pd.DataFrame(result_list, columns=rs.fields)
            
            # 重命名列以匹配SDK规范
            df = df.rename(columns={
                'date': 'trade_date',
                'code': 'code',
                'volume': 'vol'
            })
            
            # 保留需要的列
            df = df[['code', 'trade_date', 'open', 'high', 'low', 'close', 'vol']]
            
            return df
        except ValidationError:
            raise
        except Exception as e:
            if isinstance(e, DataSourceError):
                raise
            raise DataSourceError(f"获取股票周线数据失败: {e}")
        finally:
            await self._disconnect()
    
    async def get_stock_monthly(self, code: str, start_date: Optional[str] = None, 
                               end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取股票月线数据
        
        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            包含股票月线数据的DataFrame
        """
        await self._connect()
        try:
            # 验证参数
            if not code:
                raise ValidationError("股票代码不能为空")
            
            # 设置默认日期范围
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            # 调用Baostock API获取月线数据
            fields = "date,code,open,high,low,close,volume"
            rs = bs.query_history_k_data_plus(
                code=code,
                fields=fields,
                start_date=start_date,
                end_date=end_date,
                frequency="m",
                adjustflag="3"  # 不复权
            )
            
            if rs.error_code != '0':
                raise DataSourceError(f"获取股票月线数据失败: {rs.error_msg}")
            
            # 处理结果
            result_list = []
            while rs.next():
                result_list.append(rs.get_row_data())
            
            if not result_list:
                return pd.DataFrame()
            
            df = pd.DataFrame(result_list, columns=rs.fields)
            
            # 重命名列以匹配SDK规范
            df = df.rename(columns={
                'date': 'trade_date',
                'code': 'code',
                'volume': 'vol'
            })
            
            # 保留需要的列
            df = df[['code', 'trade_date', 'open', 'high', 'low', 'close', 'vol']]
            
            return df
        except ValidationError:
            raise
        except Exception as e:
            if isinstance(e, DataSourceError):
                raise
            raise DataSourceError(f"获取股票月线数据失败: {e}")
        finally:
            await self._disconnect()
    
    async def query_all_stock(self, **kwargs) -> pd.DataFrame:
        """
        获取所有证券的基本信息
        
        Returns:
            包含所有证券基本信息的DataFrame
        """
        await self._connect()
        try:
            # 直接获取所有证券详细信息
            rs = bs.query_stock_basic()
            if rs.error_code != '0':
                raise DataSourceError(f"获取所有证券信息失败: {rs.error_msg}")
            
            # 处理结果
            result_list = []
            while rs.next():
                stock_info = rs.get_row_data()
                code = stock_info[0]  # 证券代码
                stock_name = stock_info[1]  # 证券名称
                ipo_date = stock_info[2]  # 上市日期
                out_date = stock_info[3] or ''  # 退市日期
                stock_type = stock_info[4]  # 证券类型
                status = stock_info[5]  # 上市状态
                
                # 根据股票代码前缀判断市场
                if code.startswith('sh.'):
                    market = '上海'
                elif code.startswith('sz.'):
                    market = '深圳'
                else:
                    market = '未知'
                
                # 证券类型映射
                type_mapping = {
                    '1': 'stock',
                    '2': 'index',
                    '3': 'other',
                    '4': 'convertible_bond',
                    '5': 'etf'
                }
                
                # 上市状态映射
                status_mapping = {
                    '1': 'listed',
                    '0': 'delisted'
                }
                
                result_list.append({
                    'code': code,
                    'name': stock_name,
                    'market': market,
                    'listing_date': ipo_date,
                    'delisting_date': out_date,
                    'security_type': type_mapping.get(stock_type, f'unknown({stock_type})'),
                    'status': status_mapping.get(status, f'unknown({status})')
                })
            
            df = pd.DataFrame(result_list)
            return df
        finally:
            await self._disconnect()
    
    async def get_index_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取指数基础信息
        
        Returns:
            包含指数基础信息的DataFrame
        """
        # 调用query_all_stock获取所有证券数据，然后过滤出指数
        all_stocks = await self.query_all_stock(**kwargs)
        # 过滤出证券类型为指数的数据
        index_data = all_stocks[all_stocks['security_type'] == 'index']
        return index_data
    
    async def get_index_daily(self, code: str, start_date: Optional[str] = None, 
                            end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数日线数据
        
        Args:
            code: 指数代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            包含指数日线数据的DataFrame
        """
        await self._connect()
        try:
            # 验证参数
            if not code:
                raise ValidationError("指数代码不能为空")
            
            # 设置默认日期范围
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            # 调用Baostock API获取指数日线数据
            fields = "date,code,open,high,low,close,volume"
            rs = bs.query_history_k_data_plus(
                code=code,
                fields=fields,
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="3"  # 不复权
            )
            
            if rs.error_code != '0':
                raise DataSourceError(f"获取指数日线数据失败: {rs.error_msg}")
            
            # 处理结果
            result_list = []
            while rs.next():
                result_list.append(rs.get_row_data())
            
            if not result_list:
                return pd.DataFrame()
            
            df = pd.DataFrame(result_list, columns=rs.fields)
            
            # 重命名列以匹配SDK规范
            df = df.rename(columns={
                'date': 'trade_date',
                'code': 'code',
                'volume': 'vol'
            })
            
            # 保留需要的列
            df = df[['code', 'trade_date', 'open', 'high', 'low', 'close', 'vol']]
            
            return df
        except ValidationError:
            raise
        except Exception as e:
            if isinstance(e, DataSourceError):
                raise
            raise DataSourceError(f"获取指数日线数据失败: {e}")
        finally:
            await self._disconnect()
    
    async def get_index_minute(self, code: str, start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取指数分钟线数据
        
        Args:
            code: 指数代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs:
                frequency: 分钟线频率，支持5/15/30/60，默认5分钟
                
        Returns:
            包含指数分钟线数据的DataFrame
        """
        await self._connect()
        try:
            # 验证参数
            if not code:
                raise ValidationError("指数代码不能为空")
            
            # 设置默认日期
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = end_date
            
            # 获取分钟线频率参数
            frequency = kwargs.get('frequency', '5')
            if frequency not in ['5', '15', '30', '60']:
                raise ValidationError(f"不支持的分钟线频率: {frequency}")
            
            # 调用Baostock API获取指数分钟线数据
            fields = "date,code,open,high,low,close,volume"
            rs = bs.query_history_k_data_plus(
                code=code,
                fields=fields,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                adjustflag="3"  # 不复权
            )
            
            if rs.error_code != '0':
                raise DataSourceError(f"获取指数分钟线数据失败: {rs.error_msg}")
            
            # 处理结果
            result_list = []
            while rs.next():
                result_list.append(rs.get_row_data())
            
            if not result_list:
                return pd.DataFrame()
            
            df = pd.DataFrame(result_list, columns=rs.fields)
            
            # 重命名列以匹配SDK规范
            df = df.rename(columns={
                'date': 'datetime',
                'code': 'code',
                'volume': 'vol'
            })
            
            # 保留需要的列
            df = df[['code', 'datetime', 'open', 'high', 'low', 'close', 'vol']]
            
            return df
        except ValidationError:
            raise
        except Exception as e:
            if isinstance(e, DataSourceError):
                raise
            raise DataSourceError(f"获取指数分钟线数据失败: {e}")
        finally:
            await self._disconnect()
    
    async def get_fund_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取基金基础信息
        
        Returns:
            包含基金基础信息的DataFrame
            
        Raises:
            NotImplementedError: Baostock不支持基金数据获取
        """
        raise NotImplementedError("Baostock不支持基金基础信息获取，请使用其他数据源")
    
    async def get_fund_daily(self, code: str, start_date: Optional[str] = None, 
                            end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取基金日线数据
        
        Args:
            code: 基金代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            包含基金日线数据的DataFrame
            
        Raises:
            NotImplementedError: Baostock不支持基金数据获取
        """
        raise NotImplementedError("Baostock不支持基金日线数据获取，请使用其他数据源")
