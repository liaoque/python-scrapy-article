# 同花顺数据源知识库

## 概述

同花顺数据源（TongHuaShun）是一个用于从同花顺网站获取金融数据的模块，主要专注于**板块数据**的获取，包括概念板块、板块成分股以及各类K线数据。

## 核心功能

### 1. 板块数据获取

#### 概念板块列表
- **方法**: `get_all()`
- **URL**: `https://q.10jqka.com.cn/gn/`
- **返回数据**: 包含所有概念板块的代码、名称和ID
- **数据结构**:
  ```python
  {
      "code": "板块代码",
      "name": "板块名称",
      "cid": "板块ID"
  }
  ```

#### 板块成分股
- **方法**: `get_all_concept_stock(concept)`
- **URL**: `http://q.10jqka.com.cn/gn/detail/field/199112/order/desc/size/1000/page/1/ajax/1/code/{concept}`
- **返回数据**: 指定概念板块的成分股列表
- **数据结构**:
  ```python
  {
      "code": "股票代码",
      "cid": "概念板块ID"
  }
  ```

### 2. K线数据获取

同花顺数据源支持多种时间周期的K线数据：

#### 分钟线数据
- **方法**: `minute(secid)`
- **URL格式**: `https://d.10jqka.com.cn/v4/line/bk_{secid}/61/{year}.js`
- **频率代码**: `61` (1分钟)
- **数据范围**: 当前年份的1分钟K线数据

#### 30分钟线数据
- **方法**: `minute30(secid)`
- **URL格式**: `https://d.10jqka.com.cn/v4/line/bk_{secid}/41/{year}.js`
- **频率代码**: `41` (30分钟)
- **数据范围**: 从2015年到当前年份的30分钟K线数据

#### 60分钟线数据
- **方法**: `minute60(secid)`
- **URL格式**: `https://d.10jqka.com.cn/v4/line/bk_{secid}/51/{year}.js`
- **频率代码**: `51` (60分钟)
- **数据范围**: 从2015年到当前年份的60分钟K线数据

#### 日线数据
- **方法**: `daily(secid)`
- **URL格式**: `https://d.10jqka.com.cn/v4/line/bk_{secid}/01/{year}.js`
- **频率代码**: `01` (日线)
- **数据范围**: 从2015年到当前年份的日线K线数据

#### 周线数据
- **方法**: `weekly(secid)`
- **URL格式**: `https://d.10jqka.com.cn/v4/line/bk_{secid}/11/{year}.js`
- **频率代码**: `11` (周线)
- **数据范围**: 从2015年到当前年份的周线K线数据

#### 月线数据
- **方法**: `monthly(secid)`
- **URL格式**: `https://d.10jqka.com.cn/v4/line/bk_{secid}/21/last.js`
- **频率代码**: `21` (月线)
- **数据范围**: 所有历史的月线K线数据

## 数据结构

### K线数据字段

所有K线数据返回的字段结构统一：

```python
{
    "date_at": "日期时间",
    "start": float,      # 开盘价
    "end": float,        # 收盘价
    "max": float,        # 最高价
    "min": float,        # 最低价
    "count": int,        # 成交量
    "amount": float,     # 成交额
    "amplitude": float,  # 振幅
    "range": float,      # 涨跌幅
    "range_amount": float,  # 涨跌额
    "turnover_rate": float  # 换手率
}
```

### 数据计算

#### computeRange 函数

该函数用于计算涨跌幅、振幅等衍生指标：

```python
def computeRange(d):
    d = pd.DataFrame(d)
    d2 = d.shift()  # 获取前一日数据
    
    # 计算涨跌额
    d['range_amount'] = round(d['end'] - d2['end'], 3)
    
    # 计算涨跌幅
    d['range'] = round(d['range_amount'] / d2['end'], 3)
    
    # 计算振幅
    d['amplitude'] -= round((d['max'] - d2['min']) / d2['end'], 3)
    
    return d
```

## 技术实现

### 1. 请求机制

#### Cookie 验证

同花顺API需要特殊的cookie验证机制，通过 `TongHuaShunId` 类生成：

```python
class TongHuaShunId:
    def __init__(self, t, userAgent):
        # 生成18个参数的数组
        self.n[0] = self.random()  # 随机数
        self.n[1] = int(t)  # 时间戳
        self.n[3] = self.strHash(userAgent)  # 用户代理哈希
        # ... 其他参数
```

**关键参数**:
- `v`: 通过 `TongHuaShunId` 编码生成的验证字符串
- `vvv`: 固定值为 "1"

#### 请求头

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "HOST": "q.10jqka.com.cn",
    "Referer": "d.10jqka.com.cn"
}
```

### 2. 数据解析

#### JSON 数据格式

同花顺返回的数据格式为 JavaScript 格式，需要特殊处理：

```python
# 原始数据格式
html = html[38:-1]  # 去除前38个字符和最后1个字符
data = json.loads(html)  # 解析JSON

# 数据提取
for v in data["data"].split(';'):  # 按分号分割
    x = v.split(',')  # 按逗号分割字段
    # 构造数据字典
```

#### HTML 解析

对于板块列表等HTML页面，使用 lxml 进行解析：

```python
root = etree.fromstring(html, etree.HTMLParser(encoding='utf-8'))
values = root.cssselect('#gnSection')[0].get("value")
```

### 3. 缓存机制

使用类变量实现数据缓存，避免重复请求：

```python
class TongHuaShun:
    _all_trade = {}           # 板块列表缓存
    _all_concept_stock = {}   # 板块成分股缓存
    _all_days = {}            # 日线数据缓存
    _all_weeks = {}           # 周线数据缓存
    _all_months = {}          # 月线数据缓存
    _all_minute = {}          # 分钟线数据缓存
    _all_minute30 = {}        # 30分钟线数据缓存
    _all_minute60 = {}        # 60分钟线数据缓存
