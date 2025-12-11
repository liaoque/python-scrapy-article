"""
数据格式化器

负责将不同数据源的数据格式化为统一的标准格式
"""

from typing import TYPE_CHECKING, Dict, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import logging

if TYPE_CHECKING:
    from ..config import Config

logger = logging.getLogger(__name__)


class DataFormatter:
    """数据格式化器"""
    
    def __init__(self, config: 'Config'):
        """
        初始化数据格式化器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.date_format = getattr(config, 'date_format', '%Y%m%d')
        self.float_precision = getattr(config, 'float_precision', 4)
        
        # 数据源列名映射
        self._column_mappings = self._init_column_mappings()
    
    def _init_column_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        初始化不同数据源的列名映射
        
        Returns:
            列名映射字典
        """
        return {
            'baostock': {
                # 股票基础信息映射
                'code': 'ts_code',
                'tradeStatus': 'status',
                'codeType': 'market',
                # OHLCV数据映射
                'date': 'trade_date',
                'preclose': 'pre_close',
                'pctChg': 'pct_chg',
                'turn': 'turnover_rate',
                'tradestatus': 'trade_status',
                'peTTM': 'pe_ttm',
                'pbMRQ': 'pb',
                'psTTM': 'ps_ttm',
                'pcfNcfTTM': 'pcf_ncf_ttm',
                'isST': 'is_st'
            },
            'eastmoney': {
                # 东方财富数据映射
                'f43': 'close',
                'f44': 'high', 
                'f45': 'low',
                'f46': 'open',
                'f47': 'volume',
                'f48': 'amount',
                'f49': 'turnover_rate',
                'f50': 'volume_ratio',
                'f51': 'pe',
                'f52': 'pb'
            },
            'tonghuashun': {
                # 同花顺数据映射
                'price': 'close',
                'pricechange': 'change',
                'changepercent': 'pct_chg'
            }
        }

    async def format_data(self, data: pd.DataFrame, data_type: str, source: str = None) -> pd.DataFrame:
        """
        根据数据类型格式化数据
        
        Args:
            data: 原始数据
            data_type: 数据类型
            source: 数据源名称
            
        Returns:
            格式化后的数据
        """
        if data.empty:
            return data
        
        try:
            logger.debug(f"格式化数据: type={data_type}, source={source}, shape={data.shape}")
            
            # 根据数据类型选择格式化方法
            if data_type == 'stock_basic':
                return self.format_stock_basic(data, source or 'unknown')
            elif data_type in ['stock_daily', 'stock_minute']:
                return self.format_stock_ohlcv(data, source or 'unknown')
            elif data_type == 'index_basic':
                return self.format_index_basic(data, source or 'unknown')
            elif data_type == 'index_daily':
                return self.format_index_ohlcv(data, source or 'unknown')
            elif data_type == 'fund_basic':
                return self.format_fund_basic(data, source or 'unknown')
            elif data_type == 'fund_nav':
                return self.format_fund_nav(data, source or 'unknown')
            elif data_type == 'trade_cal':
                return self.format_trade_cal(data, source or 'unknown')
            else:
                # 对于未知类型，进行基本的数据清理
                logger.warning(f"未知数据类型: {data_type}, 使用基本格式化")
                return self._basic_format(data)
                
        except Exception as e:
            logger.error(f"数据格式化失败: {e}")
            # 返回基本格式化的数据，避免完全失败
            return self._basic_format(data)
    
    def format_stock_basic(self, data: pd.DataFrame, source: str) -> pd.DataFrame:
        """
        格式化股票基础信息数据
        
        Args:
            data: 原始数据
            source: 数据源名称
            
        Returns:
            格式化后的数据
        """
        from ..models import STOCK_BASIC_COLUMNS
        
        # 基本数据清理
        formatted_data = self._basic_format(data.copy())
        
        # 标准化列名（这里简化处理，实际应该根据不同数据源进行映射）
        return self._ensure_columns(formatted_data, STOCK_BASIC_COLUMNS)
    
    def format_stock_ohlcv(self, data: pd.DataFrame, source: str) -> pd.DataFrame:
        """
        格式化股票OHLCV数据（日线、分钟线等）
        
        Args:
            data: 原始数据
            source: 数据源名称
            
        Returns:
            格式化后的数据
        """
        from ..models import OHLCV_COLUMNS
        
        # 基本数据清理
        formatted_data = self._basic_format(data.copy())
        
        # 应用数据源特定的列名映射
        formatted_data = self._apply_column_mapping(formatted_data, source)
        
        # 标准化日期格式
        formatted_data = self._standardize_dates(formatted_data, ['trade_date', 'date'])
        
        # 标准化数值格式
        formatted_data = self._standardize_numeric_columns(formatted_data, 
                                                         ['open', 'high', 'low', 'close', 'volume', 'amount'])
        
        # 确保列存在并设置正确类型
        return self._ensure_columns(formatted_data, OHLCV_COLUMNS)
    
    def format_index_basic(self, data: pd.DataFrame, source: str) -> pd.DataFrame:
        """
        格式化指数基础信息数据
        
        Args:
            data: 原始数据
            source: 数据源名称
            
        Returns:
            格式化后的数据
        """
        from ..models import INDEX_BASIC_COLUMNS
        
        # 基本数据清理
        formatted_data = self._basic_format(data.copy())
        
        # 应用数据源特定的列名映射
        formatted_data = self._apply_column_mapping(formatted_data, source)
        
        # 标准化日期格式
        formatted_data = self._standardize_dates(formatted_data, ['base_date', 'list_date'])
        
        # 确保列存在并设置正确类型
        return self._ensure_columns(formatted_data, INDEX_BASIC_COLUMNS)
    
    def format_index_ohlcv(self, data: pd.DataFrame, source: str) -> pd.DataFrame:
        """
        格式化指数OHLCV数据
        
        Args:
            data: 原始数据
            source: 数据源名称
            
        Returns:
            格式化后的数据
        """
        from ..models import OHLCV_COLUMNS
        
        # 基本数据清理
        formatted_data = self._basic_format(data.copy())
        
        # 应用数据源特定的列名映射
        formatted_data = self._apply_column_mapping(formatted_data, source)
        
        # 标准化日期格式
        formatted_data = self._standardize_dates(formatted_data, ['trade_date', 'date'])
        
        # 标准化数值格式
        formatted_data = self._standardize_numeric_columns(formatted_data, 
                                                         ['open', 'high', 'low', 'close', 'volume', 'amount'])
        
        # 确保列存在并设置正确类型
        return self._ensure_columns(formatted_data, OHLCV_COLUMNS)
    
    def format_fund_basic(self, data: pd.DataFrame, source: str) -> pd.DataFrame:
        """
        格式化基金基础信息数据
        
        Args:
            data: 原始数据
            source: 数据源名称
            
        Returns:
            格式化后的数据
        """
        from ..models import FUND_BASIC_COLUMNS
        
        # 基本数据清理
        formatted_data = self._basic_format(data.copy())
        
        # 应用数据源特定的列名映射
        formatted_data = self._apply_column_mapping(formatted_data, source)
        
        # 标准化日期格式
        date_columns = ['found_date', 'due_date', 'list_date', 'issue_date', 'delist_date']
        formatted_data = self._standardize_dates(formatted_data, date_columns)
        
        # 标准化数值格式
        formatted_data = self._standardize_numeric_columns(formatted_data, ['issue_amount'])
        
        # 确保列存在并设置正确类型
        return self._ensure_columns(formatted_data, FUND_BASIC_COLUMNS)
    
    def format_fund_nav(self, data: pd.DataFrame, source: str) -> pd.DataFrame:
        """
        格式化基金净值数据
        
        Args:
            data: 原始数据
            source: 数据源名称
            
        Returns:
            格式化后的数据
        """
        # 基金净值数据的标准格式
        fund_nav_columns = {
            'ts_code': str,      # 基金代码
            'ann_date': str,     # 公告日期
            'nav_date': str,     # 净值日期
            'unit_nav': float,   # 单位净值
            'accum_nav': float,  # 累计净值
            'accum_div': float,  # 累计分红
            'net_asset': float,  # 资产净值
            'total_netasset': float  # 合计资产净值
        }
        
        # 基本数据清理
        formatted_data = self._basic_format(data.copy())
        
        # 应用数据源特定的列名映射
        formatted_data = self._apply_column_mapping(formatted_data, source)
        
        # 标准化日期格式
        formatted_data = self._standardize_dates(formatted_data, ['ann_date', 'nav_date'])
        
        # 标准化数值格式
        numeric_columns = ['unit_nav', 'accum_nav', 'accum_div', 'net_asset', 'total_netasset']
        formatted_data = self._standardize_numeric_columns(formatted_data, numeric_columns)
        
        # 确保列存在并设置正确类型
        return self._ensure_columns(formatted_data, fund_nav_columns)
    
    def format_trade_cal(self, data: pd.DataFrame, source: str) -> pd.DataFrame:
        """
        格式化交易日历数据
        
        Args:
            data: 原始数据
            source: 数据源名称
            
        Returns:
            格式化后的数据
        """
        from ..models import TRADE_CAL_COLUMNS
        
        # 基本数据清理
        formatted_data = self._basic_format(data.copy())
        
        # 标准化列名
        return self._ensure_columns(formatted_data, TRADE_CAL_COLUMNS)
    
    def _basic_format(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        基本数据格式化
        
        Args:
            data: 原始数据
            
        Returns:
            格式化后的数据
        """
        if data.empty:
            return data
        
        # 创建副本避免修改原数据
        formatted_data = data.copy()
        
        # 去除重复行
        formatted_data = formatted_data.drop_duplicates()
        
        # 重置索引
        formatted_data = formatted_data.reset_index(drop=True)
        
        # 处理列名：去除空格，转换为小写
        formatted_data.columns = formatted_data.columns.str.strip().str.lower()
        
        # 处理字符串列的空值和编码问题
        for col in formatted_data.select_dtypes(include=['object']).columns:
            # 处理空值
            formatted_data.loc[:, col] = formatted_data[col].fillna('')
            # 处理编码问题
            formatted_data.loc[:, col] = formatted_data[col].astype(str).str.strip()
        
        # 处理数值列的空值
        for col in formatted_data.select_dtypes(include=[np.number]).columns:
            # 将无穷大值替换为NaN
            formatted_data.loc[:, col] = formatted_data[col].replace([np.inf, -np.inf], np.nan)
        
        return formatted_data
    
    def _ensure_columns(self, data: pd.DataFrame, column_spec: dict) -> pd.DataFrame:
        """
        确保数据包含指定的列并设置正确的数据类型
        
        Args:
            data: 原始数据
            column_spec: 列规范字典
            
        Returns:
            格式化后的数据
        """
        # 只保留存在的列
        existing_columns = [col for col in column_spec.keys() if col in data.columns]
        
        if existing_columns:
            data = data[existing_columns]
            
            # 设置数据类型
            for col in existing_columns:
                expected_type = column_spec[col]
                try:
                    if expected_type == str:
                        data.loc[:, col] = data[col].astype(str)
                    elif expected_type == float:
                        data.loc[:, col] = pd.to_numeric(data[col], errors='coerce')
                    elif expected_type == int:
                        data.loc[:, col] = pd.to_numeric(data[col], errors='coerce').astype('Int64')
                except Exception:
                    # 如果转换失败，保持原始类型
                    pass
        
        return data
    
    def _standardize_columns(self, data: pd.DataFrame, column_mapping: dict) -> pd.DataFrame:
        """
        标准化列名
        
        Args:
            data: 原始数据
            column_mapping: 列名映射字典
            
        Returns:
            标准化后的数据
        """
        # 重命名列
        data = data.rename(columns=column_mapping)
        return data
    
    def _apply_column_mapping(self, data: pd.DataFrame, source: str) -> pd.DataFrame:
        """
        应用数据源特定的列名映射
        
        Args:
            data: 原始数据
            source: 数据源名称
            
        Returns:
            映射后的数据
        """
        if source not in self._column_mappings:
            return data
        
        mapping = self._column_mappings[source]
        
        # 只映射存在的列
        existing_mapping = {old_col: new_col for old_col, new_col in mapping.items() 
                           if old_col in data.columns}
        
        if existing_mapping:
            data = data.rename(columns=existing_mapping)
            logger.debug(f"应用列名映射 {source}: {existing_mapping}")
        
        return data
    
    def _standardize_dates(self, data: pd.DataFrame, date_columns: list) -> pd.DataFrame:
        """
        标准化日期格式
        
        Args:
            data: 原始数据
            date_columns: 日期列名列表
            
        Returns:
            标准化后的数据
        """
        for col in date_columns:
            if col in data.columns:
                try:
                    # 尝试转换为标准日期格式
                    data.loc[:, col] = self._convert_date_format(data[col])
                except Exception as e:
                    logger.warning(f"日期格式转换失败 {col}: {e}")
        
        return data
    
    def _convert_date_format(self, date_series: pd.Series) -> pd.Series:
        """
        转换日期格式为标准格式
        
        Args:
            date_series: 日期序列
            
        Returns:
            标准化后的日期序列
        """
        def convert_single_date(date_val):
            if pd.isna(date_val) or date_val == '' or date_val is None:
                return ''
            
            date_str = str(date_val).strip()
            if not date_str:
                return ''
            
            try:
                # 尝试不同的日期格式
                formats = ['%Y%m%d', '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d']
                
                for fmt in formats:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.strftime(self.date_format)
                    except ValueError:
                        continue
                
                # 如果都失败了，尝试pandas的日期解析
                dt = pd.to_datetime(date_str)
                return dt.strftime(self.date_format)
                
            except Exception:
                # 如果转换失败，返回原值
                return date_str
        
        return date_series.apply(convert_single_date)
    
    def _standardize_numeric_columns(self, data: pd.DataFrame, numeric_columns: list) -> pd.DataFrame:
        """
        标准化数值列格式
        
        Args:
            data: 原始数据
            numeric_columns: 数值列名列表
            
        Returns:
            标准化后的数据
        """
        for col in numeric_columns:
            if col in data.columns:
                try:
                    # 转换为数值类型
                    data.loc[:, col] = pd.to_numeric(data[col], errors='coerce')
                    
                    # 应用精度设置
                    if data[col].dtype == 'float64':
                        data.loc[:, col] = data[col].round(self.float_precision)
                        
                except Exception as e:
                    logger.warning(f"数值格式转换失败 {col}: {e}")
        
        return data
    
    def _standardize_data_types(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        标准化数据类型
        
        Args:
            data: 原始数据
            
        Returns:
            标准化后的数据
        """
        # 自动推断并优化数据类型
        for col in data.columns:
            try:
                # 对于字符串列，尝试转换为分类类型以节省内存
                if data[col].dtype == 'object':
                    unique_ratio = data[col].nunique() / len(data)
                    if unique_ratio < 0.5:  # 如果唯一值比例小于50%，转换为分类类型
                        data.loc[:, col] = data[col].astype('category')
                
                # 对于整数列，尝试使用更小的数据类型
                elif data[col].dtype in ['int64', 'int32']:
                    if data[col].min() >= 0:
                        if data[col].max() <= 255:
                            data.loc[:, col] = data[col].astype('uint8')
                        elif data[col].max() <= 65535:
                            data.loc[:, col] = data[col].astype('uint16')
                        elif data[col].max() <= 4294967295:
                            data.loc[:, col] = data[col].astype('uint32')
                    else:
                        if data[col].min() >= -128 and data[col].max() <= 127:
                            data.loc[:, col] = data[col].astype('int8')
                        elif data[col].min() >= -32768 and data[col].max() <= 32767:
                            data.loc[:, col] = data[col].astype('int16')
                        elif data[col].min() >= -2147483648 and data[col].max() <= 2147483647:
                            data.loc[:, col] = data[col].astype('int32')
                            
            except Exception as e:
                logger.debug(f"数据类型优化失败 {col}: {e}")
        
        return data
    
    def format_data_sync(self, data: pd.DataFrame, data_type: str, source: str = None) -> pd.DataFrame:
        """
        同步版本的数据格式化方法
        
        Args:
            data: 原始数据
            data_type: 数据类型
            source: 数据源名称
            
        Returns:
            格式化后的数据
        """
        if data.empty:
            return data
        
        try:
            logger.debug(f"同步格式化数据: type={data_type}, source={source}, shape={data.shape}")
            
            # 根据数据类型选择格式化方法
            if data_type == 'stock_basic':
                return self.format_stock_basic(data, source or 'unknown')
            elif data_type in ['stock_daily', 'stock_minute']:
                return self.format_stock_ohlcv(data, source or 'unknown')
            elif data_type == 'index_basic':
                return self.format_index_basic(data, source or 'unknown')
            elif data_type == 'index_daily':
                return self.format_index_ohlcv(data, source or 'unknown')
            elif data_type == 'fund_basic':
                return self.format_fund_basic(data, source or 'unknown')
            elif data_type == 'fund_nav':
                return self.format_fund_nav(data, source or 'unknown')
            elif data_type == 'trade_cal':
                return self.format_trade_cal(data, source or 'unknown')
            else:
                # 对于未知类型，进行基本的数据清理
                logger.warning(f"未知数据类型: {data_type}, 使用基本格式化")
                return self._basic_format(data)
                
        except Exception as e:
            logger.error(f"同步数据格式化失败: {e}")
            # 返回基本格式化的数据，避免完全失败
            return self._basic_format(data)