# QuickStock SDK

一个简洁易用的金融数据SDK，用于获取股票、指数和基金数据。默认使用Baostock作为数据源，提供同步和异步两种API接口。

## 特点

- **简单易用**：提供简洁的API接口，无需复杂配置
- **功能全面**：支持股票、指数、基金等多种金融数据
- **双接口支持**：同时提供同步和异步API接口
- **完善的错误处理**：提供清晰的错误分类和异常处理机制
- **可扩展**：支持多种数据源的扩展

## 安装

### PyPI安装

```bash
# 通过PyPI安装（推荐）
pip install quickstock

# 安装开发依赖
pip install quickstock[dev]
```

### 源码安装

```bash
# 克隆仓库
git clone <仓库地址>

# 进入项目目录
cd quick_stock_sdk

# 安装依赖
pip install -r requirements.txt
```

### 依赖

- pandas
- requests
- aiohttp
- python-dateutil
- baostock (默认数据源)

## 目录结构

```
quick_stock_sdk/
├── quickstock/              # SDK核心代码
│   ├── __init__.py         # 模块入口
│   ├── client.py           # 客户端类
│   ├── errors.py           # 错误类定义
│   └── sources/            # 数据源模块
│       ├── __init__.py     # 数据源入口
│       ├── base.py         # 数据源抽象基类
│       └── baostock.py     # Baostock数据源实现
├── example.py              # 使用示例
├── test_quickstock.py      # 测试文件
└── README.md               # 项目说明
```

## 快速开始

### 导入模块

```python
from quickstock import QuickStockClient
from quickstock.errors import (QuickStockError, DataSourceError, ValidationError)
```

### 初始化客户端

```python
# 创建客户端实例
client = QuickStockClient()
```

### 获取股票数据

#### 1. 获取股票基础信息

```python
# 同步方式
df_stock_basic = client.stock_basic()
print(df_stock_basic.head())

# 异步方式（需要在异步函数中使用）
async def get_stock_basic():
    df = await client.astock_basic()
    print(df.head())
```

#### 2. 获取股票日线数据

```python
# 同步方式
df_stock_daily = client.stock_daily(
    code="sh.600000",        # 股票代码
    start_date="2024-01-01",    # 开始日期
    end_date="2024-01-31"        # 结束日期
)
print(df_stock_daily.head())

# 异步方式
async def get_stock_daily():
    df = await client.astock_daily(
        code="sh.600000",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
    print(df.head())
```

#### 3. 获取股票分钟线数据

```python
# 同步方式
df_stock_minute = client.stock_minute(
    code="sh.600000",
    start_date="2024-01-01",
    end_date="2024-01-02"
)
print(df_stock_minute.head())

# 异步方式
async def get_stock_minute():
    df = await client.astock_minute(
        code="sh.600000",
        start_date="2024-01-01",
        end_date="2024-01-02"
    )
    print(df.head())
```

### 获取指数数据

#### 1. 获取指数基础信息

```python
# 同步方式
df_index_basic = client.index_basic()
print(df_index_basic.head())

# 异步方式
async def get_index_basic():
    df = await client.aindex_basic()
    print(df.head())
```

#### 2. 获取指数日线数据

```python
# 同步方式
df_index_daily = client.index_daily(
    code="sh.000001",        # 上证指数
    start_date="2024-01-01",
    end_date="2024-01-31"
)
print(df_index_daily.head())

# 异步方式
async def get_index_daily():
    df = await client.aindex_daily(
        code="sh.000001",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
    print(df.head())
```

### 获取基金数据

#### 1. 获取基金基础信息

```python
# 同步方式
df_fund_basic = client.fund_basic()
print(df_fund_basic.head())

# 异步方式
async def get_fund_basic():
    df = await client.afund_basic()
    print(df.head())
```

#### 2. 获取基金日线数据

```python
# 同步方式
df_fund_daily = client.fund_daily(
    code="f.150001",         # 基金代码
    start_date="2024-01-01",
    end_date="2024-01-31"
)
print(df_fund_daily.head())

# 异步方式
async def get_fund_daily():
    df = await client.afund_daily(
        code="f.150001",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
    print(df.head())
```

