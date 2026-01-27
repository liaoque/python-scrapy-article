"""
同花顺数据源测试脚本

测试同花顺数据源的各项功能
"""

import asyncio
from quickstock import QuickStockClient


async def test_tonghuashun():
    """
    测试同花顺数据源功能
    """
    client = QuickStockClient()
    
    print("=" * 60)
    print("测试同花顺数据源")
    print("=" * 60)
    
    # 测试1: 获取概念板块列表
    print("\n1. 测试获取概念板块列表...")
    try:
        concepts = await client.aconcept_list()
        print(f"   成功获取 {len(concepts)} 个概念板块")
        print(f"   前5个板块:")
        print(concepts.head())
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试2: 获取指定板块的成分股
    print("\n2. 测试获取板块成分股...")
    try:
        concepts = await client.aconcept_list()
        if len(concepts) > 0:
            first_concept = concepts.iloc[0]
            concept_cid = first_concept['cid']
            concept_name = first_concept['name']
            stocks = await client.aconcept_stocks(concept_cid)
            print(f"   成功获取概念 '{concept_name}' (cid: {concept_cid}) 的 {len(stocks)} 只成分股")
            print(f"   前10只股票:")
            print(stocks.head(10))
        else:
            print("   没有可用的概念板块")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试3: 获取板块日线数据
    print("\n3. 测试获取板块日线数据...")
    try:
        board_code = "885943"
        daily_data = await client.aboard_daily(board_code)
        print(f"   成功获取板块 {board_code} 的日线数据")
        print(f"   数据行数: {len(daily_data)}")
        print(f"   前5条数据:")
        print(daily_data.head())
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试4: 获取板块周线数据
    print("\n4. 测试获取板块周线数据...")
    try:
        board_code = "885943"
        weekly_data = await client.aboard_weekly(board_code)
        print(f"   成功获取板块 {board_code} 的周线数据")
        print(f"   数据行数: {len(weekly_data)}")
        print(f"   前5条数据:")
        print(weekly_data.head())
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试5: 获取板块月线数据
    print("\n5. 测试获取板块月线数据...")
    try:
        board_code = "885943"
        monthly_data = await client.aboard_monthly(board_code)
        print(f"   成功获取板块 {board_code} 的月线数据")
        print(f"   数据行数: {len(monthly_data)}")
        print(f"   前5条数据:")
        print(monthly_data.head())
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试6: 获取板块分钟线数据
    print("\n6. 测试获取板块分钟线数据...")
    try:
        board_code = "885943"
        minute_data = await client.aboard_minute(board_code)
        print(f"   成功获取板块 {board_code} 的分钟线数据")
        print(f"   数据行数: {len(minute_data)}")
        print(f"   前10条数据:")
        print(minute_data.head(10))
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试7: 获取板块30分钟线数据
    print("\n7. 测试获取板块30分钟线数据...")
    try:
        board_code = "885943"
        minute30_data = await client.aboard_minute30(board_code)
        print(f"   成功获取板块 {board_code} 的30分钟线数据")
        print(f"   数据行数: {len(minute30_data)}")
        print(f"   前5条数据:")
        print(minute30_data.head())
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试8: 获取板块60分钟线数据
    print("\n8. 测试获取板块60分钟线数据...")
    try:
        board_code = "885943"
        minute60_data = await client.aboard_minute60(board_code)
        print(f"   成功获取板块 {board_code} 的60分钟线数据")
        print(f"   数据行数: {len(minute60_data)}")
        print(f"   前5条数据:")
        print(minute60_data.head())
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试9: 获取行业列表
    print("\n9. 测试获取行业列表...")
    try:
        industries = await client.aindustry_list()
        print(f"   成功获取 {len(industries)} 个行业")
        print(f"   前10个行业:")
        print(industries.head(10))
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试10: 获取行业成分股
    print("\n10. 测试获取行业成分股...")
    try:
        industry_code = "881121"
        stocks = await client.aindustry_stocks(industry_code)
        print(f"   成功获取行业 {industry_code} 的 {len(stocks)} 只成分股")
        print(f"   前10只股票:")
        print(stocks.head(10))
    except Exception as e:
        print(f"   失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


def test_sync():
    """
    测试同步方法
    """
    client = QuickStockClient()
    
    print("\n" + "=" * 60)
    print("测试同步方法")
    print("=" * 60)
    
    # 测试同步获取概念板块列表
    print("\n1. 测试同步获取概念板块列表...")
    try:
        concepts = client.concept_list()
        print(f"   成功获取 {len(concepts)} 个概念板块")
        print(f"   前5个板块:")
        print(concepts.head())
    except Exception as e:
        print(f"   失败: {e}")

    print("\n2. 测试获取板块成分股...")
    try:
        concepts = client.concept_list()
        if len(concepts) > 0:
            first_concept = concepts.iloc[0]
            concept_cid = first_concept['cid']
            concept_name = first_concept['name']
            stocks = client.concept_stocks(concept_cid)
            print(f"   成功获取概念 '{concept_name}' (cid: {concept_cid}) 的 {len(stocks)} 只成分股")
            print(f"   前10只股票:")
            print(stocks.head(10))
        else:
            print("   没有可用的概念板块")
    except Exception as e:
        print(f"   失败: {e}")
    # 测试同步获取板块日线数据
    print("\n3. 测试同步获取板块日线数据...")
    try:
        board_code = "885943"
        daily_data = client.board_daily(board_code)
        print(f"   成功获取板块 {board_code} 的日线数据")
        print(f"   数据行数: {len(daily_data)}")
        print(f"   前5条数据:")
        print(daily_data.head())
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试4: 获取行业列表
    print("\n4. 测试获取行业列表...")
    try:
        industries = client.industry_list()
        print(f"   成功获取 {len(industries)} 个行业")
        print(f"   前10个行业:")
        print(industries.head(10))
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试5: 获取行业成分股
    print("\n5. 测试获取行业成分股...")
    try:
        industry_code = "881121"
        stocks = client.industry_stocks(industry_code)
        print(f"   成功获取行业 {industry_code} 的 {len(stocks)} 只成分股")
        print(f"   前10只股票:")
        print(stocks.head(10))
    except Exception as e:
        print(f"   失败: {e}")
    
    print("\n" + "=" * 60)
    print("同步测试完成")
    print("=" * 60)


if __name__ == "__main__":
    print("选择测试模式:")
    print("1. 异步测试")
    print("2. 同步测试")
    print("3. 全部测试")
    
    choice = input("请输入选项 (1/2/3): ").strip()
    
    if choice == "1":
        asyncio.run(test_tonghuashun())
    elif choice == "2":
        test_sync()
    elif choice == "3":
        test_sync()
        asyncio.run(test_tonghuashun())
    else:
        print("无效选项，运行全部测试...")
        test_sync()
        asyncio.run(test_tonghuashun())
