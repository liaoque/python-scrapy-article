Quick Start
===========

快速入门指南将帮助您快速了解如何使用 QuickStock SDK。

基本用法
--------

首先导入 QuickStockClient:

.. code-block:: python

    from quickstock import QuickStockClient

    # 创建客户端实例
    client = QuickStockClient()

    # 获取股票日线数据
    df = client.stock_daily('000001.SZ', '20230101', '20231231')
    print(df.head())

配置客户端
----------

可以通过传递配置参数来自定义客户端行为:

.. code-block:: python

    from quickstock import QuickStockClient, Config

    config = Config(
        timeout=30,
        max_retries=3
    )

    client = QuickStockClient(config=config)

获取不同类型的数据
------------------

1. 股票日线数据:

.. code-block:: python

    df = client.stock_daily('000001.SZ', '20230101', '20231231')

2. 股票周线数据:

.. code-block:: python

    df = client.stock_weekly('000001.SZ')

3. 股票月线数据:

.. code-block:: python

    df = client.stock_monthly('000001.SZ', '20230101', '20231231')

4. 指数数据:

.. code-block:: python

    # 获取指数基本信息
    df = client.index_basic()

    # 获取指数日线数据
    df = client.index_daily('000001.SH', '20230101', '20231231')

5. 涨停统计:

.. code-block:: python

    stats = client.limit_up_stats('20231201')
    print(stats)

错误处理
--------

使用 try-except 块来捕获和处理可能的异常:

.. code-block:: python

    from quickstock import QuickStockError, ValidationError

    try:
        df = client.stock_daily('INVALID_CODE', '20230101', '20231231')
    except ValidationError as e:
        print(f"参数验证错误: {e}")
    except QuickStockError as e:
        print(f"数据获取错误: {e}")

了解更多
--------

有关更详细的使用方法，请参阅 :doc:`user_guide/index` 和 :doc:`api/index`。