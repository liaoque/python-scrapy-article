# Baostock API功能总结

## 1. 平台介绍
- Baostock是一个免费、开源的证券数据平台
- 通过Python API提供丰富的历史行情数据和上市公司财务数据
- 返回数据格式主要为pandas DataFrame
- 支持Python 3.5+版本

## 2. 核心功能模块

### 2.1 历史行情数据
- **日K线数据**：从1990年至今
- **周/月K线数据**：从1990年至今
- **分钟K线数据**：5/15/30/60分钟线，近5年数据
- **主要函数**：`query_history_k_data_plus()`

### 2.2 财务数据
- **资产负债表**：从2007年至今的季度数据
- **利润表**：从2007年至今的季度数据
- **现金流量表**：从2007年至今的季度数据
- **主要函数**：`query_balance_data()`, `query_profit_data()`

### 2.3 公司报告数据
- **业绩预告**：从2003年至今
- **业绩快报**：从2006年至今
- **主要函数**：`query_forecast_report()`, `query_performance_express_report()`

### 2.4 指数数据
- **综合指数**：如上证指数、深证成指
- **规模指数**：如沪深300、中证500、上证50
- **行业指数**：一级行业指数、二级行业指数
- **主要函数**：`query_sz50_stocks()`, `query_hs300_stocks()`, `query_zz500_stocks()`

### 2.5 辅助数据
- **交易日期**：从1990年至今的交易日数据
- **证券基本资料**：股票代码、名称等基本信息
- **除权除息信息**：分红送转数据
- **主要函数**：`query_trade_dates()`, `query_all_stock()`, `query_dividend_data()`

## 3. API使用模式

### 3.1 基本流程
```python
import baostock as bs
import pandas as pd

# 1. 登录系统
lg = bs.login()
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

# 2. 查询数据
rs = bs.query_history_k_data_plus("sh.600000",
    "date,code,open,high,low,close,volume",
    start_date='2024-01-01', end_date='2024-12-31',
    frequency="d", adjustflag="3")

# 3. 处理结果
result_list = []
while (rs.error_code == '0') & rs.next():
    result_list.append(rs.get_row_data())
result_df = pd.DataFrame(result_list, columns=rs.fields)

# 4. 输出数据
result_df.to_csv("D:/history_k_data.csv", encoding="gbk", index=False)

# 5. 登出系统
bs.logout()
```

### 3.2 关键参数说明

#### 股票代码格式
- 上海证券交易所：`sh.600000`
- 深圳证券交易所：`sz.000001`

#### 日期格式
- YYYY-MM-DD（如：2024-01-01）

#### K线频率
- 日线：`"d"`
- 周线：`"w"`
- 月线：`"m"`
- 5分钟线：`"5"`
- 15分钟线：`"15"`
- 30分钟线：`"30"`
- 60分钟线：`"60"`

#### 复权类型
- 不复权：`"3"`
- 前复权：`"2"`
- 后复权：`"1"`

### 3.3 证券基本资料查询示例

```python
import baostock as bs
import pandas as pd

# 登陆系统
lg = bs.login()
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

# 获取证券基本资料（按代码）
rs = bs.query_stock_basic(code="sh.600000")
# rs = bs.query_stock_basic(code_name="浦发银行")  # 支持模糊查询
print('query_stock_basic respond error_code:'+rs.error_code)
print('query_stock_basic respond  error_msg:'+rs.error_msg)

# 打印结果集
data_list = []
while (rs.error_code == '0') & rs.next():
    # 获取一条记录，将记录合并在一起
    data_list.append(rs.get_row_data())
result = pd.DataFrame(data_list, columns=rs.fields)
# 结果集输出到csv文件
result.to_csv("D:/stock_basic.csv", encoding="gbk", index=False)
print(result)

# 登出系统
bs.logout()
```

#### 证券基本资料返回字段说明
- `code`: 证券代码
- `code_name`: 证券名称
- `ipoDate`: 上市日期
- `outDate`: 退市日期
- `type`: 证券类型（1：股票，2：指数，3：其它，4：可转债，5：ETF）
- `status`: 上市状态（1：上市，0：退市）

## 4. 主要API函数列表

### 4.1 系统操作
- `bs.login()`: 登录系统
- `bs.logout()`: 登出系统

### 4.2 行情数据
- `query_history_k_data_plus(code, fields, start_date, end_date, frequency, adjustflag)`: 查询历史K线数据
- `query_stock_basic(code, code_name)`: 获取证券基本资料，支持按代码或名称查询，支持模糊查询
- `query_all_stock(date)`: 获取指定日期的所有股票代码

### 4.3 指数相关
- `query_sz50_stocks()`: 查询上证50成分股
- `query_hs300_stocks()`: 查询沪深300成分股
- `query_zz500_stocks()`: 查询中证500成分股

**注意**: Baostock没有专门的`query_index_basic`函数，获取指数基本信息可以使用`query_stock_basic`函数：
1. 通过指数代码直接查询，如`query_stock_basic(code="sh.000001")`获取上证指数
2. 通过type参数筛选指数，type=2表示指数类型

### 4.4 财务数据
- `query_balance_data(code, year, quarter)`: 查询资产负债表数据
- `query_profit_data(code, year, quarter)`: 查询利润表数据
- `query_cash_flow_data(code, year, quarter)`: 查询现金流量表数据

### 4.5 公司报告
- `query_forecast_report(code, start_date, end_date)`: 查询业绩预告
- `query_performance_express_report(code, start_date, end_date)`: 查询业绩快报

### 4.6 辅助数据
- `query_trade_dates(start_date, end_date)`: 查询交易日期
- `query_dividend_data(code, year, yearType)`: 查询分红送转数据
- `query_money_supply_data_month(start_date, end_date)`: 查询货币供应量数据

## 5. 数据更新时间

### 每日更新
- 日K线：交易日17:30
- 复权因子：交易日18:00
- 分钟线：次日11:00
- 财务报告数据：次日1:30

### 每周更新
- 周线：周六17:30
- 指数成分股：每周一下午

## 6. 使用限制
- 无需注册，免费使用
- 数据范围：A股市场为主
- 分钟线数据限制：近5年

## 7. 安装与依赖

### 安装方式
```bash
pip install baostock
```

### 依赖库
- pandas
- Python 3.5+

## 8. 错误处理
- 所有API调用返回`error_code`和`error_msg`
- 成功调用：`error_code == '0'`
- 失败时返回具体错误信息

## 9. 最佳实践
1. 始终在数据查询前后调用login/logout
2. 处理返回结果时检查error_code
3. 批量查询时注意控制频率
4. 使用pandas DataFrame进行数据处理和分析
5. 根据需求选择合适的复权类型