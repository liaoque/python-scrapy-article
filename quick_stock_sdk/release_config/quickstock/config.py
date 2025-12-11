"""
配置管理系统

提供SDK的配置管理功能，支持配置文件加载、保存、验证等。

QuickStock SDK采用实时数据获取模式，所有数据直接从外部数据源获取，
不使用本地缓存或数据库持久化。配置系统主要管理：
- 数据源配置和优先级
- 网络请求参数（超时、重试、并发等）
- 数据格式和转换选项
- 日志记录设置
- 性能优化参数

示例:
    # 使用默认配置
    from quickstock import QuickStockClient
    client = QuickStockClient()
    
    # 使用自定义配置
    from quickstock.config import Config
    config = Config(
        request_timeout=60,
        max_retries=5,
        log_level='DEBUG'
    )
    client = QuickStockClient(config=config)
    
    # 从配置文件加载
    config = Config.from_file('~/.quickstock/config.yaml')
    client = QuickStockClient(config=config)
    
    # 动态更新配置
    client.config.update(request_timeout=45)
"""

import os
import json
import yaml
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from pathlib import Path

from .core.errors import ValidationError


@dataclass
class Config:
    """
    SDK配置类
    
    管理QuickStock SDK的所有配置参数。SDK采用实时数据获取模式，
    所有数据直接从外部数据源获取，不使用本地缓存或数据库持久化。
    
    主要配置类别:
    - 数据源配置: 启用/禁用不同的数据源，设置数据源优先级
    - 网络配置: 请求超时、重试策略、并发控制、连接池管理
    - 数据格式配置: 日期格式、浮点精度等
    - 内存优化配置: 流式处理、批处理大小、内存限制
    - 日志配置: 日志级别、日志文件路径
    - 股票代码转换配置: 自动代码格式转换、验证策略
    - 财务报告配置: 批处理大小、速率限制、重试策略
    
    Attributes:
        tushare_token: Tushare API令牌（可选）
        enable_baostock: 是否启用Baostock数据源
        enable_eastmoney: 是否启用东方财富数据源
        enable_tonghuashun: 是否启用同花顺数据源
        request_timeout: 请求超时时间（秒）
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）
        max_concurrent_requests: 最大并发请求数
        connection_pool_size: 连接池总大小
        connection_pool_per_host: 每个主机的连接数
        connection_keepalive_timeout: 连接保持时间（秒）
        connection_cleanup_enabled: 是否启用连接清理
        date_format: 日期格式字符串
        float_precision: 浮点数精度
        stream_chunk_size: 流式处理块大小
        memory_limit_mb: 内存限制（MB）
        memory_batch_size: 内存批处理大小
        aggressive_memory_optimization: 是否启用激进内存优化
        log_level: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
        log_file: 日志文件路径
        enable_auto_code_conversion: 是否启用自动股票代码转换
        strict_code_validation: 是否启用严格代码验证
        log_code_conversions: 是否记录代码转换日志
        code_conversion_timeout: 代码转换超时时间（秒）
        enable_code_format_inference: 是否启用代码格式自动推断
        enable_exchange_inference: 是否启用交易所自动推断
        code_conversion_batch_size: 批量转换的批次大小
        code_conversion_error_strategy: 错误处理策略（strict/lenient/ignore）
        financial_reports_enabled: 是否启用财务报告功能
        financial_reports_batch_size: 财务报告批处理最大股票数量
        financial_reports_timeout: 财务报告请求超时时间（秒）
        financial_reports_retry_attempts: 财务报告最大重试次数
        financial_reports_retry_delay: 财务报告初始重试延迟（秒）
        financial_reports_rate_limit: 财务报告每秒最大请求数
        financial_reports_queue_size: 财务报告请求队列大小
        financial_reports_enable_metrics: 是否启用性能指标收集
        financial_reports_baostock_endpoint: Baostock API端点
        financial_reports_auth_required: 是否需要认证
        financial_reports_auth_token: 认证令牌
        data_source_priority: 各数据类型的数据源优先级配置
    
    Example:
        >>> # 创建默认配置
        >>> config = Config()
        >>> 
        >>> # 创建自定义配置
        >>> config = Config(
        ...     request_timeout=60,
        ...     max_retries=5,
        ...     log_level='DEBUG',
        ...     enable_auto_code_conversion=True
        ... )
        >>> 
        >>> # 从文件加载配置
        >>> config = Config.from_file('~/.quickstock/config.yaml')
        >>> 
        >>> # 更新配置
        >>> config.update(request_timeout=45, max_retries=3)
        >>> 
        >>> # 保存配置到文件
        >>> config.to_file('~/.quickstock/config.yaml')
    """
    
    # 数据源配置
    tushare_token: Optional[str] = None
    enable_baostock: bool = True
    enable_eastmoney: bool = True
    enable_tonghuashun: bool = True
    
    # 网络配置
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    max_concurrent_requests: int = 10  # 最大并发请求数
    
    # 连接池配置
    connection_pool_size: int = 100  # 连接池总大小
    connection_pool_per_host: int = 30  # 每个主机的连接数
    connection_keepalive_timeout: int = 30  # 连接保持时间
    connection_cleanup_enabled: bool = True  # 启用连接清理
    
    # 数据格式配置
    date_format: str = "%Y%m%d"
    float_precision: int = 4
    
    # 内存优化配置
    stream_chunk_size: int = 10000
    memory_limit_mb: float = 500.0
    memory_batch_size: int = 50
    aggressive_memory_optimization: bool = False
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = "~/.quickstock/quickstock.log"
    
    # 股票代码转换配置
    enable_auto_code_conversion: bool = True
    strict_code_validation: bool = False
    log_code_conversions: bool = False
    code_conversion_timeout: float = 1.0  # 代码转换超时时间（秒）
    enable_code_format_inference: bool = True  # 启用代码格式自动推断
    enable_exchange_inference: bool = True  # 启用交易所自动推断
    code_conversion_batch_size: int = 1000  # 批量转换的批次大小
    code_conversion_error_strategy: str = "strict"  # 错误处理策略: strict, lenient, ignore
    
    # 财务报告配置
    financial_reports_enabled: bool = True
    financial_reports_batch_size: int = 50  # 批处理最大股票数量
    financial_reports_timeout: int = 30  # 请求超时时间（秒）
    financial_reports_retry_attempts: int = 3  # 最大重试次数
    financial_reports_retry_delay: float = 1.0  # 初始重试延迟（秒）
    financial_reports_rate_limit: float = 2.0  # 每秒最大请求数
    financial_reports_queue_size: int = 1000  # 请求队列大小
    financial_reports_enable_metrics: bool = True  # 启用性能指标收集
    financial_reports_baostock_endpoint: str = "http://baostock.com"  # baostock API端点
    financial_reports_auth_required: bool = False  # 是否需要认证
    financial_reports_auth_token: Optional[str] = None  # 认证令牌
    
    # 数据源优先级配置
    data_source_priority: Dict[str, list] = field(default_factory=lambda: {
        'stock_basic': ['baostock', 'tushare'],
        'stock_daily': ['baostock', 'tushare', 'eastmoney'],  # Baostock优先，避免东方财富封IP
        'stock_minute': ['eastmoney', 'tonghuashun'],
        'index_basic': ['tushare', 'baostock'],
        'index_daily': ['tushare', 'baostock'],
        'fund_basic': ['tushare'],
        'fund_nav': ['tushare'],
        'trade_cal': ['baostock', 'tushare'],
        'concept': ['tonghuashun'],
        'financial_reports': ['baostock'],
        'earnings_forecast': ['baostock'],
        'flash_reports': ['baostock']
    })
    
    def __post_init__(self):
        """初始化后的验证和处理"""
        self._expand_paths()
        self._validate_config()
    
    def _expand_paths(self):
        """展开路径中的~符号"""
        if self.log_file and self.log_file.startswith('~'):
            self.log_file = os.path.expanduser(self.log_file)
    
    def _validate_config(self):
        """验证配置参数"""
        # 验证网络配置
        if self.request_timeout <= 0:
            raise ValidationError("request_timeout必须大于0")
        
        if self.max_retries < 0:
            raise ValidationError("max_retries不能小于0")
        
        if self.retry_delay < 0:
            raise ValidationError("retry_delay不能小于0")
        
        if self.max_concurrent_requests <= 0:
            raise ValidationError("max_concurrent_requests必须大于0")
        
        # 验证连接池配置
        if self.connection_pool_size <= 0:
            raise ValidationError("connection_pool_size必须大于0")
        
        if self.connection_pool_per_host <= 0:
            raise ValidationError("connection_pool_per_host必须大于0")
        
        if self.connection_keepalive_timeout <= 0:
            raise ValidationError("connection_keepalive_timeout必须大于0")
        
        # 验证数据格式配置
        if self.float_precision < 0:
            raise ValidationError("float_precision不能小于0")
        
        # 验证日志级别
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level.upper() not in valid_log_levels:
            raise ValidationError(f"log_level必须是以下之一: {valid_log_levels}")
        
        # 验证数据源优先级配置
        if not isinstance(self.data_source_priority, dict):
            raise ValidationError("data_source_priority必须是字典类型")
        
        # 验证内存优化配置
        if self.stream_chunk_size <= 0:
            raise ValidationError("stream_chunk_size必须大于0")
        
        if self.memory_limit_mb <= 0:
            raise ValidationError("memory_limit_mb必须大于0")
        
        if self.memory_batch_size <= 0:
            raise ValidationError("memory_batch_size必须大于0")
        
        # 验证代码转换配置
        if self.code_conversion_timeout <= 0:
            raise ValidationError("code_conversion_timeout必须大于0")
        
        if self.code_conversion_batch_size <= 0:
            raise ValidationError("code_conversion_batch_size必须大于0")
        
        valid_error_strategies = ['strict', 'lenient', 'ignore']
        if self.code_conversion_error_strategy not in valid_error_strategies:
            raise ValidationError(f"code_conversion_error_strategy必须是以下之一: {valid_error_strategies}")
        
        # 验证财务报告配置
        if self.financial_reports_batch_size <= 0:
            raise ValidationError("financial_reports_batch_size必须大于0")
        
        if self.financial_reports_timeout <= 0:
            raise ValidationError("financial_reports_timeout必须大于0")
        
        if self.financial_reports_retry_attempts < 0:
            raise ValidationError("financial_reports_retry_attempts不能小于0")
        
        if self.financial_reports_retry_delay < 0:
            raise ValidationError("financial_reports_retry_delay不能小于0")
        
        if self.financial_reports_rate_limit <= 0:
            raise ValidationError("financial_reports_rate_limit必须大于0")
        
        if self.financial_reports_queue_size <= 0:
            raise ValidationError("financial_reports_queue_size必须大于0")
        
        if not isinstance(self.financial_reports_baostock_endpoint, str) or not self.financial_reports_baostock_endpoint.strip():
            raise ValidationError("financial_reports_baostock_endpoint必须是非空字符串")
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """
        从配置文件加载配置
        
        支持JSON和YAML格式的配置文件。配置文件应包含Config类的属性名称和值。
        
        Args:
            config_path: 配置文件路径，支持JSON和YAML格式
            
        Returns:
            配置对象
            
        Raises:
            FileNotFoundError: 配置文件不存在
            ValidationError: 配置文件格式错误或内容无效
            
        Example:
            >>> # YAML配置文件示例 (~/.quickstock/config.yaml):
            >>> # request_timeout: 60
            >>> # max_retries: 5
            >>> # log_level: DEBUG
            >>> # enable_auto_code_conversion: true
            >>> # data_source_priority:
            >>> #   stock_daily: [baostock, eastmoney]
            >>> #   stock_minute: [eastmoney, tonghuashun]
            >>> 
            >>> config = Config.from_file('~/.quickstock/config.yaml')
        """
        config_path = os.path.expanduser(config_path)
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.endswith('.json'):
                    config_data = json.load(f)
                elif config_path.endswith(('.yaml', '.yml')):
                    config_data = yaml.safe_load(f)
                else:
                    # 尝试JSON格式
                    try:
                        f.seek(0)
                        config_data = json.load(f)
                    except json.JSONDecodeError:
                        # 尝试YAML格式
                        f.seek(0)
                        config_data = yaml.safe_load(f)
            
            # 创建配置对象
            return cls(**config_data)
            
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValidationError(f"配置文件格式错误: {e}")
        except TypeError as e:
            raise ValidationError(f"配置参数错误: {e}")
    
    def to_file(self, config_path: str, format: str = 'auto'):
        """
        保存配置到文件
        
        将当前配置保存到指定的文件中，支持JSON和YAML格式。
        
        Args:
            config_path: 配置文件路径
            format: 文件格式 ('json', 'yaml', 'auto')
                   'auto'会根据文件扩展名自动判断，默认为JSON
        
        Raises:
            ValidationError: 格式参数无效
            
        Example:
            >>> config = Config(request_timeout=60, max_retries=5)
            >>> config.to_file('~/.quickstock/config.yaml', format='yaml')
            >>> config.to_file('~/.quickstock/config.json', format='json')
        """
        config_path = os.path.expanduser(config_path)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # 确定文件格式
        if format == 'auto':
            if config_path.endswith('.json'):
                format = 'json'
            elif config_path.endswith(('.yaml', '.yml')):
                format = 'yaml'
            else:
                format = 'json'  # 默认使用JSON
        
        if format not in ['json', 'yaml']:
            raise ValidationError(f"不支持的文件格式: {format}")
        
        # 转换为字典
        config_dict = asdict(self)
        
        # 保存文件
        with open(config_path, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            else:  # yaml
                yaml.dump(config_dict, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
    
    @classmethod
    def get_default_config_path(cls) -> str:
        """
        获取默认配置文件路径
        
        Returns:
            默认配置文件路径
        """
        return os.path.expanduser("~/.quickstock/config.yaml")
    
    @classmethod
    def load_default(cls) -> 'Config':
        """
        加载默认配置
        
        如果默认配置文件（~/.quickstock/config.yaml）存在则加载，
        否则返回使用默认参数的配置对象。
        
        Returns:
            配置对象
            
        Example:
            >>> config = Config.load_default()
            >>> # 如果 ~/.quickstock/config.yaml 存在，则从文件加载
            >>> # 否则使用默认配置参数
        """
        default_path = cls.get_default_config_path()
        if os.path.exists(default_path):
            return cls.from_file(default_path)
        else:
            return cls()
    
    def save_as_default(self):
        """
        将当前配置保存为默认配置
        
        将当前配置保存到默认配置文件路径（~/.quickstock/config.yaml）。
        之后调用Config.load_default()将加载此配置。
        
        Example:
            >>> config = Config(request_timeout=60, max_retries=5)
            >>> config.save_as_default()
            >>> # 之后可以通过 Config.load_default() 加载此配置
        """
        self.to_file(self.get_default_config_path(), 'yaml')
    
    def update(self, **kwargs):
        """
        动态更新配置参数
        
        更新一个或多个配置参数，并自动重新验证配置的有效性。
        
        Args:
            **kwargs: 要更新的配置参数（键值对）
            
        Raises:
            ValidationError: 参数名称不存在或参数值无效
            
        Example:
            >>> config = Config()
            >>> config.update(request_timeout=60, max_retries=5)
            >>> config.update(log_level='DEBUG')
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValidationError(f"未知的配置参数: {key}")
        
        # 重新验证配置
        self._validate_config()
    
    def get_data_source_priority(self, data_type: str) -> list:
        """
        获取指定数据类型的数据源优先级
        
        返回指定数据类型应使用的数据源列表，按优先级排序。
        SDK将按顺序尝试这些数据源，直到成功获取数据。
        
        Args:
            data_type: 数据类型（如'stock_daily', 'stock_minute', 'trade_cal'等）
            
        Returns:
            数据源优先级列表（如['baostock', 'eastmoney']）
            
        Example:
            >>> config = Config()
            >>> priority = config.get_data_source_priority('stock_daily')
            >>> print(priority)  # ['baostock', 'tushare', 'eastmoney']
        """
        return self.data_source_priority.get(data_type, [])
    
    def set_data_source_priority(self, data_type: str, priority_list: list):
        """
        设置指定数据类型的数据源优先级
        
        自定义某个数据类型应使用的数据源及其优先级顺序。
        
        Args:
            data_type: 数据类型（如'stock_daily', 'stock_minute'等）
            priority_list: 数据源优先级列表（如['eastmoney', 'baostock']）
            
        Example:
            >>> config = Config()
            >>> # 设置日线数据优先使用东方财富，其次使用Baostock
            >>> config.set_data_source_priority('stock_daily', ['eastmoney', 'baostock'])
        """
        self.data_source_priority[data_type] = priority_list
    
    def enable_code_conversion(self, enable: bool = True):
        """
        启用或禁用自动代码转换
        
        Args:
            enable: 是否启用自动代码转换
        """
        self.enable_auto_code_conversion = enable
    
    def set_code_conversion_error_strategy(self, strategy: str):
        """
        设置代码转换错误处理策略
        
        Args:
            strategy: 错误处理策略 ('strict', 'lenient', 'ignore')
        """
        valid_strategies = ['strict', 'lenient', 'ignore']
        if strategy not in valid_strategies:
            raise ValidationError(f"错误处理策略必须是以下之一: {valid_strategies}")
        self.code_conversion_error_strategy = strategy
    
    def get_code_conversion_config(self) -> Dict[str, Any]:
        """
        获取股票代码转换相关的所有配置
        
        返回包含所有代码转换相关配置参数的字典。
        
        Returns:
            代码转换配置字典，包含以下键：
            - enable_auto_code_conversion: 是否启用自动代码转换
            - strict_code_validation: 是否启用严格代码验证
            - log_code_conversions: 是否记录代码转换日志
            - code_conversion_timeout: 代码转换超时时间
            - enable_code_format_inference: 是否启用代码格式自动推断
            - enable_exchange_inference: 是否启用交易所自动推断
            - code_conversion_batch_size: 批量转换的批次大小
            - code_conversion_error_strategy: 错误处理策略
            
        Example:
            >>> config = Config()
            >>> code_config = config.get_code_conversion_config()
            >>> print(code_config['enable_auto_code_conversion'])  # True
        """
        return {
            'enable_auto_code_conversion': self.enable_auto_code_conversion,
            'strict_code_validation': self.strict_code_validation,
            'log_code_conversions': self.log_code_conversions,
            'code_conversion_timeout': self.code_conversion_timeout,
            'enable_code_format_inference': self.enable_code_format_inference,
            'enable_exchange_inference': self.enable_exchange_inference,
            'code_conversion_batch_size': self.code_conversion_batch_size,
            'code_conversion_error_strategy': self.code_conversion_error_strategy
        }
    
    def get_financial_reports_config(self) -> Dict[str, Any]:
        """
        获取财务报告相关的所有配置
        
        返回包含所有财务报告相关配置参数的字典。
        
        Returns:
            财务报告配置字典，包含以下键：
            - financial_reports_enabled: 是否启用财务报告功能
            - financial_reports_batch_size: 批处理最大股票数量
            - financial_reports_timeout: 请求超时时间
            - financial_reports_retry_attempts: 最大重试次数
            - financial_reports_retry_delay: 初始重试延迟
            - financial_reports_rate_limit: 每秒最大请求数
            - financial_reports_queue_size: 请求队列大小
            - financial_reports_enable_metrics: 是否启用性能指标收集
            - financial_reports_baostock_endpoint: Baostock API端点
            - financial_reports_auth_required: 是否需要认证
            - financial_reports_auth_token: 认证令牌
            
        Example:
            >>> config = Config()
            >>> fr_config = config.get_financial_reports_config()
            >>> print(fr_config['financial_reports_batch_size'])  # 50
        """
        return {
            'financial_reports_enabled': self.financial_reports_enabled,
            'financial_reports_batch_size': self.financial_reports_batch_size,
            'financial_reports_timeout': self.financial_reports_timeout,
            'financial_reports_retry_attempts': self.financial_reports_retry_attempts,
            'financial_reports_retry_delay': self.financial_reports_retry_delay,
            'financial_reports_rate_limit': self.financial_reports_rate_limit,
            'financial_reports_queue_size': self.financial_reports_queue_size,
            'financial_reports_enable_metrics': self.financial_reports_enable_metrics,
            'financial_reports_baostock_endpoint': self.financial_reports_baostock_endpoint,
            'financial_reports_auth_required': self.financial_reports_auth_required,
            'financial_reports_auth_token': self.financial_reports_auth_token
        }
    
    def set_financial_reports_batch_size(self, batch_size: int):
        """
        设置财务报告批处理大小
        
        Args:
            batch_size: 批处理大小
            
        Raises:
            ValidationError: 参数无效
        """
        if not isinstance(batch_size, int) or batch_size <= 0:
            raise ValidationError("batch_size必须是大于0的整数")
        
        self.financial_reports_batch_size = batch_size
    
    def set_financial_reports_rate_limit(self, rate_limit: float):
        """
        设置财务报告API速率限制
        
        Args:
            rate_limit: 每秒最大请求数
            
        Raises:
            ValidationError: 参数无效
        """
        if not isinstance(rate_limit, (int, float)) or rate_limit <= 0:
            raise ValidationError("rate_limit必须是大于0的数字")
        
        self.financial_reports_rate_limit = float(rate_limit)
    
    def set_financial_reports_retry_config(self, retry_attempts: int, retry_delay: float):
        """
        设置财务报告重试配置
        
        Args:
            retry_attempts: 最大重试次数
            retry_delay: 初始重试延迟（秒）
            
        Raises:
            ValidationError: 参数无效
        """
        if not isinstance(retry_attempts, int) or retry_attempts < 0:
            raise ValidationError("retry_attempts必须是非负整数")
        
        if not isinstance(retry_delay, (int, float)) or retry_delay < 0:
            raise ValidationError("retry_delay必须是非负数字")
        
        self.financial_reports_retry_attempts = retry_attempts
        self.financial_reports_retry_delay = float(retry_delay)
    
    def enable_financial_reports(self, enable: bool = True):
        """
        启用或禁用财务报告功能
        
        Args:
            enable: 是否启用财务报告功能
        """
        self.financial_reports_enabled = enable
    
    def set_financial_reports_auth(self, auth_token: Optional[str] = None, auth_required: bool = False):
        """
        设置财务报告API认证
        
        Args:
            auth_token: 认证令牌
            auth_required: 是否需要认证
        """
        self.financial_reports_auth_token = auth_token
        self.financial_reports_auth_required = auth_required
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将配置对象转换为字典
        
        将所有配置参数转换为字典格式，便于序列化或查看。
        
        Returns:
            包含所有配置参数的字典
            
        Example:
            >>> config = Config(request_timeout=60)
            >>> config_dict = config.to_dict()
            >>> print(config_dict['request_timeout'])  # 60
        """
        return asdict(self)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Config(tushare_token={'***' if self.tushare_token else None})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()