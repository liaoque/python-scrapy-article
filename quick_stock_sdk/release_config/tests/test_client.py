import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from quickstock.client import QuickStockClient, QuickStockError
from quickstock.config import Config


class TestQuickStockClient:
    """测试QuickStockClient类的功能"""

    def setup_method(self):
        """设置测试环境"""
        # 创建模拟配置
        self.mock_config = MagicMock(spec=Config)
        self.mock_config.log_level = "INFO"
        self.mock_config.log_file = None
        self.mock_config.enable_auto_code_conversion = True
        self.mock_config.log_code_conversions = False
        self.mock_config.code_conversion_error_strategy = "strict"
        self.mock_config.data_source_priority = []
        self.mock_config.providers = {}
        
        # 创建模拟数据管理器
        self.mock_data_manager = MagicMock()
        self.mock_data_manager.source_manager = MagicMock()

    def test_initialization_success(self):
        """测试客户端初始化成功"""
        with patch('quickstock.client.Config.load_default', return_value=self.mock_config):
            with patch('quickstock.client.DataManager', return_value=self.mock_data_manager):
                client = QuickStockClient()
                assert client._initialized is True
                assert client.config is not None
                assert client.data_manager is not None

    def test_initialization_with_custom_config(self):
        """测试使用自定义配置初始化客户端"""
        with patch('quickstock.client.DataManager', return_value=self.mock_data_manager):
            client = QuickStockClient(config=self.mock_config)
            assert client.config is not None

    def test_initialization_failure(self):
        """测试客户端初始化失败"""
        with patch('quickstock.client.Config.load_default', return_value=self.mock_config):
            with patch('quickstock.client.DataManager', side_effect=Exception("初始化失败")):
                with pytest.raises(QuickStockError) as excinfo:
                    QuickStockClient()
                assert "初始化失败" in str(excinfo.value)

    def test_normalize_code(self):
        """测试股票代码标准化"""
        with patch('quickstock.client.Config.load_default', return_value=self.mock_config):
            with patch('quickstock.client.DataManager', return_value=self.mock_data_manager):
                client = QuickStockClient()
                normalized = client.normalize_code("600000")
                assert isinstance(normalized, str)

    def test_convert_code(self):
        """测试股票代码转换"""
        with patch('quickstock.client.Config.load_default', return_value=self.mock_config):
            with patch('quickstock.client.DataManager', return_value=self.mock_data_manager):
                client = QuickStockClient()
                # 设置enable_auto_code_conversion为True
                client.config.enable_auto_code_conversion = True
                # 模拟convert_stock_code函数
                with patch('quickstock.client.convert_stock_code') as mock_convert:
                    mock_convert.return_value = "600000.SH"
                    
                    converted = client.convert_code("600000", "standard")
                    assert converted == "600000.SH"

    def test_validate_code(self):
        """测试股票代码验证"""
        with patch('quickstock.client.Config.load_default', return_value=self.mock_config):
            with patch('quickstock.client.DataManager', return_value=self.mock_data_manager):
                client = QuickStockClient()
                # 模拟source_manager.validate_code方法
                client.data_manager.source_manager.validate_code.return_value = True
                
                is_valid = client.validate_code("SH600000")
                assert is_valid is True

    def test_stock_basic(self):
        """测试获取股票基本信息"""
        with patch('quickstock.client.Config.load_default', return_value=self.mock_config):
            with patch('quickstock.client.DataManager', return_value=self.mock_data_manager):
                client = QuickStockClient()
                # 模拟data_manager.get_data方法
                mock_data = pd.DataFrame()
                client.data_manager.get_data.return_value = mock_data
                
                result = client.stock_basic(exchange="SSE")
                # 验证调用是否正确
                client.data_manager.get_data.assert_called_once()

    def test_stock_daily(self):
        """测试获取股票日线数据"""
        with patch('quickstock.client.Config.load_default', return_value=self.mock_config):
            with patch('quickstock.client.DataManager', return_value=self.mock_data_manager):
                client = QuickStockClient()
                # 模拟data_manager.get_data方法
                mock_data = pd.DataFrame()
                client.data_manager.get_data.return_value = mock_data
                
                # 调用stock_daily方法，使用正确的参数名ts_code
                client.stock_daily(ts_code="600000.SH", start_date="2023-01-01", end_date="2023-01-31")
                # 验证调用是否正确
                client.data_manager.get_data.assert_called_once()

    def test_not_initialized(self):
        """测试未初始化的客户端"""
        # 创建客户端但不初始化
        client = QuickStockClient.__new__(QuickStockClient)
        client._initialized = False
        
        with pytest.raises(QuickStockError) as excinfo:
            client.stock_basic()
        assert "客户端未正确初始化" in str(excinfo.value)
