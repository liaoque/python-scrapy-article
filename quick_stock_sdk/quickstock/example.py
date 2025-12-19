"""
QuickStock SDK使用示例

展示如何使用QuickStock SDK获取股票、指数和基金数据
"""

from quickstock import QuickStockClient
from quickstock.errors import ValidationError, DataSourceError


def example_stock_data():
    """
    股票数据获取示例
    """
    print("=== 股票数据获取示例 ===")
    
    # 创建客户端实例
    client = QuickStockClient()
    
    # 1. 获取股票基础信息
    print("\n1. 获取股票基础信息:")
    df_stock_basic = client.stock_basic()
    print(f"   返回{len(df_stock_basic)}条股票信息")
    print("   部分股票代码和名称:")
    print(df_stock_basic[['code', 'name', 'industry']].head())
    
    # 2. 获取股票日线数据
    print("\n2. 获取股票日线数据 (sh.600000):")
    df_stock_daily = client.stock_daily(code="sh.600000", start_date="2024-01-01", end_date="2024-01-31")
    print(f"   返回{len(df_stock_daily)}条日线数据")
    print("   部分日线数据:")
    print(df_stock_daily[['trade_date', 'open', 'high', 'low', 'close', 'vol']].head())
    
    # 3. 获取股票分钟线数据
    print("\n3. 获取股票分钟线数据 (sh.600000):")
    df_stock_minute = client.stock_minute(code="sh.600000")
    print(f"   返回{len(df_stock_minute)}条分钟线数据")
    if not df_stock_minute.empty:
        print("   部分分钟线数据:")
        print(df_stock_minute[['datetime', 'open', 'high', 'low', 'close', 'vol']].head())
    else:
        print("   没有返回分钟线数据")


def example_index_data():
    """
    指数数据获取示例
    """
    print("\n\n=== 指数数据获取示例 ===")
    
    # 创建客户端实例
    client = QuickStockClient()
    
    # 1. 获取指数基础信息
    print("\n1. 获取指数基础信息:")
    df_index_basic = client.index_basic()
    print(f"   返回{len(df_index_basic)}条指数信息")
    print("   部分指数代码和名称:")
    print(df_index_basic[['code', 'name', 'listing_date']].head())
    
    # 2. 获取指数日线数据
    print("\n2. 获取上证指数日线数据 (sh.000001):")
    df_index_daily = client.index_daily(code="sh.000001", start_date="2024-01-01", end_date="2024-01-31")
    print(f"   返回{len(df_index_daily)}条日线数据")
    print("   部分日线数据:")
    print(df_index_daily[['trade_date', 'open', 'high', 'low', 'close', 'vol']].head())


def example_fund_data():
    """
    基金数据获取示例
    """
    print("\n\n=== 基金数据获取示例 ===")
    
    # 创建客户端实例
    client = QuickStockClient()
    
    # 1. 获取基金基础信息
    print("\n1. 获取基金基础信息:")
    try:
        df_fund_basic = client.fund_basic()
        print(f"   返回{len(df_fund_basic)}条基金信息")
        print("   部分基金代码和名称:")
        print(df_fund_basic[['code', 'name']].head())
    except NotImplementedError as e:
        print(f"   注意: {e}")
    
    # 2. 获取基金日线数据
    print("\n2. 获取基金日线数据 (f.150001):")
    try:
        df_fund_daily = client.fund_daily(code="f.150001", start_date="2024-01-01", end_date="2024-01-31")
        print(f"   返回{len(df_fund_daily)}条日线数据")
        print("   部分日线数据:")
        print(df_fund_daily[['trade_date', 'open', 'high', 'low', 'close', 'vol']].head())
    except NotImplementedError as e:
        print(f"   注意: {e}")


def example_error_handling():
    """
    错误处理示例
    """
    print("\n\n=== 错误处理示例 ===")
    
    # 创建客户端实例
    client = QuickStockClient()
    
    # 测试无效的股票代码
    print("\n1. 测试无效的股票代码:")
    try:
        client.stock_daily(code="")
    except ValidationError as e:
        print(f"   捕获到预期的验证错误: {type(e).__name__}")
    
    # 测试其他可能的错误
    print("\n2. 测试数据获取错误处理:")
    try:
        # 这里模拟一个不存在的数据源错误
        raise DataSourceError("模拟数据源错误")
    except DataSourceError as e:
        print(f"   捕获到预期的数据源错误: {type(e).__name__}")


if __name__ == "__main__":
    """
    运行所有示例
    """
    print("QuickStock SDK使用示例\n")
    
    # 运行各个示例
    example_stock_data()
    example_index_data()
    example_fund_data()
    example_error_handling()
    
    print("\n\n=== 示例结束 ===")
