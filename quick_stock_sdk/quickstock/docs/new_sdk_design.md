# QuickStock SDK 简化设计方案

## 1. 设计理念

本设计方案基于用户反馈，采用**极简设计原则**：
- **硬编码数据源**：直接在内部写死使用Baostock作为唯一数据源，避免复杂的数据源切换机制
- **单一职责**：每个模块只做一件事，保持代码简洁易读
- **清晰API**：提供直观、一致的接口，降低使用门槛
- **模块化设计**：逻辑分层清晰，便于维护和扩展

## 2. 核心架构

### 2.1 目录结构

```
quickstock/
├── __init__.py          # 包初始化，导出主要类和函数
├── client.py            # 核心客户端类，提供统一API
├── baostock_source.py   # Baostock数据源实现
├── errors.py            # 自定义异常类
└── utils.py             # 工具函数
```

### 2.2 模块职责

| 模块 | 主要职责 |
|------|---------|
| client.py | 提供统一的用户接口，直接使用Baostock数据源 |
| baostock_source.py | 封装Baostock API调用，处理登录/登出和数据获取 |
| errors.py | 定义自定义异常类，统一错误处理 |
| utils.py | 工具函数（如股票代码标准化、日期处理等） |

## 3. 核心实现

### 3.1 错误处理模块 (errors.py)

```python
# 基础异常类
class QuickStockError(Exception):
    """QuickStock SDK基础异常"""
    pass

# 数据源相关异常
class DataSourceError(QuickStockError):
    """数据源异常"""
    pass

class AuthenticationError(DataSourceError):
    """认证失败异常"""
    pass

class DataNotFoundError(DataSourceError):
    """数据未找到异常"""
    pass

class APIError(DataSourceError):
    """API调用失败异常"""
    pass

# 参数验证异常
class ValidationError(QuickStockError):
    """参数验证异常"""
    pass
```

### 3.2 工具函数模块 (utils.py)

```python
import re
from datetime import datetime

def normalize_stock_code(code):
    """
    标准化股票代码
    :param code: 股票代码（如：600000, sh600000, sz.000001）
    :return: 标准化后的代码（如：sh.600000, sz.000001）
    """
    code = str(code).strip()
    
    # 匹配已包含交易所前缀的代码
    match = re.match(r'^(sh|sz)[\.|_]?([0-9]{6})$', code, re.IGNORECASE)
    if match:
        exchange = match.group(1).lower()
        stock_code = match.group(2)
        return f"{exchange}.{stock_code}"
    
    # 仅数字代码
    if re.match(r'^[0-9]{6}$', code):
        # 根据代码判断交易所
        if code.startswith(('00', '30')):
            return f"sz.{code}"  # 深圳
        elif code.startswith(('60', '50', '51')):
            return f"sh.{code}"  # 上海
    
    raise ValidationError(f"无效的股票代码: {code}")

def format_date(date_str):
    """
    格式化日期为YYYY-MM-DD格式
    :param date_str: 日期字符串
    :return: 格式化后的日期字符串
    """
    if not date_str:
        return None
    
    try:
        # 尝试解析各种日期格式
        if isinstance(date_str, datetime):
            return date_str.strftime("%Y-%m-%d")
        
        # 支持的格式：YYYYMMDD, YYYY-MM-DD, YYYY/MM/DD
        for fmt in ['%Y%m%d', '%Y-%m-%d', '%Y/%m/%d']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        raise ValidationError(f"无效的日期格式: {date_str}")
    except Exception as e:
        raise ValidationError(f"日期处理错误: {e}")
```

### 3.3 Baostock数据源实现 (baostock_source.py)

