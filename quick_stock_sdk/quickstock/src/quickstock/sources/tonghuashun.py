"""
同花顺数据源实现

基于同花顺API的数据源实现，主要提供板块数据获取功能
"""

import random
import time
from typing import Optional, Dict, Any, List
import pandas as pd
import requests
from lxml import etree
import json
from datetime import datetime
from io import StringIO
from bs4 import BeautifulSoup
import akshare as ak

from ..errors import (DataSourceError, ValidationError, 
                     NetworkError, DataNotFoundError)
from .base import BaseSource


class TongHuaShunId:
    """
    同花顺Cookie验证ID生成器
    
    用于生成同花顺API所需的Cookie验证字符串
    """
    
    def __init__(self, t, userAgent):
        self.n = [0] * 18
        self.n[0] = self.random()
        self.n[1] = int(t)
        self.n[3] = self.strHash(userAgent)
        self.n[4] = 1
        self.n[5] = 10
        self.n[6] = 5
        self.n[15] = 0
        self.n[16] = 1
        self.n[17] = 3
        self.n[13] = 3748
        self.n[2] = self.timeNow()
    
    def encode(self, n):
        r = self._hash(n)
        n = self._encode(n, [3, r])
        return self._base64(n)
    
    def _encode(self, n, o):
        a = 0
        i = 2
        u = o[1]
        while a < len(n):
            o.append(n[a] ^ (u & 255))
            u = ~(u * 131)
            a += 1
            i += 1
        return o
    
    def strHash(self, userAgent):
        c = 0
        for v in userAgent:
            c = (c << 5) - c + ord(v)
            c &= 0xFFFFFFFF
        return c
    
    def _hash(self, n):
        e = 0
        for i in n:
            e = (e << 5) - e + i
        return e & 255
    
    def _base64(self, n):
        m = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        f = []
        for i in range(0, len(n), 3):
            l = (n[i] << 16) | (n[i + 1] << 8) | n[i + 2]
            f.append(m[(l >> 18) & 63])
            f.append(m[(l >> 12) & 63])
            f.append(m[(l >> 6) & 63])
            f.append(m[l & 63])
        return ''.join(f)
    
    def to_buff(self, n):
        u = [4, 4, 4, 4, 1, 1, 1, 3, 2, 2, 2, 2, 2, 2, 2, 4, 2, 1]
        c = [0] * 43
        s = -1
        for v in range(len(u)):
            l = n[v]
            p = u[v]
            s += p
            d = s
            while p != 0:
                c[d] = (l & 255)
                l >>= 8
                p -= 1
                d -= 1
        return c
    
    def random(self):
        return int(random.random() * 4294967295)
    
    def timeNow(self):
        try:
            time_now = int(time.time() * 1000)
            result = time_now // int("1111101000", 2)
            return result
        except Exception:
            time_now = int(time.time() * 1000)
            result = time_now // int("1000", 10)
            return result
    
    def __str__(self):
        n = self.to_buff(self.n)
        return self.encode(n)


