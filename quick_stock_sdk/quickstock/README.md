# QuickStock SDK

一个简洁易用的金融数据SDK，用于获取股票、指数、基金和板块数据。默认使用Baostock作为数据源，同时支持同花顺数据源获取板块数据，提供同步和异步两种API接口。

## 特点

- **简单易用**：提供简洁的API接口，无需复杂配置
- **功能全面**：支持股票、指数、基金、板块等多种金融数据
- **双接口支持**：同时提供同步和异步API接口
- **完善的错误处理**：提供清晰的错误分类和异常处理机制
- **可扩展**：支持多种数据源的扩展
- **多数据源**：集成Baostock和同花顺数据源，满足不同数据需求

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
# 同步方式 - 支持批量获取
df_stock_daily = client.stock_daily(
    codes=["sh.600000", "sz.000001"],  # 股票代码列表
    start_date="2024-01-01",
    end_date="2024-01-31"
)
print(df_stock_daily.head())

# 异步方式
async def get_stock_daily():
    df = await client.astock_daily(
        codes=["sh.600000", "sz.000001"],
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
    print(df.head())
```

#### 3. 获取股票分钟线数据

```python
# 同步方式 - 支持批量获取
df_stock_minute = client.stock_minute(
    codes=["sh.600000", "sz.000001"],
    start_date="2024-01-01",
    end_date="2024-01-02",
    frequency="5"  # 可选: 5/15/30/60 分钟
)
print(df_stock_minute.head())

# 异步方式
async def get_stock_minute():
    df = await client.astock_minute(
        codes=["sh.600000", "sz.000001"],
        start_date="2024-01-01",
        end_date="2024-01-02",
        frequency="5"
    )
    print(df.head())
```

#### 4. 获取股票周线/月线数据

```python
# 同步方式 - 获取周线数据
df_stock_weekly = client.stock_weekly(
    codes=["sh.600000", "sz.000001"],
    start_date="2024-01-01",
    end_date="2024-12-31"
)
print(df_stock_weekly.head())

# 同步方式 - 获取月线数据
df_stock_monthly = client.stock_monthly(
    codes=["sh.600000", "sz.000001"],
    start_date="2024-01-01",
    end_date="2024-12-31"
)
print(df_stock_monthly.head())
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
# 同步方式 - 支持批量获取
df_index_daily = client.index_daily(
    codes=["sh.000001", "sz.399001"],  # 上证指数、深证成指
    start_date="2024-01-01",
    end_date="2024-01-31"
)
print(df_index_daily.head())

# 异步方式
async def get_index_daily():
    df = await client.aindex_daily(
        codes=["sh.000001", "sz.399001"],
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
    print(df.head())
```

#### 3. 获取指数分钟线/周线/月线数据

```python
# 同步方式 - 获取分钟线数据
df_index_minute = client.index_minute(
    codes=["sh.000001", "sz.399001"],
    start_date="2024-01-01",
    end_date="2024-01-02",
    frequency="5"
)

# 同步方式 - 获取周线数据
df_index_weekly = client.index_weekly(
    codes=["sh.000001", "sz.399001"],
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# 同步方式 - 获取月线数据
df_index_monthly = client.index_monthly(
    codes=["sh.000001", "sz.399001"],
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

#### 4. 批量获取说明

当 `codes` 列表中的代码数量超过 100 个时，SDK 会自动分批获取，每批 100 个代码：

```python
# 自动分批处理
all_codes = [f"sh.{600000+i}" for i in range(150)]  # 150个股票代码
df = client.stock_daily(
    codes=all_codes,
    start_date="2024-01-01",
    end_date="2024-01-31"
)
# SDK会自动分成2批（100 + 50）获取数据
```

### 获取板块数据（同花顺数据源）

#### 1. 获取概念板块列表

```python
# 同步方式
df_concepts = client.concept_list()
print(f"共 {len(df_concepts)} 个概念板块")
print(df_concepts.head())

# 异步方式
async def get_concept_list():
    df = await client.aconcept_list()
    print(f"共 {len(df)} 个概念板块")
    print(df.head())
```

#### 2. 获取板块成分股

```python
# 同步方式 - 获取指定概念板块的成分股
concept_code = "885943"  # 人工智能概念
df_stocks = client.concept_stocks(concept_code)
print(f"板块包含 {len(df_stocks)} 只股票")
print(df_stocks.head(10))

# 异步方式
async def get_concept_stocks():
    df = await client.aconcept_stocks("885943")
    print(f"板块包含 {len(df)} 只股票")
    print(df.head(10))
```

#### 3. 获取板块K线数据

```python
# 同步方式 - 获取板块日线数据
board_code = "885943"
df_board_daily = client.board_daily(board_code)
print(f"日线数据行数: {len(df_board_daily)}")
print(df_board_daily.head())

# 同步方式 - 获取板块周线数据
df_board_weekly = client.board_weekly(board_code)
print(f"周线数据行数: {len(df_board_weekly)}")
print(df_board_weekly.head())

# 同步方式 - 获取板块月线数据
df_board_monthly = client.board_monthly(board_code)
print(f"月线数据行数: {len(df_board_monthly)}")
print(df_board_monthly.head())

# 同步方式 - 获取板块分钟线数据（1分钟）
df_board_minute = client.board_minute(board_code)
print(f"分钟线数据行数: {len(df_board_minute)}")
print(df_board_minute.head(10))

# 同步方式 - 获取板块30分钟线数据
df_board_minute30 = client.board_minute30(board_code)
print(f"30分钟线数据行数: {len(df_board_minute30)}")
print(df_board_minute30.head())

# 同步方式 - 获取板块60分钟线数据
df_board_minute60 = client.board_minute60(board_code)
print(f"60分钟线数据行数: {len(df_board_minute60)}")
print(df_board_minute60.head())
```

#### 4. 板块代码格式说明

同花顺数据源支持两种板块代码格式：
- 原始格式：`885943`
- 带前缀格式：`bk_885943`

SDK会自动处理两种格式，无需手动转换。

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
- 周线数据
- 月线数据

### 基金数据
- 基础信息
- 日线数据

### 板块数据（同花顺数据源）
- 概念板块列表
- 板块成分股
- 板块日线数据
- 板块周线数据
- 板块月线数据
- 板块分钟线数据（1分钟、30分钟、60分钟）

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
- `stock_daily(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取股票日线数据（支持批量）
- `astock_daily(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取股票日线数据（支持批量）

#### 分钟线数据
- `stock_minute(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取股票分钟线数据（支持批量）
- `astock_minute(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取股票分钟线数据（支持批量）

#### 周线数据
- `stock_weekly(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取股票周线数据（支持批量）
- `astock_weekly(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取股票周线数据（支持批量）

#### 月线数据
- `stock_monthly(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取股票月线数据（支持批量）
- `astock_monthly(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取股票月线数据（支持批量）

### 指数数据API

#### 基础信息
- `index_basic(**kwargs) -> pd.DataFrame` - 同步获取指数基础信息
- `aindex_basic(**kwargs) -> pd.DataFrame` - 异步获取指数基础信息

#### 日线数据
- `index_daily(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取指数日线数据（支持批量）
- `aindex_daily(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取指数日线数据（支持批量）

#### 分钟线数据
- `index_minute(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取指数分钟线数据（支持批量）
- `aindex_minute(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取指数分钟线数据（支持批量）

#### 周线数据
- `index_weekly(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取指数周线数据（支持批量）
- `aindex_weekly(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取指数周线数据（支持批量）

#### 月线数据
- `index_monthly(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取指数月线数据（支持批量）
- `aindex_monthly(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取指数月线数据（支持批量）

### 基金数据API

#### 基础信息
- `fund_basic(**kwargs) -> pd.DataFrame` - 同步获取基金基础信息
- `afund_basic(**kwargs) -> pd.DataFrame` - 异步获取基金基础信息

#### 日线数据
- `fund_daily(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取基金日线数据（支持批量）
- `afund_daily(codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取基金日线数据（支持批量）

### 板块数据API（同花顺数据源）

#### 概念板块列表
- `concept_list() -> pd.DataFrame` - 同步获取所有概念板块列表
- `aconcept_list() -> pd.DataFrame` - 异步获取所有概念板块列表

#### 板块成分股
- `concept_stocks(concept_code: str) -> pd.DataFrame` - 同步获取指定概念板块的成分股
- `aconcept_stocks(concept_code: str) -> pd.DataFrame` - 异步获取指定概念板块的成分股

#### 板块日线数据
- `board_daily(board_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取板块日线数据
- `aboard_daily(board_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取板块日线数据

#### 板块周线数据
- `board_weekly(board_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取板块周线数据
- `aboard_weekly(board_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取板块周线数据

#### 板块月线数据
- `board_monthly(board_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取板块月线数据
- `aboard_monthly(board_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取板块月线数据

#### 板块分钟线数据（1分钟）
- `board_minute(board_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取板块1分钟线数据
- `aboard_minute(board_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取板块1分钟线数据

#### 板块30分钟线数据
- `board_minute30(board_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取板块30分钟线数据
- `aboard_minute30(board_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取板块30分钟线数据

#### 板块60分钟线数据
- `board_minute60(board_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 同步获取板块60分钟线数据
- `aboard_minute60(board_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame` - 异步获取板块60分钟线数据

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
