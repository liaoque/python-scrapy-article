Code Conversion
===============

股票代码转换功能可以帮助你在不同的代码格式之间进行转换。

股票代码标准化
-------------

不同数据源可能会使用不同的股票代码格式，QuickStock SDK 提供了代码标准化功能:

.. code-block:: python

    from quickstock import QuickStockClient

    client = QuickStockClient()

    # 标准化股票代码
    normalized = client.normalize_code('000001')
    print(normalized)  # 输出: 000001.SZ

    # 判断市场
    market = client.classify_market('000001.SZ')
    print(market)  # 输出: 深圳A股

代码转换示例
----------

1. 通达信格式转标准格式:

.. code-block:: python

    # 通达信格式转标准格式
    std_code = client.tdx_to_standard('000001')
    print(std_code)  # 输出: 000001.SZ

2. 同花顺格式转标准格式:

.. code-block:: python

    # 同花顺格式转标准格式
    std_code = client.ths_to_standard('000001.SZ')
    print(std_code)  # 输出: 000001.SZ

3. 东财格式转标准格式:

.. code-block:: python

    # 东财格式转标准格式
    std_code = client.eastmoney_to_standard('000001.SZ')
    print(std_code)  # 输出: 000001.SZ

ST股票识别
---------

QuickStock SDK 还可以识别 ST 股票:

.. code-block:: python

    # 判断是否为ST股票
    is_st = client.is_st_stock('ST曙光')
    print(is_st)  # 输出: True

    # 获取股票分类
    classification = client.classify_stock('000001.SZ', '平安银行')
    print(classification)  # 输出分类信息