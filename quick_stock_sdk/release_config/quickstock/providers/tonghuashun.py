"""
同花顺数据提供者

提供同花顺数据源的数据获取功能，包括概念板块数据和价格数据
"""

import asyncio
import datetime
import json
import logging
import re
import time
from typing import Optional, Dict, Any, List
import pandas as pd
import requests
from lxml import etree
import random

from .base import DataProvider, RateLimit
from ..core.errors import DataSourceError, NetworkError, ValidationError
from ..utils.validators import validate_stock_code, validate_date_format
from ..utils.code_converter import StockCodeConverter


class TonghuashunProvider(DataProvider):
    """同花顺数据提供者"""
    
    def __init__(self, config):
        """
        初始化同花顺数据提供者
        
        Args:
            config: 配置对象
        """
        super().__init__(config)
        self.base_url = "https://q.10jqka.com.cn"
        self.data_url = "https://d.10jqka.com.cn"
        self.session = requests.Session()
        
        # 设置请求头
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            'HOST': "q.10jqka.com.cn",
            'Referer': "d.10jqka.com.cn"
        }
        

        
        # 日志
        self.logger = logging.getLogger(__name__)
    
    def _convert_stock_code(self, ts_code: str) -> str:
        """
        转换股票代码为同花顺格式
        
        Args:
            ts_code: 任意格式的股票代码
            
        Returns:
            同花顺格式代码 (如: hs_600000)
        """
        try:
            # 检查是否已经是同花顺格式
            if re.match(r'^hs_([0-9]{6})$', ts_code.lower()):
                return ts_code.lower()
            
            # 使用统一的代码转换器
            return StockCodeConverter.to_tonghuashun_format(ts_code)
        except Exception as e:
            self.logger.error(f"股票代码转换失败: {ts_code} -> 同花顺格式, 错误: {e}")
            # 记录转换错误到日志
            self.logger.debug(f"转换失败详情 - 输入代码: {ts_code}, 目标格式: tonghuashun, 异常类型: {type(e).__name__}")
            raise ValidationError(f"无法将股票代码 {ts_code} 转换为同花顺格式: {str(e)}")
    
    def _convert_to_standard_code(self, tonghuashun_code: str) -> str:
        """
        将同花顺格式的代码转换为标准格式
        
        Args:
            tonghuashun_code: 同花顺格式代码（如hs_600000）
            
        Returns:
            标准格式代码（如600000.SH）
        """
        try:
            # 使用统一的代码转换器
            return StockCodeConverter.from_tonghuashun_format(tonghuashun_code)
        except Exception as e:
            self.logger.error(f"股票代码转换失败: {tonghuashun_code} -> 标准格式, 错误: {e}")
            # 记录转换错误到日志
            self.logger.debug(f"转换失败详情 - 输入代码: {tonghuashun_code}, 目标格式: standard, 异常类型: {type(e).__name__}")
            raise ValidationError(f"无法将同花顺代码 {tonghuashun_code} 转换为标准格式: {str(e)}")
    
    def get_provider_name(self) -> str:
        """获取提供者名称"""
        return "tonghuashun"
    
    def get_rate_limit(self) -> RateLimit:
        """获取速率限制信息"""
        return RateLimit(
            requests_per_second=2.0,
            requests_per_minute=100,
            requests_per_hour=5000
        )
    
    def _generate_tonghuashun_id(self, timestamp: float, user_agent: str) -> str:
        """
        生成同花顺请求所需的ID
        
        Args:
            timestamp: 时间戳
            user_agent: 用户代理字符串
            
        Returns:
            生成的ID字符串
        """
        n = [0] * 18
        n[0] = int(random.random() * 4294967295)
        n[1] = int(timestamp)
        n[3] = self._str_hash(user_agent)
        n[4] = 1
        n[5] = 10
        n[6] = 5
        n[15] = 0
        n[16] = 1
        n[17] = 3
        n[13] = 3748
        n[2] = self._time_now()
        
        buff = self._to_buff(n)
        return self._encode_id(buff)
    
    def _str_hash(self, user_agent: str) -> int:
        """计算字符串哈希值"""
        c = 0
        for v in user_agent:
            c = (c << 5) - c + ord(v)
            c &= 0xFFFFFFFF
        return c
    
    def _time_now(self) -> int:
        """获取当前时间"""
        try:
            time_now = int(time.time() * 1000)
            result = time_now // int("1111101000", 2)
            return result
        except Exception:
            time_now = int(time.time() * 1000)
            result = time_now // int("1000", 10)
            return result
    
    def _to_buff(self, n: List[int]) -> List[int]:
        """转换为缓冲区"""
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
    
    def _encode_id(self, n: List[int]) -> str:
        """编码ID"""
        r = self._hash(n)
        n = self._encode_array(n, [3, r])
        return self._base64_encode(n)
    
    def _hash(self, n: List[int]) -> int:
        """计算哈希值"""
        e = 0
        for i in n:
            e = (e << 5) - e + i
        return e & 255
    
    def _encode_array(self, n: List[int], o: List[int]) -> List[int]:
        """编码数组"""
        a = 0
        i = 2
        u = o[1]
        while a < len(n):
            o.append(n[a] ^ (u & 255))
            u = ~(u * 131)
            a += 1
            i += 1
        return o
    
    def _base64_encode(self, n: List[int]) -> str:
        """Base64编码"""
        m = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        f = []
        for i in range(0, len(n), 3):
            l = (n[i] << 16) | (n[i + 1] << 8) | n[i + 2]
            f.append(m[(l >> 18) & 63])
            f.append(m[(l >> 12) & 63])
            f.append(m[(l >> 6) & 63])
            f.append(m[l & 63])
        return ''.join(f)
    
    async def _make_request(self, url: str, headers: Optional[Dict[str, str]] = None) -> str:
        """
        发起HTTP请求
        
        Args:
            url: 请求URL
            headers: 请求头
            
        Returns:
            响应内容
            
        Raises:
            NetworkError: 网络请求失败
            DataSourceError: 数据源错误
        """
        try:
            # 合并请求头
            request_headers = self.headers.copy()
            if headers:
                request_headers.update(headers)
            
            # 生成cookies
            timestamp = time.time()
            cookies = {
                "v": self._generate_tonghuashun_id(timestamp, request_headers["User-Agent"]),
                "vvv": "1"
            }
            
            # 发起请求
            response = self.session.get(
                url, 
                headers=request_headers, 
                cookies=cookies,
                timeout=self.config.request_timeout
            )
            
            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                raise DataSourceError(f"数据不存在: {url}")
            else:
                raise NetworkError(f"请求失败，状态码: {response.status_code}, URL: {url}")
                
        except requests.exceptions.Timeout:
            raise NetworkError(f"请求超时: {url}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"网络请求异常: {str(e)}")
    
    async def get_concept_list(self) -> pd.DataFrame:
        """
        获取概念板块列表
        
        Returns:
            概念板块列表DataFrame
        """
        try:
            url = f"{self.base_url}/gn/"
            html = await self._make_request(url)
            
            root = etree.fromstring(html, etree.HTMLParser(encoding='utf-8'))
            value_element = root.cssselect('#gnSection')
            
            if not value_element:
                raise DataSourceError("无法找到概念板块数据")
            
            value = value_element[0].get("value")
            if not value:
                raise DataSourceError("概念板块数据为空")
            
            values = json.loads(value)
            
            concepts = [{
                "code": item["platecode"],
                "name": item["platename"],
                "cid": item["cid"],
            } for key, item in values.items()]
            
            df = pd.DataFrame(concepts)
            return df
            
        except json.JSONDecodeError as e:
            raise DataSourceError(f"解析概念板块数据失败: {str(e)}")
        except Exception as e:
            raise DataSourceError(f"获取概念板块列表失败: {str(e)}")
    
    async def get_concept_stocks(self, concept_code: str) -> pd.DataFrame:
        """
        获取概念板块成分股
        
        Args:
            concept_code: 概念板块代码
            
        Returns:
            成分股列表DataFrame
        """
        try:
            url = f"{self.base_url}/gn/detail/field/199112/order/desc/size/1000/page/1/ajax/1/code/{concept_code}"
            html = await self._make_request(url)
            
            root = etree.fromstring(html, etree.HTMLParser(encoding='utf-8'))
            stock_elements = root.cssselect('tr td:nth-child(2) a')
            
            stocks = []
            for item in stock_elements:
                if item.text:
                    try:
                        # 验证并标准化股票代码
                        standard_code = StockCodeConverter.normalize_code(item.text)
                        stocks.append({
                            "code": standard_code,
                            "cid": concept_code,
                        })
                        self.logger.debug(f"概念成分股代码已标准化: {item.text} -> {standard_code}")
                    except Exception as e:
                        self.logger.warning(f"跳过无效的概念成分股代码: {item.text}, 错误: {e}")
                        continue
            
            df = pd.DataFrame(stocks)
            return df
            
        except Exception as e:
            raise DataSourceError(f"获取概念板块成分股失败: {str(e)}")
    
    async def get_concept_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取概念板块基础信息
        
        Args:
            **kwargs: 查询参数
                - refresh: 是否强制刷新缓存
                
        Returns:
            概念板块基础信息DataFrame，包含以下字段：
            - code: 概念代码
            - name: 概念名称  
            - cid: 概念ID
        """
        return await self.get_concept_list()
    
    async def get_concept_constituent(self, concept_code: str, **kwargs) -> pd.DataFrame:
        """
        获取概念板块成分股
        
        Args:
            concept_code: 概念板块代码
            **kwargs: 查询参数
                - refresh: 是否强制刷新缓存
                
        Returns:
            成分股DataFrame，包含以下字段：
            - code: 股票代码
            - cid: 概念ID
        """
        return await self.get_concept_stocks(concept_code)
    
    async def search_concept_by_name(self, name: str) -> pd.DataFrame:
        """
        根据名称搜索概念板块
        
        Args:
            name: 概念名称（支持模糊匹配）
            
        Returns:
            匹配的概念板块DataFrame
        """
        concepts_df = await self.get_concept_list()
        
        if concepts_df.empty:
            return pd.DataFrame()
        
        # 模糊匹配概念名称
        matched = concepts_df[concepts_df['name'].str.contains(name, na=False)]
        return matched
    
    async def get_stock_concepts(self, stock_code: str) -> pd.DataFrame:
        """
        获取股票所属的概念板块
        
        Args:
            stock_code: 股票代码
            
        Returns:
            股票所属概念板块DataFrame
        """
        concepts_df = await self.get_concept_list()
        result_concepts = []
        
        # 标准化输入的股票代码
        try:
            standard_stock_code = StockCodeConverter.normalize_code(stock_code)
            self.logger.debug(f"查询股票概念的代码已标准化: {stock_code} -> {standard_stock_code}")
        except Exception as e:
            self.logger.warning(f"股票代码标准化失败，使用原始代码: {stock_code}, 错误: {e}")
            standard_stock_code = stock_code
        
        for _, concept in concepts_df.iterrows():
            try:
                stocks_df = await self.get_concept_stocks(concept['cid'])
                if not stocks_df.empty and standard_stock_code in stocks_df['code'].values:
                    result_concepts.append({
                        'stock_code': standard_stock_code,
                        'concept_code': concept['code'],
                        'concept_name': concept['name'],
                        'concept_cid': concept['cid']
                    })
            except Exception as e:
                # 忽略单个概念获取失败的情况
                self.logger.warning(f"获取概念 {concept['code']} 成分股失败: {str(e)}")
                continue
        
        return pd.DataFrame(result_concepts)
    
    async def get_concept_stats(self, concept_code: str) -> Dict[str, Any]:
        """
        获取概念板块统计信息
        
        Args:
            concept_code: 概念板块代码
            
        Returns:
            概念板块统计信息字典
        """
        try:
            # 获取概念基础信息
            concepts_df = await self.get_concept_list()
            concept_info = concepts_df[concepts_df['code'] == concept_code]
            
            if concept_info.empty:
                raise DataSourceError(f"概念板块 {concept_code} 不存在")
            
            concept_row = concept_info.iloc[0]
            
            # 获取成分股
            stocks_df = await self.get_concept_stocks(concept_row['cid'])
            
            stats = {
                'concept_code': concept_code,
                'concept_name': concept_row['name'],
                'concept_cid': concept_row['cid'],
                'stock_count': len(stocks_df),
                'constituent_stocks': stocks_df['code'].tolist() if not stocks_df.empty else []
            }
            
            return stats
            
        except Exception as e:
            raise DataSourceError(f"获取概念板块统计信息失败: {str(e)}")
    
    def _compute_range(self, data: List[Dict]) -> pd.DataFrame:
        """
        计算价格数据的涨跌幅等指标
        
        Args:
            data: 原始价格数据列表
            
        Returns:
            计算后的DataFrame
        """
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        df_shifted = df.shift()
        
        # 计算涨跌额和涨跌幅
        df['range_amount'] = round(df['end'] - df_shifted['end'], 3)
        df['range'] = round(df['range_amount'] / df_shifted['end'], 3)
        df['amplitude'] = round((df['max'] - df['min']) / df_shifted['end'], 3)
        
        return df
    
    def _parse_price_data(self, raw_data: str, secid: str) -> List[Dict]:
        """
        解析价格数据
        
        Args:
            raw_data: 原始数据字符串
            secid: 证券ID
            
        Returns:
            解析后的价格数据列表
        """
        try:
            # 移除JavaScript前缀
            if raw_data.startswith('quotebridge_v4_line_bk_'):
                # 找到JSON数据的开始位置
                start_pos = raw_data.find('(') + 1
                end_pos = raw_data.rfind(')')
                json_str = raw_data[start_pos:end_pos]
            else:
                json_str = raw_data
            
            data = json.loads(json_str)
            
            # 获取数据部分
            key = f"bk_{secid}"
            if key not in data or 'data' not in data[key]:
                return []
            
            data_str = data[key]['data']
            if not data_str:
                return []
            
            # 解析数据行
            price_data = []
            for line in data_str.split(';'):
                if not line.strip():
                    continue
                
                parts = line.split(',')
                if len(parts) < 10:
                    continue
                
                try:
                    price_data.append({
                        "date_at": parts[0],
                        "start": float(parts[1]),
                        "end": float(parts[4]),
                        "max": float(parts[2]),
                        "min": float(parts[3]),
                        "count": int(parts[5]),  # 成交量
                        "amount": float(parts[6]),  # 成交额
                        "amplitude": float(parts[2]) - float(parts[3]),  # 振幅
                        "range": 0.0,  # 涨跌幅，后续计算
                        "range_amount": float(parts[9]) if len(parts) > 9 else 0.0,  # 涨跌额
                        "turnover_rate": 0.0,  # 换手率
                    })
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"解析价格数据行失败: {line}, 错误: {str(e)}")
                    continue
            
            return price_data
            
        except json.JSONDecodeError as e:
            raise DataSourceError(f"解析价格数据JSON失败: {str(e)}")
        except Exception as e:
            raise DataSourceError(f"解析价格数据失败: {str(e)}")
    
    async def get_concept_minute_data(self, concept_code: str, freq: str = '1min') -> pd.DataFrame:
        """
        获取概念板块分钟数据
        
        Args:
            concept_code: 概念代码
            freq: 频率 ('1min', '30min', '60min')
            
        Returns:
            分钟数据DataFrame
        """
        # 验证频率参数
        freq_map = {
            '1min': '61',
            '30min': '41', 
            '60min': '51'
        }
        
        if freq not in freq_map:
            raise ValidationError(f"不支持的频率: {freq}, 支持的频率: {list(freq_map.keys())}")
        
        freq_code = freq_map[freq]

        
        try:
            current_year = datetime.date.today().year
            all_data = []
            
            # 获取多年数据
            for year in range(current_year, 2014, -1):
                url = f"{self.data_url}/v4/line/bk_{concept_code}/{freq_code}/{year}.js"
                
                try:
                    raw_data = await self._make_request(url)
                    year_data = self._parse_price_data(raw_data, concept_code)
                    all_data.extend(year_data)
                except DataSourceError as e:
                    if "数据不存在" in str(e):
                        # 该年份没有数据，继续下一年
                        continue
                    else:
                        raise
                except Exception as e:
                    self.logger.warning(f"获取{year}年数据失败: {str(e)}")
                    continue
            
            # 计算技术指标
            df = self._compute_range(all_data)
            

            
            return df
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(f"获取概念板块分钟数据失败: {str(e)}")
    
    async def get_concept_daily_data(self, concept_code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取概念板块日线数据
        
        Args:
            concept_code: 概念代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            日线数据DataFrame
        """
        # 验证日期格式
        if start_date:
            validate_date_format(start_date)
        if end_date:
            validate_date_format(end_date)
        
        try:
            current_year = datetime.date.today().year
            all_data = []
            
            # 获取多年数据
            for year in range(current_year, 2014, -1):
                url = f"{self.data_url}/v4/line/bk_{concept_code}/01/{year}.js"
                
                try:
                    raw_data = await self._make_request(url)
                    year_data = self._parse_price_data(raw_data, concept_code)
                    all_data.extend(year_data)
                except DataSourceError as e:
                    if "数据不存在" in str(e):
                        continue
                    else:
                        raise
                except Exception as e:
                    self.logger.warning(f"获取{year}年日线数据失败: {str(e)}")
                    continue
            
            # 计算技术指标
            df = self._compute_range(all_data)
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(f"获取概念板块日线数据失败: {str(e)}")
        
        # 过滤日期范围
        if not df.empty and (start_date or end_date):
            if start_date:
                df = df[df['date_at'] >= start_date]
            if end_date:
                df = df[df['date_at'] <= end_date]
        
        return df
    
    async def get_concept_weekly_data(self, concept_code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取概念板块周线数据
        
        Args:
            concept_code: 概念代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            周线数据DataFrame
        """
        # 验证日期格式
        if start_date:
            validate_date_format(start_date)
        if end_date:
            validate_date_format(end_date)
        
        try:
            current_year = datetime.date.today().year
            all_data = []
            
            # 获取多年数据
            for year in range(current_year, 2014, -1):
                url = f"{self.data_url}/v4/line/bk_{concept_code}/11/{year}.js"
                
                try:
                    raw_data = await self._make_request(url)
                    year_data = self._parse_price_data(raw_data, concept_code)
                    all_data.extend(year_data)
                except DataSourceError as e:
                    if "数据不存在" in str(e):
                        continue
                    else:
                        raise
                except Exception as e:
                    self.logger.warning(f"获取{year}年周线数据失败: {str(e)}")
                    continue
            
            # 计算技术指标
            df = self._compute_range(all_data)
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(f"获取概念板块周线数据失败: {str(e)}")
        
        # 过滤日期范围
        if not df.empty and (start_date or end_date):
            if start_date:
                df = df[df['date_at'] >= start_date]
            if end_date:
                df = df[df['date_at'] <= end_date]
        
        return df
    
    async def get_concept_monthly_data(self, concept_code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取概念板块月线数据
        
        Args:
            concept_code: 概念代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            月线数据DataFrame
        """
        # 验证日期格式
        if start_date:
            validate_date_format(start_date)
        if end_date:
            validate_date_format(end_date)
        
        try:
            url = f"{self.data_url}/v4/line/bk_{concept_code}/21/last.js"
            raw_data = await self._make_request(url)
            all_data = self._parse_price_data(raw_data, concept_code)
            
            # 计算技术指标
            df = self._compute_range(all_data)
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(f"获取概念板块月线数据失败: {str(e)}")
        
        # 过滤日期范围
        if not df.empty and (start_date or end_date):
            if start_date:
                df = df[df['date_at'] >= start_date]
            if end_date:
                df = df[df['date_at'] <= end_date]
        
        return df
    
    # 实现抽象方法（基础功能，同花顺主要用于概念数据）
    async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
        """获取股票基础信息（同花顺不支持）"""
        raise NotImplementedError("同花顺数据源不支持股票基础信息获取")
    
    async def get_stock_daily(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票日线数据（同花顺不支持）"""
        raise NotImplementedError("同花顺数据源不支持股票日线数据获取")
    
    async def get_trade_cal(self, start_date: str, end_date: str) -> pd.DataFrame:
        """获取交易日历（同花顺不支持）"""
        raise NotImplementedError("同花顺数据源不支持交易日历获取")
    
    def convert_input_code(self, code: str) -> str:
        """将输入代码转换为同花顺所需格式"""
        return self._convert_stock_code(code)
    
    def convert_output_code(self, code: str) -> str:
        """将同花顺返回的代码转换为标准格式"""
        return self._convert_to_standard_code(code)
    
    def get_required_format(self) -> str:
        """获取同花顺要求的代码格式"""
        return "tonghuashun"
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 尝试获取概念板块列表来检查服务可用性
            url = f"{self.base_url}/gn/"
            html = await self._make_request(url)
            
            # 如果能成功获取HTML内容，认为服务可用
            return html is not None and len(html) > 0
            
        except Exception as e:
            self.logger.warning(f"健康检查失败: {e}")
            return False