```

**使用方式**:
```python
def daily(self, secid):
    if secid in self._all_days:
        return self._all_days[secid]  # 返回缓存数据
    # ... 获取新数据
    self._all_days[secid] = data  # 存入缓存
    return data
```

## API 接口规范

### 频率代码对照表

| 频率 | 代码 | 说明 |
|------|------|------|
| 1分钟 | 61 | 当日分钟线 |
| 5分钟 | 65 | 未实现 |
| 15分钟 | 66 | 未实现 |
| 30分钟 | 41 | 历史数据 |
| 60分钟 | 51 | 历史数据 |
| 日线 | 01 | 历史数据 |
| 周线 | 11 | 历史数据 |
| 月线 | 21 | 历史数据 |

### URL 模式

#### 板块数据
- 板块列表: `https://q.10jqka.com.cn/gn/`
- 板块成分股: `http://q.10jqka.com.cn/gn/detail/field/199112/order/desc/size/1000/page/1/ajax/1/code/{concept}`

#### K线数据
- 基础格式: `https://d.10jqka.com.cn/v4/line/bk_{secid}/{frequency}/{year}.js`
- 最新数据: `https://d.10jqka.com.cn/v4/line/bk_{secid}/{frequency}/last.js`

## 与其他数据源对比

### 同花顺 vs 东方财富

| 特性 | 同花顺 | 东方财富 |
|------|--------|----------|
| 数据类型 | 板块数据为主 | 股票、指数、基金 |
| 分钟线 | 支持1分钟 | 支持1分钟 |
| 历史数据 | 2015年起 | 更长历史 |
| 验证机制 | 复杂Cookie验证 | 简单参数验证 |
| 数据格式 | JavaScript | JSON |

### 同花顺 vs Baostock

| 特性 | 同花顺 | Baostock |
|------|--------|----------|
| 数据类型 | 板块数据 | 股票、指数、基金 |
| 实时性 | 实时 | 延迟 |
| 认证 | Cookie验证 | Token认证 |
| 稳定性 | 中等 | 高 |
| 使用难度 | 较高 | 较低 |

## 使用示例

### 基本使用

```python
from quick_stock.remote.tonghuashun import TongHuaShun

ths = TongHuaShun()

# 获取所有概念板块
concepts = ths.get_all()
print(f"共 {len(concepts)} 个概念板块")

# 获取指定板块的成分股
concept_stocks = ths.get_all_concept_stock("885943")
print(f"板块包含 {len(concept_stocks)} 只股票")

# 获取板块日线数据
daily_data = ths.daily("885943")
print(daily_data.head())

# 获取板块分钟线数据
minute_data = ths.minute("885943")
print(minute_data.head())
```

### 数据分析

```python
import pandas as pd

# 获取板块日线数据
df = ths.daily("885943")

# 转换为DataFrame
df = pd.DataFrame(df)

# 按日期排序
df = df.sort_values('date_at')

# 计算平均涨跌幅
avg_range = df['range'].mean()
print(f"平均涨跌幅: {avg_range:.2%}")

# 查找最大涨幅
max_range = df.loc[df['range'].idxmax()]
print(f"最大涨幅日期: {max_range['date_at']}")
print(f"最大涨幅: {max_range['range']:.2%}")
```

## 限制与注意事项

### 1. 数据限制

- **历史数据**: 仅支持2015年以来的数据
- **分钟线**: 仅支持当日1分钟数据，不支持历史分钟线
- **板块数据**: 仅支持概念板块，不支持行业板块

### 2. 请求限制

- **频率限制**: 避免高频请求，可能触发反爬机制
- **Cookie验证**: Cookie有时效性，需要定期更新
- **数据格式**: JavaScript格式需要特殊处理

### 3. 代码规范

- **板块代码**: 使用 `bk_{code}` 格式，如 `bk_885943`
- **概念代码**: 使用原始代码，如 `885943`
- **日期格式**: 使用字符串格式，如 `2024-01-01`

## 改进建议

### 1. 功能扩展

- **添加5分钟、15分钟线**: 完善分钟线数据支持
- **行业板块支持**: 添加行业板块数据获取
- **实时行情**: 添加实时行情数据接口

### 2. 性能优化

- **异步请求**: 使用异步IO提高请求效率
- **批量获取**: 支持批量获取多个板块数据
- **缓存持久化**: 将缓存数据保存到文件，避免重复请求

### 3. 错误处理

- **重试机制**: 添加请求失败重试逻辑
- **异常处理**: 完善异常处理和错误提示
- **日志记录**: 添加详细的日志记录

### 4. 代码优化

- **类型注解**: 添加类型注解提高代码可读性
- **文档字符串**: 完善方法的文档字符串
- **单元测试**: 添加单元测试确保代码质量

## 相关文件

### 核心文件

- `tonghuashun.py`: 同花顺数据源主文件
- `req.py`: 请求工具类，包含Cookie生成和请求发送

### 依赖文件

- `stock.py`: 股票数据源（东方财富）
- `index.py`: 指数数据源（东方财富）
- `fund.py`: 基金数据源（东方财富）

## 总结

同花顺数据源是一个专注于板块数据获取的工具，具有以下特点：

**优点**:
- 板块数据丰富，包含概念板块和成分股
- 支持多种时间周期的K线数据
- 数据实时性较好

**缺点**:
- Cookie验证机制复杂
- 历史数据有限
- 代码可维护性有待提高

**适用场景**:
- 板块分析和研究
- 板块成分股追踪
- 板块行情监控

**不适用场景**:
- 个股详细分析（建议使用Baostock或东方财富）
- 长期历史数据分析
- 高频交易策略
