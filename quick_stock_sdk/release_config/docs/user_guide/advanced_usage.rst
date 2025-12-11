Advanced Usage
==============

高级用法涵盖了 QuickStock SDK 的一些高级特性和使用技巧。

并发数据获取
----------

QuickStock SDK 支持并发获取多个数据:

.. code-block:: python

    from quickstock import QuickStockClient, DataRequest

    client = QuickStockClient()
    
    # 创建多个数据请求
    requests = [
        DataRequest(data_type='stock_daily', ts_code='000001.SZ', start_date='20230101', end_date='20231231'),
        DataRequest(data_type='stock_daily', ts_code='000002.SZ', start_date='20230101', end_date='20231231'),
        DataRequest(data_type='stock_daily', ts_code='000003.SZ', start_date='20230101', end_date='20231231'),
    ]
    
    # 并发获取数据
    results = client.get_data_batch(requests)
    
    for i, df in enumerate(results):
        print(f"数据集 {i+1}: {len(df)} 条记录")

自定义配置
--------

可以通过多种方式自定义配置:

.. code-block:: python

    from quickstock import QuickStockClient, Config

    # 方法1: 通过代码配置
    config = Config(
        timeout=60,
        max_retries=5,
        max_concurrent_requests=20
    )
    client = QuickStockClient(config=config)
    
    # 方法2: 通过配置文件
    client = QuickStockClient(config_file='config.yaml')

性能监控
------

QuickStock SDK 提供了性能监控功能:

.. code-block:: python

    from quickstock import QuickStockClient

    client = QuickStockClient()
    
    # 获取性能统计信息
    stats = client.get_performance_stats()
    print(stats)
    
    # 获取内存使用情况
    memory_stats = client.get_memory_stats()
    print(memory_stats)

错误重试机制
----------

QuickStock SDK 内置了错误重试机制:

.. code-block:: python

    from quickstock import QuickStockClient

    client = QuickStockClient()
    
    # 自动重试机制会在网络错误时自动重试
    df = client.stock_daily('000001.SZ', '20230101', '20231231')