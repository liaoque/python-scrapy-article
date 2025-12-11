"""
参数验证器

提供各种参数验证函数和装饰器
"""

import re
import functools
from datetime import datetime, date
from typing import Any, Callable, List, Optional, Union, Dict
import pandas as pd
import numpy as np
import logging

from ..core.errors import ValidationError

logger = logging.getLogger(__name__)


def validate_stock_code(code: str) -> bool:
    """
    验证股票代码格式（支持多种数据源格式）
    
    Args:
        code: 股票代码
        
    Returns:
        是否为有效的股票代码
    """
    if not code or not isinstance(code, str):
        return False
    
    code = code.strip()
    
    # 支持的股票代码格式
    patterns = [
        r'^[0-9]{6}$',                    # 6位数字代码 (如: 000001)
        r'^[0-9]{6}\.(SH|SZ)$',           # 标准格式 (如: 000001.SZ)
        r'^(SH|SZ)[0-9]{6}$',             # 交易所前缀 (如: SZ000001)
        r'^(sh|sz)\.[0-9]{6}$',           # Baostock格式 (如: sh.600000)
        r'^[01]\.[0-9]{6}$',              # 东方财富格式 (如: 1.600000)
        r'^hs_[0-9]{6}$',                 # 同花顺格式 (如: hs_600000)
    ]
    
    for pattern in patterns:
        if re.match(pattern, code, re.IGNORECASE):
            return True
    
    return False


def validate_stock_code_strict(code: str) -> bool:
    """
    严格验证股票代码格式（抛出异常版本）
    
    Args:
        code: 股票代码
        
    Returns:
        是否为有效的股票代码
        
    Raises:
        ValidationError: 股票代码格式无效
    """
    if not code or not isinstance(code, str):
        raise ValidationError("股票代码不能为空且必须为字符串")
    
    if not validate_stock_code(code):
        raise ValidationError(f"无效的股票代码格式: {code}")
    
    return True


def validate_date_format(date_str: str, allow_empty: bool = False) -> bool:
    """
    验证日期格式
    
    Args:
        date_str: 日期字符串
        allow_empty: 是否允许空值
        
    Returns:
        是否为有效的日期格式
        
    Raises:
        ValidationError: 日期格式无效
    """
    if not date_str:
        if allow_empty:
            return True
        else:
            raise ValidationError("日期不能为空")
    
    if not isinstance(date_str, str):
        raise ValidationError("日期必须为字符串格式")
    
    date_str = date_str.strip()
    
    # 支持的日期格式
    formats = [
        ('%Y%m%d', r'^\d{8}$'),           # YYYYMMDD
        ('%Y-%m-%d', r'^\d{4}-\d{2}-\d{2}$'),  # YYYY-MM-DD
        ('%Y/%m/%d', r'^\d{4}/\d{2}/\d{2}$'),  # YYYY/MM/DD
        ('%Y.%m.%d', r'^\d{4}\.\d{2}\.\d{2}$') # YYYY.MM.DD
    ]
    
    for date_format, pattern in formats:
        if re.match(pattern, date_str):
            try:
                datetime.strptime(date_str, date_format)
                return True
            except ValueError:
                continue
    
    raise ValidationError(f"无效的日期格式: {date_str}")


def validate_date_range(start_date: str, end_date: str, allow_empty: bool = False) -> bool:
    """
    验证日期范围
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        allow_empty: 是否允许空值
        
    Returns:
        日期范围是否有效
        
    Raises:
        ValidationError: 日期范围无效
    """
    # 验证单个日期格式
    if start_date:
        validate_date_format(start_date, allow_empty)
    if end_date:
        validate_date_format(end_date, allow_empty)
    
    # 如果两个日期都存在，验证范围
    if start_date and end_date:
        # 标准化日期格式进行比较
        start_normalized = _normalize_date(start_date)
        end_normalized = _normalize_date(end_date)
        
        if start_normalized > end_normalized:
            raise ValidationError(f"开始日期不能大于结束日期: {start_date} > {end_date}")
    
    return True


