Error Handling
==============

错误处理是使用 QuickStock SDK 时的重要部分。

常见异常类型
----------

QuickStock SDK 定义了多种异常类型:

1. ``QuickStockError`` - 基础异常类
2. ``ValidationError`` - 参数验证错误
3. ``NetworkError`` - 网络错误
4. ``RateLimitError`` - 请求频率超限
5. ``AuthenticationError`` - 认证错误
6. ``DataUnavailableError`` - 数据不可用

异常处理示例
----------

.. code-block:: python

    from quickstock import QuickStockClient, QuickStockError, ValidationError, NetworkError

    client = QuickStockClient()
    
    try:
        df = client.stock_daily('INVALID_CODE', '20230101', '20231231')
    except ValidationError as e:
        print(f"参数验证失败: {e}")
    except NetworkError as e:
        print(f"网络错误: {e}")
    except QuickStockError as e:
        print(f"QuickStock 错误: {e}")
    except Exception as e:
        print(f"未知错误: {e}")

重试机制
------

QuickStock SDK 内置了重试机制，可以在网络不稳定时自动重试:

.. code-block:: python

    from quickstock import QuickStockClient

    client = QuickStockClient()
    
    # 默认会进行重试
    df = client.stock_daily('000001.SZ', '20230101', '20231231')
    
    # 自定义重试次数
    df = client.stock_daily('000001.SZ', '20230101', '20231231', max_retries=5)

日志记录
------

QuickStock SDK 使用 Python 标准日志模块记录操作日志:

.. code-block:: python

    import logging
    from quickstock import QuickStockClient

    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    client = QuickStockClient()
    
    # 操作会被记录到日志中
    df = client.stock_daily('000001.SZ', '20230101', '20231231')

故障排查
------

如果遇到问题，可以启用调试日志来获取更多信息:

.. code-block:: python

    import logging
    from quickstock import QuickStockClient

    # 启用调试日志
    logging.basicConfig(level=logging.DEBUG)
    
    client = QuickStockClient()
    df = client.stock_daily('000001.SZ', '20230101', '20231231')