```python
import baostock as bs
import pandas as pd
from .errors import AuthenticationError, APIError, DataNotFoundError
from .utils import format_date

class BaostockSource:
    """
    Baostock数据源实现类
    封装Baostock API调用，处理登录/登出和数据获取
    """
    
    def __init__(self):
        """初始化数据源"""
        self._is_logged_in = False
        self._login()
    
    def _login(self):
        """登录Baostock系统"""
        try:
            lg = bs.login()
            if lg.error_code != '0':
                raise AuthenticationError(f"登录失败: {lg.error_msg}")
            self._is_logged_in = True
        except Exception as e:
            raise AuthenticationError(f"登录异常: {e}")
    
    def _ensure_login(self):
        """确保已登录，如果未登录则重新登录"""
        if not self._is_logged_in:
            self._login()
    
    def _check_result(self, result):
        """检查API调用结果"""
        if result.error_code != '0':
            if result.error_code == '10001':
                raise DataNotFoundError(f"数据未找到: {result.error_msg}")
            raise APIError(f"API调用失败: {result.error_msg}")
    
    def stock_daily(self, code, start_date=None, end_date=None, adjust="none"):
        """
        获取股票日K线数据
        :param code: 股票代码
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param adjust: 复权类型 (none: 不复权, front: 前复权, back: 后复权)
        :return: 日K线数据 (DataFrame)
        """
        self._ensure_login()
        
        adjust_map = {
            "none": "3",
            "front": "2",
            "back": "1"
        }
        
        fields = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST"
        
        try:
            result = bs.query_history_k_data_plus(
                code=code,
                fields=fields,
                start_date=format_date(start_date),
                end_date=format_date(end_date),
                frequency="d",
                adjustflag=adjust_map[adjust]
            )
            
            self._check_result(result)
            
            # 处理结果
            data_list = []
            while result.next():
                data_list.append(result.get_row_data())
            
            df = pd.DataFrame(data_list, columns=result.fields)
            return df
        except KeyError:
            raise ValueError(f"无效的复权类型: {adjust}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, APIError, DataNotFoundError)):
                raise
            raise APIError(f"获取日K线数据失败: {e}")
    
    def stock_weekly(self, code, start_date=None, end_date=None, adjust="none"):
        """
        获取股票周K线数据
        """
        self._ensure_login()
        
        adjust_map = {
            "none": "3",
            "front": "2",
            "back": "1"
        }
        
        fields = "date,code,open,high,low,close,volume,amount,adjustflag,turn,tradestatus,pctChg"
        
        try:
            result = bs.query_history_k_data_plus(
                code=code,
                fields=fields,
                start_date=format_date(start_date),
                end_date=format_date(end_date),
                frequency="w",
                adjustflag=adjust_map[adjust]
            )
            
            self._check_result(result)
            
            data_list = []
            while result.next():
                data_list.append(result.get_row_data())
            
            df = pd.DataFrame(data_list, columns=result.fields)
            return df
        except KeyError:
            raise ValueError(f"无效的复权类型: {adjust}")
        except Exception as e:
            if isinstance(e, (AuthenticationError, APIError, DataNotFoundError)):
                raise
            raise APIError(f"获取周K线数据失败: {e}")
    
    def stock_basic(self, date=None):
        """
        获取所有股票基本信息
        :param date: 指定日期，默认当前日期
        :return: 股票基本信息 (DataFrame)
        """
        self._ensure_login()
        
        try:
            result = bs.query_all_stock(date=format_date(date))
            self._check_result(result)
            
            data_list = []
            while result.next():
                data_list.append(result.get_row_data())
            
            df = pd.DataFrame(data_list, columns=result.fields)
            return df
        except Exception as e:
            if isinstance(e, (AuthenticationError, APIError, DataNotFoundError)):
                raise
            raise APIError(f"获取股票基本信息失败: {e}")
    
    def index_daily(self, code, start_date=None, end_date=None):
        """
        获取指数日K线数据
        """
        self._ensure_login()
        
        fields = "date,code,open,high,low,close,volume,amount,pctChg"
        
        try:
            result = bs.query_history_k_data_plus(
                code=code,
                fields=fields,
                start_date=format_date(start_date),
                end_date=format_date(end_date),
                frequency="d",
                adjustflag="3"  # 指数不提供复权数据
            )
            
            self._check_result(result)
            
            data_list = []
            while result.next():
                data_list.append(result.get_row_data())
            
            df = pd.DataFrame(data_list, columns=result.fields)
            return df
        except Exception as e:
            if isinstance(e, (AuthenticationError, APIError, DataNotFoundError)):
                raise
            raise APIError(f"获取指数日K线数据失败: {e}")
    
    def sz50_stocks(self):
        """
        获取上证50成分股
        """
        self._ensure_login()
        
        try:
            result = bs.query_sz50_stocks()
            self._check_result(result)
            
            data_list = []
            while result.next():
                data_list.append(result.get_row_data())
            
            df = pd.DataFrame(data_list, columns=result.fields)
            return df
        except Exception as e:
            if isinstance(e, (AuthenticationError, APIError, DataNotFoundError)):
                raise
            raise APIError(f"获取上证50成分股失败: {e}")
    
    def hs300_stocks(self):
        """
        获取沪深300成分股
        """
        self._ensure_login()
        
        try:
            result = bs.query_hs300_stocks()
            self._check_result(result)
            
            data_list = []
            while result.next():
                data_list.append(result.get_row_data())
            
            df = pd.DataFrame(data_list, columns=result.fields)
            return df
        except Exception as e:
            if isinstance(e, (AuthenticationError, APIError, DataNotFoundError)):
                raise
            raise APIError(f"获取沪深300成分股失败: {e}")
    
    def zz500_stocks(self):
        """
        获取中证500成分股
        """
        self._ensure_login()
        
        try:
            result = bs.query_zz500_stocks()
            self._check_result(result)
            
            data_list = []
            while result.next():
                data_list.append(result.get_row_data())
            
            df = pd.DataFrame(data_list, columns=result.fields)
            return df
        except Exception as e:
            if isinstance(e, (AuthenticationError, APIError, DataNotFoundError)):
                raise
            raise APIError(f"获取中证500成分股失败: {e}")
    
    def __del__(self):
        """析构函数，自动登出"""
        if self._is_logged_in:
            try:
                bs.logout()
            except Exception:
                pass  # 忽略登出错误
```

