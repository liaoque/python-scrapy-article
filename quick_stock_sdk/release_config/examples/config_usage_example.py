"""
QuickStock SDK 配置使用示例

演示如何使用配置系统来自定义SDK行为。
QuickStock SDK采用实时数据获取模式，不使用本地缓存或数据库持久化。
"""

from quickstock import QuickStockClient
from quickstock.config import Config


def example_1_default_config():
    """示例1: 使用默认配置"""
    print("=" * 60)
    print("示例1: 使用默认配置")
    print("=" * 60)
    
    # 使用默认配置创建客户端
    client = QuickStockClient()
    
    # 获取配置信息
    print(f"请求超时: {client.config.request_timeout}秒")
    print(f"最大重试次数: {client.config.max_retries}")
    print(f"日志级别: {client.config.log_level}")
    print(f"自动代码转换: {client.config.enable_auto_code_conversion}")
    print()


def example_2_custom_config():
    """示例2: 使用自定义配置"""
    print("=" * 60)
    print("示例2: 使用自定义配置")
    print("=" * 60)
    
    # 创建自定义配置
    config = Config(
        request_timeout=60,          # 增加超时时间
        max_retries=5,               # 增加重试次数
        log_level='DEBUG',           # 启用调试日志
        enable_auto_code_conversion=True,  # 启用自动代码转换
        max_concurrent_requests=20   # 增加并发请求数
    )
    
    # 使用自定义配置创建客户端
    client = QuickStockClient(config=config)
    
    print(f"请求超时: {client.config.request_timeout}秒")
    print(f"最大重试次数: {client.config.max_retries}")
    print(f"日志级别: {client.config.log_level}")
    print(f"最大并发请求数: {client.config.max_concurrent_requests}")
    print()


def example_3_load_from_file():
    """示例3: 从配置文件加载"""
    print("=" * 60)
    print("示例3: 从配置文件加载")
    print("=" * 60)
    
    try:
        # 从YAML文件加载配置
        config = Config.from_file('~/.quickstock/config.yaml')
        client = QuickStockClient(config=config)
        
        print("成功从配置文件加载配置")
        print(f"请求超时: {client.config.request_timeout}秒")
        print(f"日志级别: {client.config.log_level}")
    except FileNotFoundError:
        print("配置文件不存在，使用默认配置")
        config = Config()
        client = QuickStockClient(config=config)
    print()


def example_4_dynamic_update():
    """示例4: 动态更新配置"""
    print("=" * 60)
    print("示例4: 动态更新配置")
    print("=" * 60)
    
    # 创建客户端
    client = QuickStockClient()
    
    print(f"初始超时时间: {client.config.request_timeout}秒")
    
    # 动态更新配置
    client.config.update(
        request_timeout=45,
        max_retries=4,
        log_level='WARNING'
    )
    
    print(f"更新后超时时间: {client.config.request_timeout}秒")
    print(f"更新后重试次数: {client.config.max_retries}")
    print(f"更新后日志级别: {client.config.log_level}")
    print()


def example_5_save_config():
    """示例5: 保存配置到文件"""
    print("=" * 60)
    print("示例5: 保存配置到文件")
    print("=" * 60)
    
    # 创建自定义配置
    config = Config(
        request_timeout=60,
        max_retries=5,
        log_level='DEBUG',
        enable_auto_code_conversion=True
    )
    
    # 保存为默认配置
    config.save_as_default()
    print("配置已保存到 ~/.quickstock/config.yaml")
    
    # 也可以保存到其他位置
    config.to_file('~/my_custom_config.yaml', format='yaml')
    print("配置已保存到 ~/my_custom_config.yaml")
    print()


def example_6_data_source_priority():
    """示例6: 配置数据源优先级"""
    print("=" * 60)
    print("示例6: 配置数据源优先级")
    print("=" * 60)
    
    config = Config()
    
    # 查看当前数据源优先级
    print("股票日线数据源优先级:")
    priority = config.get_data_source_priority('stock_daily')
    print(f"  {priority}")
    
    # 修改数据源优先级（例如：优先使用东方财富）
    config.set_data_source_priority('stock_daily', ['eastmoney', 'baostock'])
    print("\n修改后的优先级:")
    priority = config.get_data_source_priority('stock_daily')
    print(f"  {priority}")
    print()


