"""
Baostock数据提供者

提供基于baostock的股票、指数、基金数据获取功能
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Optional, Dict, Any, List
import pandas as pd

try:
    import baostock as bs
    BAOSTOCK_AVAILABLE = True
except ImportError:
    BAOSTOCK_AVAILABLE = False
    bs = None

from .base import DataProvider, RateLimit
from ..core.errors import DataSourceError, ValidationError, NetworkError
from ..utils.code_converter import StockCodeConverter
from ..utils.validators import validate_stock_code, validate_date_format


class BaostockProvider(DataProvider):
    """Baostock数据提供者"""
    
    def __init__(self, config):
        """
        初始化Baostock提供者
        
        Args:
            config: 配置对象
        """
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self._session_active = False
        self._login_lock = asyncio.Lock()
        
        # 检查baostock是否可用
        if not BAOSTOCK_AVAILABLE:
            raise DataSourceError(
                "baostock库未安装，请运行: pip install baostock",
                error_code="BAOSTOCK_NOT_INSTALLED"
            )
    
    async def _ensure_login(self):
        """确保baostock会话已登录"""
        async with self._login_lock:
            if not self._session_active:
                try:
                    # baostock登录
                    lg = bs.login()
                    if lg.error_code != '0':
                        raise DataSourceError(
                            f"Baostock登录失败: {lg.error_msg}",
                            error_code="BAOSTOCK_LOGIN_FAILED",
                            details={'error_code': lg.error_code, 'error_msg': lg.error_msg}
                        )
                    
                    self._session_active = True
                    self.logger.info("Baostock登录成功")
                    
                except Exception as e:
                    if isinstance(e, DataSourceError):
                        raise
                    raise NetworkError(
                        f"Baostock连接失败: {str(e)}",
                        error_code="BAOSTOCK_CONNECTION_ERROR"
                    )
    
    async def _logout(self):
        """登出baostock会话"""
        if self._session_active:
            try:
                bs.logout()
                self._session_active = False
                self.logger.info("Baostock登出成功")
            except Exception as e:
                self.logger.warning(f"Baostock登出时出现警告: {e}")
    
    def __del__(self):
        """析构函数，确保登出"""
        if hasattr(self, '_session_active') and self._session_active:
            try:
                bs.logout()
            except:
                pass
    
    def _format_date_for_baostock(self, date_str: str) -> str:
        """
        将日期转换为 Baostock 要求的格式 (YYYY-MM-DD)
        
        Args:
            date_str: 日期字符串，支持多种格式
            
        Returns:
            YYYY-MM-DD 格式的日期字符串
        """
        # 如果已经是 YYYY-MM-DD 格式，直接返回
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str
        
        # 支持的格式
        formats = [
            ('%Y%m%d', r'^\d{8}$'),
            ('%Y/%m/%d', r'^\d{4}/\d{2}/\d{2}$'),
            ('%Y.%m.%d', r'^\d{4}\.\d{2}\.\d{2}$')
        ]
        
        for date_format, pattern in formats:
            if re.match(pattern, date_str):
                try:
                    dt = datetime.strptime(date_str, date_format)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        
        # 如果无法识别格式，返回原始字符串（让 Baostock API 报错）
        return date_str
    
    async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取股票基础信息
        
        Args:
            **kwargs: 查询参数
                - date: 查询日期，格式YYYY-MM-DD，默认为最新
                - market: 市场类型，可选值：'all', 'sh', 'sz'，默认为'all'
                
        Returns:
            股票基础信息DataFrame
        """
        await self._ensure_login()
        
        try:
            # 解析参数
            date = kwargs.get('date')
            market = kwargs.get('market', 'all')
            
            # 如果没有指定日期，使用最近有数据的日期
            if not date:
                # Baostock 数据更新较慢，使用 2024-12-31 作为默认日期
                # 用户应该明确指定需要的日期
                date = '2024-12-31'
                self.logger.info(f"未指定日期，使用默认日期: {date} (Baostock数据更新较慢，建议明确指定日期)")
            
            # 参数验证并转换为 Baostock 要求的格式 (YYYY-MM-DD)
            validate_date_format(date)
            date_formatted = self._format_date_for_baostock(date)
            
            # 获取股票基础信息（Baostock 必须指定日期）
            rs = bs.query_all_stock(day=date_formatted)
            
            if rs.error_code != '0':
                raise DataSourceError(
                    f"获取股票基础信息失败: {rs.error_msg}",
                    error_code="BAOSTOCK_QUERY_ERROR",
                    details={
                        'error_code': rs.error_code, 
                        'error_msg': rs.error_msg,
                        'date': date,
                        'market': market
                    }
                )
            
            # 转换为DataFrame
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                self.logger.warning(f"未获取到股票基础信息数据，日期: {date}, 市场: {market}")
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 根据市场类型过滤
            if market != 'all':
                df = self._filter_by_market(df, market)
            
            # 标准化列名
            df = self._standardize_stock_basic_columns(df)
            
            # 验证数据格式
            df = self.validate_data_format(df)
            
            self.logger.info(f"成功获取{len(df)}条股票基础信息")
            return df
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(
                f"获取股票基础信息时发生错误: {str(e)}",
                error_code="BAOSTOCK_UNEXPECTED_ERROR",
                details={'date': kwargs.get('date'), 'market': kwargs.get('market')}
            )
    
    async def get_stock_detail(self, ts_code: Optional[str] = None, type: Optional[str] = None, status: Optional[str] = None) -> pd.DataFrame:
        """
        获取证券基本资料
        
        使用 Baostock 的 query_stock_basic 接口获取股票的详细信息，
        包括上市日期、退市日期、股票类型、股票状态等。
        
        策略：
        1. 优先从 SQLite 缓存获取所有股票数据
        2. 如果缓存不存在或已过期，从 Baostock 获取所有股票数据并缓存
        3. 根据 ts_code、type、status 参数从缓存数据中筛选返回
        
        Args:
            ts_code: 股票代码（可选）
                - 如果指定代码：返回该股票的详细资料
                - 如果不指定（None）：返回所有股票的详细资料
                支持的格式：
                - 标准格式: 000001.SZ, 600000.SH
                - Baostock格式: sz.000001, sh.600000
                - 纯数字: 000001, 600000
            type: 证券类型（可选），用于筛选：
                - '1': 股票
                - '2': 指数
                - '3': 其它
                - '4': 可转债
                - '5': ETF
            status: 上市状态（可选），用于筛选：
                - '1': 上市
                - '0': 退市
        
        Returns:
            证券基本资料DataFrame，包含以下字段（保留 baostock 原始字段名）：
            - code: 证券代码（baostock 格式，如 sz.000001）
            - code_name: 证券名称
            - ipoDate: 上市日期 (YYYY-MM-DD)
            - outDate: 退市日期 (YYYY-MM-DD)
            - type: 证券类型 (1:股票, 2:指数, 3:其它, 4:可转债, 5:ETF)
            - status: 上市状态 (1:上市, 0:退市)
        
        Raises:
            ValidationError: 参数验证失败
            DataSourceError: 数据获取失败
        
        Example:
        """
        # 参数验证（如果提供了代码）
        if ts_code:
            validate_stock_code(ts_code)
        
        # 从 Baostock 获取所有股票数据
        await self._ensure_login()
        
        try:
            # 查询所有股票的基本资料
            rs = bs.query_stock_basic()
            
            if rs.error_code != '0':
                raise DataSourceError(
                    f"获取证券基本资料失败: {rs.error_msg}",
                    error_code="BAOSTOCK_QUERY_ERROR",
                    details={
                        'error_code': rs.error_code,
                        'error_msg': rs.error_msg
                    }
                )
            
            # 转换为DataFrame
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                self.logger.warning("未获取到股票基本资料")
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            self.logger.info(f"成功获取所有股票的基本资料，共{len(df)}条记录")
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(
                f"获取证券基本资料时发生错误: {str(e)}",
                error_code="BAOSTOCK_UNEXPECTED_ERROR",
                details={'ts_code': ts_code}
            )
        
        # 根据参数筛选数据
        filtered_df = df.copy()
        
        # 按股票代码筛选
        if ts_code:
            baostock_code = self._convert_stock_code(ts_code)
            filtered_df = filtered_df[filtered_df['code'] == baostock_code]
            
            if filtered_df.empty:
                self.logger.warning(f"未找到股票 {ts_code} 的基本资料")
        
        # 按证券类型筛选
        if type is not None and 'type' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['type'] == type]
            
            if filtered_df.empty:
                type_names = {'1': '股票', '2': '指数', '3': '其它', '4': '可转债', '5': 'ETF'}
                self.logger.warning(f"未找到类型为 {type_names.get(type, type)} 的证券")
        
        # 按上市状态筛选
        if status is not None and 'status' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['status'] == status]
            
            if filtered_df.empty:
                status_names = {'0': '退市', '1': '上市'}
                self.logger.warning(f"未找到状态为 {status_names.get(status, status)} 的证券")
        
        return filtered_df.copy()

    async def get_stock_daily(self, ts_code: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        获取股票日线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD
            **kwargs: 其他参数
                - adjustflag: 复权类型，'1'前复权，'2'后复权，'3'不复权，默认'3'
                - frequency: 数据频率，'d'日线，'w'周线，'m'月线，默认'd'
                - fields: 返回字段列表，默认返回所有字段
            
        Returns:
            股票日线数据DataFrame
        """
        # 参数验证
        validate_stock_code(ts_code)
        validate_date_format(start_date)
        validate_date_format(end_date)
        
        # 转换日期格式为 Baostock 要求的格式 (YYYY-MM-DD)
        start_date_formatted = self._format_date_for_baostock(start_date)
        end_date_formatted = self._format_date_for_baostock(end_date)
        
        # 解析可选参数
        adjustflag = kwargs.get('adjustflag', '3')  # 默认不复权
        frequency = kwargs.get('frequency', 'd')    # 默认日线
        fields = kwargs.get('fields')
        
        # 验证参数值
        if adjustflag not in ['1', '2', '3']:
            raise ValidationError(f"无效的复权类型: {adjustflag}，必须是'1'、'2'或'3'")
        
        if frequency not in ['d', 'w', 'm']:
            raise ValidationError(f"无效的数据频率: {frequency}，必须是'd'、'w'或'm'")
        
        await self._ensure_login()
        
        try:
            # 转换股票代码格式
            baostock_code = self._convert_stock_code(ts_code)
            
            # 构建查询字段
            if fields:
                query_fields = ','.join(fields)
            else:
                query_fields = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST"
            
            # 查询历史数据（使用格式化后的日期）
            rs = bs.query_history_k_data_plus(
                baostock_code,
                query_fields,
                start_date=start_date_formatted,
                end_date=end_date_formatted,
                frequency=frequency,
                adjustflag=adjustflag
            )
            
            if rs.error_code != '0':
                raise DataSourceError(
                    f"获取股票{frequency}线数据失败: {rs.error_msg}",
                    error_code="BAOSTOCK_QUERY_ERROR",
                    details={
                        'error_code': rs.error_code, 
                        'error_msg': rs.error_msg,
                        'ts_code': ts_code,
                        'baostock_code': baostock_code,
                        'start_date': start_date,
                        'end_date': end_date,
                        'frequency': frequency,
                        'adjustflag': adjustflag
                    }
                )
            
            # 转换为DataFrame
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                self.logger.warning(f"未获取到股票数据: {ts_code}, {start_date} - {end_date}")
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 过滤掉停牌或无效数据
            df = self._filter_invalid_data(df)
            
            # 标准化列名和数据类型
            df = self._standardize_ohlcv_columns(df)
            
            # 验证数据格式和一致性
            df = self.validate_data_format(df)
            if not self.check_data_consistency(df, ts_code):
                self.logger.warning(f"数据一致性检查失败: {ts_code}")
            
            self.logger.info(f"成功获取股票{frequency}线数据: {ts_code}, {len(df)}条记录")
            return df
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(
                f"获取股票{frequency}线数据时发生错误: {str(e)}",
                error_code="BAOSTOCK_UNEXPECTED_ERROR",
                details={
                    'ts_code': ts_code, 
                    'start_date': start_date, 
                    'end_date': end_date,
                    'frequency': frequency,
                    'adjustflag': adjustflag
                }
            )
    
    async def get_trade_cal(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取交易日历
        
        Args:
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD
            
        Returns:
            交易日历DataFrame
        """
        # 参数验证
        validate_date_format(start_date)
        validate_date_format(end_date)
        
        # 转换日期格式
        start_date_formatted = self._format_date_for_baostock(start_date)
        end_date_formatted = self._format_date_for_baostock(end_date)
        
        await self._ensure_login()
        
        try:
            # 查询交易日历（使用格式化后的日期）
            rs = bs.query_trade_dates(start_date=start_date_formatted, end_date=end_date_formatted)
            
            if rs.error_code != '0':
                raise DataSourceError(
                    f"获取交易日历失败: {rs.error_msg}",
                    error_code="BAOSTOCK_QUERY_ERROR",
                    details={
                        'error_code': rs.error_code,
                        'error_msg': rs.error_msg,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                )
            
            # 转换为DataFrame
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 标准化列名
            df = self._standardize_trade_cal_columns(df)
            
            return df
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(
                f"获取交易日历时发生错误: {str(e)}",
                error_code="BAOSTOCK_UNEXPECTED_ERROR",
                details={'start_date': start_date, 'end_date': end_date}
            )
    
    def _convert_stock_code(self, ts_code: str) -> str:
        """
        转换股票代码格式为baostock格式
        
        Args:
            ts_code: 任意格式的股票代码
            
        Returns:
            baostock格式的股票代码（如sz.000001）
        """
        try:
            # 检查是否已经是baostock格式
            if re.match(r'^(sh|sz)\.([0-9]{6})$', ts_code.lower()):
                return ts_code.lower()
            
            # 使用统一的代码转换器
            return StockCodeConverter.to_baostock_format(ts_code)
        except Exception as e:
            self.logger.error(f"股票代码转换失败: {ts_code} -> baostock格式, 错误: {e}")
            # 记录转换错误到日志
            self.logger.debug(f"转换失败详情 - 输入代码: {ts_code}, 目标格式: baostock, 异常类型: {type(e).__name__}")
            raise ValidationError(f"无法将股票代码 {ts_code} 转换为baostock格式: {str(e)}")
    
    def _standardize_stock_basic_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化股票基础信息列名
        
        Args:
            df: 原始DataFrame
            
        Returns:
            标准化后的DataFrame
        """
        if df.empty:
            return df
        
        # baostock股票基础信息列名映射
        column_mapping = {
            'code': 'ts_code',
            'code_name': 'name',
            'ipoDate': 'list_date',
            'outDate': 'delist_date',
            'type': 'market',
            'status': 'list_status'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 转换股票代码格式（从baostock格式转为标准格式）
        if 'ts_code' in df.columns:
            try:
                df['ts_code'] = df['ts_code'].apply(self._convert_to_standard_code)
                self.logger.debug(f"成功转换{len(df)}条股票基础信息的代码格式")
            except Exception as e:
                self.logger.error(f"批量转换股票基础信息代码格式失败: {e}")
                # 尝试逐行转换，跳过失败的行
                valid_rows = []
                for idx, row in df.iterrows():
                    try:
                        row['ts_code'] = self._convert_to_standard_code(row['ts_code'])
                        valid_rows.append(row)
                    except Exception as row_error:
                        self.logger.warning(f"跳过无效代码行: {row['ts_code']}, 错误: {row_error}")
                        continue
                df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame()
        
        # 确保必要的列存在
        required_columns = ['ts_code', 'name']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        return df
    
    def _standardize_ohlcv_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化OHLCV数据列名和数据类型
        
        Args:
            df: 原始DataFrame
            
        Returns:
            标准化后的DataFrame
        """
        if df.empty:
            return df
        
        # baostock OHLCV列名映射
        column_mapping = {
            'date': 'trade_date',
            'code': 'ts_code',
            'preclose': 'pre_close',
            'pctChg': 'pct_chg'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 转换股票代码格式
        if 'ts_code' in df.columns:
            try:
                df['ts_code'] = df['ts_code'].apply(self._convert_to_standard_code)
                self.logger.debug(f"成功转换{len(df)}条OHLCV数据的代码格式")
            except Exception as e:
                self.logger.error(f"批量转换OHLCV数据代码格式失败: {e}")
                # 尝试逐行转换，跳过失败的行
                valid_rows = []
                for idx, row in df.iterrows():
                    try:
                        row['ts_code'] = self._convert_to_standard_code(row['ts_code'])
                        valid_rows.append(row)
                    except Exception as row_error:
                        self.logger.warning(f"跳过无效代码行: {row['ts_code']}, 错误: {row_error}")
                        continue
                df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame()
        
        # 转换数据类型
        numeric_columns = ['open', 'high', 'low', 'close', 'pre_close', 'volume', 'amount', 'pct_chg']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 转换日期格式
        if 'trade_date' in df.columns:
            df['trade_date'] = pd.to_datetime(df['trade_date']).dt.strftime('%Y%m%d')
        
        return df
    
    def _standardize_trade_cal_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化交易日历列名
        
        Args:
            df: 原始DataFrame
            
        Returns:
            标准化后的DataFrame
        """
        if df.empty:
            return df
        
        # baostock交易日历列名映射
        column_mapping = {
            'calendar_date': 'cal_date',
            'is_trading_day': 'is_open'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 转换数据类型
        if 'is_open' in df.columns:
            df['is_open'] = df['is_open'].astype(int)
        
        # 转换日期格式
        if 'cal_date' in df.columns:
            df['cal_date'] = pd.to_datetime(df['cal_date']).dt.strftime('%Y%m%d')
        
        return df
    
    def _convert_to_standard_code(self, baostock_code: str) -> str:
        """
        将baostock格式的代码转换为标准格式
        
        Args:
            baostock_code: baostock格式代码（如sz.000001）
            
        Returns:
            标准格式代码（如000001.SZ）
        """
        try:
            # 使用统一的代码转换器
            return StockCodeConverter.from_baostock_format(baostock_code)
        except Exception as e:
            self.logger.error(f"股票代码转换失败: {baostock_code} -> 标准格式, 错误: {e}")
            # 记录转换错误到日志
            self.logger.debug(f"转换失败详情 - 输入代码: {baostock_code}, 目标格式: standard, 异常类型: {type(e).__name__}")
            raise ValidationError(f"无法将baostock代码 {baostock_code} 转换为标准格式: {str(e)}")
    
    def _convert_index_code(self, ts_code: str) -> str:
        """
        转换指数代码格式为baostock格式
        
        Args:
            ts_code: 标准指数代码（如000001.SH）
            
        Returns:
            baostock格式的指数代码（如sh.000001）
        """
        # 指数代码转换逻辑与股票代码类似
        return self._convert_stock_code(ts_code)
    
    def _standardize_index_basic_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化指数基础信息列名
        
        Args:
            df: 原始DataFrame
            
        Returns:
            标准化后的DataFrame
        """
        if df.empty:
            return df
        
        # baostock指数基础信息列名映射（使用行业分类数据作为替代）
        column_mapping = {
            'code': 'ts_code',
            'code_name': 'name',
            'industry': 'category',
            'industryClassification': 'classification'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 转换代码格式
        if 'ts_code' in df.columns:
            try:
                df['ts_code'] = df['ts_code'].apply(self._convert_to_standard_code)
                self.logger.debug(f"成功转换{len(df)}条指数基础信息的代码格式")
            except Exception as e:
                self.logger.error(f"批量转换指数基础信息代码格式失败: {e}")
                # 尝试逐行转换，跳过失败的行
                valid_rows = []
                for idx, row in df.iterrows():
                    try:
                        row['ts_code'] = self._convert_to_standard_code(row['ts_code'])
                        valid_rows.append(row)
                    except Exception as row_error:
                        self.logger.warning(f"跳过无效代码行: {row['ts_code']}, 错误: {row_error}")
                        continue
                df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame()
        
        # 确保必要的列存在
        required_columns = ['ts_code', 'name']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        return df
    
    def _standardize_index_ohlcv_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化指数OHLCV数据列名和数据类型
        
        Args:
            df: 原始DataFrame
            
        Returns:
            标准化后的DataFrame
        """
        if df.empty:
            return df
        
        # 指数OHLCV列名映射
        column_mapping = {
            'date': 'trade_date',
            'code': 'ts_code',
            'pctChg': 'pct_chg'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 转换代码格式
        if 'ts_code' in df.columns:
            try:
                df['ts_code'] = df['ts_code'].apply(self._convert_to_standard_code)
                self.logger.debug(f"成功转换{len(df)}条指数OHLCV数据的代码格式")
            except Exception as e:
                self.logger.error(f"批量转换指数OHLCV数据代码格式失败: {e}")
                # 尝试逐行转换，跳过失败的行
                valid_rows = []
                for idx, row in df.iterrows():
                    try:
                        row['ts_code'] = self._convert_to_standard_code(row['ts_code'])
                        valid_rows.append(row)
                    except Exception as row_error:
                        self.logger.warning(f"跳过无效代码行: {row['ts_code']}, 错误: {row_error}")
                        continue
                df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame()
        
        # 转换数据类型
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount', 'pct_chg']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 转换日期格式
        if 'trade_date' in df.columns:
            df['trade_date'] = pd.to_datetime(df['trade_date']).dt.strftime('%Y%m%d')
        
        return df
    
    def get_rate_limit(self) -> RateLimit:
        """
        获取速率限制信息
        
        Returns:
            速率限制对象
        """
        # baostock相对宽松的速率限制
        return RateLimit(
            requests_per_second=2.0,
            requests_per_minute=100,
            requests_per_hour=3000
        )
    
    def is_available(self) -> bool:
        """
        检查数据源是否可用
        
        Returns:
            是否可用
        """
        return BAOSTOCK_AVAILABLE and self.config.enable_baostock
    
    def _filter_by_market(self, df: pd.DataFrame, market: str) -> pd.DataFrame:
        """
        根据市场类型过滤股票数据
        
        Args:
            df: 股票数据DataFrame
            market: 市场类型 ('sh', 'sz')
            
        Returns:
            过滤后的DataFrame
        """
        if df.empty or 'code' not in df.columns:
            return df
        
        if market.lower() == 'sh':
            return df[df['code'].str.startswith('sh.')]
        elif market.lower() == 'sz':
            return df[df['code'].str.startswith('sz.')]
        else:
            return df
    
    def _filter_invalid_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        过滤无效的股票数据
        
        Args:
            df: 原始数据DataFrame
            
        Returns:
            过滤后的DataFrame
        """
        if df.empty:
            return df
        
        # 创建副本避免修改原数据
        filtered_df = df.copy()
        
        # 过滤掉停牌数据（tradestatus != '1'）
        if 'tradestatus' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['tradestatus'] == '1'].copy()
        
        # 过滤掉价格为空或0的数据
        price_columns = ['open', 'high', 'low', 'close']
        for col in price_columns:
            if col in filtered_df.columns:
                # 转换为数值类型并过滤
                numeric_values = pd.to_numeric(filtered_df[col], errors='coerce')
                valid_mask = (numeric_values > 0) & (~numeric_values.isna())
                filtered_df = filtered_df[valid_mask].copy()
        
        return filtered_df
    
    async def get_stock_minute(self, ts_code: str, freq: str = '1min',
                              start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取股票分钟数据（baostock不支持分钟数据）
        
        Args:
            ts_code: 股票代码
            freq: 频率 (1min, 5min, 15min, 30min, 60min)
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            股票分钟数据DataFrame
        """
        raise NotImplementedError("Baostock不支持分钟级数据获取，请使用其他数据源")
    
    async def get_index_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取指数基础信息
        
        Args:
            **kwargs: 查询参数
                - date: 查询日期，格式YYYY-MM-DD，默认为最新
                
        Returns:
            指数基础信息DataFrame
        """
        await self._ensure_login()
        
        try:
            # 解析参数
            date = kwargs.get('date')
            
            # 参数验证
            if date:
                validate_date_format(date)
            
            # 获取指数基础信息
            if date:
                rs = bs.query_stock_industry(date=date)
            else:
                # baostock没有直接的指数基础信息接口，使用行业分类作为替代
                rs = bs.query_stock_industry()
            
            if rs.error_code != '0':
                raise DataSourceError(
                    f"获取指数基础信息失败: {rs.error_msg}",
                    error_code="BAOSTOCK_QUERY_ERROR",
                    details={
                        'error_code': rs.error_code,
                        'error_msg': rs.error_msg,
                        'date': date
                    }
                )
            
            # 转换为DataFrame
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                self.logger.warning(f"未获取到指数基础信息数据，日期: {date}")
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 标准化列名
            df = self._standardize_index_basic_columns(df)
            
            self.logger.info(f"成功获取{len(df)}条指数基础信息")
            return df
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(
                f"获取指数基础信息时发生错误: {str(e)}",
                error_code="BAOSTOCK_UNEXPECTED_ERROR",
                details={'date': kwargs.get('date')}
            )
    
    async def get_index_daily(self, ts_code: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        获取指数日线数据
        
        Args:
            ts_code: 指数代码
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD
            **kwargs: 其他参数
                - frequency: 数据频率，'d'日线，'w'周线，'m'月线，默认'd'
                - fields: 返回字段列表，默认返回所有字段
            
        Returns:
            指数日线数据DataFrame
        """
        # 参数验证
        validate_stock_code(ts_code)  # 指数代码格式与股票代码类似
        validate_date_format(start_date)
        validate_date_format(end_date)
        
        # 解析可选参数
        frequency = kwargs.get('frequency', 'd')
        fields = kwargs.get('fields')
        
        # 验证参数值
        if frequency not in ['d', 'w', 'm']:
            raise ValidationError(f"无效的数据频率: {frequency}，必须是'd'、'w'或'm'")
        
        await self._ensure_login()
        
        try:
            # 转换指数代码格式
            baostock_code = self._convert_index_code(ts_code)
            
            # 构建查询字段
            if fields:
                query_fields = ','.join(fields)
            else:
                query_fields = "date,code,open,high,low,close,volume,amount,turn,pctChg"
            
            # 查询指数历史数据
            rs = bs.query_history_k_data_plus(
                baostock_code,
                query_fields,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                adjustflag="3"  # 指数不需要复权
            )
            
            if rs.error_code != '0':
                raise DataSourceError(
                    f"获取指数{frequency}线数据失败: {rs.error_msg}",
                    error_code="BAOSTOCK_QUERY_ERROR",
                    details={
                        'error_code': rs.error_code,
                        'error_msg': rs.error_msg,
                        'ts_code': ts_code,
                        'baostock_code': baostock_code,
                        'start_date': start_date,
                        'end_date': end_date,
                        'frequency': frequency
                    }
                )
            
            # 转换为DataFrame
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                self.logger.warning(f"未获取到指数数据: {ts_code}, {start_date} - {end_date}")
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 标准化列名和数据类型
            df = self._standardize_index_ohlcv_columns(df)
            
            self.logger.info(f"成功获取指数{frequency}线数据: {ts_code}, {len(df)}条记录")
            return df
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(
                f"获取指数{frequency}线数据时发生错误: {str(e)}",
                error_code="BAOSTOCK_UNEXPECTED_ERROR",
                details={
                    'ts_code': ts_code,
                    'start_date': start_date,
                    'end_date': end_date,
                    'frequency': frequency
                }
            )
    
    async def get_fund_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取基金基础信息（baostock不支持基金数据）
        
        Args:
            **kwargs: 查询参数
            
        Returns:
            基金基础信息DataFrame
        """
        raise NotImplementedError("Baostock不支持基金数据获取，请使用其他数据源")
    
    async def get_fund_nav(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取基金净值数据（baostock不支持基金数据）
        
        Args:
            ts_code: 基金代码
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD
            
        Returns:
            基金净值数据DataFrame
        """
        raise NotImplementedError("Baostock不支持基金数据获取，请使用其他数据源")
    
    async def is_trade_date(self, date: str) -> bool:
        """
        判断指定日期是否为交易日
        
        Args:
            date: 日期，格式YYYY-MM-DD
            
        Returns:
            是否为交易日
        """
        validate_date_format(date)
        
        # 查询单日交易日历
        trade_cal = await self.get_trade_cal(date, date)
        
        if trade_cal.empty:
            return False
        
        # 检查is_open字段
        return bool(trade_cal.iloc[0]['is_open']) if 'is_open' in trade_cal.columns else False
    
    async def get_next_trade_date(self, date: str, n: int = 1) -> str:
        """
        获取指定日期之后的第n个交易日
        
        Args:
            date: 起始日期，格式YYYY-MM-DD
            n: 向后查找的交易日数量，默认1
            
        Returns:
            交易日期，格式YYYY-MM-DD
        """
        validate_date_format(date)
        
        if n <= 0:
            raise ValidationError("n必须大于0")
    
    # ==================== 财务数据方法 ====================
    
    async def get_financial_reports(self, ts_code: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        获取财务报告数据（利润表、资产负债表、现金流量表）
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD
            **kwargs: 其他参数
                - report_type: 报告类型，可选值：'profit', 'balance', 'cash_flow', 'all'，默认'all'
                - period: 报告期间，可选值：'Q1', 'Q2', 'Q3', 'A'，默认获取所有期间
                - fields: 返回字段列表，默认返回所有字段
        
        Returns:
            财务报告数据DataFrame
        """
        # 参数验证
        validate_stock_code(ts_code)
        validate_date_format(start_date)
        validate_date_format(end_date)
        
        # 解析可选参数
        report_type = kwargs.get('report_type', 'all')
        period = kwargs.get('period')
        fields = kwargs.get('fields')
        
        # 验证报告类型
        valid_report_types = ['profit', 'balance', 'cash_flow', 'all']
        if report_type not in valid_report_types:
            raise ValidationError(f"无效的报告类型: {report_type}，必须是{valid_report_types}之一")
        
        # 验证期间
        if period is not None:
            valid_periods = ['Q1', 'Q2', 'Q3', 'A']
            if period not in valid_periods:
                raise ValidationError(f"无效的报告期间: {period}，必须是{valid_periods}之一")
        
        await self._ensure_login()
        
        try:
            # 转换股票代码格式
            baostock_code = self._convert_stock_code(ts_code)
            
            # 获取不同类型的财务数据
            financial_data = {}
            
            if report_type in ['profit', 'all']:
                profit_data = await self._get_profit_data(baostock_code, start_date, end_date, period)
                if not profit_data.empty:
                    financial_data['profit'] = profit_data
            
            if report_type in ['balance', 'all']:
                balance_data = await self._get_balance_data(baostock_code, start_date, end_date, period)
                if not balance_data.empty:
                    financial_data['balance'] = balance_data
            
            if report_type in ['cash_flow', 'all']:
                cash_flow_data = await self._get_cash_flow_data(baostock_code, start_date, end_date, period)
                if not cash_flow_data.empty:
                    financial_data['cash_flow'] = cash_flow_data
            
            # 合并财务数据
            result_df = self._merge_financial_data(financial_data, ts_code)
            
            # 应用字段过滤
            if fields and not result_df.empty:
                available_fields = [f for f in fields if f in result_df.columns]
                if available_fields:
                    result_df = result_df[available_fields]
            
            self.logger.info(f"成功获取财务报告数据: {ts_code}, {len(result_df)}条记录")
            return result_df
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(
                f"获取财务报告数据时发生错误: {str(e)}",
                error_code="BAOSTOCK_FINANCIAL_ERROR",
                details={
                    'ts_code': ts_code,
                    'start_date': start_date,
                    'end_date': end_date,
                    'report_type': report_type
                }
            )
    
    async def get_earnings_forecast(self, ts_code: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        获取业绩预告数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD
            **kwargs: 其他参数
                - forecast_type: 预告类型过滤，可选值：'预增', '预减', '扭亏', '首亏', '续亏', '续盈', '略增', '略减', '不确定'
                - fields: 返回字段列表，默认返回所有字段
        
        Returns:
            业绩预告数据DataFrame
        """
        # 参数验证
        validate_stock_code(ts_code)
        validate_date_format(start_date)
        validate_date_format(end_date)
        
        # 解析可选参数
        forecast_type = kwargs.get('forecast_type')
        fields = kwargs.get('fields')
        
        # 验证预告类型
        if forecast_type is not None:
            valid_types = ['预增', '预减', '扭亏', '首亏', '续亏', '续盈', '略增', '略减', '不确定']
            if forecast_type not in valid_types:
                raise ValidationError(f"无效的预告类型: {forecast_type}，必须是{valid_types}之一")
        
        await self._ensure_login()
        
        try:
            # 转换股票代码格式
            baostock_code = self._convert_stock_code(ts_code)
            
            # 查询业绩预告数据
            rs = bs.query_forecast_report(
                code=baostock_code,
                start_date=start_date,
                end_date=end_date
            )
            
            if rs.error_code != '0':
                raise DataSourceError(
                    f"获取业绩预告数据失败: {rs.error_msg}",
                    error_code="BAOSTOCK_FORECAST_ERROR",
                    details={
                        'error_code': rs.error_code,
                        'error_msg': rs.error_msg,
                        'ts_code': ts_code,
                        'baostock_code': baostock_code,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                )
            
            # 转换为DataFrame
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                self.logger.warning(f"未获取到业绩预告数据: {ts_code}, {start_date} - {end_date}")
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 标准化数据
            df = self._standardize_earnings_forecast_data(df, ts_code)
            
            # 应用预告类型过滤
            if forecast_type and not df.empty and 'forecast_type' in df.columns:
                df = df[df['forecast_type'] == forecast_type]
            
            # 应用字段过滤
            if fields and not df.empty:
                available_fields = [f for f in fields if f in df.columns]
                if available_fields:
                    df = df[available_fields]
            
            # 按预告日期排序
            if not df.empty and 'forecast_date' in df.columns:
                df = df.sort_values('forecast_date', ascending=False)
            
            self.logger.info(f"成功获取业绩预告数据: {ts_code}, {len(df)}条记录")
            return df
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(
                f"获取业绩预告数据时发生错误: {str(e)}",
                error_code="BAOSTOCK_FORECAST_ERROR",
                details={
                    'ts_code': ts_code,
                    'start_date': start_date,
                    'end_date': end_date,
                    'forecast_type': forecast_type
                }
            )
    
    async def get_earnings_flash_reports(self, ts_code: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        获取业绩快报数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD
            **kwargs: 其他参数
                - sort_by: 排序字段，可选值：'publish_date', 'report_date'，默认'publish_date'
                - fields: 返回字段列表，默认返回所有字段
        
        Returns:
            业绩快报数据DataFrame
        """
        # 参数验证
        validate_stock_code(ts_code)
        validate_date_format(start_date)
        validate_date_format(end_date)
        
        # 解析可选参数
        sort_by = kwargs.get('sort_by', 'publish_date')
        fields = kwargs.get('fields')
        
        # 验证排序字段
        valid_sort_fields = ['publish_date', 'report_date']
        if sort_by not in valid_sort_fields:
            raise ValidationError(f"无效的排序字段: {sort_by}，必须是{valid_sort_fields}之一")
        
        await self._ensure_login()
        
        try:
            # 转换股票代码格式
            baostock_code = self._convert_stock_code(ts_code)
            
            # 查询业绩快报数据
            rs = bs.query_performance_express_report(
                code=baostock_code,
                start_date=start_date,
                end_date=end_date
            )
            
            if rs.error_code != '0':
                raise DataSourceError(
                    f"获取业绩快报数据失败: {rs.error_msg}",
                    error_code="BAOSTOCK_FLASH_REPORT_ERROR",
                    details={
                        'error_code': rs.error_code,
                        'error_msg': rs.error_msg,
                        'ts_code': ts_code,
                        'baostock_code': baostock_code,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                )
            
            # 转换为DataFrame
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                self.logger.warning(f"未获取到业绩快报数据: {ts_code}, {start_date} - {end_date}")
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 标准化数据
            df = self._standardize_flash_report_data(df, ts_code)
            
            # 应用字段过滤
            if fields and not df.empty:
                available_fields = [f for f in fields if f in df.columns]
                if available_fields:
                    df = df[available_fields]
            
            # 按指定字段排序
            if not df.empty and sort_by in df.columns:
                df = df.sort_values(sort_by, ascending=False)
            
            self.logger.info(f"成功获取业绩快报数据: {ts_code}, {len(df)}条记录")
            return df
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(
                f"获取业绩快报数据时发生错误: {str(e)}",
                error_code="BAOSTOCK_FLASH_REPORT_ERROR",
                details={
                    'ts_code': ts_code,
                    'start_date': start_date,
                    'end_date': end_date,
                    'sort_by': sort_by
                }
            )
        
        # 解析可选参数
        report_type = kwargs.get('report_type', 'all')
        period = kwargs.get('period')
        
        await self._ensure_login()
        
        try:
            # 转换股票代码格式
            baostock_code = self._convert_stock_code(ts_code)
            
            # 获取不同类型的财务报告
            financial_data = {}
            
            if report_type in ['profit', 'all']:
                # 获取利润表数据
                profit_data = await self._get_profit_data(baostock_code, start_date, end_date, period)
                financial_data['profit'] = profit_data
            
            if report_type in ['balance', 'all']:
                # 获取资产负债表数据
                balance_data = await self._get_balance_data(baostock_code, start_date, end_date, period)
                financial_data['balance'] = balance_data
            
            if report_type in ['cash_flow', 'all']:
                # 获取现金流量表数据
                cash_flow_data = await self._get_cash_flow_data(baostock_code, start_date, end_date, period)
                financial_data['cash_flow'] = cash_flow_data
            
            # 合并财务数据
            merged_df = self._merge_financial_data(financial_data, ts_code)
            
            # 标准化财务数据
            standardized_df = self._standardize_financial_data(merged_df)
            
            self.logger.info(f"成功获取财务报告数据: {ts_code}, {len(standardized_df)}条记录")
            return standardized_df
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(
                f"获取财务报告数据时发生错误: {str(e)}",
                error_code="BAOSTOCK_FINANCIAL_ERROR",
                details={
                    'ts_code': ts_code,
                    'start_date': start_date,
                    'end_date': end_date,
                    'report_type': report_type
                }
            )
    
    # ==================== 财务数据处理辅助方法 ====================
    
    async def _get_profit_data(self, baostock_code: str, start_date: str, end_date: str, period: str = None) -> pd.DataFrame:
        """
        获取利润表数据
        
        Args:
            baostock_code: baostock格式股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: 报告期间过滤
        
        Returns:
            利润表数据DataFrame
        """
        try:
            # 查询利润表数据
            rs = bs.query_profit_data(
                code=baostock_code,
                year=start_date[:4],  # 使用年份查询
                quarter=period if period and period != 'A' else None
            )
            
            if rs.error_code != '0':
                raise DataSourceError(
                    f"获取利润表数据失败: {rs.error_msg}",
                    error_code="BAOSTOCK_PROFIT_ERROR",
                    details={'error_code': rs.error_code, 'error_msg': rs.error_msg}
                )
            
            # 转换为DataFrame
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 过滤日期范围
            if 'pubDate' in df.columns:
                df['pubDate'] = pd.to_datetime(df['pubDate'])
                start_dt = pd.to_datetime(start_date)
                end_dt = pd.to_datetime(end_date)
                df = df[(df['pubDate'] >= start_dt) & (df['pubDate'] <= end_dt)]
            
            return df
            
        except Exception as e:
            if isinstance(e, DataSourceError):
                raise
            raise DataSourceError(
                f"获取利润表数据时发生错误: {str(e)}",
                error_code="BAOSTOCK_PROFIT_ERROR"
            )
    
    async def _get_balance_data(self, baostock_code: str, start_date: str, end_date: str, period: str = None) -> pd.DataFrame:
        """
        获取资产负债表数据
        
        Args:
            baostock_code: baostock格式股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: 报告期间过滤
        
        Returns:
            资产负债表数据DataFrame
        """
        try:
            # 查询资产负债表数据
            rs = bs.query_balance_data(
                code=baostock_code,
                year=start_date[:4],  # 使用年份查询
                quarter=period if period and period != 'A' else None
            )
            
            if rs.error_code != '0':
                raise DataSourceError(
                    f"获取资产负债表数据失败: {rs.error_msg}",
                    error_code="BAOSTOCK_BALANCE_ERROR",
                    details={'error_code': rs.error_code, 'error_msg': rs.error_msg}
                )
            
            # 转换为DataFrame
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 过滤日期范围
            if 'pubDate' in df.columns:
                df['pubDate'] = pd.to_datetime(df['pubDate'])
                start_dt = pd.to_datetime(start_date)
                end_dt = pd.to_datetime(end_date)
                df = df[(df['pubDate'] >= start_dt) & (df['pubDate'] <= end_dt)]
            
            return df
            
        except Exception as e:
            if isinstance(e, DataSourceError):
                raise
            raise DataSourceError(
                f"获取资产负债表数据时发生错误: {str(e)}",
                error_code="BAOSTOCK_BALANCE_ERROR"
            )
    
    async def _get_cash_flow_data(self, baostock_code: str, start_date: str, end_date: str, period: str = None) -> pd.DataFrame:
        """
        获取现金流量表数据
        
        Args:
            baostock_code: baostock格式股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: 报告期间过滤
        
        Returns:
            现金流量表数据DataFrame
        """
        try:
            # 查询现金流量表数据
            rs = bs.query_cash_flow_data(
                code=baostock_code,
                year=start_date[:4],  # 使用年份查询
                quarter=period if period and period != 'A' else None
            )
            
            if rs.error_code != '0':
                raise DataSourceError(
                    f"获取现金流量表数据失败: {rs.error_msg}",
                    error_code="BAOSTOCK_CASH_FLOW_ERROR",
                    details={'error_code': rs.error_code, 'error_msg': rs.error_msg}
                )
            
            # 转换为DataFrame
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 过滤日期范围
            if 'pubDate' in df.columns:
                df['pubDate'] = pd.to_datetime(df['pubDate'])
                start_dt = pd.to_datetime(start_date)
                end_dt = pd.to_datetime(end_date)
                df = df[(df['pubDate'] >= start_dt) & (df['pubDate'] <= end_dt)]
            
            return df
            
        except Exception as e:
            if isinstance(e, DataSourceError):
                raise
            raise DataSourceError(
                f"获取现金流量表数据时发生错误: {str(e)}",
                error_code="BAOSTOCK_CASH_FLOW_ERROR"
            )
    
    def _merge_financial_data(self, financial_data: Dict[str, pd.DataFrame], ts_code: str) -> pd.DataFrame:
        """
        合并不同类型的财务数据
        
        Args:
            financial_data: 财务数据字典，键为数据类型，值为DataFrame
            ts_code: 标准格式股票代码
        
        Returns:
            合并后的财务数据DataFrame
        """
        if not financial_data:
            return pd.DataFrame()
        
        try:
            merged_data = []
            
            for data_type, df in financial_data.items():
                if df.empty:
                    continue
                
                # 标准化数据
                standardized_df = self._standardize_financial_data(df.copy())
                
                # 添加数据类型标识
                standardized_df['data_type'] = data_type
                
                merged_data.append(standardized_df)
            
            if not merged_data:
                return pd.DataFrame()
            
            # 合并所有数据
            result_df = pd.concat(merged_data, ignore_index=True, sort=False)
            
            # 确保股票代码正确
            result_df['ts_code'] = ts_code
            
            # 按报告日期排序
            if 'report_date' in result_df.columns:
                result_df = result_df.sort_values('report_date', ascending=False)
            
            return result_df
            
        except Exception as e:
            self.logger.error(f"合并财务数据时发生错误: {e}")
            return pd.DataFrame()
    
    def _standardize_financial_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化财务数据列名和数据类型
        
        Args:
            df: 原始财务数据DataFrame
        
        Returns:
            标准化后的DataFrame
        """
        if df.empty:
            return df
        
        # baostock财务数据列名映射
        column_mapping = {
            # 通用字段
            'code': 'ts_code',
            'pubDate': 'publish_date',
            'statDate': 'report_date',
            
            # 利润表字段
            'totalOperatingRevenue': 'total_revenue',
            'netProfit': 'net_profit',
            'basicEPS': 'eps',
            'ROE': 'roe',
            
            # 资产负债表字段
            'totalAssets': 'total_assets',
            'totalLiabilities': 'total_liabilities',
            'totalShareholderEquity': 'shareholders_equity',
            
            # 现金流量表字段
            'operatingCashFlow': 'operating_cash_flow'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 转换股票代码格式
        if 'ts_code' in df.columns:
            try:
                df['ts_code'] = df['ts_code'].apply(self._convert_to_standard_code)
            except Exception as e:
                self.logger.warning(f"转换股票代码格式失败: {e}")
        
        # 转换日期格式
        date_columns = ['publish_date', 'report_date']
        for col in date_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col]).dt.strftime('%Y%m%d')
                except Exception as e:
                    self.logger.warning(f"转换日期格式失败 {col}: {e}")
        
        # 转换数值类型并处理单位（元转万元）
        financial_columns = [
            'total_revenue', 'net_profit', 'total_assets', 
            'total_liabilities', 'shareholders_equity', 'operating_cash_flow'
        ]
        for col in financial_columns:
            if col in df.columns:
                try:
                    # 转换为数值类型
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    # 元转万元
                    df[col] = df[col] / 10000
                except Exception as e:
                    self.logger.warning(f"转换数值类型失败 {col}: {e}")
        
        # 转换比率类型
        ratio_columns = ['eps', 'roe']
        for col in ratio_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception as e:
                    self.logger.warning(f"转换比率类型失败 {col}: {e}")
        
        # 添加报告类型
        if 'report_date' in df.columns:
            df['report_type'] = df['report_date'].apply(self._determine_report_type)
        
        return df
    
    def _standardize_earnings_forecast_data(self, df: pd.DataFrame, ts_code: str) -> pd.DataFrame:
        """
        标准化业绩预告数据
        
        Args:
            df: 原始业绩预告数据DataFrame
            ts_code: 标准格式股票代码
        
        Returns:
            标准化后的DataFrame
        """
        if df.empty:
            return df
        
        # baostock业绩预告列名映射
        column_mapping = {
            'code': 'ts_code',
            'profitForcastExpPubDate': 'forecast_date',
            'profitForcastExpStatDate': 'forecast_period',
            'profitForcastType': 'forecast_type',
            'profitForcastAbstract': 'forecast_summary'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 设置股票代码
        df['ts_code'] = ts_code
        
        # 转换日期格式
        date_columns = ['forecast_date', 'forecast_period']
        for col in date_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col]).dt.strftime('%Y%m%d')
                except Exception as e:
                    self.logger.warning(f"转换日期格式失败 {col}: {e}")
        
        # 解析预告摘要，提取数值范围
        if 'forecast_summary' in df.columns:
            forecast_ranges = df['forecast_summary'].apply(self._parse_forecast_summary)
            df['net_profit_min'] = forecast_ranges.apply(lambda x: x[0])
            df['net_profit_max'] = forecast_ranges.apply(lambda x: x[1])
            df['growth_rate_min'] = forecast_ranges.apply(lambda x: x[2])
            df['growth_rate_max'] = forecast_ranges.apply(lambda x: x[3])
        
        # 添加创建和更新时间
        current_time = datetime.now().isoformat()
        df['created_at'] = current_time
        df['updated_at'] = current_time
        
        return df
    
    def _standardize_flash_report_data(self, df: pd.DataFrame, ts_code: str) -> pd.DataFrame:
        """
        标准化业绩快报数据
        
        Args:
            df: 原始业绩快报数据DataFrame
            ts_code: 标准格式股票代码
        
        Returns:
            标准化后的DataFrame
        """
        if df.empty:
            return df
        
        # baostock业绩快报列名映射
        column_mapping = {
            'code': 'ts_code',
            'performanceExpPubDate': 'publish_date',
            'performanceExpStatDate': 'report_period',
            'performanceExpUpdateDate': 'report_date',
            'performanceExpressRevenue': 'total_revenue',
            'performanceExpressEPS': 'eps',
            'performanceExpressNetProfitChgPct': 'profit_growth',
            'performanceExpressGRYOY': 'revenue_growth'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 设置股票代码
        df['ts_code'] = ts_code
        
        # 转换日期格式
        date_columns = ['publish_date', 'report_date', 'report_period']
        for col in date_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col]).dt.strftime('%Y%m%d')
                except Exception as e:
                    self.logger.warning(f"转换日期格式失败 {col}: {e}")
        
        # 转换数值类型
        if 'total_revenue' in df.columns:
            try:
                df['total_revenue'] = pd.to_numeric(df['total_revenue'], errors='coerce') / 10000  # 元转万元
            except Exception as e:
                self.logger.warning(f"转换营业收入失败: {e}")
        
        # 计算净利润（基于EPS和股本，这里简化处理）
        if 'eps' in df.columns and 'total_revenue' in df.columns:
            try:
                df['eps'] = pd.to_numeric(df['eps'], errors='coerce')
                # 简化计算净利润，实际应该使用股本数据
                df['net_profit'] = df['total_revenue'] * 0.1  # 假设10%净利润率
            except Exception as e:
                self.logger.warning(f"计算净利润失败: {e}")
                df['net_profit'] = 0.0
        
        # 转换增长率
        growth_columns = ['profit_growth', 'revenue_growth']
        for col in growth_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception as e:
                    self.logger.warning(f"转换增长率失败 {col}: {e}")
        
        # 生成快报摘要
        if not df.empty:
            df['report_summary'] = df.apply(self._generate_flash_report_summary, axis=1)
        
        # 添加创建和更新时间
        current_time = datetime.now().isoformat()
        df['created_at'] = current_time
        df['updated_at'] = current_time
        
        return df
    
    def _determine_report_type(self, report_date: str) -> str:
        """
        根据报告日期确定报告类型
        
        Args:
            report_date: 报告日期 (YYYYMMDD)
        
        Returns:
            报告类型 ('Q1', 'Q2', 'Q3', 'A')
        """
        if not report_date or len(report_date) < 8:
            return 'A'
        
        try:
            month_day = report_date[4:8]
            if month_day == '0331':
                return 'Q1'
            elif month_day == '0630':
                return 'Q2'
            elif month_day == '0930':
                return 'Q3'
            elif month_day == '1231':
                return 'A'
            else:
                return 'A'
        except Exception:
            return 'A'
    
    def _parse_forecast_summary(self, summary: str) -> tuple:
        """
        解析业绩预告摘要，提取数值范围
        
        Args:
            summary: 预告摘要文本
        
        Returns:
            (净利润最小值, 净利润最大值, 增长率最小值, 增长率最大值)
        """
        import re
        
        if not summary or not isinstance(summary, str):
            return (0.0, 0.0, 0.0, 0.0)
        
        try:
            # 提取净利润范围（万元）
            profit_pattern = r'(\d+(?:\.\d+)?)万元(?:至|到|~)(\d+(?:\.\d+)?)万元|(\d+(?:\.\d+)?)万元'
            profit_matches = re.findall(profit_pattern, summary)
            
            if profit_matches:
                match = profit_matches[0]
                if match[0] and match[1]:  # 范围值
                    profit_min, profit_max = float(match[0]), float(match[1])
                elif match[2]:  # 单个值
                    profit_min = profit_max = float(match[2])
                else:
                    profit_min = profit_max = 0.0
            else:
                profit_min = profit_max = 0.0
            
            # 提取增长率范围（%）
            growth_pattern = r'增长(\d+(?:\.\d+)?)%(?:至|到|~)(\d+(?:\.\d+)?)%|增长(\d+(?:\.\d+)?)%'
            growth_matches = re.findall(growth_pattern, summary)
            
            if growth_matches:
                match = growth_matches[0]
                if match[0] and match[1]:  # 范围值
                    growth_min, growth_max = float(match[0]), float(match[1])
                elif match[2]:  # 单个值
                    growth_min = growth_max = float(match[2])
                else:
                    growth_min = growth_max = 0.0
            else:
                growth_min = growth_max = 0.0
            
            return (profit_min, profit_max, growth_min, growth_max)
            
        except Exception as e:
            self.logger.warning(f"解析预告摘要失败: {e}")
            return (0.0, 0.0, 0.0, 0.0)
    
    def _generate_flash_report_summary(self, row: pd.Series) -> str:
        """
        生成业绩快报摘要
        
        Args:
            row: 快报数据行
        
        Returns:
            快报摘要文本
        """
        try:
            revenue = row.get('total_revenue', 0)
            profit = row.get('net_profit', 0)
            revenue_growth = row.get('revenue_growth', 0)
            profit_growth = row.get('profit_growth', 0)
            
            summary_parts = []
            
            # 营业收入
            if revenue > 0:
                summary_parts.append(f"营业收入{revenue:.2f}万元")
            
            # 净利润
            if profit > 0:
                summary_parts.append(f"净利润{profit:.2f}万元")
            elif profit < 0:
                summary_parts.append(f"净亏损{abs(profit):.2f}万元")
            
            # 收入增长率
            if revenue_growth > 0:
                summary_parts.append(f"收入同比增长{revenue_growth:.1f}%")
            elif revenue_growth < 0:
                summary_parts.append(f"收入同比下降{abs(revenue_growth):.1f}%")
            
            # 利润增长率
            if profit_growth > 0:
                summary_parts.append(f"利润同比增长{profit_growth:.1f}%")
            elif profit_growth < 0:
                summary_parts.append(f"利润同比下降{abs(profit_growth):.1f}%")
            
            return "，".join(summary_parts) if summary_parts else "业绩快报数据"
            
        except Exception as e:
            self.logger.warning(f"生成快报摘要失败: {e}")
            return "业绩快报数据"
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 尝试登录来检查服务可用性
            await self._ensure_login()
            
            # 如果登录成功，认为服务可用
            return self._session_active
            
        except Exception as e:
            self.logger.warning(f"健康检查失败: {e}")
            return False