def validate_frequency(freq: str) -> bool:
    """
    验证数据频率
    
    Args:
        freq: 频率字符串
        
    Returns:
        频率是否有效
        
    Raises:
        ValidationError: 频率无效
    """
    if not freq or not isinstance(freq, str):
        raise ValidationError("频率不能为空且必须为字符串")
    
    valid_frequencies = [
        '1min', '5min', '15min', '30min', '60min',  # 分钟级
        '1d', 'daily',                              # 日级
        '1w', 'weekly',                             # 周级
        '1m', 'monthly'                             # 月级
    ]
    
    if freq.lower() not in [f.lower() for f in valid_frequencies]:
        raise ValidationError(f"不支持的频率: {freq}, 支持的频率: {valid_frequencies}")
    
    return True


def validate_numeric_range(value: Union[int, float], min_val: Optional[float] = None, 
                          max_val: Optional[float] = None, field_name: str = "数值") -> bool:
    """
    验证数值范围
    
    Args:
        value: 数值
        min_val: 最小值
        max_val: 最大值
        field_name: 字段名称
        
    Returns:
        数值是否在有效范围内
        
    Raises:
        ValidationError: 数值超出范围
    """
    if not isinstance(value, (int, float)):
        raise ValidationError(f"{field_name}必须为数值类型")
    
    if pd.isna(value) or np.isinf(value):
        raise ValidationError(f"{field_name}不能为NaN或无穷大")
    
    if min_val is not None and value < min_val:
        raise ValidationError(f"{field_name}不能小于{min_val}: {value}")
    
    if max_val is not None and value > max_val:
        raise ValidationError(f"{field_name}不能大于{max_val}: {value}")
    
    return True


def validate_list_length(lst: List[Any], min_length: int = 0, max_length: Optional[int] = None,
                        field_name: str = "列表") -> bool:
    """
    验证列表长度
    
    Args:
        lst: 列表
        min_length: 最小长度
        max_length: 最大长度
        field_name: 字段名称
        
    Returns:
        列表长度是否有效
        
    Raises:
        ValidationError: 列表长度无效
    """
    if not isinstance(lst, list):
        raise ValidationError(f"{field_name}必须为列表类型")
    
    length = len(lst)
    
    if length < min_length:
        raise ValidationError(f"{field_name}长度不能小于{min_length}: {length}")
    
    if max_length is not None and length > max_length:
        raise ValidationError(f"{field_name}长度不能大于{max_length}: {length}")
    
    return True


def validate_fields(fields: Optional[List[str]], valid_fields: List[str]) -> bool:
    """
    验证字段列表
    
    Args:
        fields: 请求的字段列表
        valid_fields: 有效字段列表
        
    Returns:
        字段是否有效
        
    Raises:
        ValidationError: 字段无效
    """
    if fields is None:
        return True
    
    if not isinstance(fields, list):
        raise ValidationError("字段列表必须为列表类型")
    
    invalid_fields = [field for field in fields if field not in valid_fields]
    if invalid_fields:
        raise ValidationError(f"无效的字段: {invalid_fields}, 有效字段: {valid_fields}")
    
    return True


