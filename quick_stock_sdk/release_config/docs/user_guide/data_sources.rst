Data Sources
============

数据源配置和管理是 QuickStock SDK 的重要组成部分。

支持的数据源
----------

QuickStock SDK 支持多种数据源:

1. 同花顺 (tonghuashun)
2. 东方财富 (eastmoney)
3. Baostock (baostock)

配置数据源优先级
--------------

可以通过配置文件或代码设置数据源的优先级:

.. code-block:: python

    from quickstock import QuickStockClient, Config

    # 设置数据源优先级
    config = Config(
        timeout=30
    )
    
    client = QuickStockClient(config=config)

数据源切换
---------

当首选数据源不可用时，QuickStock SDK 会自动切换到备用数据源:

.. code-block:: python

    from quickstock import QuickStockClient

    client = QuickStockClient()
    
    # 获取数据时会自动选择可用的数据源
    df = client.stock_daily('000001.SZ', '20230101', '20231231')

自定义数据源
----------

你也可以实现自己的数据源适配器:

.. code-block:: python

    from quickstock.providers.base import BaseDataProvider
    
    class CustomDataProvider(BaseDataProvider):
        async def fetch_data(self, request):
            # 实现你的数据获取逻辑
            pass
    
    # 注册自定义数据源
    client.register_provider('custom', CustomDataProvider)

数据源健康检查
------------

可以检查各个数据源的健康状态:

.. code-block:: python

    from quickstock import QuickStockClient

    client = QuickStockClient()
    
    # 检查数据源健康状态
    health_status = client.check_data_source_health()
    print(health_status)