"""
东方财富数据提供者

基于东方财富API获取股票数据
"""

import asyncio
import aiohttp
import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
import hashlib
import time
import re
from functools import wraps

from .base import DataProvider, RateLimit
from ..core.errors import DataSourceError, NetworkError, ValidationError, RateLimitError
from ..utils.validators import validate_stock_code, validate_date_format
from ..utils.code_converter import StockCodeConverter

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(self, *args, **kwargs)
                except (NetworkError, aiohttp.ClientError) as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (backoff_factor ** attempt)
                        logger.warning(f"请求失败，{wait_time:.1f}秒后重试 (第{attempt + 1}次): {e}")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"重试{max_retries}次后仍然失败: {e}")
                except Exception as e:
                    # 对于非网络错误，不进行重试
                    logger.error(f"请求出现非网络错误: {e}")
                    raise
            
            raise last_exception
        return wrapper
    return decorator


def rate_limit(requests_per_second: float = 2.0):
    """速率限制装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # 检查速率限制
            await self._check_rate_limit(requests_per_second)
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator


class EastmoneyProvider(DataProvider):
    """东方财富数据提供者"""
    
    def __init__(self, config):
        """
        初始化东方财富提供者
        
        Args:
            config: 配置对象
        """
        super().__init__(config)
        self.base_url = "https://push2his.eastmoney.com/api/qt"
        self.trends_url = "https://push2his.eastmoney.com/api/qt/stock/trends2/get"
        self.kline_url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        
        # 请求头
        self.headers = {
            "HOST": "push2his.eastmoney.com",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        

        
        # 连接池（继承自基类）
        # self._connection_pool 在基类中定义
        
        # 速率限制
        self._last_request_time = 0
        self._request_count = 0
        self._request_window_start = time.time()
        
        # 重试配置
        self.max_retries = getattr(config, 'max_retries', 3)
        self.retry_delay = getattr(config, 'retry_delay', 1.0)
        self.backoff_factor = 2.0
    
    async def _get_connection_pool(self):
        """获取连接池（使用基类方法）"""
        pool = await self.get_connection_pool()
        
        # 设置东方财富API的速率限制
        pool.set_rate_limit(self.base_url, 2.0)  # 每秒2个请求
        pool.set_rate_limit(self.trends_url, 1.0)  # 分时数据更严格
        pool.set_rate_limit(self.kline_url, 2.0)  # K线数据
        
        return pool
    
    async def _check_rate_limit(self, requests_per_second: float):
        """检查速率限制"""
        current_time = time.time()
        
        # 重置请求窗口
        if current_time - self._request_window_start >= 1.0:
            self._request_count = 0
            self._request_window_start = current_time
        
        # 检查是否超过速率限制
        if self._request_count >= requests_per_second:
            wait_time = 1.0 - (current_time - self._request_window_start)
            if wait_time > 0:
                logger.debug(f"速率限制，等待 {wait_time:.2f} 秒")
                await asyncio.sleep(wait_time)
                self._request_count = 0
                self._request_window_start = time.time()
        
        self._request_count += 1
        self._last_request_time = current_time
    

    
    def _deduplicate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据去重"""
        if df.empty:
            return df
        
        # 根据不同的数据类型选择去重列
        if 'trade_date' in df.columns:
            # 日线、周线、月线数据
            df = df.drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
        elif 'trade_time' in df.columns:
            # 分钟数据
            df = df.drop_duplicates(subset=['ts_code', 'trade_time'], keep='last')
        
        # 重置索引
        df = df.reset_index(drop=True)
        
        return df
    
    async def _make_request(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        发起HTTP请求（使用连接池）
        
        Args:
            url: 请求URL
            params: 请求参数
            
        Returns:
            响应数据
            
        Raises:
            NetworkError: 网络请求失败
            DataSourceError: 数据源返回错误
        """
        try:

            
            # 使用连接池发起请求
            pool = await self._get_connection_pool()
            
            async with pool.pool.request('GET', url, params=params, headers=self.headers) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                    except Exception as e:
                        raise DataSourceError(f"响应JSON解析失败: {str(e)}")
                    
                    if data.get('rc') == 0:  # 东方财富API成功响应码
                        return data
                    elif data.get('rc') == -1:
                        error_msg = data.get('rt', 'Unknown API error')
                        raise DataSourceError(f"东方财富API返回错误: {error_msg}")
                    else:
                        raise DataSourceError(f"东方财富API返回未知状态码: {data.get('rc')}")
                elif response.status == 429:
                    raise RateLimitError("请求频率过高，被服务器限制")
                elif response.status >= 500:
                    raise NetworkError(f"服务器错误: {response.status}")
                else:
                    raise NetworkError(f"HTTP请求失败: {response.status}")
                    
        except (DataSourceError, NetworkError, RateLimitError):
            # 重新抛出已知异常
            raise
        except Exception as e:
            raise DataSourceError(f"请求处理异常: {str(e)}")
    
    def _convert_stock_code(self, ts_code: str) -> str:
        """
        转换股票代码为东方财富格式
        
        Args:
            ts_code: 任意格式的股票代码
            
        Returns:
            东方财富格式代码 (如: 0.000001)
        """
        try:
            # 检查是否已经是东方财富格式
            if re.match(r'^([01])\.([0-9]{6})$', ts_code):
                return ts_code
            
            # 使用统一的代码转换器
            return StockCodeConverter.to_eastmoney_format(ts_code)
        except Exception as e:
            logger.error(f"股票代码转换失败: {ts_code} -> 东方财富格式, 错误: {e}")
            # 记录转换错误到日志
            logger.debug(f"转换失败详情 - 输入代码: {ts_code}, 目标格式: eastmoney, 异常类型: {type(e).__name__}")
            raise ValidationError(f"无法将股票代码 {ts_code} 转换为东方财富格式: {str(e)}")
    
    def _convert_to_standard_code(self, eastmoney_code: str) -> str:
        """
        将东方财富格式的代码转换为标准格式
        
        Args:
            eastmoney_code: 东方财富格式代码（如1.600000）
            
        Returns:
            标准格式代码（如600000.SH）
        """
        try:
            # 使用统一的代码转换器
            return StockCodeConverter.from_eastmoney_format(eastmoney_code)
        except Exception as e:
            logger.error(f"股票代码转换失败: {eastmoney_code} -> 标准格式, 错误: {e}")
            # 记录转换错误到日志
            logger.debug(f"转换失败详情 - 输入代码: {eastmoney_code}, 目标格式: standard, 异常类型: {type(e).__name__}")
            raise ValidationError(f"无法将东方财富代码 {eastmoney_code} 转换为标准格式: {str(e)}")
    
    def _parse_kline_data(self, klines: List[str]) -> List[Dict[str, Any]]:
        """
        解析K线数据
        
        Args:
            klines: K线数据字符串列表
            
        Returns:
            解析后的数据列表
        """
        result = []
        for kline in klines:
            parts = kline.split(',')
            if len(parts) >= 11:
                try:
                    data = {
                        "trade_date": parts[0],
                        "open": float(parts[1]),
                        "close": float(parts[2]),
                        "high": float(parts[3]),
                        "low": float(parts[4]),
                        "volume": int(parts[5]),
                        "amount": float(parts[6]),
                        "amplitude": float(parts[7]),
                        "pct_chg": float(parts[8]),
                        "change": float(parts[9]),
                        "turnover_rate": float(parts[10]) if len(parts) > 10 else 0.0
                    }
                    result.append(data)
                except (ValueError, IndexError) as e:
                    logger.warning(f"解析K线数据失败: {kline}, 错误: {e}")
                    continue
        return result
    
    def get_provider_name(self) -> str:
        """获取提供者名称"""
        return "eastmoney"
    
    def get_rate_limit(self) -> RateLimit:
        """获取速率限制信息"""
        return RateLimit(
            requests_per_second=2.0,
            requests_per_minute=100,
            requests_per_hour=5000
        )
    
    async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取股票基础信息
        
        注意：东方财富API不直接提供股票列表，这里返回空DataFrame
        实际使用中可能需要从其他数据源获取股票列表
        """
        logger.warning("东方财富提供者不支持股票基础信息获取，建议使用baostock或tushare")
        return pd.DataFrame()
    
    async def get_stock_daily(self, ts_code: str, start_date: str, 
                             end_date: str) -> pd.DataFrame:
        """
        获取股票日线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            股票日线数据DataFrame
        """
        # 参数验证
        validate_stock_code(ts_code)
        validate_date_format(start_date)
        validate_date_format(end_date)
        

        
        # 转换股票代码
        secid = self._convert_stock_code(ts_code)
        
        # 构建请求参数
        params = {
            'secid': secid,
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
            'fields1': 'f1,f2,f3,f4,f5,f6',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
            'klt': '101',  # 日线
            'fqt': '1',    # 前复权
            'beg': start_date,
            'end': end_date,
            'smplmt': '100000',
            'lmt': '100'
        }
        
        try:
            # 发起请求
            response = await self._make_request(self.kline_url, params)
            
            # 解析数据
            klines = response.get('data', {}).get('klines', [])
            if not klines:
                logger.warning(f"未获取到股票 {ts_code} 的日线数据")
                print(self.kline_url)
                os.exit()
                return pd.DataFrame()
            
            # 转换为DataFrame
            data_list = self._parse_kline_data(klines)
            df = pd.DataFrame(data_list)
            
            # 添加股票代码列（确保使用标准格式）
            try:
                # 验证并标准化输入的股票代码
                standard_code = StockCodeConverter.normalize_code(ts_code)
                df['ts_code'] = standard_code
                logger.debug(f"股票代码已标准化: {ts_code} -> {standard_code}")
            except Exception as e:
                logger.warning(f"股票代码标准化失败，使用原始代码: {ts_code}, 错误: {e}")
                df['ts_code'] = ts_code
            
            # 重新排列列顺序
            columns = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 
                      'volume', 'amount', 'pct_chg', 'change', 'amplitude', 'turnover_rate']
            df = df.reindex(columns=columns, fill_value=0)
            
            # 数据去重
            df = self._deduplicate_data(df)
            

            
            logger.info(f"成功获取股票 {ts_code} 日线数据 {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"获取股票 {ts_code} 日线数据失败: {e}")
            raise DataSourceError(f"获取股票日线数据失败: {e}")
    
    async def get_stock_minute(self, ts_code: str, freq: str = '1min',
                              start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取股票分钟数据
        
        Args:
            ts_code: 股票代码
            freq: 频率 (1min, 30min, 60min)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            股票分钟数据DataFrame
        """
        # 参数验证
        validate_stock_code(ts_code)
        if start_date:
            validate_date_format(start_date)
        if end_date:
            validate_date_format(end_date)
        
        # 转换股票代码
        secid = self._convert_stock_code(ts_code)
        
        # 根据频率选择不同的API
        if freq == '1min':
            return await self._get_minute_data(secid, ts_code)
        elif freq in ['30min', '60min']:
            return await self._get_kline_minute_data(secid, ts_code, freq, start_date, end_date)
        else:
            raise ValidationError(f"不支持的分钟频率: {freq}")
    
    async def _get_minute_data(self, secid: str, ts_code: str) -> pd.DataFrame:
        """
        获取1分钟数据（使用trends2接口）
        
        Args:
            secid: 东方财富格式股票代码
            ts_code: 原始股票代码
            
        Returns:
            1分钟数据DataFrame
        """
        params = {
            'fields1': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58',
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
            'secid': secid,
            'ndays': '1',
            'iscr': '0',
            'iscca': '0'
        }
        
        try:
            response = await self._make_request(self.trends_url, params)
            
            # 解析数据
            trends = response.get('data', {}).get('trends', [])
            if not trends:
                logger.warning(f"未获取到股票 {ts_code} 的1分钟数据")
                return pd.DataFrame()
            
            # 转换为DataFrame
            data_list = self._parse_trends_data(trends)
            df = pd.DataFrame(data_list)
            
            # 添加股票代码列
            df['ts_code'] = ts_code
            
            # 重新排列列顺序
            columns = ['ts_code', 'trade_time', 'open', 'high', 'low', 'close', 
                      'volume', 'amount', 'pct_chg', 'change', 'amplitude', 'turnover_rate']
            df = df.reindex(columns=columns, fill_value=0)
            
            logger.info(f"成功获取股票 {ts_code} 1分钟数据 {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"获取股票 {ts_code} 1分钟数据失败: {e}")
            raise DataSourceError(f"获取股票1分钟数据失败: {e}")
    
    async def _get_kline_minute_data(self, secid: str, ts_code: str, freq: str,
                                   start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取K线分钟数据（30分钟、60分钟）
        
        Args:
            secid: 东方财富格式股票代码
            ts_code: 原始股票代码
            freq: 频率 (30min, 60min)
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            分钟数据DataFrame
        """
        # 频率映射
        freq_map = {
            '30min': '30',
            '60min': '60'
        }
        
        klt = freq_map.get(freq)
        if not klt:
            raise ValidationError(f"不支持的频率: {freq}")
        
        # 设置默认日期
        if not start_date:
            start_date = ""
        if not end_date:
            end_date = "20500101"
        
        params = {
            'secid': secid,
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
            'fields1': 'f1,f2,f3,f4,f5,f6',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
            'klt': klt,
            'fqt': '1',    # 前复权
            'beg': start_date,
            'end': end_date,
            'smplmt': '100000',
            'lmt': '100'
        }
        
        try:
            response = await self._make_request(self.kline_url, params)
            
            # 解析数据
            klines = response.get('data', {}).get('klines', [])
            if not klines:
                logger.warning(f"未获取到股票 {ts_code} 的{freq}数据")
                return pd.DataFrame()
            
            # 转换为DataFrame
            data_list = self._parse_kline_data(klines)
            df = pd.DataFrame(data_list)
            
            # 添加股票代码列
            df['ts_code'] = ts_code
            
            # 重新排列列顺序
            columns = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 
                      'volume', 'amount', 'pct_chg', 'change', 'amplitude', 'turnover_rate']
            df = df.reindex(columns=columns, fill_value=0)
            
            logger.info(f"成功获取股票 {ts_code} {freq}数据 {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"获取股票 {ts_code} {freq}数据失败: {e}")
            raise DataSourceError(f"获取股票{freq}数据失败: {e}")
    
    def _parse_trends_data(self, trends: List[str]) -> List[Dict[str, Any]]:
        """
        解析分时数据
        
        Args:
            trends: 分时数据字符串列表
            
        Returns:
            解析后的数据列表
        """
        result = []
        for trend in trends:
            parts = trend.split(',')
            if len(parts) >= 11:
                try:
                    data = {
                        "trade_time": parts[0],
                        "open": float(parts[1]),
                        "close": float(parts[2]),
                        "high": float(parts[3]),
                        "low": float(parts[4]),
                        "volume": int(parts[5]),
                        "amount": float(parts[6]),
                        "amplitude": float(parts[7]),
                        "pct_chg": float(parts[8]),
                        "change": float(parts[9]),
                        "turnover_rate": float(parts[10]) if len(parts) > 10 else 0.0
                    }
                    result.append(data)
                except (ValueError, IndexError) as e:
                    logger.warning(f"解析分时数据失败: {trend}, 错误: {e}")
                    continue
        return result
    
    async def get_stock_weekly(self, ts_code: str, start_date: str = None, 
                              end_date: str = None) -> pd.DataFrame:
        """
        获取股票周线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            股票周线数据DataFrame
        """
        # 参数验证
        validate_stock_code(ts_code)
        if start_date:
            validate_date_format(start_date)
        if end_date:
            validate_date_format(end_date)
        
        # 转换股票代码
        secid = self._convert_stock_code(ts_code)
        
        # 设置默认日期
        if not start_date:
            start_date = ""
        if not end_date:
            end_date = "20500101"
        
        # 构建请求参数
        params = {
            'secid': secid,
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
            'fields1': 'f1,f2,f3,f4,f5,f6',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
            'klt': '102',  # 周线
            'fqt': '1',    # 前复权
            'beg': start_date,
            'end': end_date,
            'smplmt': '100000',
            'lmt': '100'
        }
        
        try:
            response = await self._make_request(self.kline_url, params)
            
            # 解析数据
            klines = response.get('data', {}).get('klines', [])
            if not klines:
                logger.warning(f"未获取到股票 {ts_code} 的周线数据")
                return pd.DataFrame()
            
            # 转换为DataFrame
            data_list = self._parse_kline_data(klines)
            df = pd.DataFrame(data_list)
            
            # 添加股票代码列
            df['ts_code'] = ts_code
            
            # 重新排列列顺序
            columns = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 
                      'volume', 'amount', 'pct_chg', 'change', 'amplitude', 'turnover_rate']
            df = df.reindex(columns=columns, fill_value=0)
            
            logger.info(f"成功获取股票 {ts_code} 周线数据 {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"获取股票 {ts_code} 周线数据失败: {e}")
            raise DataSourceError(f"获取股票周线数据失败: {e}")
    
    async def get_stock_monthly(self, ts_code: str, start_date: str = None, 
                               end_date: str = None) -> pd.DataFrame:
        """
        获取股票月线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            股票月线数据DataFrame
        """
        # 参数验证
        validate_stock_code(ts_code)
        if start_date:
            validate_date_format(start_date)
        if end_date:
            validate_date_format(end_date)
        
        # 转换股票代码
        secid = self._convert_stock_code(ts_code)
        
        # 设置默认日期
        if not start_date:
            start_date = ""
        if not end_date:
            end_date = "20500101"
        
        # 构建请求参数
        params = {
            'secid': secid,
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
            'fields1': 'f1,f2,f3,f4,f5,f6',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
            'klt': '103',  # 月线
            'fqt': '1',    # 前复权
            'beg': start_date,
            'end': end_date,
            'smplmt': '100000',
            'lmt': '100'
        }
        
        try:
            response = await self._make_request(self.kline_url, params)
            
            # 解析数据
            klines = response.get('data', {}).get('klines', [])
            if not klines:
                logger.warning(f"未获取到股票 {ts_code} 的月线数据")
                return pd.DataFrame()
            
            # 转换为DataFrame
            data_list = self._parse_kline_data(klines)
            df = pd.DataFrame(data_list)
            
            # 添加股票代码列
            df['ts_code'] = ts_code
            
            # 重新排列列顺序
            columns = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 
                      'volume', 'amount', 'pct_chg', 'change', 'amplitude', 'turnover_rate']
            df = df.reindex(columns=columns, fill_value=0)
            
            logger.info(f"成功获取股票 {ts_code} 月线数据 {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"获取股票 {ts_code} 月线数据失败: {e}")
            raise DataSourceError(f"获取股票月线数据失败: {e}")

    async def get_trade_cal(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取交易日历
        
        注意：东方财富API不直接提供交易日历，这里返回空DataFrame
        """
        logger.warning("东方财富提供者不支持交易日历获取，建议使用baostock")
        return pd.DataFrame()
    

    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 尝试获取连接池
            pool = await self._get_connection_pool()
            
            # 简单的连接测试 - 只检查能否建立连接
            test_url = "https://push2his.eastmoney.com"
            
            async with pool.pool.request('GET', test_url, headers=self.headers) as response:
                # 只要能成功连接并返回响应（不管状态码），就认为服务可用
                return response.status in [200, 301, 302, 403, 404]  # 这些状态码表示服务在线
            
        except Exception as e:
            logger.warning(f"健康检查失败: {e}")
            return False
    
    def convert_input_code(self, code: str) -> str:
        """将输入代码转换为东方财富所需格式"""
        return self._convert_stock_code(code)
    
    def convert_output_code(self, code: str) -> str:
        """将东方财富返回的代码转换为标准格式"""
        return self._convert_to_standard_code(code)
    
    def get_required_format(self) -> str:
        """获取东方财富要求的代码格式"""
        return "eastmoney"
    
    async def close(self):
        """关闭连接池"""
        await super().close()  # 调用基类的close方法