def _normalize_date(date_str: str) -> str:
    """
    标准化日期格式为YYYYMMDD
    
    Args:
        date_str: 日期字符串
        
    Returns:
        标准化后的日期字符串
    """
    formats = [
        '%Y%m%d', '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d'
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime('%Y%m%d')
        except ValueError:
            continue
    
    raise ValidationError(f"无法解析日期格式: {date_str}")


# 装饰器函数

def validate_params(**validators) -> Callable:
    """
    参数验证装饰器
    
    Args:
        **validators: 参数验证器字典
        
    Returns:
        装饰器函数
        
    Example:
        @validate_params(
            ts_code=validate_stock_code,
            start_date=lambda x: validate_date_format(x, allow_empty=True)
        )
        def get_stock_data(ts_code: str, start_date: str = None):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取函数参数名
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # 验证参数
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    param_value = bound_args.arguments[param_name]
                    try:
                        if callable(validator):
                            validator(param_value)
                        else:
                            # 如果validator是字典，包含验证函数和参数
                            if isinstance(validator, dict):
                                validate_func = validator['func']
                                validate_args = validator.get('args', [])
                                validate_kwargs = validator.get('kwargs', {})
                                validate_func(param_value, *validate_args, **validate_kwargs)
                    except ValidationError as e:
                        raise ValidationError(f"参数 {param_name} 验证失败: {e}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_data_request(data_type: str, ts_code: Optional[str] = None,
                         start_date: Optional[str] = None, end_date: Optional[str] = None,
                         freq: Optional[str] = None, fields: Optional[List[str]] = None,
                         **extra_params) -> bool:
    """
    验证数据请求参数
    
    Args:
        data_type: 数据类型
        ts_code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        freq: 频率
        fields: 字段列表
        **extra_params: 额外参数
        
    Returns:
        参数是否有效
        
    Raises:
        ValidationError: 参数验证失败
    """
    # 验证数据类型
    valid_data_types = [
        'stock_basic', 'stock_daily', 'stock_minute',
        'index_basic', 'index_daily',
        'fund_basic', 'fund_nav',
        'trade_cal'
    ]
    
    if data_type not in valid_data_types:
        raise ValidationError(f"不支持的数据类型: {data_type}, 支持的类型: {valid_data_types}")
    
    # 验证股票代码（如果提供）
    if ts_code:
        validate_stock_code_strict(ts_code)
    
    # 验证日期范围
    if start_date or end_date:
        validate_date_range(start_date or '', end_date or '', allow_empty=True)
    
    # 验证频率
    if freq:
        validate_frequency(freq)
    
    # 验证字段列表（这里简化处理，实际应该根据数据类型验证）
    if fields:
        validate_list_length(fields, min_length=1, max_length=50, field_name="字段列表")
    
    return True


# 常用验证器组合

class StockDataValidator:
    """股票数据验证器"""
    
    @staticmethod
    def validate_basic_request(**kwargs) -> bool:
        """验证股票基础信息请求"""
        return validate_data_request('stock_basic', **kwargs)
    
    @staticmethod
    def validate_daily_request(ts_code: str, **kwargs) -> bool:
        """验证股票日线数据请求"""
        validate_stock_code_strict(ts_code)
        return validate_data_request('stock_daily', ts_code=ts_code, **kwargs)
    
    @staticmethod
    def validate_minute_request(ts_code: str, freq: str = '1min', **kwargs) -> bool:
        """验证股票分钟数据请求"""
        validate_stock_code_strict(ts_code)
        validate_frequency(freq)
        return validate_data_request('stock_minute', ts_code=ts_code, freq=freq, **kwargs)


class IndexDataValidator:
    """指数数据验证器"""
    
    @staticmethod
    def validate_basic_request(**kwargs) -> bool:
        """验证指数基础信息请求"""
        return validate_data_request('index_basic', **kwargs)
    
    @staticmethod
    def validate_daily_request(ts_code: str, **kwargs) -> bool:
        """验证指数日线数据请求"""
        # 指数代码格式可能与股票不同，这里简化处理
        return validate_data_request('index_daily', ts_code=ts_code, **kwargs)


class FundDataValidator:
    """基金数据验证器"""
    
    @staticmethod
    def validate_basic_request(**kwargs) -> bool:
        """验证基金基础信息请求"""
        return validate_data_request('fund_basic', **kwargs)
    
    @staticmethod
    def validate_nav_request(ts_code: str, **kwargs) -> bool:
        """验证基金净值数据请求"""
        return validate_data_request('fund_nav', ts_code=ts_code, **kwargs)


class TradeCalValidator:
    """交易日历验证器"""
    
    @staticmethod
    def validate_request(start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> bool:
        """验证交易日历请求"""
        return validate_data_request('trade_cal', start_date=start_date, end_date=end_date, **kwargs)