### 3.4 核心客户端 (client.py)

```python
from .baostock_source import BaostockSource
from .utils import normalize_stock_code
from .errors import QuickStockError

class QuickStockClient:
    """
    QuickStock SDK核心客户端类
    提供统一的API接口，直接使用Baostock作为数据源
    """
    
    def __init__(self):
        """初始化客户端，创建Baostock数据源实例"""
        self._source = BaostockSource()  # 直接硬编码使用Baostock数据源
    
    def stock_daily(self, code, start_date=None, end_date=None, adjust="none"):
        """
        获取股票日K线数据
        :param code: 股票代码
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param adjust: 复权类型 (none: 不复权, front: 前复权, back: 后复权)
        :return: 日K线数据 (DataFrame)
        """
        normalized_code = normalize_stock_code(code)
        return self._source.stock_daily(normalized_code, start_date, end_date, adjust)
    
    def stock_weekly(self, code, start_date=None, end_date=None, adjust="none"):
        """
        获取股票周K线数据
        """
        normalized_code = normalize_stock_code(code)
        return self._source.stock_weekly(normalized_code, start_date, end_date, adjust)
    
    def stock_basic(self, date=None):
        """
        获取所有股票基本信息
        """
        return self._source.stock_basic(date)
    
    def index_daily(self, code, start_date=None, end_date=None):
        """
        获取指数日K线数据
        """
        normalized_code = normalize_stock_code(code)
        return self._source.index_daily(normalized_code, start_date, end_date)
    
    def sz50_stocks(self):
        """
        获取上证50成分股
        """
        return self._source.sz50_stocks()
    
    def hs300_stocks(self):
        """
        获取沪深300成分股
        """
        return self._source.hs300_stocks()
    
    def zz500_stocks(self):
        """
        获取中证500成分股
        """
        return self._source.zz500_stocks()
```

### 3.5 包初始化 (__init__.py)

```python
from .client import QuickStockClient
from .errors import (
    QuickStockError,
    DataSourceError,
    AuthenticationError,
    APIError,
    DataNotFoundError,
    ValidationError
)

# 导出主要类和异常
__all__ = [
    'QuickStockClient',
    'QuickStockError',
    'DataSourceError',
    'AuthenticationError',
    'APIError',
    'DataNotFoundError',
    'ValidationError'
]
```

## 4. 使用示例

### 4.1 基本用法

```python
from quickstock import QuickStockClient

# 创建客户端实例
client = QuickStockClient()  # 直接使用Baostock数据源

# 获取股票日K线数据
# 支持多种股票代码格式：600000, sh600000, sz.000001
stock_data = client.stock_daily(
    code="600000",
    start_date="2024-01-01",
    end_date="2024-12-31",
    adjust="front"
)
print(stock_data.head())

# 获取指数数据
index_data = client.index_daily(
    code="sh.000001",  # 上证指数
    start_date="2024-01-01",
    end_date="2024-12-31"
)
print(index_data.head())

# 获取上证50成分股
sz50_stocks = client.sz50_stocks()
print(sz50_stocks.head())
```

### 4.2 错误处理

```python
from quickstock import QuickStockClient, DataNotFoundError, APIError

try:
    client = QuickStockClient()
    # 获取不存在的股票数据
    data = client.stock_daily(code="999999", start_date="2024-01-01")
except DataNotFoundError as e:
    print(f"数据未找到: {e}")
except APIError as e:
    print(f"API调用失败: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

## 5. 未来扩展说明

虽然当前设计直接硬编码使用Baostock作为数据源，但如果未来需要切换到其他数据源（如同花顺、东方财富），可以通过以下方式实现：

1. 创建新的数据源实现类（如`tonghuashun_source.py`）
2. 修改`client.py`中的数据源初始化，将`self._source = BaostockSource()`替换为`self._source = TongHuaShunSource()`

这种方式保持了简单性，同时提供了基本的扩展能力。

## 6. 与现有版本对比

| 特性 | quick_stock | release_config | 新设计 |
|------|-------------|----------------|-------|
| 数据源管理 | 简单直接 | 复杂配置 | 硬编码Baostock，简单高效 |
| API清晰度 | 高 | 中 | 高 |
| 代码复杂度 | 低 | 高 | 低 |
| 可维护性 | 低 | 中 | 高 |
| 错误处理 | 简单 | 复杂 | 清晰统一 |
| 扩展能力 | 低 | 高 | 基础扩展能力 |

## 7. 总结

本设计方案通过硬编码Baostock作为数据源，简化了SDK的架构和实现，同时保持了良好的可维护性和易用性。核心优势包括：

1. **简单直观**：用户可以快速上手，无需复杂配置
2. **易于维护**：代码结构清晰，逻辑分层合理
3. **稳定可靠**：直接使用成熟的Baostock API，减少中间环节
4. **一致API**：提供统一的接口，便于使用和迁移

这种设计符合用户"数据源应该一开始直接在全局创建，取哪个数据源，内部直接写死即可"的要求，避免了过度设计带来的复杂性。