class TongHuaShunSource(BaseSource):
    """
    同花顺数据源实现类
    
    主要提供板块数据获取功能，包括：
    - 概念板块列表
    - 板块成分股
    - 板块K线数据（日线、周线、月线、分钟线）
    
    注意：同花顺数据源不支持股票、指数、基金的基础数据和历史数据
    """
    
    def __init__(self, name: str = "tonghuashun"):
        """
        初始化同花顺数据源
        
        Args:
            name: 数据源名称
        """
        super().__init__(name)
        self._user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        self._cache = {
            'concepts': {},
            'concept_stocks': {},
            'daily': {},
            'weekly': {},
            'monthly': {},
            'minute': {},
            'minute30': {},
            'minute60': {}
        }
    
    def _get_cookies(self):
        """
        生成同花顺API所需的Cookie
        
        Returns:
            Cookie字典
        """
        resp = time.time()
        cookies = {}
        cookies["v"] = TongHuaShunId(resp, self._user_agent).__str__()
        cookies["vvv"] = "1"
        return cookies
    
    def _get_headers(self, host=None):
        """
        获取请求头
        
        Args:
            host: 主机名，默认为q.10jqka.com.cn
            
        Returns:
            请求头字典
        """
        headers = {
            "User-Agent": self._user_agent,
            "Referer": "d.10jqka.com.cn"
        }
        if host:
            headers["HOST"] = host
        return headers
    
    def _request(self, url, host="q.10jqka.com.cn"):
        """
        发送HTTP请求
        
        Args:
            url: 请求URL
            host: 主机名
            
        Returns:
            响应内容
            
        Raises:
            NetworkError: 网络请求失败时抛出
        """
        try:
            response = requests.get(
                url,
                cookies=self._get_cookies(),
                headers=self._get_headers(host)
            )
            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                return False
            else:
                raise NetworkError(f"HTTP请求失败，状态码: {response.status_code}")
        except Exception as e:
            if isinstance(e, NetworkError):
                raise
            raise NetworkError(f"网络请求失败: {e}")
    
    def _parse_kline_data(self, data_str, frequency):
        """
        解析K线数据
        
        Args:
            data_str: 数据字符串
            frequency: 频率类型
            
        Returns:
            解析后的数据列表
        """
        result = []
        for v in data_str.split(';'):
            if not v:
                continue
            x = v.split(',')
            if len(x) < 10:
                continue
            
            def safe_float(val, default=0.0):
                """安全转换为float"""
                try:
                    return float(val) if val and val.strip() else default
                except (ValueError, TypeError):
                    return default
            
            def safe_int(val, default=0):
                """安全转换为int"""
                try:
                    return int(val) if val and val.strip() else default
                except (ValueError, TypeError):
                    return default
            
            try:
                result.append({
                    "date_at": x[0] if len(x) > 0 and x[0] else "",
                    "start": safe_float(x[1] if len(x) > 1 else ""),
                    "end": safe_float(x[4] if len(x) > 4 else ""),
                    "max": safe_float(x[2] if len(x) > 2 else ""),
                    "min": safe_float(x[3] if len(x) > 3 else ""),
                    "count": safe_int(x[5] if len(x) > 5 else ""),
                    "amount": safe_float(x[6] if len(x) > 6 else ""),
                    "amplitude": safe_float(x[2] if len(x) > 2 else "") - safe_float(x[3] if len(x) > 3 else ""),
                    "range": 0.0,
                    "range_amount": safe_float(x[9] if len(x) > 9 else ""),
                    "turnover_rate": 0.0
                })
            except Exception:
                continue
        
        return self._compute_range(result)
    
    def _compute_range(self, data):
        """
        计算涨跌幅、振幅等衍生指标
        
        Args:
            data: 原始数据列表
            
        Returns:
            计算后的DataFrame
        """
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        # 确保数值列是float类型
        numeric_cols = ['start', 'end', 'max', 'min', 'count', 'amount', 'amplitude', 'range', 'range_amount', 'turnover_rate']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
        
        df2 = df.shift()
        
        # 计算涨跌额
        df['range_amount'] = round(df['end'] - df2['end'], 3)
        
        # 计算涨跌幅
        df['range'] = round(df['range_amount'] / df2['end'], 3)
        
        # 计算振幅
        df['amplitude'] -= round((df['max'] - df2['min']) / df2['end'], 3)
        
        return df
    
    def _normalize_board_code(self, code):
        """
        标准化板块代码
        
        Args:
            code: 板块代码
            
        Returns:
            标准化后的板块代码
        """
        if code.startswith('bk_'):
            return code
        return f"bk_{code}"
    
    async def get_concept_list(self) -> pd.DataFrame:
        """
        获取所有概念板块列表
        
        Returns:
            包含概念板块信息的DataFrame，字段包括：
            - code: 板块代码
            - name: 板块名称
            - cid: 板块ID
        """
        url = "https://q.10jqka.com.cn/gn/"
        html = self._request(url)
        
        try:
            root = etree.fromstring(html, etree.HTMLParser(encoding='utf-8'))
            value = root.cssselect('#gnSection')[0].get("value")
            values = json.loads(value)
            
            result = [{
                "code": item["platecode"],
                "name": item["platename"],
                "cid": item["cid"],
            } for key, item in values.items()]
            
            df = pd.DataFrame(result)
            return df
        except Exception as e:
            raise DataSourceError(f"解析概念板块列表失败: {e}")
    
    async def get_concept_stocks(self, concept_code: str) -> pd.DataFrame:
        """
        获取指定概念板块的成分股
        
        Args:
            concept_code: 概念板块ID（cid），不是板块代码（code）
                        可以从get_concept_list()返回的cid字段获取
        
        Returns:
            包含成分股信息的DataFrame，字段包括：
            - code: 股票代码
            - cid: 概念板块ID
        """
        url = f"http://q.10jqka.com.cn/gn/detail/field/199112/order/desc/size/1000/page/1/ajax/1/code/{concept_code}"
        html = self._request(url)
        
        try:
            root = etree.fromstring(html, etree.HTMLParser(encoding='utf-8'))
            values = root.cssselect('tr td:nth-child(2) a')
            
            result = [{
                "code": item.text,
                "cid": concept_code,
            } for item in values]
            
            df = pd.DataFrame(result)
            return df
        except Exception as e:
            raise DataSourceError(f"解析板块成分股失败: {e}")
    
    async def get_industry_list(self) -> pd.DataFrame:
        """
        获取所有行业板块列表
        
        使用akshare接口获取行业分类信息
        
        Returns:
            包含行业板块信息的DataFrame，字段包括：
            - code: 行业代码
            - name: 行业名称
        """
        try:
            df = ak.stock_board_industry_name_ths()
            return df
        except Exception as e:
            raise DataSourceError(f"获取行业列表失败: {e}")
    
    async def get_industry_stocks(self, industry_code: str) -> pd.DataFrame:
        """
        获取指定行业的成分股
        
        Args:
            industry_code: 行业代码，如'881101'（医药行业）
            
        Returns:
            包含行业成分股信息的DataFrame，字段包括：
            - code: 股票代码
            - name: 股票名称
            - industry_code: 行业代码
        """
        url = f"http://q.10jqka.com.cn/thshy/detail/field/199112/order/desc/page/1/ajax/1/code/{industry_code}"
        html = self._request(url, host='q.10jqka.com.cn')
        
        try:
            root = etree.fromstring(html, etree.HTMLParser(encoding='utf-8'))
            
            page_info = root.cssselect('.page_info')
            if not page_info:
                return pd.DataFrame()
            
            page_num = int(page_info[0].text.split('/')[1])
            
            big_df = pd.DataFrame()
            
            for page in range(1, page_num + 1):
                url = f"http://q.10jqka.com.cn/thshy/detail/field/199112/order/desc/page/{page}/ajax/1/code/{industry_code}"
                html = self._request(url, host='q.10jqka.com.cn')
                
                try:
                    soup = BeautifulSoup(html, features='lxml')
                    table = soup.find('table')
                    if table:
                        temp_df = pd.read_html(StringIO(str(table)))[0]
                        if not temp_df.empty:
                            if big_df.empty:
                                big_df = temp_df
                            else:
                                big_df = pd.concat([big_df, temp_df], ignore_index=True)
                except Exception as e:
                    continue
            
            if not big_df.empty:
                big_df = big_df.rename(columns={
                    '代码': 'code',
                    '名称': 'name'
                })
                big_df['industry_code'] = industry_code
            
            return big_df
        except Exception as e:
            raise DataSourceError(f"解析行业成分股失败: {e}")
    
    async def get_board_daily(self, board_code: str, start_date: Optional[str] = None, 
                            end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块日线数据
        
        Args:
            board_code: 板块代码
            start_date: 开始日期（暂未使用）
            end_date: 结束日期（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块日线数据的DataFrame
        """
        board_code = self._normalize_board_code(board_code)
        
        if board_code in self._cache['daily']:
            return self._cache['daily'][board_code]
        
        year = datetime.now().year
        all_data = []
        
        while year > 2014:
            url = f"https://d.10jqka.com.cn/v4/line/{board_code}/01/{year}.js"
            html = self._request(url)
            
            if html is False:
                break
            
            try:
                html = html[38:-1]
                data = json.loads(html)
                data_str = data.get("data", "")
                
                if data_str:
                    parsed_df = self._parse_kline_data(data_str, 'daily')
                    if not parsed_df.empty:
                        all_data.extend(parsed_df.to_dict('records'))
            except Exception as e:
                raise DataSourceError(f"解析板块日线数据失败: {e}")
            
            year -= 1
        
        if all_data:
            df = pd.DataFrame(all_data)
            self._cache['daily'][board_code] = df
            return df
        
        return pd.DataFrame()
    
    async def get_board_weekly(self, board_code: str, start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块周线数据
        
        Args:
            board_code: 板块代码
            start_date: 开始日期（暂未使用）
            end_date: 结束日期（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块周线数据的DataFrame
        """
        board_code = self._normalize_board_code(board_code)
        
        if board_code in self._cache['weekly']:
            return self._cache['weekly'][board_code]
        
        year = datetime.now().year
        all_data = []
        
        while year > 2014:
            url = f"https://d.10jqka.com.cn/v4/line/{board_code}/11/{year}.js"
            html = self._request(url)
            
            if html is False:
                break
            
            try:
                html = html[38:-1]
                data = json.loads(html)
                data_str = data.get("data", "")
                if data_str:
                    parsed_df = self._parse_kline_data(data_str, 'weekly')
                    if not parsed_df.empty:
                        all_data.extend(parsed_df.to_dict('records'))
            except Exception as e:
                raise DataSourceError(f"解析板块周线数据失败: {e}")
            
            year -= 1
        
        if all_data:
            df = pd.DataFrame(all_data)
            self._cache['weekly'][board_code] = df
            return df
        
        return pd.DataFrame()
    
    async def get_board_monthly(self, board_code: str, start_date: Optional[str] = None, 
                              end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块月线数据
        
        Args:
            board_code: 板块代码
            start_date: 开始日期（暂未使用）
            end_date: 结束日期（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块月线数据的DataFrame
        """
        board_code = self._normalize_board_code(board_code)
        
        if board_code in self._cache['monthly']:
            return self._cache['monthly'][board_code]
        
        url = f"https://d.10jqka.com.cn/v4/line/{board_code}/21/last.js"
        html = self._request(url)
        
        try:
            html = html[38:-1]
            data = json.loads(html)
            data_str = data.get("data", "")
            
            if data_str:
                df = self._parse_kline_data(data_str, 'monthly')
                self._cache['monthly'][board_code] = df
                return df
            
            return pd.DataFrame()
        except Exception as e:
            raise DataSourceError(f"解析板块月线数据失败: {e}")
    
    async def get_board_minute(self, board_code: str, start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块分钟线数据（1分钟）
        
        Args:
            board_code: 板块代码
            start_date: 开始日期（暂未使用）
            end_date: 结束日期（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块分钟线数据的DataFrame
        """
        board_code = self._normalize_board_code(board_code)
        
        if board_code in self._cache['minute']:
            return self._cache['minute'][board_code]
        
        year = datetime.now().year
        url = f"https://d.10jqka.com.cn/v4/line/{board_code}/61/{year}.js"
        html = self._request(url)
        
        try:
            html = html[38:-1]
            data = json.loads(html)
            data_str = data.get("data", "")
            
            if data_str:
                df = self._parse_kline_data(data_str, 'minute')
                self._cache['minute'][board_code] = df
                return df
            
            return pd.DataFrame()
        except Exception as e:
            raise DataSourceError(f"解析板块分钟线数据失败: {e}")
    
    async def get_board_minute30(self, board_code: str, start_date: Optional[str] = None, 
                               end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块30分钟线数据
        
        Args:
            board_code: 板块代码
            start_date: 开始日期（暂未使用）
            end_date: 结束日期（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块30分钟线数据的DataFrame
        """
        board_code = self._normalize_board_code(board_code)
        
        if board_code in self._cache['minute30']:
            return self._cache['minute30'][board_code]
        
        year = datetime.now().year
        all_data = []
        
        while year > 2014:
            url = f"https://d.10jqka.com.cn/v4/line/{board_code}/41/{year}.js"
            html = self._request(url)
            
            if html is False:
                break
            
            try:
                html = html[38:-1]
                data = json.loads(html)
                data_str = data.get("data", "")
                if data_str:
                    parsed_df = self._parse_kline_data(data_str, 'minute30')
                    if not parsed_df.empty:
                        all_data.extend(parsed_df.to_dict('records'))
            except Exception as e:
                raise DataSourceError(f"解析板块30分钟线数据失败: {e}")
            
            year -= 1
        
        if all_data:
            df = pd.DataFrame(all_data)
            self._cache['minute30'][board_code] = df
            return df
        
        return pd.DataFrame()
    
    async def get_board_minute60(self, board_code: str, start_date: Optional[str] = None, 
                               end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取板块60分钟线数据
        
        Args:
            board_code: 板块代码
            start_date: 开始日期（暂未使用）
            end_date: 结束日期（暂未使用）
            **kwargs: 其他参数
            
        Returns:
            包含板块60分钟线数据的DataFrame
        """
        board_code = self._normalize_board_code(board_code)
        
        if board_code in self._cache['minute60']:
            return self._cache['minute60'][board_code]
        
        year = datetime.now().year
        all_data = []
        
        while year > 2014:
            url = f"https://d.10jqka.com.cn/v4/line/{board_code}/51/{year}.js"
            html = self._request(url)
            
            if html is False:
                break
            
            try:
                html = html[38:-1]
                data = json.loads(html)
                data_str = data.get("data", "")
                if data_str:
                    parsed_df = self._parse_kline_data(data_str, 'minute60')
                    if not parsed_df.empty:
                        all_data.extend(parsed_df.to_dict('records'))
            except Exception as e:
                raise DataSourceError(f"解析板块60分钟线数据失败: {e}")
            
            year -= 1
        
        if all_data:
            df = pd.DataFrame(all_data)
            self._cache['minute60'][board_code] = df
            return df
        
        return pd.DataFrame()
    
    async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
        """
        同花顺数据源不支持股票基础数据
        
        Raises:
            NotImplementedError: 始终抛出此异常
        """
        raise NotImplementedError("同花顺数据源不支持股票基础数据，请使用Baostock数据源")
    
    async def get_stock_daily(self, codes: List[str], start_date: Optional[str] = None, 
                            end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        同花顺数据源不支持股票日线数据
        
        Raises:
            NotImplementedError: 始终抛出此异常
        """
        raise NotImplementedError("同花顺数据源不支持股票日线数据，请使用Baostock数据源")
    
    async def get_stock_minute(self, codes: List[str], start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        同花顺数据源不支持股票分钟线数据
        
        Raises:
            NotImplementedError: 始终抛出此异常
        """
        raise NotImplementedError("同花顺数据源不支持股票分钟线数据，请使用Baostock数据源")
    
    async def get_stock_weekly(self, codes: List[str], start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        同花顺数据源不支持股票周线数据
        
        Raises:
            NotImplementedError: 始终抛出此异常
        """
        raise NotImplementedError("同花顺数据源不支持股票周线数据，请使用Baostock数据源")
    
    async def get_stock_monthly(self, codes: List[str], start_date: Optional[str] = None, 
                               end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        同花顺数据源不支持股票月线数据
        
        Raises:
            NotImplementedError: 始终抛出此异常
        """
        raise NotImplementedError("同花顺数据源不支持股票月线数据，请使用Baostock数据源")
    
    async def get_index_basic(self, **kwargs) -> pd.DataFrame:
        """
        同花顺数据源不支持指数基础数据
        
        Raises:
            NotImplementedError: 始终抛出此异常
        """
        raise NotImplementedError("同花顺数据源不支持指数基础数据，请使用Baostock数据源")
    
    async def get_index_daily(self, codes: List[str], start_date: Optional[str] = None, 
                            end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        同花顺数据源不支持指数日线数据
        
        Raises:
            NotImplementedError: 始终抛出此异常
        """
        raise NotImplementedError("同花顺数据源不支持指数日线数据，请使用Baostock数据源")
    
    async def get_index_minute(self, codes: List[str], start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        同花顺数据源不支持指数分钟线数据
        
        Raises:
            NotImplementedError: 始终抛出此异常
        """
        raise NotImplementedError("同花顺数据源不支持指数分钟线数据，请使用Baostock数据源")
    
    async def get_index_weekly(self, codes: List[str], start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        同花顺数据源不支持指数周线数据
        
        Raises:
            NotImplementedError: 始终抛出此异常
        """
        raise NotImplementedError("同花顺数据源不支持指数周线数据，请使用Baostock数据源")
    
    async def get_index_monthly(self, codes: List[str], start_date: Optional[str] = None, 
                               end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        同花顺数据源不支持指数月线数据
        
        Raises:
            NotImplementedError: 始终抛出此异常
        """
        raise NotImplementedError("同花顺数据源不支持指数月线数据，请使用Baostock数据源")
    
    async def get_fund_basic(self, **kwargs) -> pd.DataFrame:
        """
        同花顺数据源不支持基金基础数据
        
        Raises:
            NotImplementedError: 始终抛出此异常
        """
        raise NotImplementedError("同花顺数据源不支持基金基础数据，请使用Baostock数据源")
    
    async def get_fund_daily(self, codes: List[str], start_date: Optional[str] = None, 
                            end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        同花顺数据源不支持基金日线数据
        
        Raises:
            NotImplementedError: 始终抛出此异常
        """
        raise NotImplementedError("同花顺数据源不支持基金日线数据，请使用Baostock数据源")
    
    async def get_fund_minute(self, codes: List[str], start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        同花顺数据源不支持基金分钟线数据
        
        Raises:
            NotImplementedError: 始终抛出此异常
        """
        raise NotImplementedError("同花顺数据源不支持基金分钟线数据，请使用Baostock数据源")
    
    async def get_fund_weekly(self, codes: List[str], start_date: Optional[str] = None, 
                             end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        同花顺数据源不支持基金周线数据
        
        Raises:
            NotImplementedError: 始终抛出此异常
        """
        raise NotImplementedError("同花顺数据源不支持基金周线数据，请使用Baostock数据源")
    
    async def get_fund_monthly(self, codes: List[str], start_date: Optional[str] = None, 
                               end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        同花顺数据源不支持基金月线数据
        
        Raises:
            NotImplementedError: 始终抛出此异常
        """
        raise NotImplementedError("同花顺数据源不支持基金月线数据，请使用Baostock数据源")
    
    async def query_trade_dates(self, start_date: Optional[str] = None, 
                               end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        同花顺数据源不支持交易日查询
        
        Raises:
            NotImplementedError: 始终抛出此异常
        """
        raise NotImplementedError("同花顺数据源不支持交易日查询，请使用Baostock数据源")
