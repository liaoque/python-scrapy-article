Basic Usage
===========

基础用法指南介绍了 QuickStock SDK 的基本功能和使用方法。

创建客户端
----------

使用 QuickStock SDK 的第一步是创建一个客户端实例:

.. code-block:: python

    from quickstock import QuickStockClient

    # 使用默认配置创建客户端
    client = QuickStockClient()

    # 或者使用自定义配置
    from quickstock import Config
    config = Config(
        timeout=30
    )
    client = QuickStockClient(config=config)

获取股票数据
-----------

QuickStock SDK 支持获取多种类型的股票数据:

股票日线数据
~~~~~~~~~~~~

.. code-block:: python

    # 获取指定股票的日线数据
    df = client.stock_daily('000001.SZ', '20230101', '20231231')
    print(df.head())

股票周线数据
~~~~~~~~~~~~

.. code-block:: python

    # 获取指定股票的周线数据
    df = client.stock_weekly('000001.SZ')
    print(df.head())

股票月线数据
~~~~~~~~~~~~

.. code-block:: python

    # 获取指定股票的月线数据
    df = client.stock_monthly('000001.SZ', '20230101', '20231231')
    print(df.head())

获取指数数据
-----------

除了股票数据，还可以获取指数相关信息:

指数基本信息
~~~~~~~~~~~~

.. code-block:: python

    # 获取所有指数的基本信息
    df = client.index_basic()
    print(df.head())

    # 获取特定市场的指数
    df = client.index_basic(market='SSE')  # 上交所指数

指数日线数据
~~~~~~~~~~~~

.. code-block:: python

    # 获取指数的日线数据
    df = client.index_daily('000001.SH', '20230101', '20231231')
    print(df.head())

获取涨跌停统计数据
-----------------

QuickStock SDK 还提供了涨跌停统计数据的获取功能:

.. code-block:: python

    # 获取指定日期的涨停统计数据
    stats = client.limit_up_stats('20231201')
    print(stats)

数据处理和分析
-------------

获取的数据以 pandas DataFrame 格式返回，可以方便地进行进一步处理:

.. code-block:: python

    import pandas as pd

    # 获取数据
    df = client.stock_daily('000001.SZ', '20230101', '20231231')

    # 基本统计信息
    print(df.describe())

    # 筛选涨幅大于5%的记录
    high_gain = df[df['pct_chg'] > 5]
    print(high_gain)

    # 计算移动平均线
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()