def example_7_code_conversion_config():
    """示例7: 配置股票代码转换"""
    print("=" * 60)
    print("示例7: 配置股票代码转换")
    print("=" * 60)
    
    config = Config()
    
    # 获取代码转换配置
    code_config = config.get_code_conversion_config()
    print("代码转换配置:")
    for key, value in code_config.items():
        print(f"  {key}: {value}")
    
    # 修改代码转换策略
    config.enable_code_conversion(True)
    config.set_code_conversion_error_strategy('lenient')
    
    print("\n修改后:")
    print(f"  自动代码转换: {config.enable_auto_code_conversion}")
    print(f"  错误处理策略: {config.code_conversion_error_strategy}")
    print()


def example_8_financial_reports_config():
    """示例8: 配置财务报告功能"""
    print("=" * 60)
    print("示例8: 配置财务报告功能")
    print("=" * 60)
    
    config = Config()
    
    # 获取财务报告配置
    fr_config = config.get_financial_reports_config()
    print("财务报告配置:")
    print(f"  启用状态: {fr_config['financial_reports_enabled']}")
    print(f"  批处理大小: {fr_config['financial_reports_batch_size']}")
    print(f"  速率限制: {fr_config['financial_reports_rate_limit']} 请求/秒")
    print(f"  重试次数: {fr_config['financial_reports_retry_attempts']}")
    
    # 修改财务报告配置
    config.set_financial_reports_batch_size(100)
    config.set_financial_reports_rate_limit(5.0)
    config.set_financial_reports_retry_config(retry_attempts=5, retry_delay=2.0)
    
    print("\n修改后:")
    print(f"  批处理大小: {config.financial_reports_batch_size}")
    print(f"  速率限制: {config.financial_reports_rate_limit} 请求/秒")
    print(f"  重试次数: {config.financial_reports_retry_attempts}")
    print()


def example_9_memory_optimization():
    """示例9: 配置内存优化"""
    print("=" * 60)
    print("示例9: 配置内存优化")
    print("=" * 60)
    
    # 为大数据量场景优化内存配置
    config = Config(
        stream_chunk_size=5000,           # 减小块大小
        memory_limit_mb=1000.0,           # 增加内存限制
        memory_batch_size=100,            # 增加批处理大小
        aggressive_memory_optimization=True  # 启用激进优化
    )
    
    print("内存优化配置:")
    print(f"  流式处理块大小: {config.stream_chunk_size}")
    print(f"  内存限制: {config.memory_limit_mb} MB")
    print(f"  批处理大小: {config.memory_batch_size}")
    print(f"  激进优化: {config.aggressive_memory_optimization}")
    print()


def example_10_network_optimization():
    """示例10: 配置网络优化"""
    print("=" * 60)
    print("示例10: 配置网络优化")
    print("=" * 60)
    
    # 为高并发场景优化网络配置
    config = Config(
        request_timeout=60,                  # 增加超时时间
        max_retries=5,                       # 增加重试次数
        retry_delay=2.0,                     # 增加重试延迟
        max_concurrent_requests=50,          # 增加并发数
        connection_pool_size=200,            # 增加连接池大小
        connection_pool_per_host=50,         # 增加每主机连接数
        connection_keepalive_timeout=60      # 增加连接保持时间
    )
    
    print("网络优化配置:")
    print(f"  请求超时: {config.request_timeout}秒")
    print(f"  最大重试: {config.max_retries}次")
    print(f"  最大并发: {config.max_concurrent_requests}")
    print(f"  连接池大小: {config.connection_pool_size}")
    print(f"  每主机连接数: {config.connection_pool_per_host}")
    print()


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("QuickStock SDK 配置使用示例")
    print("=" * 60 + "\n")
    
    example_1_default_config()
    example_2_custom_config()
    example_3_load_from_file()
    example_4_dynamic_update()
    example_5_save_config()
    example_6_data_source_priority()
    example_7_code_conversion_config()
    example_8_financial_reports_config()
    example_9_memory_optimization()
    example_10_network_optimization()
    
    print("=" * 60)
    print("所有示例运行完成")
    print("=" * 60)


if __name__ == '__main__':
    main()
