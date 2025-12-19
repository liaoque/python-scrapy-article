"""
QuickStock SDK测试文件

验证SDK的核心功能是否正常工作
"""

import pytest
import pandas as pd
from quickstock import QuickStockClient
from quickstock.errors import (ValidationError, DataSourceError)


def test_client_initialization():
    """
    测试客户端初始化
    """
    client = QuickStockClient()
    assert client is not None
    print("✓ 客户端初始化测试通过")


def test_stock_basic():
    """
    测试获取股票基础信息（同步方法）
    """
    client = QuickStockClient()
    df = client.stock_basic()
    
    # 验证返回结果
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'code' in df.columns
    assert 'name' in df.columns
    assert 'industry' in df.columns
    
    print("✓ 股票基础信息测试通过")
    print(f"  返回数据行数: {len(df)}")
    print(f"  股票代码示例: {df['code'].iloc[:2].tolist()}")


def test_stock_daily():
    """
    测试获取股票日线数据（同步方法）
    """
    client = QuickStockClient()
    df = client.stock_daily(code="sh.600000")
    
    # 验证返回结果
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'code' in df.columns
    assert 'trade_date' in df.columns
    assert 'open' in df.columns
    assert 'high' in df.columns
    assert 'low' in df.columns
    assert 'close' in df.columns
    assert 'vol' in df.columns
    
    print("✓ 股票日线数据测试通过")
    print(f"  返回数据行数: {len(df)}")
    print(f"  日期范围: {df['trade_date'].min()} 至 {df['trade_date'].max()}")


def test_stock_minute():
    """
    测试获取股票分钟线数据（同步方法）
    """
    client = QuickStockClient()
    # 使用昨天的日期来获取分钟线数据，确保有数据返回
    import datetime
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    df = client.stock_minute(code="sh.600000", start_date=yesterday, end_date=yesterday)
    
    # 验证返回结果
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'code' in df.columns
    assert 'datetime' in df.columns
    assert 'open' in df.columns
    assert 'close' in df.columns
    
    print("✓ 股票分钟线数据测试通过")
    print(f"  返回数据行数: {len(df)}")


def test_index_basic():
    """
    测试获取指数基础信息（同步方法）
    """
    client = QuickStockClient()
    df = client.index_basic()
    
    # 验证返回结果
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'code' in df.columns
    assert 'name' in df.columns
    
    print("✓ 指数基础信息测试通过")
    print(f"  返回数据行数: {len(df)}")
    print(f"  指数代码示例: {df['code'].iloc[:2].tolist()}")


def test_index_daily():
    """
    测试获取指数日线数据（同步方法）
    """
    client = QuickStockClient()
    df = client.index_daily(code="sh.000001")
    
    # 验证返回结果
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'code' in df.columns
    assert 'trade_date' in df.columns
    assert 'open' in df.columns
    assert 'close' in df.columns
    
    print("✓ 指数日线数据测试通过")
    print(f"  返回数据行数: {len(df)}")


def test_fund_basic():
    """
    测试获取基金基础信息（同步方法）
    预期行为：Baostock不支持基金数据，抛出NotImplementedError
    """
    client = QuickStockClient()
    
    with pytest.raises(NotImplementedError):
        client.fund_basic()
    
    print("✓ 基金基础信息测试通过（预期的NotImplementedError）")


def test_validation_error():
    """
    测试参数验证错误
    """
    client = QuickStockClient()
    
    with pytest.raises(ValidationError):
        client.stock_daily(code="")
    
    print("✓ 参数验证错误测试通过")


if __name__ == "__main__":
    """
    运行所有测试
    """
    print("开始测试QuickStock SDK...\n")
    
    # 运行所有测试函数
    test_client_initialization()
    test_stock_basic()
    test_stock_daily()
    test_stock_minute()
    test_index_basic()
    test_index_daily()
    test_fund_basic()
    test_validation_error()
    
    print("\n✓ 所有测试通过！")
