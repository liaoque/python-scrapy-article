"""
诊断工具

提供系统诊断和问题排查功能
"""

import sys
import os
import psutil
import traceback
import logging
from typing import Dict, Any, List
from datetime import datetime

from ..config import Config
from ..core.errors import QuickStockError


class DiagnosticsRunner:
    """诊断运行器"""
    
    def __init__(self):
        self.logger = logging.getLogger('quickstock.diagnostics')
        self.results = {}
    
    def run_system_diagnostics(self) -> Dict[str, Any]:
        """运行系统诊断"""
        try:
            system_info = {
                'python_version': sys.version,
                'platform': sys.platform,
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
                'memory_available_gb': psutil.virtual_memory().available / 1024 / 1024 / 1024,
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage_percent': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
            }
            
            return {
                'status': 'success',
                'data': system_info
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def run_quickstock_diagnostics(self) -> Dict[str, Any]:
        """运行QuickStock诊断"""
        try:
            # 导入版本信息
            try:
                from .. import __version__
                version = __version__
            except ImportError:
                version = 'unknown'
            
            # 客户端初始化测试
            from .. import QuickStockClient
            client = QuickStockClient()
            
            # 配置检查
            config = client.get_config()
            config_info = {
                'enable_auto_code_conversion': config.enable_auto_code_conversion,
                'strict_code_validation': config.strict_code_validation,
                'code_conversion_error_strategy': config.code_conversion_error_strategy
            }
            
            # 代码转换测试
            conversion_tests = {}
            test_codes = ["000001.SZ", "sz.000001", "1.600000", "hs_300001"]
            
            for code in test_codes:
                try:
                    normalized = client.normalize_code(code)
                    conversion_tests[code] = {
                        'status': 'success',
                        'result': normalized
                    }
                except Exception as e:
                    conversion_tests[code] = {
                        'status': 'error',
                        'error': str(e)
                    }
            
            # 不再使用缓存，删除缓存状态检查
            
            # 数据源状态
            try:
                provider_health = client.get_provider_health()
            except Exception as e:
                provider_health = {'error': str(e)}
            
            return {
                'status': 'success',
                'data': {
                    'version': version,
                    'client_initialized': True,
                    'config': config_info,
                    'conversion_tests': conversion_tests,
                    'provider_health': provider_health
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def run_network_diagnostics(self) -> Dict[str, Any]:
        """运行网络诊断"""
        try:
            import requests
            
            test_urls = [
                ('tushare', 'https://api.tushare.pro'),
                ('baostock', 'http://baostock.com'),
                ('eastmoney', 'https://push2.eastmoney.com')
            ]
            
            network_tests = {}
            
            for name, url in test_urls:
                try:
                    response = requests.get(url, timeout=10)
                    network_tests[name] = {
                        'status': 'success',
                        'status_code': response.status_code,
                        'response_time': response.elapsed.total_seconds()
                    }
                except Exception as e:
                    network_tests[name] = {
                        'status': 'error',
                        'error': str(e)
                    }
            
            return {
                'status': 'success',
                'data': network_tests
            }
            
        except ImportError:
            return {
                'status': 'error',
                'error': 'requests库未安装'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def run_config_diagnostics(self) -> Dict[str, Any]:
        """运行配置诊断"""
        try:
            config_path = Config.get_default_config_path()
            
            config_info = {
                'default_path': config_path,
                'exists': os.path.exists(config_path),
                'readable': False,
                'writable': False,
                'syntax_valid': False,
                'size_bytes': 0
            }
            
            if config_info['exists']:
                config_info['readable'] = os.access(config_path, os.R_OK)
                config_info['writable'] = os.access(config_path, os.W_OK)
                config_info['size_bytes'] = os.path.getsize(config_path)
                
                # 语法检查
                try:
                    Config.from_file(config_path)
                    config_info['syntax_valid'] = True
                except Exception as e:
                    config_info['syntax_error'] = str(e)
            
            return {
                'status': 'success',
                'data': config_info
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def run_all_diagnostics(self) -> Dict[str, Any]:
        """运行所有诊断"""
        timestamp = datetime.now().isoformat()
        
        diagnostics = {
            'timestamp': timestamp,
            'system': self.run_system_diagnostics(),
            'quickstock': self.run_quickstock_diagnostics(),
            'network': self.run_network_diagnostics(),
            'config': self.run_config_diagnostics()
        }
        
        # 计算总体状态
        all_success = all(
            result.get('status') == 'success' 
            for result in diagnostics.values() 
            if isinstance(result, dict) and 'status' in result
        )
        
        diagnostics['overall_status'] = 'success' if all_success else 'partial_failure'
        
        return diagnostics
    
    def format_diagnostics_report(self, diagnostics: Dict[str, Any]) -> str:
        """格式化诊断报告"""
        lines = []
        lines.append("QuickStock SDK 诊断报告")
        lines.append("=" * 50)
        lines.append(f"时间: {diagnostics.get('timestamp', 'unknown')}")
        lines.append(f"总体状态: {diagnostics.get('overall_status', 'unknown')}")
        lines.append("")
        
        # 系统信息
        system = diagnostics.get('system', {})
        if system.get('status') == 'success':
            data = system['data']
            lines.append("=== 系统信息 ===")
            lines.append(f"Python版本: {data.get('python_version', 'unknown')}")
            lines.append(f"平台: {data.get('platform', 'unknown')}")
            lines.append(f"CPU核心数: {data.get('cpu_count', 'unknown')}")
            lines.append(f"CPU使用率: {data.get('cpu_percent', 'unknown'):.1f}%")
            lines.append(f"总内存: {data.get('memory_total_gb', 0):.2f} GB")
            lines.append(f"可用内存: {data.get('memory_available_gb', 0):.2f} GB")
            lines.append(f"内存使用率: {data.get('memory_percent', 'unknown'):.1f}%")
            lines.append(f"磁盘使用率: {data.get('disk_usage_percent', 'unknown'):.1f}%")
        else:
            lines.append("=== 系统信息 ===")
            lines.append(f"错误: {system.get('error', 'unknown')}")
        lines.append("")
        
        # QuickStock信息
        quickstock = diagnostics.get('quickstock', {})
        if quickstock.get('status') == 'success':
            data = quickstock['data']
            lines.append("=== QuickStock信息 ===")
            lines.append(f"版本: {data.get('version', 'unknown')}")
            lines.append(f"客户端初始化: {'成功' if data.get('client_initialized') else '失败'}")
            
            config = data.get('config', {})
            lines.append("配置:")
            lines.append(f"  自动代码转换: {'启用' if config.get('enable_auto_code_conversion') else '禁用'}")
            lines.append(f"  严格验证: {'启用' if config.get('strict_code_validation') else '禁用'}")
            lines.append(f"  错误策略: {config.get('code_conversion_error_strategy', 'unknown')}")
            
            # 代码转换测试
            conversion_tests = data.get('conversion_tests', {})
            lines.append("代码转换测试:")
            for code, result in conversion_tests.items():
                if result['status'] == 'success':
                    lines.append(f"  {code} -> {result['result']}")
                else:
                    lines.append(f"  {code} -> 错误: {result['error']}")
            
            # 数据源状态
            provider_health = data.get('provider_health', {})
            if 'error' not in provider_health:
                lines.append("数据源状态:")
                for name, status in provider_health.items():
                    health = "健康" if status.get('healthy', False) else "异常"
                    lines.append(f"  {name}: {health}")
        else:
            lines.append("=== QuickStock信息 ===")
            lines.append(f"错误: {quickstock.get('error', 'unknown')}")
        lines.append("")
        
        # 网络信息
        network = diagnostics.get('network', {})
        if network.get('status') == 'success':
            data = network['data']
            lines.append("=== 网络连接 ===")
            for name, result in data.items():
                if result['status'] == 'success':
                    lines.append(f"{name}: 连接正常 ({result['status_code']}, {result['response_time']:.2f}s)")
                else:
                    lines.append(f"{name}: 连接失败 - {result['error']}")
        else:
            lines.append("=== 网络连接 ===")
            lines.append(f"错误: {network.get('error', 'unknown')}")
        lines.append("")
        
        # 配置信息
        config = diagnostics.get('config', {})
        if config.get('status') == 'success':
            data = config['data']
            lines.append("=== 配置文件 ===")
            lines.append(f"路径: {data.get('default_path', 'unknown')}")
            lines.append(f"存在: {'是' if data.get('exists') else '否'}")
            if data.get('exists'):
                lines.append(f"可读: {'是' if data.get('readable') else '否'}")
                lines.append(f"可写: {'是' if data.get('writable') else '否'}")
                lines.append(f"语法正确: {'是' if data.get('syntax_valid') else '否'}")
                lines.append(f"大小: {data.get('size_bytes', 0)} 字节")
                if 'syntax_error' in data:
                    lines.append(f"语法错误: {data['syntax_error']}")
        else:
            lines.append("=== 配置文件 ===")
            lines.append(f"错误: {config.get('error', 'unknown')}")
        
        lines.append("")
        lines.append("=== 诊断完成 ===")
        
        return "\n".join(lines)


def run_diagnostics() -> str:
    """运行诊断并返回格式化报告"""
    runner = DiagnosticsRunner()
    diagnostics = runner.run_all_diagnostics()
    return runner.format_diagnostics_report(diagnostics)


def run_full_diagnostics() -> None:
    """运行完整诊断并打印报告"""
    print(run_diagnostics())


def run_quick_diagnostics() -> Dict[str, Any]:
    """运行快速诊断"""
    runner = DiagnosticsRunner()
    
    # 只运行关键诊断
    diagnostics = {
        'timestamp': datetime.now().isoformat(),
        'quickstock': runner.run_quickstock_diagnostics(),
        'config': runner.run_config_diagnostics()
    }
    
    return diagnostics


if __name__ == "__main__":
    run_full_diagnostics()