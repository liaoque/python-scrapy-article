# QuickStock SDK

QuickStock SDK是一个现代化的金融数据获取SDK，提供统一的股票、基金、指数数据访问接口。专注于实时数据获取，轻量级设计，无缓存和数据库依赖。

## 特性

- 🚀 **多数据源支持**: 集成东方财富、同花顺、Baostock等数据源
- 🔄 **异步API**: 支持异步数据获取，提升并发性能
- 📊 **标准化格式**: 统一的数据格式，简化数据处理
- 🎯 **实时数据**: 直接从数据源获取最新数据，确保数据实时性
- 🛡️ **智能容错**: 完善的错误处理和自动重试机制
- 🔀 **自动切换**: 数据源故障时自动切换到备用源
- 🎨 **代码转换**: 智能识别和转换多种股票代码格式
- ⚙️ **灵活配置**: 可定制的配置管理系统
- 📈 **性能优化**: 连接池、并发控制、内存优化

## 安装

```bash
pip install quickstock
```

可选依赖：

```bash
# 安装Baostock支持
pip install quickstock[baostock]

# 安装开发依赖
pip install quickstock[dev]
```

## 快速开始

```python
from quickstock import QuickStockClient

# 创建客户端
client = QuickStockClient()

# 获取股票基础信息
stocks = client.stock_basic()

# 获取股票日线数据
daily_data = client.stock_daily('000001.SZ')

# 获取分钟级数据
minute_data = client.stock_minute('000001.SZ', freq='1min')

# 获取指数数据
indices = client.index_basic()
index_data = client.index_daily('000001.SH')

# 获取基金数据
funds = client.fund_basic()
nav_data = client.fund_nav('000001.OF')

# 交易日历
trade_cal = client.trade_cal()
is_trade = client.is_trade_date('20240115')
```

## 系统要求

- Python >= 3.7
- pandas >= 1.3.0
- numpy >= 1.20.0
- requests >= 2.25.0
- aiohttp >= 3.8.0
- pyyaml >= 5.4.0

## 许可证

MIT License