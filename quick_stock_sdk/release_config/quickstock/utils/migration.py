"""
配置迁移工具

帮助用户从旧版本配置迁移到新版本
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from ..config import Config
from ..core.errors import ValidationError


class ConfigMigrator:
    """配置迁移器"""
    
    def __init__(self):
        self.logger = logging.getLogger('quickstock.migration')
        
        # 配置版本映射
        self.version_migrations = {
            '1.0.0': self._migrate_from_1_0_0,
            '1.1.0': self._migrate_from_1_1_0,
            # 可以添加更多版本的迁移函数
        }
        
        # 新增配置项的默认值
        self.new_config_defaults = {
            'enable_auto_code_conversion': True,
            'strict_code_validation': False,
            'log_code_conversions': False,
            'code_conversion_timeout': 1.0,
            'enable_code_format_inference': True,
            'enable_exchange_inference': True,
            'code_conversion_batch_size': 1000,
            'code_conversion_error_strategy': 'strict'
        }
    
    def detect_config_version(self, config_data: Dict[str, Any]) -> Optional[str]:
        """
        检测配置文件版本
        
        Args:
            config_data: 配置数据字典
            
        Returns:
            配置版本字符串，如果无法检测则返回None
        """
        # 检查是否有版本标识
        if 'version' in config_data:
            return config_data['version']
        
        # 根据配置项推断版本
        if 'enable_auto_code_conversion' in config_data:
            return '1.2.0'  # 当前版本
        elif 'aggressive_memory_optimization' in config_data:
            return '1.1.0'
        elif 'connection_pool_size' in config_data:
            return '1.0.0'
        else:
            return None  # 可能是更早的版本或自定义配置
    
    def migrate_config(self, config_data: Dict[str, Any], target_version: str = '1.2.0') -> Tuple[Dict[str, Any], List[str]]:
        """
        迁移配置到目标版本
        
        Args:
            config_data: 原始配置数据
            target_version: 目标版本
            
        Returns:
            (迁移后的配置数据, 迁移日志列表)
        """
        migration_log = []
        current_version = self.detect_config_version(config_data)
        
        if current_version is None:
            migration_log.append("无法检测配置版本，将应用所有必要的迁移")
            current_version = '0.0.0'
        
        migration_log.append(f"检测到配置版本: {current_version}")
        migration_log.append(f"目标版本: {target_version}")
        
        # 如果已经是目标版本或更新，直接返回
        if self._compare_versions(current_version, target_version) >= 0:
            migration_log.append("配置已经是最新版本，无需迁移")
            return config_data, migration_log
        
        # 执行迁移
        migrated_data = config_data.copy()
        
        # 按版本顺序执行迁移
        for version, migration_func in self.version_migrations.items():
            if self._compare_versions(current_version, version) < 0 and \
               self._compare_versions(version, target_version) <= 0:
                migration_log.append(f"执行版本 {version} 的迁移")
                migrated_data = migration_func(migrated_data, migration_log)
        
        # 添加新的配置项
        self._add_new_config_items(migrated_data, migration_log)
        
        # 设置版本标识
        migrated_data['version'] = target_version
        migration_log.append(f"迁移完成，配置版本更新为: {target_version}")
        
        return migrated_data, migration_log
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """
        比较版本号
        
        Args:
            version1: 版本1
            version2: 版本2
            
        Returns:
            -1: version1 < version2
             0: version1 == version2
             1: version1 > version2
        """
        def parse_version(version):
            return tuple(map(int, version.split('.')))
        
        v1 = parse_version(version1)
        v2 = parse_version(version2)
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    
    def _migrate_from_1_0_0(self, config_data: Dict[str, Any], migration_log: List[str]) -> Dict[str, Any]:
        """从版本1.0.0迁移"""
        migrated = config_data.copy()
        
        # 1.0.0 -> 1.1.0 的迁移逻辑
        # 例如：重命名配置项、调整默认值等
        
        migration_log.append("应用1.0.0版本迁移规则")
        return migrated
    
    def _migrate_from_1_1_0(self, config_data: Dict[str, Any], migration_log: List[str]) -> Dict[str, Any]:
        """从版本1.1.0迁移"""
        migrated = config_data.copy()
        
        # 1.1.0 -> 1.2.0 的迁移逻辑
        # 主要是添加代码转换相关的配置项
        
        migration_log.append("应用1.1.0版本迁移规则")
        return migrated
    
    def _add_new_config_items(self, config_data: Dict[str, Any], migration_log: List[str]):
        """添加新的配置项"""
        added_items = []
        
        for key, default_value in self.new_config_defaults.items():
            if key not in config_data:
                config_data[key] = default_value
                added_items.append(key)
        
        if added_items:
            migration_log.append(f"添加新配置项: {', '.join(added_items)}")
    
    def migrate_config_file(self, config_path: str, backup: bool = True) -> List[str]:
        """
        迁移配置文件
        
        Args:
            config_path: 配置文件路径
            backup: 是否创建备份
            
        Returns:
            迁移日志列表
            
        Raises:
            FileNotFoundError: 配置文件不存在
            ValidationError: 迁移失败
        """
        config_path = os.path.expanduser(config_path)
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        migration_log = []
        migration_log.append(f"开始迁移配置文件: {config_path}")
        
        try:
            # 读取原始配置
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.endswith('.json'):
                    original_data = json.load(f)
                    file_format = 'json'
                else:
                    original_data = yaml.safe_load(f)
                    file_format = 'yaml'
            
            # 创建备份
            if backup:
                backup_path = f"{config_path}.backup"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    if file_format == 'json':
                        json.dump(original_data, f, indent=2, ensure_ascii=False)
                    else:
                        yaml.dump(original_data, f, default_flow_style=False, allow_unicode=True)
                migration_log.append(f"创建备份文件: {backup_path}")
            
            # 执行迁移
            migrated_data, migrate_log = self.migrate_config(original_data)
            migration_log.extend(migrate_log)
            
            # 验证迁移后的配置
            try:
                Config(**migrated_data)
                migration_log.append("迁移后的配置验证通过")
            except Exception as e:
                raise ValidationError(f"迁移后的配置验证失败: {e}")
            
            # 保存迁移后的配置
            with open(config_path, 'w', encoding='utf-8') as f:
                if file_format == 'json':
                    json.dump(migrated_data, f, indent=2, ensure_ascii=False)
                else:
                    yaml.dump(migrated_data, f, default_flow_style=False, allow_unicode=True)
            
            migration_log.append(f"配置文件迁移完成: {config_path}")
            
        except Exception as e:
            migration_log.append(f"迁移失败: {e}")
            raise ValidationError(f"配置文件迁移失败: {e}") from e
        
        return migration_log
    
    def check_compatibility(self, config_path: str) -> Dict[str, Any]:
        """
        检查配置文件兼容性
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            兼容性检查结果
        """
        config_path = os.path.expanduser(config_path)
        result = {
            'compatible': True,
            'version': None,
            'missing_items': [],
            'deprecated_items': [],
            'recommendations': []
        }
        
        try:
            # 读取配置文件
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.endswith('.json'):
                    config_data = json.load(f)
                else:
                    config_data = yaml.safe_load(f)
            
            # 检测版本
            result['version'] = self.detect_config_version(config_data)
            
            # 检查缺失的配置项
            for key in self.new_config_defaults:
                if key not in config_data:
                    result['missing_items'].append(key)
            
            # 检查是否需要迁移
            if result['missing_items']:
                result['compatible'] = False
                result['recommendations'].append("建议运行配置迁移以获得最新功能")
            
            # 检查配置是否可以正常加载
            try:
                Config(**config_data)
            except Exception as e:
                result['compatible'] = False
                result['recommendations'].append(f"配置验证失败: {e}")
            
        except Exception as e:
            result['compatible'] = False
            result['recommendations'].append(f"无法读取配置文件: {e}")
        
        return result
    
    def generate_migration_report(self, config_path: str) -> str:
        """
        生成迁移报告
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            迁移报告文本
        """
        compatibility = self.check_compatibility(config_path)
        
        report = []
        report.append("QuickStock SDK 配置迁移报告")
        report.append("=" * 40)
        report.append(f"配置文件: {config_path}")
        report.append(f"当前版本: {compatibility['version'] or '未知'}")
        report.append(f"兼容性: {'是' if compatibility['compatible'] else '否'}")
        report.append("")
        
        if compatibility['missing_items']:
            report.append("缺失的配置项:")
            for item in compatibility['missing_items']:
                default_value = self.new_config_defaults.get(item, 'N/A')
                report.append(f"  - {item}: {default_value}")
            report.append("")
        
        if compatibility['deprecated_items']:
            report.append("已弃用的配置项:")
            for item in compatibility['deprecated_items']:
                report.append(f"  - {item}")
            report.append("")
        
        if compatibility['recommendations']:
            report.append("建议:")
            for rec in compatibility['recommendations']:
                report.append(f"  - {rec}")
            report.append("")
        
        if not compatibility['compatible']:
            report.append("迁移命令:")
            report.append(f"  python -m quickstock.utils.migration migrate {config_path}")
        
        return "\n".join(report)


def migrate_config_file(config_path: str, backup: bool = True) -> None:
    """
    迁移配置文件的便捷函数
    
    Args:
        config_path: 配置文件路径
        backup: 是否创建备份
    """
    migrator = ConfigMigrator()
    
    try:
        migration_log = migrator.migrate_config_file(config_path, backup)
        
        print("配置迁移完成!")
        print("\n迁移日志:")
        for log_entry in migration_log:
            print(f"  {log_entry}")
            
    except Exception as e:
        print(f"配置迁移失败: {e}")
        raise


def check_config_compatibility(config_path: str) -> None:
    """
    检查配置兼容性的便捷函数
    
    Args:
        config_path: 配置文件路径
    """
    migrator = ConfigMigrator()
    
    try:
        report = migrator.generate_migration_report(config_path)
        print(report)
        
    except Exception as e:
        print(f"兼容性检查失败: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python -m quickstock.utils.migration check <config_path>")
        print("  python -m quickstock.utils.migration migrate <config_path>")
        sys.exit(1)
    
    command = sys.argv[1]
    config_path = sys.argv[2] if len(sys.argv) > 2 else Config.get_default_config_path()
    
    if command == "check":
        check_config_compatibility(config_path)
    elif command == "migrate":
        backup = "--no-backup" not in sys.argv
        migrate_config_file(config_path, backup)
    else:
        print(f"未知命令: {command}")
        sys.exit(1)