## 错误处理

```python
from quickstock import QuickStockClient
from quickstock.errors import (ValidationError, DataSourceError, NetworkError)

client = QuickStockClient()

# 处理参数验证错误
try:
    client.stock_daily(code="")  # 空股票代码
except ValidationError as e:
    print(f"参数错误: {e}")

# 处理网络错误
try:
    client.stock_basic()
except NetworkError as e:
    print(f"网络错误: {e}")

# 处理数据源错误
try:
    client.stock_daily(ts_code="sh.600000")
except DataSourceError as e:
    print(f"数据源错误: {e}")
```

## 支持的数据类型

### 股票数据
- 基础信息
- 日线数据
- 分钟线数据
- 周线数据
- 月线数据

### 指数数据
- 基础信息
- 日线数据
- 分钟线数据

### 基金数据
- 基础信息
- 日线数据

## API参考

### 客户端类

#### QuickStockClient

`QuickStockClient()`

创建SDK客户端实例，默认使用Baostock数据源。

### 股票数据API

#### 基础信息
- `stock_basic(**kwargs) -> pd.DataFrame` - 同步获取股票基础信息
- `astock_basic(**kwargs) -> pd.DataFrame` - 异步获取股票基础信息

#### 日线数据
- `stock_daily(code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取股票日线数据
- `astock_daily(code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取股票日线数据

#### 分钟线数据
- `stock_minute(code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取股票分钟线数据
- `astock_minute(code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取股票分钟线数据

#### 周线数据
- `stock_weekly(code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取股票周线数据
- `astock_weekly(code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取股票周线数据

#### 月线数据
- `stock_monthly(code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取股票月线数据
- `astock_monthly(code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取股票月线数据

### 指数数据API

#### 基础信息
- `index_basic(**kwargs) -> pd.DataFrame` - 同步获取指数基础信息
- `aindex_basic(**kwargs) -> pd.DataFrame` - 异步获取指数基础信息

#### 日线数据
- `index_daily(code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取指数日线数据
- `aindex_daily(code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取指数日线数据

#### 分钟线数据
- `index_minute(code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取指数分钟线数据
- `aindex_minute(code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取指数分钟线数据

### 基金数据API

#### 基础信息
- `fund_basic(**kwargs) -> pd.DataFrame` - 同步获取基金基础信息
- `afund_basic(**kwargs) -> pd.DataFrame` - 异步获取基金基础信息

#### 日线数据
- `fund_daily(code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取基金日线数据
- `afund_daily(code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取基金日线数据

### 错误类

- `QuickStockError` - 基础异常类
- `DataSourceError` - 数据源异常类
  - `AuthenticationError` - 认证异常
  - `NetworkError` - 网络异常
  - `DataNotFoundError` - 数据未找到异常
- `ValidationError` - 参数验证异常

## 测试

运行测试脚本：

```bash
python test_quickstock.py
```

运行示例脚本：

```bash
python example.py
```

## 扩展数据源

要添加新的数据源，需要继承`BaseSource`类并实现所有抽象方法：

```python
from quickstock.sources.base import BaseSource

class NewDataSource(BaseSource):
    def __init__(self, name="new_source"):
        super().__init__(name)
    
    async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
        # 实现获取股票基础信息的逻辑
        pass
    
    # 实现其他抽象方法...
```

然后在客户端中使用新的数据源：

```python
from quickstock import QuickStockClient
from new_source import NewDataSource

client = QuickStockClient()
client.new_source = NewDataSource()

# 使用新数据源获取数据
df = client.new_source.get_stock_basic()
```

## 版本历史

- v1.0.0 (2024-01-01)
  - 初始版本
  - 支持股票、指数、基金数据
  - 提供同步和异步API
  - 默认使用Baostock数据源

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，请通过以下方式联系：

- Email: [your-email@example.com]
- GitHub: [your-github-repo]
