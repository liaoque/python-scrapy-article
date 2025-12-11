"""
QuickStock SDK主客户端类

提供统一的金融数据访问接口，类似tushare的调用方式
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Union, List, Tuple
import pandas as pd

from .config import Config
from .core.data_manager import DataManager
from .models import DataRequest
from .core.errors import QuickStockError, ValidationError
from .utils.validators import validate_stock_code, validate_date_format
from .utils.code_converter import normalize_stock_code, convert_stock_code


class QuickStockClient:
    """
    QuickStock SDK的主入口类
    提供统一的数据访问接口
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化客户端
        
        Args:
            config: 配置对象，包含数据源配置等
            
        Raises:
            QuickStockError: 初始化失败
        """
        try:
            # 加载配置
            self.config = config or Config.load_default()
            
            # 设置日志
            self._setup_logging()
            
            # 初始化数据管理器
            self.data_manager = DataManager(self.config)
            
            # 客户端状态
            self._initialized = True
            
            self.logger.info("QuickStock客户端初始化成功")
            
        except Exception as e:
            error_msg = f"QuickStock客户端初始化失败: {e}"
            if hasattr(self, 'logger'):
                self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def _setup_logging(self):
        """设置日志配置"""
        self.logger = logging.getLogger('quickstock')
        
        # 如果已经配置过日志，直接返回
        if self.logger.handlers:
            return
        
        # 设置日志级别
        self.logger.setLevel(getattr(logging, self.config.log_level.upper()))
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（如果配置了日志文件）
        if self.config.log_file:
            try:
                import os
                os.makedirs(os.path.dirname(self.config.log_file), exist_ok=True)
                
                file_handler = logging.FileHandler(self.config.log_file, encoding='utf-8')
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                self.logger.warning(f"无法创建日志文件: {e}")
    
    def _ensure_initialized(self):
        """确保客户端已正确初始化"""
        if not hasattr(self, '_initialized') or not self._initialized:
            raise QuickStockError("客户端未正确初始化")
    
    def _is_standard_format(self, code: str) -> bool:
        """
        检查是否为标准格式代码
        
        Args:
            code: 股票代码
            
        Returns:
            是否为标准格式
        """
        if not code or not isinstance(code, str):
            return False
        
        code = code.strip()
        
        # 只接受标准格式：6位数字.交易所代码
        import re
        pattern = r'^[0-9]{6}\.(SH|SZ)$'
        return bool(re.match(pattern, code, re.IGNORECASE))
    
    def _run_async(self, coro):
        """
        运行异步协程
        
        Args:
            coro: 异步协程
            
        Returns:
            协程执行结果
        """
        import inspect
        
        # 如果不是协程，直接返回
        if not inspect.iscoroutine(coro):
            return coro
        
        try:
            # 尝试获取当前事件循环
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 在运行的事件循环中，使用新线程运行协程
                import threading
                import concurrent.futures
                
                def run_coro():
                    new_loop = asyncio.new_event_loop()
                    try:
                        return new_loop.run_until_complete(coro)
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_coro)
                    return future.result()
            else:
                # 如果在同步环境中，直接运行协程
                return loop.run_until_complete(coro)
        except RuntimeError:
            # 没有事件循环，创建新的
            return asyncio.run(coro)
    
    def get_config(self) -> Config:
        """
        获取当前配置
        
        Returns:
            配置对象
        """
        self._ensure_initialized()
        return self.config
    
    def update_config(self, **kwargs):
        """
        更新配置参数
        
        Args:
            **kwargs: 要更新的配置参数
            
        Raises:
            ValidationError: 配置参数无效
        """
        self._ensure_initialized()
        
        try:
            self.config.update(**kwargs)
            self.logger.info(f"配置已更新: {list(kwargs.keys())}")
        except Exception as e:
            raise ValidationError(f"配置更新失败: {e}") from e
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """
        获取数据源统计信息
        
        Returns:
            数据源统计信息字典
        """
        self._ensure_initialized()
        return self.data_manager.source_manager.get_provider_stats()
    
    def get_provider_health(self) -> Dict[str, Any]:
        """
        获取数据源健康状态
        
        Returns:
            数据源健康状态字典
        """
        self._ensure_initialized()
        return self.data_manager.source_manager.get_provider_health()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        获取内存统计信息
        
        Returns:
            内存统计信息字典
        """
        self._ensure_initialized()
        return self.data_manager.get_memory_stats()
    
    def optimize_memory_usage(self) -> Dict[str, Any]:
        """
        优化内存使用
        
        Returns:
            优化后的内存统计信息
        """
        self._ensure_initialized()
        return self.data_manager.optimize_memory_usage()
    
    def health_check(self) -> Dict[str, bool]:
        """
        执行健康检查
        
        Returns:
            健康检查结果
        """
        self._ensure_initialized()
        
        try:
            # 异步健康检查
            coro = self.data_manager.source_manager.health_check_all()
            return self._run_async(coro)
        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            return {}
    
    def test_connection(self, provider_name: str = None) -> bool:
        """
        测试数据源连接
        
        Args:
            provider_name: 数据源名称，如果为None则测试所有数据源
            
        Returns:
            连接测试结果
        """
        self._ensure_initialized()
        
        try:
            if provider_name:
                # 测试指定数据源
                coro = self.data_manager.source_manager.test_provider(provider_name)
                return self._run_async(coro)
            else:
                # 测试所有数据源
                health_results = self.health_check()
                return any(health_results.values()) if health_results else False
        except Exception as e:
            self.logger.error(f"连接测试失败: {e}")
            return False
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        # 清理资源
        try:
            if hasattr(self, 'data_manager'):
                # 这里可以添加清理逻辑
                pass
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.warning(f"资源清理时出现警告: {e}")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        # 异步清理资源
        try:
            if hasattr(self, 'data_manager'):
                # 清理数据源连接
                if hasattr(self.data_manager, 'source_manager'):
                    await self.data_manager.source_manager.close_all()
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.warning(f"异步资源清理时出现警告: {e}")
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"QuickStockClient(initialized={getattr(self, '_initialized', False)})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()
    
    # 代码转换工具方法
    def normalize_code(self, code: str) -> str:
        """
        标准化股票代码
        
        支持多种格式的股票代码输入，统一转换为标准格式 (000001.SZ)
        
        Args:
            code: 股票代码，支持以下格式：
                - 标准格式: 000001.SZ, 600000.SH
                - Baostock格式: sz.000001, sh.600000
                - 东方财富格式: 0.000001, 1.600000
                - 同花顺格式: hs_000001, hs_600000
                - 纯数字: 000001, 600000
        
        Returns:
            标准格式的股票代码
            
        Example:
            >>> client = QuickStockClient()
            >>> client.normalize_code('sh.600000')  # '600000.SH'
            >>> client.normalize_code('1.600000')   # '600000.SH'
            >>> client.normalize_code('hs_000001')  # '000001.SZ'
        """
        return normalize_stock_code(code)
    
    def convert_code(self, code: str, target_format: str) -> str:
        """
        转换股票代码到指定格式
        
        Args:
            code: 原始股票代码
            target_format: 目标格式
                - 'standard': 标准格式 (000001.SZ)
                - 'baostock': Baostock格式 (sz.000001)
                - 'eastmoney': 东方财富格式 (0.000001)
                - 'tonghuashun': 同花顺格式 (hs_000001)
        
        Returns:
            转换后的股票代码
            
        Example:
            >>> client = QuickStockClient()
            >>> client.convert_code('000001.SZ', 'baostock')    # 'sz.000001'
            >>> client.convert_code('600000.SH', 'eastmoney')   # '1.600000'
        """
        return convert_stock_code(code, target_format)
    
    def parse_code(self, code: str) -> Tuple[str, str]:
        """
        解析股票代码，返回代码和交易所
        
        Args:
            code: 股票代码，支持多种格式
        
        Returns:
            (股票代码, 交易所) 元组
            
        Example:
            >>> client = QuickStockClient()
            >>> client.parse_code('000001.SZ')     # ('000001', 'SZ')
            >>> client.parse_code('sh.600000')     # ('600000', 'SH')
            >>> client.parse_code('1.600000')      # ('600000', 'SH')
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.parse_stock_code(code)
    
    def validate_code(self, code: str) -> bool:
        """
        验证股票代码格式是否有效
        
        Args:
            code: 股票代码
        
        Returns:
            是否为有效的股票代码格式
            
        Example:
            >>> client = QuickStockClient()
            >>> client.validate_code('000001.SZ')    # True
            >>> client.validate_code('invalid')      # False
        """
        try:
            self.normalize_code(code)
            return True
        except Exception:
            return False
    
    def get_supported_formats(self) -> List[str]:
        """
        获取支持的股票代码格式列表
        
        Returns:
            支持的格式列表
            
        Example:
            >>> client = QuickStockClient()
            >>> client.get_supported_formats()
            ['standard', 'baostock', 'eastmoney', 'tonghuashun', 'exchange_prefix', 'pure_number']
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.get_supported_formats()
    
    def identify_code_format(self, code: str) -> Optional[str]:
        """
        识别股票代码格式
        
        Args:
            code: 股票代码
        
        Returns:
            格式名称，如果无法识别返回None
            
        Example:
            >>> client = QuickStockClient()
            >>> client.identify_code_format('000001.SZ')    # 'standard'
            >>> client.identify_code_format('sh.600000')    # 'baostock'
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.identify_code_format(code)
    
    def suggest_code_corrections(self, code: str) -> List[str]:
        """
        为无效代码提供修正建议
        
        Args:
            code: 无效的股票代码
        
        Returns:
            修正建议列表
            
        Example:
            >>> client = QuickStockClient()
            >>> client.suggest_code_corrections('000001.sz')
            ['尝试: 000001.SZ']
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.suggest_code_corrections(code)
    
    def batch_normalize_codes(self, codes: List[str]) -> List[str]:
        """
        批量标准化股票代码
        
        Args:
            codes: 股票代码列表
        
        Returns:
            标准化后的股票代码列表
            
        Example:
            >>> client = QuickStockClient()
            >>> client.batch_normalize_codes(['000001.SZ', 'sh.600000'])
            ['000001.SZ', '600000.SH']
        """
        from .utils.code_converter import batch_normalize_codes
        return batch_normalize_codes(codes)
    
    def batch_convert_codes(self, codes: List[str], target_format: str) -> List[str]:
        """
        批量转换股票代码到指定格式
        
        Args:
            codes: 股票代码列表
            target_format: 目标格式
        
        Returns:
            转换后的股票代码列表
            
        Example:
            >>> client = QuickStockClient()
            >>> client.batch_convert_codes(['000001.SZ', '600000.SH'], 'baostock')
            ['sz.000001', 'sh.600000']
        """
        from .utils.code_converter import batch_convert_codes
        return batch_convert_codes(codes, target_format)
    
    def validate_code_with_details(self, code: str) -> Dict[str, Any]:
        """
        验证股票代码并返回详细信息
        
        Args:
            code: 股票代码
        
        Returns:
            详细的验证结果字典，包含：
            - is_valid: 是否有效
            - issues: 检测到的问题列表
            - suggestions: 修正建议列表
            - detected_format: 检测到的格式
            - parsed_code: 解析后的代码
            - parsed_exchange: 解析后的交易所
            
        Example:
            >>> client = QuickStockClient()
            >>> result = client.validate_code_with_details('000001.sz')
            >>> print(result['suggestions'])
            ['尝试: 000001.SZ']
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.validate_code_with_details(code)
    
    def get_code_format_help(self, format_name: str = None) -> Dict[str, Any]:
        """
        获取股票代码格式帮助信息
        
        Args:
            format_name: 格式名称，如果为None则返回所有格式的帮助
        
        Returns:
            格式帮助信息字典
            
        Example:
            >>> client = QuickStockClient()
            >>> help_info = client.get_code_format_help('standard')
            >>> print(help_info['description'])
            '6位数字代码 + 点号 + 交易所代码(SH/SZ)'
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.get_format_help(format_name)
    
    def suggest_code_auto_correction(self, code: str) -> Dict[str, Any]:
        """
        为无效代码提供自动修正建议
        
        Args:
            code: 无效的股票代码
        
        Returns:
            自动修正建议字典，包含：
            - can_auto_correct: 是否可以自动修正
            - corrections: 修正选项列表（按置信度排序）
            - suggestions: 人工建议列表
            
        Example:
            >>> client = QuickStockClient()
            >>> suggestions = client.suggest_code_auto_correction('000001.sz')
            >>> if suggestions['can_auto_correct']:
            ...     best_correction = suggestions['corrections'][0]
            ...     print(f"建议修正为: {best_correction['corrected']}")
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.suggest_auto_correction(code)
    
    def get_validation_help(self) -> Dict[str, Any]:
        """
        获取代码验证帮助信息
        
        Returns:
            验证帮助信息字典，包含：
            - supported_formats: 支持的格式详情
            - validation_rules: 验证规则
            - common_errors: 常见错误及解决方案
            - examples: 有效和无效代码示例
            
        Example:
            >>> client = QuickStockClient()
            >>> help_info = client.get_validation_help()
            >>> print("支持的格式:")
            >>> for fmt, info in help_info['supported_formats'].items():
            ...     print(f"  {info['name']}: {info['pattern']}")
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.get_validation_help()
    
    def batch_validate_codes(self, codes: List[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        批量验证股票代码
        
        Args:
            codes: 股票代码列表
        
        Returns:
            (成功结果列表, 错误信息列表) 元组
            
        Example:
            >>> client = QuickStockClient()
            >>> codes = ['000001.SZ', '600000.SH', 'invalid']
            >>> valid, invalid = client.batch_validate_codes(codes)
            >>> print(f"有效代码: {len(valid)}, 无效代码: {len(invalid)}")
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.batch_convert_codes_with_errors(codes, 'standard')
    
    def _validate_and_normalize_code(self, ts_code: str, param_name: str = "股票代码") -> str:
        """
        验证并标准化股票代码（向后兼容版本）
        
        Args:
            ts_code: 股票代码
            param_name: 参数名称（用于错误信息）
            
        Returns:
            标准化后的股票代码
            
        Raises:
            ValidationError: 代码验证失败
        """
        if not ts_code:
            raise ValidationError(f"{param_name}不能为空")
        
        # 保存原始代码用于错误信息
        original_code = ts_code
        
        # 检查是否启用自动代码转换
        if not self.config.enable_auto_code_conversion:
            # 向后兼容模式：只验证标准格式代码
            if not self._is_standard_format(ts_code):
                raise ValidationError(f"{param_name}格式无效: {original_code}. 请使用标准格式（如：000001.SZ）")
            return ts_code
        
        try:
            # 自动标准化股票代码
            ts_code = self.normalize_code(ts_code)
            
            # 记录转换日志（如果启用）
            if self.config.log_code_conversions and original_code != ts_code:
                self.logger.debug(f"{param_name}标准化: {original_code} -> {ts_code}")
            
            # 验证标准化后的代码
            if not validate_stock_code(ts_code):
                raise ValidationError(f"{param_name}格式无效: {original_code}")
                
            return ts_code
            
        except Exception as e:
            # 根据错误处理策略处理异常
            return self._handle_code_validation_error(e, original_code, param_name)
    
    def _handle_code_validation_error(self, error: Exception, original_code: str, param_name: str) -> str:
        """
        处理代码验证错误（向后兼容）
        
        Args:
            error: 原始异常
            original_code: 原始代码
            param_name: 参数名称
            
        Returns:
            处理后的代码（如果可能）
            
        Raises:
            ValidationError: 无法处理的验证错误
        """
        # 如果是ImportError，说明代码转换器不可用，使用回退逻辑
        if isinstance(error, ImportError):
            # 在回退模式下，只接受标准格式代码
            if self._is_standard_format(original_code):
                return original_code
            raise ValidationError(f"{param_name}格式无效: {original_code}")
        
        # 导入新的异常类型
        try:
            from .utils.code_converter import CodeConversionError, InvalidCodeFormatError, ExchangeInferenceError
        except ImportError:
            # 如果新的转换器不可用，使用旧的验证逻辑（只接受标准格式）
            if self._is_standard_format(original_code):
                return original_code
            raise ValidationError(f"{param_name}格式无效: {original_code}")
        
        error_strategy = self.config.code_conversion_error_strategy
        
        if isinstance(error, CodeConversionError):
            if error_strategy == 'ignore':
                # 忽略错误，使用原始代码
                self.logger.warning(f"{param_name}转换失败，使用原始代码: {original_code}")
                return original_code
            elif error_strategy == 'lenient':
                # 宽松模式：尝试使用原始代码或提供建议
                if validate_stock_code(original_code):
                    self.logger.warning(f"{param_name}转换失败，但原始代码有效: {original_code}")
                    return original_code
                else:
                    # 提供用户友好的错误信息
                    error_msg = f"{param_name}验证失败: {error.get_user_friendly_message()}"
                    self.logger.warning(error_msg)
                    raise ValidationError(error_msg)
            else:  # strict
                error_msg = f"{param_name}验证失败: {error.get_user_friendly_message()}"
                self.logger.warning(error_msg)
                raise ValidationError(error_msg)
        
        elif isinstance(error, ValidationError):
            if error_strategy == 'ignore':
                self.logger.warning(f"{param_name}验证失败，使用原始代码: {original_code}")
                return original_code
            elif error_strategy == 'lenient':
                # 增强现有的ValidationError
                error_msg = f"{param_name}格式无效: {original_code}"
                if hasattr(error, 'suggestions') and error.suggestions:
                    error_msg += f". 建议: {'; '.join(error.suggestions[:3])}"
                raise ValidationError(error_msg)
            else:  # strict
                raise error
        
        else:
            # 其他异常（包括一般的Exception）
            if error_strategy == 'ignore':
                self.logger.warning(f"{param_name}验证时发生未知错误，使用原始代码: {original_code}")
                return original_code
            elif error_strategy == 'lenient':
                # 宽松模式：如果原始代码有效，使用原始代码
                if validate_stock_code(original_code):
                    self.logger.warning(f"{param_name}转换失败，但原始代码有效: {original_code}")
                    return original_code
                else:
                    self.logger.warning(f"{param_name}验证时发生未知错误: {error}")
                    raise ValidationError(f"{param_name}格式无效: {original_code}")
            else:  # strict
                self.logger.warning(f"{param_name}验证时发生未知错误: {error}")
                raise ValidationError(f"{param_name}格式无效: {original_code}")
    
    # 股票相关接口
    def stock_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取股票基础信息
        
        Args:
            **kwargs: 查询参数
                - exchange: 交易所代码 (SSE上交所, SZSE深交所)
                - list_status: 上市状态 (L上市, D退市, P暂停)
                - fields: 指定返回字段
                - limit: 限制返回条数
                
        Returns:
            包含股票基础信息的DataFrame
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 创建数据请求
            request = DataRequest(
                data_type='stock_basic',
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取股票基础信息成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取股票基础信息失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def stock_detail(self, ts_code: str = None, type: str = None, status: str = None, **kwargs) -> pd.DataFrame:
        """
        获取证券基本资料（详细信息）
        
        使用 Baostock 数据源获取股票的详细信息，包括上市日期、退市日期、股票类型、股票状态等。
        
        Args:
            ts_code: 股票代码（可选），支持多种格式：
                - 标准格式: 000001.SZ, 600000.SH
                - Baostock格式: sz.000001, sh.600000
                - 纯数字: 000001, 600000
                - 如果不指定（None）：返回所有股票的详细资料
            type: 证券类型（可选），用于筛选：
                - '1': 股票
                - '2': 指数
                - '3': 其它
                - '4': 可转债
                - '5': ETF
                - 如果不指定：返回所有类型
            status: 上市状态（可选），用于筛选：
                - '1': 上市
                - '0': 退市
                - 如果不指定：返回所有状态
            **kwargs: 其他参数（预留）
        
        Returns:
            包含证券基本资料的DataFrame，字段包括（保留 baostock 原始字段名）：
            - code: 证券代码（baostock 格式，如 sz.000001）
            - code_name: 证券名称
            - ipoDate: 上市日期 (YYYY-MM-DD)
            - outDate: 退市日期 (YYYY-MM-DD)
            - type: 证券类型 (1:股票, 2:指数, 3:其它, 4:可转债, 5:ETF)
            - status: 上市状态 (1:上市, 0:退市)
        
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        
        Example:
            >>> client = QuickStockClient()
            >>> 
            >>> # 获取单只股票
            >>> detail = client.stock_detail('000001.SZ')
            >>> print(detail[['code', 'code_name', 'ipoDate', 'status']])
            >>> 
            >>> # 获取所有上市股票（不包括退市）
            >>> stocks = client.stock_detail(type='1', status='1')
            >>> print(f"共 {len(stocks)} 只上市股票")
            >>> 
            >>> # 获取所有指数
            >>> indices = client.stock_detail(type='2')
            >>> print(f"共 {len(indices)} 个指数")
            >>> 
            >>> # 获取所有ETF
            >>> etfs = client.stock_detail(type='5', status='1')
            >>> print(f"共 {len(etfs)} 只ETF")
            >>> 
            >>> # 获取所有退市股票
            >>> delisted = client.stock_detail(status='0')
            >>> print(f"共 {len(delisted)} 只退市股票")
        
        Note:
            此方法目前仅支持 Baostock 数据源
        """
        self._ensure_initialized()
        
        try:
            # 参数验证
            if type is not None and type not in ['1', '2', '3', '4', '5']:
                raise ValidationError(
                    f"无效的证券类型: {type}. 必须是 '1'(股票), '2'(指数), '3'(其它), '4'(可转债), '5'(ETF) 之一"
                )
            
            if status is not None and status not in ['0', '1']:
                raise ValidationError(
                    f"无效的上市状态: {status}. 必须是 '0'(退市) 或 '1'(上市)"
                )
            
            # 如果指定了股票代码，验证并标准化
            if ts_code:
                ts_code = self._validate_and_normalize_code(ts_code, "股票代码")
                self.logger.info(f"开始获取股票 {ts_code} 的基本资料")
            else:
                filter_desc = []
                if type:
                    type_names = {'1': '股票', '2': '指数', '3': '其它', '4': '可转债', '5': 'ETF'}
                    filter_desc.append(f"类型={type_names.get(type, type)}")
                if status:
                    status_names = {'0': '退市', '1': '上市'}
                    filter_desc.append(f"状态={status_names.get(status, status)}")
                
                if filter_desc:
                    self.logger.info(f"开始获取股票基本资料（筛选条件: {', '.join(filter_desc)}）")
                else:
                    self.logger.info("开始获取所有股票的基本资料")
            
            # 调用 Baostock Provider 的方法
            result = self._run_async(
                self.data_manager.source_manager.providers['baostock'].get_stock_detail(
                    ts_code=ts_code,
                    type=type,
                    status=status
                )
            )
            
            self.logger.info(f"获取股票基本资料成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取股票基本资料失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
        
    def stock_daily(self, ts_code: str, start_date: str = None, 
                   end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取股票日线数据
        
        Args:
            ts_code: 股票代码，支持多种格式：
                - 标准格式: 000001.SZ, 600000.SH
                - Baostock格式: sz.000001, sh.600000  
                - 东方财富格式: 0.000001, 1.600000
                - 同花顺格式: hs_000001, hs_600000
                - 纯数字: 000001, 600000
            start_date: 开始日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            **kwargs: 其他参数
                - adj: 复权类型 (None不复权, qfq前复权, hfq后复权)
                - fields: 指定返回字段
                
        Returns:
            包含股票日线数据的DataFrame
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 使用增强的代码验证和标准化
            ts_code = self._validate_and_normalize_code(ts_code, "股票代码")
            
            if start_date and not validate_date_format(start_date):
                raise ValidationError(f"开始日期格式无效: {start_date}")
            
            if end_date and not validate_date_format(end_date):
                raise ValidationError(f"结束日期格式无效: {end_date}")
            
            # 创建数据请求
            request = DataRequest(
                data_type='stock_daily',
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取股票{ts_code}日线数据成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取股票日线数据失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
        
    def stock_minute(self, ts_code: str, freq: str = '1min', 
                    start_date: str = None, end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取股票分钟数据
        
        Args:
            ts_code: 股票代码 (如: 000001.SZ)
            freq: 频率 (1min, 5min, 15min, 30min, 60min)
            start_date: 开始日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            **kwargs: 其他参数
                - adj: 复权类型
                - fields: 指定返回字段
                
        Returns:
            包含股票分钟数据的DataFrame
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 使用增强的代码验证和标准化
            ts_code = self._validate_and_normalize_code(ts_code, "股票代码")
            
            valid_freqs = ['1min', '5min', '15min', '30min', '60min']
            if freq not in valid_freqs:
                raise ValidationError(f"频率参数无效: {freq}，支持的频率: {valid_freqs}")
            
            if start_date and not validate_date_format(start_date):
                raise ValidationError(f"开始日期格式无效: {start_date}")
            
            if end_date and not validate_date_format(end_date):
                raise ValidationError(f"结束日期格式无效: {end_date}")
            
            # 创建数据请求
            request = DataRequest(
                data_type='stock_minute',
                ts_code=ts_code,
                freq=freq,
                start_date=start_date,
                end_date=end_date,
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取股票{ts_code}分钟数据({freq})成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取股票分钟数据失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def stock_weekly(self, ts_code: str, start_date: str = None, 
                    end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取股票周线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数
                
        Returns:
            包含股票周线数据的DataFrame
        """
        self._ensure_initialized()
        
        try:
            # 使用增强的代码验证和标准化
            ts_code = self._validate_and_normalize_code(ts_code, "股票代码")
            
            # 创建数据请求
            request = DataRequest(
                data_type='stock_weekly',
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取股票{ts_code}周线数据成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取股票周线数据失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def price_distribution_stats(self, trade_date: str, **kwargs) -> Union[pd.DataFrame, Dict[str, Any], str]:
        """
        获取股票涨跌分布统计
        
        从数据源实时获取指定交易日的股票涨跌分布统计数据，包括不同涨跌幅区间的股票数量和百分比。
        
        Args:
            trade_date: 交易日期 (YYYYMMDD 或 YYYY-MM-DD)
            **kwargs: 其他参数
                - include_st: 是否包含ST股票 (默认True)
                - market_filter: 市场过滤器 ['shanghai', 'shenzhen', 'star', 'beijing', 'total', 'non_st', 'st']
                - custom_ranges: 自定义区间定义 Dict[str, Tuple[float, float]]
                - format: 返回格式 ('dataframe', 'dict', 'json') (默认'dataframe')
                - force_refresh: 是否强制从数据源刷新 (默认False)
                - timeout: 请求超时时间（秒）(默认30)
        
        Returns:
            涨跌分布统计结果，格式根据format参数决定：
            - 'dataframe': pandas DataFrame
            - 'dict': 字典格式
            - 'json': JSON字符串
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
            
        Example:
            >>> client = QuickStockClient()
            >>> # 获取DataFrame格式结果
            >>> df = client.price_distribution_stats('20240315')
            >>> 
            >>> # 获取字典格式结果，只包含非ST股票
            >>> result = client.price_distribution_stats(
            ...     '2024-03-15', 
            ...     include_st=False,
            ...     format='dict'
            ... )
            >>> 
            >>> # 使用自定义区间
            >>> custom_ranges = {
            ...     '0-2%': (0.0, 2.0),
            ...     '2-5%': (2.0, 5.0),
            ...     '>=5%': (5.0, float('inf'))
            ... }
            >>> df = client.price_distribution_stats(
            ...     '20240315',
            ...     custom_ranges=custom_ranges
            ... )
        """
        self._ensure_initialized()
        
        try:
            # 导入必要的模块
            from .services.price_distribution_stats_service import PriceDistributionStatsService
            from .models.price_distribution_models import PriceDistributionRequest
            import json
            
            # 参数验证和标准化
            format_type = kwargs.get('format', 'dataframe').lower()
            if format_type not in ['dataframe', 'dict', 'json']:
                raise ValidationError(f"Invalid format: {format_type}. Valid options: dataframe, dict, json")
            
            include_st = kwargs.get('include_st', True)
            market_filter = kwargs.get('market_filter', None)
            custom_ranges = kwargs.get('custom_ranges', None)
            force_refresh = kwargs.get('force_refresh', False)
            timeout = kwargs.get('timeout', 30)
            
            # 创建请求对象
            request = PriceDistributionRequest(
                trade_date=trade_date,
                include_st=include_st,
                market_filter=market_filter,
                distribution_ranges=custom_ranges,
                force_refresh=force_refresh,
                save_to_db=False,  # 不再保存到数据库
                timeout=timeout
            )
            
            # 创建服务实例
            service = PriceDistributionStatsService(self.data_manager, self.logger)
            
            # 获取统计数据
            coro = service.get_price_distribution_stats(request)
            stats = self._run_async(coro)
            
            # 根据格式返回结果
            if format_type == 'dict':
                result = stats.to_dict()
            elif format_type == 'json':
                result = json.dumps(stats.to_dict(), ensure_ascii=False, indent=2)
            else:  # dataframe
                result = self._convert_stats_to_dataframe(stats)
            
            self.logger.info(f"获取涨跌分布统计成功: {trade_date}, 总股票数: {stats.total_stocks}")
            return result
            
        except Exception as e:
            error_msg = f"获取涨跌分布统计失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def _convert_stats_to_dataframe(self, stats) -> pd.DataFrame:
        """
        将统计结果转换为DataFrame格式
        
        Args:
            stats: PriceDistributionStats对象
            
        Returns:
            DataFrame格式的统计结果
        """
        try:
            # 准备数据行
            rows = []
            
            # 添加总体统计
            summary = stats.get_summary()
            rows.append({
                'market': 'total',
                'market_name': '总体市场',
                'total_stocks': summary['total_stocks'],
                'positive_count': summary['positive_count'],
                'negative_count': summary['negative_count'],
                'positive_percentage': summary['positive_percentage'],
                'negative_percentage': summary['negative_percentage']
            })
            
            # 添加各市场统计
            market_names = {
                'shanghai': '上海证券交易所',
                'shenzhen': '深圳证券交易所',
                'star': '科创板',
                'beijing': '北京证券交易所',
                'non_st': '非ST股票',
                'st': 'ST股票'
            }
            
            for market, market_name in market_names.items():
                market_summary = stats.get_market_summary(market)
                if market_summary:
                    rows.append({
                        'market': market,
                        'market_name': market_name,
                        'total_stocks': market_summary['total_stocks'],
                        'positive_count': market_summary['positive_count'],
                        'negative_count': market_summary['negative_count'],
                        'positive_percentage': round(market_summary['positive_count'] / market_summary['total_stocks'] * 100, 2) if market_summary['total_stocks'] > 0 else 0,
                        'negative_percentage': round(market_summary['negative_count'] / market_summary['total_stocks'] * 100, 2) if market_summary['total_stocks'] > 0 else 0
                    })
            
            # 创建基础DataFrame
            df = pd.DataFrame(rows)
            
            # 添加详细的区间分布数据
            for range_name in stats.positive_ranges.keys():
                df[f'positive_{range_name}'] = 0
                df[f'positive_{range_name}_pct'] = 0.0
            
            for range_name in stats.negative_ranges.keys():
                df[f'negative_{range_name}'] = 0
                df[f'negative_{range_name}_pct'] = 0.0
            
            # 填充总体市场的区间数据
            for i, row in df.iterrows():
                market = row['market']
                if market == 'total':
                    # 填充正涨幅区间
                    for range_name, count in stats.positive_ranges.items():
                        df.at[i, f'positive_{range_name}'] = count
                        df.at[i, f'positive_{range_name}_pct'] = stats.positive_percentages.get(range_name, 0.0)
                    
                    # 填充负涨幅区间
                    for range_name, count in stats.negative_ranges.items():
                        df.at[i, f'negative_{range_name}'] = count
                        df.at[i, f'negative_{range_name}_pct'] = stats.negative_percentages.get(range_name, 0.0)
                
                elif market in stats.market_breakdown:
                    market_data = stats.market_breakdown[market]
                    
                    # 填充正涨幅区间
                    for range_name, count in market_data.get('positive_ranges', {}).items():
                        df.at[i, f'positive_{range_name}'] = count
                        df.at[i, f'positive_{range_name}_pct'] = market_data.get('positive_percentages', {}).get(range_name, 0.0)
                    
                    # 填充负涨幅区间
                    for range_name, count in market_data.get('negative_ranges', {}).items():
                        df.at[i, f'negative_{range_name}'] = count
                        df.at[i, f'negative_{range_name}_pct'] = market_data.get('negative_percentages', {}).get(range_name, 0.0)
            
            # 添加元数据列
            df['trade_date'] = stats.trade_date
            df['formatted_date'] = stats.get_formatted_date()
            df['processing_time'] = stats.processing_time
            df['data_quality_score'] = stats.data_quality_score
            df['created_at'] = stats.created_at
            
            # 重新排列列顺序
            base_columns = ['trade_date', 'formatted_date', 'market', 'market_name', 
                          'total_stocks', 'positive_count', 'negative_count', 
                          'positive_percentage', 'negative_percentage']
            
            range_columns = [col for col in df.columns if col.startswith(('positive_', 'negative_')) and col not in base_columns]
            meta_columns = ['processing_time', 'data_quality_score', 'created_at']
            
            df = df[base_columns + sorted(range_columns) + meta_columns]
            
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to convert stats to DataFrame: {e}")
            # 返回简化的DataFrame
            return pd.DataFrame([{
                'trade_date': stats.trade_date,
                'total_stocks': stats.total_stocks,
                'positive_count': stats.get_total_positive_count(),
                'negative_count': stats.get_total_negative_count(),
                'error': str(e)
            }])
    
    # ==================== 涨停统计相关接口 ====================
    
    def daily_limit_up_stats(self, trade_date: str, **kwargs) -> Dict[str, int]:
        """
        获取指定日期的涨停统计数据
        
        从数据源实时获取指定交易日的涨停股票统计信息，包括总涨停数量、各市场涨停数量等。
        
        Args:
            trade_date: 交易日期 (YYYYMMDD 或 YYYY-MM-DD)
            **kwargs: 其他参数
                - force_refresh: 是否强制从数据源刷新 (默认False)
                - include_st: 是否包含ST股票 (默认True)
                - market_filter: 市场过滤器列表 (可选)
                - timeout: 请求超时时间 (默认30秒)
                
        Returns:
            涨停统计字典，包含：
            - total: 总涨停数量
            - non_st: 非ST涨停数量  
            - shanghai: 上证涨停数量
            - shenzhen: 深证涨停数量
            - star: 科创板涨停数量
            - beijing: 北证涨停数量
            - st: ST涨停数量
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
            
        Example:
            >>> client = QuickStockClient()
            >>> stats = client.daily_limit_up_stats('20241015')
            >>> print(f"总涨停数量: {stats['total']}")
            >>> print(f"非ST涨停: {stats['non_st']}")
        """
        self._ensure_initialized()
        
        try:
            from .models import LimitUpStatsRequest
            from .services.limit_up_stats_service import LimitUpStatsService
            from .core.repository import LimitUpStatsRepository
            
            # 创建涨停统计请求
            request = LimitUpStatsRequest(
                trade_date=trade_date,
                include_st=kwargs.get('include_st', True),
                market_filter=kwargs.get('market_filter'),
                force_refresh=kwargs.get('force_refresh', False),
                save_to_db=False,  # 不再保存到数据库
                timeout=kwargs.get('timeout', 30)
            )
            
            # 从数据源获取
            service = LimitUpStatsService(self.data_manager, self.logger)
            stats_result = self._run_async(service.get_daily_limit_up_stats(request))
            
            self.logger.info(f"获取 {request.trade_date} 涨停统计成功: 总计 {stats_result.total}")
            return stats_result.get_summary()
            
        except Exception as e:
            error_msg = f"获取涨停统计失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    


    
    def stock_monthly(self, ts_code: str, start_date: str = None, 
                     end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取股票月线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数
                
        Returns:
            包含股票月线数据的DataFrame
        """
        self._ensure_initialized()
        
        try:
            # 使用增强的代码验证和标准化
            ts_code = self._validate_and_normalize_code(ts_code, "股票代码")
            
            # 创建数据请求
            request = DataRequest(
                data_type='stock_monthly',
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取股票{ts_code}月线数据成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取股票月线数据失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    # 指数相关接口
    def index_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取指数基础信息
        
        Args:
            **kwargs: 查询参数
                - market: 市场代码 (SSE上交所, SZSE深交所, CSI中证)
                - publisher: 发布商
                - category: 指数类别
                - fields: 指定返回字段
                - limit: 限制返回条数
                
        Returns:
            包含指数基础信息的DataFrame
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 创建数据请求
            request = DataRequest(
                data_type='index_basic',
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取指数基础信息成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取指数基础信息失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
        
    def index_daily(self, ts_code: str, start_date: str = None,
                   end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取指数日线数据
        
        Args:
            ts_code: 指数代码 (如: 000001.SH)
            start_date: 开始日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            **kwargs: 其他参数
                - fields: 指定返回字段
                
        Returns:
            包含指数日线数据的DataFrame
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 参数验证
            if not ts_code:
                raise ValidationError("指数代码不能为空")
            
            if start_date and not validate_date_format(start_date):
                raise ValidationError(f"开始日期格式无效: {start_date}")
            
            if end_date and not validate_date_format(end_date):
                raise ValidationError(f"结束日期格式无效: {end_date}")
            
            # 创建数据请求
            request = DataRequest(
                data_type='index_daily',
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取指数{ts_code}日线数据成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取指数日线数据失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def index_weight(self, index_code: str, trade_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取指数成分股权重
        
        Args:
            index_code: 指数代码
            trade_date: 交易日期
            **kwargs: 其他参数
                
        Returns:
            包含指数成分股权重的DataFrame
        """
        self._ensure_initialized()
        
        try:
            # 参数验证
            if not index_code:
                raise ValidationError("指数代码不能为空")
            
            if trade_date and not validate_date_format(trade_date):
                raise ValidationError(f"交易日期格式无效: {trade_date}")
            
            # 创建数据请求
            request = DataRequest(
                data_type='index_weight',
                ts_code=index_code,
                start_date=trade_date,
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取指数{index_code}成分股权重成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取指数成分股权重失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    # 基金相关接口
    def fund_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取基金基础信息
        
        Args:
            **kwargs: 查询参数
                - market: 市场类型 (E场内, O场外)
                - fund_type: 基金类型
                - status: 基金状态 (D正常, I发行, L上市)
                - fields: 指定返回字段
                - limit: 限制返回条数
                
        Returns:
            包含基金基础信息的DataFrame
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 创建数据请求
            request = DataRequest(
                data_type='fund_basic',
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取基金基础信息成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取基金基础信息失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
        
    def fund_nav(self, ts_code: str, start_date: str = None,
                end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取基金净值数据
        
        Args:
            ts_code: 基金代码 (如: 110022.OF)
            start_date: 开始日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            **kwargs: 其他参数
                - fields: 指定返回字段
                
        Returns:
            包含基金净值数据的DataFrame
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 参数验证
            if not ts_code:
                raise ValidationError("基金代码不能为空")
            
            if start_date and not validate_date_format(start_date):
                raise ValidationError(f"开始日期格式无效: {start_date}")
            
            if end_date and not validate_date_format(end_date):
                raise ValidationError(f"结束日期格式无效: {end_date}")
            
            # 创建数据请求
            request = DataRequest(
                data_type='fund_nav',
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取基金{ts_code}净值数据成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取基金净值数据失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def fund_portfolio(self, ts_code: str, end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取基金持仓数据
        
        Args:
            ts_code: 基金代码
            end_date: 截止日期
            **kwargs: 其他参数
                
        Returns:
            包含基金持仓数据的DataFrame
        """
        self._ensure_initialized()
        
        try:
            # 参数验证
            if not ts_code:
                raise ValidationError("基金代码不能为空")
            
            if end_date and not validate_date_format(end_date):
                raise ValidationError(f"截止日期格式无效: {end_date}")
            
            # 创建数据请求
            request = DataRequest(
                data_type='fund_portfolio',
                ts_code=ts_code,
                end_date=end_date,
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取基金{ts_code}持仓数据成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取基金持仓数据失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    # 交易日历接口
    def trade_cal(self, exchange: str = 'SSE', start_date: str = None, 
                 end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取交易日历
        
        Args:
            exchange: 交易所代码 (SSE上交所, SZSE深交所)
            start_date: 开始日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            **kwargs: 其他参数
                - is_open: 是否交易日 (0休市, 1交易)
                - fields: 指定返回字段
                
        Returns:
            包含交易日历的DataFrame
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 参数验证
            if start_date and not validate_date_format(start_date):
                raise ValidationError(f"开始日期格式无效: {start_date}")
            
            if end_date and not validate_date_format(end_date):
                raise ValidationError(f"结束日期格式无效: {end_date}")
            
            # 创建数据请求
            request = DataRequest(
                data_type='trade_cal',
                start_date=start_date,
                end_date=end_date,
                extra_params={'exchange': exchange, **kwargs}
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取交易日历成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取交易日历失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
        
    def is_trade_date(self, date: str, exchange: str = 'SSE') -> bool:
        """
        判断是否为交易日
        
        Args:
            date: 日期字符串 (格式: YYYYMMDD 或 YYYY-MM-DD)
            exchange: 交易所代码 (SSE上交所, SZSE深交所)
            
        Returns:
            是否为交易日
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 参数验证
            if not date:
                raise ValidationError("日期不能为空")
            
            if not validate_date_format(date):
                raise ValidationError(f"日期格式无效: {date}")
            
            # 获取指定日期的交易日历
            trade_cal = self.trade_cal(
                exchange=exchange,
                start_date=date,
                end_date=date
            )
            
            if trade_cal.empty:
                # 如果没有找到记录，默认为非交易日
                return False
            
            # 检查is_open字段
            is_open = trade_cal.iloc[0].get('is_open', 0)
            result = bool(is_open)
            
            self.logger.debug(f"日期{date}交易日判断结果: {result}")
            return result
            
        except Exception as e:
            error_msg = f"交易日判断失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def get_trade_dates(self, start_date: str, end_date: str, 
                       exchange: str = 'SSE') -> List[str]:
        """
        获取指定时间范围内的交易日列表
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            exchange: 交易所代码
            
        Returns:
            交易日列表
        """
        self._ensure_initialized()
        
        try:
            # 获取交易日历
            trade_cal = self.trade_cal(
                exchange=exchange,
                start_date=start_date,
                end_date=end_date
            )
            
            # 筛选交易日
            trade_dates = trade_cal[trade_cal['is_open'] == 1]['cal_date'].tolist()
            
            self.logger.info(f"获取交易日列表成功，共{len(trade_dates)}个交易日")
            return trade_dates
            
        except Exception as e:
            error_msg = f"获取交易日列表失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def get_prev_trade_date(self, date: str, exchange: str = 'SSE') -> Optional[str]:
        """
        获取指定日期的上一个交易日
        
        Args:
            date: 指定日期
            exchange: 交易所代码
            
        Returns:
            上一个交易日，如果没有则返回None
        """
        self._ensure_initialized()
        
        try:
            from datetime import datetime, timedelta
            
            # 解析日期
            if len(date) == 8:
                date_obj = datetime.strptime(date, '%Y%m%d')
            else:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
            
            # 向前查找30天内的交易日历
            start_date_obj = date_obj - timedelta(days=30)
            start_date_str = start_date_obj.strftime('%Y%m%d')
            end_date_str = (date_obj - timedelta(days=1)).strftime('%Y%m%d')
            
            # 获取交易日历
            trade_cal = self.trade_cal(
                exchange=exchange,
                start_date=start_date_str,
                end_date=end_date_str
            )
            
            # 筛选交易日并按日期降序排序
            trade_dates = trade_cal[trade_cal['is_open'] == 1].sort_values(
                'cal_date', ascending=False
            )
            
            if not trade_dates.empty:
                prev_date = trade_dates.iloc[0]['cal_date']
                self.logger.debug(f"日期{date}的上一个交易日: {prev_date}")
                return prev_date
            
            return None
            
        except Exception as e:
            error_msg = f"获取上一个交易日失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def get_next_trade_date(self, date: str, exchange: str = 'SSE') -> Optional[str]:
        """
        获取指定日期的下一个交易日
        
        Args:
            date: 指定日期
            exchange: 交易所代码
            
        Returns:
            下一个交易日，如果没有则返回None
        """
        self._ensure_initialized()
        
        try:
            from datetime import datetime, timedelta
            
            # 解析日期
            if len(date) == 8:
                date_obj = datetime.strptime(date, '%Y%m%d')
            else:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
            
            # 向后查找30天内的交易日历
            start_date_str = (date_obj + timedelta(days=1)).strftime('%Y%m%d')
            end_date_obj = date_obj + timedelta(days=30)
            end_date_str = end_date_obj.strftime('%Y%m%d')
            
            # 获取交易日历
            trade_cal = self.trade_cal(
                exchange=exchange,
                start_date=start_date_str,
                end_date=end_date_str
            )
            
            # 筛选交易日并按日期升序排序
            trade_dates = trade_cal[trade_cal['is_open'] == 1].sort_values(
                'cal_date', ascending=True
            )
            
            if not trade_dates.empty:
                next_date = trade_dates.iloc[0]['cal_date']
                self.logger.debug(f"日期{date}的下一个交易日: {next_date}")
                return next_date
            
            return None
            
        except Exception as e:
            error_msg = f"获取下一个交易日失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    # 异步API接口
    async def stock_basic_async(self, **kwargs) -> pd.DataFrame:
        """
        异步获取股票基础信息
        
        Args:
            **kwargs: 查询参数
                
        Returns:
            包含股票基础信息的DataFrame
        """
        self._ensure_initialized()
        
        # 创建数据请求
        request = DataRequest(
            data_type='stock_basic',
            extra_params=kwargs
        )
        
        # 异步获取数据
        result = await self.data_manager.get_data(request)
        self.logger.info(f"异步获取股票基础信息成功，共{len(result)}条记录")
        return result
    
    async def stock_daily_async(self, ts_code: str, start_date: str = None, 
                               end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        异步获取股票日线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数
                
        Returns:
            包含股票日线数据的DataFrame
        """
        self._ensure_initialized()
        
        # 参数验证
        if not ts_code:
            raise ValidationError("股票代码不能为空")
        
        if not validate_stock_code(ts_code):
            raise ValidationError(f"股票代码格式无效: {ts_code}")
        
        if start_date and not validate_date_format(start_date):
            raise ValidationError(f"开始日期格式无效: {start_date}")
        
        if end_date and not validate_date_format(end_date):
            raise ValidationError(f"结束日期格式无效: {end_date}")
        
        # 创建数据请求
        request = DataRequest(
            data_type='stock_daily',
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date,
            extra_params=kwargs
        )
        
        # 异步获取数据
        result = await self.data_manager.get_data(request)
        self.logger.info(f"异步获取股票{ts_code}日线数据成功，共{len(result)}条记录")
        return result
    
    async def stock_minute_async(self, ts_code: str, freq: str = '1min', 
                                start_date: str = None, end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        异步获取股票分钟数据
        
        Args:
            ts_code: 股票代码
            freq: 频率
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数
                
        Returns:
            包含股票分钟数据的DataFrame
        """
        self._ensure_initialized()
        
        # 参数验证
        if not ts_code:
            raise ValidationError("股票代码不能为空")
        
        if not validate_stock_code(ts_code):
            raise ValidationError(f"股票代码格式无效: {ts_code}")
        
        valid_freqs = ['1min', '5min', '15min', '30min', '60min']
        if freq not in valid_freqs:
            raise ValidationError(f"频率参数无效: {freq}，支持的频率: {valid_freqs}")
        
        # 创建数据请求
        request = DataRequest(
            data_type='stock_minute',
            ts_code=ts_code,
            freq=freq,
            start_date=start_date,
            end_date=end_date,
            extra_params=kwargs
        )
        
        # 异步获取数据
        result = await self.data_manager.get_data(request)
        self.logger.info(f"异步获取股票{ts_code}分钟数据({freq})成功，共{len(result)}条记录")
        return result
    
    async def get_data_batch_async(self, requests: List[DataRequest]) -> List[pd.DataFrame]:
        """
        异步批量获取数据
        
        Args:
            requests: 数据请求列表
            
        Returns:
            数据结果列表
        """
        self._ensure_initialized()
        
        results = await self.data_manager.get_data_batch(requests)
        self.logger.info(f"异步批量获取数据完成，共{len(requests)}个请求")
        return results
    
    async def trade_cal_async(self, exchange: str = 'SSE', start_date: str = None, 
                             end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        异步获取交易日历
        
        Args:
            exchange: 交易所代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数
                
        Returns:
            包含交易日历的DataFrame
        """
        self._ensure_initialized()
        
        # 参数验证
        if start_date and not validate_date_format(start_date):
            raise ValidationError(f"开始日期格式无效: {start_date}")
        
        if end_date and not validate_date_format(end_date):
            raise ValidationError(f"结束日期格式无效: {end_date}")
        
        # 创建数据请求
        request = DataRequest(
            data_type='trade_cal',
            start_date=start_date,
            end_date=end_date,
            extra_params={'exchange': exchange, **kwargs}
        )
        
        # 异步获取数据
        result = await self.data_manager.get_data(request)
        self.logger.info(f"异步获取交易日历成功，共{len(result)}条记录")
        return result
    
    # 财务报告相关接口
    def get_financial_reports(self, ts_code: str, start_date: str = None, 
                             end_date: str = None, report_type: str = None, **kwargs) -> List[Dict[str, Any]]:
        """
        获取财务报告数据
        
        从数据源获取指定股票的财务报告数据，包括营业收入、净利润、总资产等关键财务指标。
        
        Args:
            ts_code: 股票代码，支持多种格式：
                - 标准格式: 000001.SZ, 600000.SH
                - Baostock格式: sz.000001, sh.600000  
                - 东方财富格式: 0.000001, 1.600000
                - 同花顺格式: hs_000001, hs_600000
                - 纯数字: 000001, 600000
            start_date: 开始日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            report_type: 报告类型 (Q1, Q2, Q3, A)，可选
            **kwargs: 其他参数
                - fields: 指定返回字段
                - force_refresh: 是否强制从数据源刷新
                
        Returns:
            财务报告数据列表，每个元素为字典格式
            
        Raises:
            ValidationError: 参数验证失败
            FinancialDataError: 财务数据获取失败
            
        Example:
            >>> client = QuickStockClient()
            >>> # 获取平安银行最近的财务报告
            >>> reports = client.get_financial_reports('000001.SZ')
            >>> # 获取指定期间的年报
            >>> reports = client.get_financial_reports('000001.SZ', 
            ...                                       start_date='20230101', 
            ...                                       end_date='20231231', 
            ...                                       report_type='A')
        """
        self._ensure_initialized()
        
        try:
            from .models import FinancialReportsRequest
            from .services.financial_reports_service import FinancialReportsService
            
            # 使用增强的代码验证和标准化
            ts_code = self._validate_and_normalize_code(ts_code, "股票代码")
            
            # 验证日期格式
            if start_date and not validate_date_format(start_date):
                raise ValidationError(f"开始日期格式无效: {start_date}")
            
            if end_date and not validate_date_format(end_date):
                raise ValidationError(f"结束日期格式无效: {end_date}")
            
            # 创建财务报告请求
            request = FinancialReportsRequest(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                report_type=report_type,
                fields=kwargs.get('fields'),
                extra_params=kwargs
            )
            
            # 创建服务实例
            service = FinancialReportsService(
                self.data_manager, 
                self.logger
            )
            
            # 获取数据
            coro = service.get_financial_reports(request)
            reports = self._run_async(coro)
            
            # 转换为字典格式
            result = [report.to_dict() for report in reports]
            
            self.logger.info(f"获取股票{ts_code}财务报告成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取财务报告失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def get_earnings_forecast(self, ts_code: str, start_date: str = None, 
                             end_date: str = None, forecast_type: str = None, **kwargs) -> List[Dict[str, Any]]:
        """
        获取业绩预告数据
        
        从数据源获取指定股票的业绩预告数据，包括预告类型、预告净利润变动幅度等信息。
        
        Args:
            ts_code: 股票代码，支持多种格式
            start_date: 开始日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            forecast_type: 预告类型 (预增, 预减, 扭亏, 首亏, 续亏, 续盈, 略增, 略减, 不确定)，可选
            **kwargs: 其他参数
                - fields: 指定返回字段
                - force_refresh: 是否强制从数据源刷新
                
        Returns:
            业绩预告数据列表，每个元素为字典格式
            
        Raises:
            ValidationError: 参数验证失败
            ForecastDataError: 业绩预告数据获取失败
            
        Example:
            >>> client = QuickStockClient()
            >>> # 获取平安银行的业绩预告
            >>> forecasts = client.get_earnings_forecast('000001.SZ')
            >>> # 获取预增类型的业绩预告
            >>> forecasts = client.get_earnings_forecast('000001.SZ', forecast_type='预增')
        """
        self._ensure_initialized()
        
        try:
            from .models import EarningsForecastRequest
            from .services.financial_reports_service import FinancialReportsService
            
            # 使用增强的代码验证和标准化
            ts_code = self._validate_and_normalize_code(ts_code, "股票代码")
            
            # 验证日期格式
            if start_date and not validate_date_format(start_date):
                raise ValidationError(f"开始日期格式无效: {start_date}")
            
            if end_date and not validate_date_format(end_date):
                raise ValidationError(f"结束日期格式无效: {end_date}")
            
            # 创建业绩预告请求
            request = EarningsForecastRequest(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                forecast_type=forecast_type,
                extra_params=kwargs
            )
            
            # 创建服务实例
            service = FinancialReportsService(
                self.data_manager, 
                self.logger
            )
            
            # 获取数据
            coro = service.get_earnings_forecast(request)
            forecasts = self._run_async(coro)
            
            # 转换为字典格式
            result = [forecast.to_dict() for forecast in forecasts]
            
            self.logger.info(f"获取股票{ts_code}业绩预告成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取业绩预告失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def get_earnings_flash_reports(self, ts_code: str, start_date: str = None, 
                                  end_date: str = None, **kwargs) -> List[Dict[str, Any]]:
        """
        获取业绩快报数据
        
        从数据源获取指定股票的业绩快报数据，业绩快报是正式财报前的业绩速报。
        
        Args:
            ts_code: 股票代码，支持多种格式
            start_date: 开始日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            **kwargs: 其他参数
                - sort_by: 排序字段 (publish_date, report_date, report_period)
                - fields: 指定返回字段
                - force_refresh: 是否强制从数据源刷新
                
        Returns:
            业绩快报数据列表，每个元素为字典格式
            
        Raises:
            ValidationError: 参数验证失败
            FlashReportError: 业绩快报数据获取失败
            
        Example:
            >>> client = QuickStockClient()
            >>> # 获取平安银行的业绩快报
            >>> flash_reports = client.get_earnings_flash_reports('000001.SZ')
            >>> # 按报告日期排序
            >>> flash_reports = client.get_earnings_flash_reports('000001.SZ', sort_by='report_date')
        """
        self._ensure_initialized()
        
        try:
            from .models import FlashReportsRequest
            from .services.financial_reports_service import FinancialReportsService
            
            # 使用增强的代码验证和标准化
            ts_code = self._validate_and_normalize_code(ts_code, "股票代码")
            
            # 验证日期格式
            if start_date and not validate_date_format(start_date):
                raise ValidationError(f"开始日期格式无效: {start_date}")
            
            if end_date and not validate_date_format(end_date):
                raise ValidationError(f"结束日期格式无效: {end_date}")
            
            # 创建业绩快报请求
            request = FlashReportsRequest(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                sort_by=kwargs.get('sort_by', 'publish_date'),
                extra_params=kwargs
            )
            
            # 创建服务实例
            service = FinancialReportsService(
                self.data_manager, 
                self.logger
            )
            
            # 获取数据
            coro = service.get_earnings_flash_reports(request)
            flash_reports = self._run_async(coro)
            
            # 转换为字典格式
            result = [report.to_dict() for report in flash_reports]
            
            self.logger.info(f"获取股票{ts_code}业绩快报成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取业绩快报失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def get_batch_financial_data(self, stock_codes: List[str], data_types: List[str] = None,
                                start_date: str = None, end_date: str = None, **kwargs) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        批量获取多股票的财务数据
        
        从数据源批量获取多只股票的财务数据，支持并发请求以提高效率。
        
        Args:
            stock_codes: 股票代码列表，支持多种格式
            data_types: 数据类型列表，可选值：
                - 'financial_reports': 财务报告
                - 'earnings_forecast': 业绩预告  
                - 'flash_reports': 业绩快报
                如果为None，则获取所有类型
            start_date: 开始日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            **kwargs: 其他参数
                - max_workers: 最大并发数，默认5
                - timeout: 超时时间（秒），默认60
                - force_refresh: 是否强制从数据源刷新
                
        Returns:
            嵌套字典，结构为：{股票代码: {数据类型: [数据列表]}}
            
        Raises:
            ValidationError: 参数验证失败
            FinancialDataError: 财务数据获取失败
            
        Example:
            >>> client = QuickStockClient()
            >>> # 批量获取多只股票的所有财务数据
            >>> codes = ['000001.SZ', '000002.SZ', '600000.SH']
            >>> data = client.get_batch_financial_data(codes)
            >>> # 只获取财务报告和业绩预告
            >>> data = client.get_batch_financial_data(codes, 
            ...                                       data_types=['financial_reports', 'earnings_forecast'])
        """
        self._ensure_initialized()
        
        try:
            from .services.financial_reports_service import FinancialReportsService
            
            # 参数验证
            if not stock_codes:
                raise ValidationError("股票代码列表不能为空")
            
            if len(stock_codes) > 50:  # 限制批量大小
                raise ValidationError(f"批量大小超过限制，最大支持50只股票，当前{len(stock_codes)}只")
            
            # 标准化股票代码
            normalized_codes = []
            for code in stock_codes:
                normalized_code = self._validate_and_normalize_code(code, "股票代码")
                normalized_codes.append(normalized_code)
            
            # 验证日期格式
            if start_date and not validate_date_format(start_date):
                raise ValidationError(f"开始日期格式无效: {start_date}")
            
            if end_date and not validate_date_format(end_date):
                raise ValidationError(f"结束日期格式无效: {end_date}")
            
            # 设置默认数据类型
            if data_types is None:
                data_types = ['financial_reports', 'earnings_forecast', 'flash_reports']
            
            # 验证数据类型
            valid_types = ['financial_reports', 'earnings_forecast', 'flash_reports']
            for data_type in data_types:
                if data_type not in valid_types:
                    raise ValidationError(f"无效的数据类型: {data_type}，支持的类型: {valid_types}")
            
            # 创建服务实例
            service = FinancialReportsService(
                self.data_manager, 
                self.logger
            )
            
            # 构建批量请求参数
            batch_params = {
                'stock_codes': normalized_codes,
                'data_types': data_types,
                'start_date': start_date,
                'end_date': end_date,
                'max_workers': kwargs.get('max_workers', 5),
                'timeout': kwargs.get('timeout', 60),
                'force_refresh': kwargs.get('force_refresh', False)
            }
            
            # 执行批量获取
            coro = service.get_batch_financial_data(**batch_params)
            batch_results = self._run_async(coro)
            
            # 转换结果格式
            result = {}
            for stock_code, stock_data in batch_results.items():
                result[stock_code] = {}
                for data_type, data_list in stock_data.items():
                    if data_list:
                        result[stock_code][data_type] = [item.to_dict() for item in data_list]
                    else:
                        result[stock_code][data_type] = []
            
            total_records = sum(
                len(data_list) 
                for stock_data in result.values() 
                for data_list in stock_data.values()
            )
            
            self.logger.info(f"批量获取财务数据成功，{len(normalized_codes)}只股票，共{total_records}条记录")
            return result
            
        except Exception as e:
            error_msg = f"批量获取财务数据失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e