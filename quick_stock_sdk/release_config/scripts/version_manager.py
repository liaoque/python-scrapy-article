#!/usr/bin/env python3
"""
版本管理脚本

用于管理QuickStock SDK的版本号，支持自动更新版本号和生成发布说明。

使用方法:
    python release_config/scripts/version_manager.py --help
    python release_config/scripts/version_manager.py bump patch
    python release_config/scripts/version_manager.py bump minor
    python release_config/scripts/version_manager.py bump major
    python release_config/scripts/version_manager.py current
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime


class VersionManager:
    """版本管理器"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.init_file = self.project_root / "quickstock" / "__init__.py"
        self.changelog_file = self.project_root / "CHANGELOG.md"
        
    def get_current_version(self) -> str:
        """获取当前版本号"""
        if not self.init_file.exists():
            raise FileNotFoundError(f"Cannot find {self.init_file}")
        
        content = self.init_file.read_text(encoding='utf-8')
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        
        if not match:
            raise ValueError("Cannot find version in __init__.py")
        
        return match.group(1)
    
    def parse_version(self, version: str) -> Tuple[int, int, int]:
        """解析版本号"""
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:-.*)?$', version)
        if not match:
            raise ValueError(f"Invalid version format: {version}")
        
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    
    def format_version(self, major: int, minor: int, patch: int) -> str:
        """格式化版本号"""
        return f"{major}.{minor}.{patch}"
    
    def bump_version(self, bump_type: str) -> str:
        """升级版本号"""
        current = self.get_current_version()
        major, minor, patch = self.parse_version(current)
        
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")
        
        new_version = self.format_version(major, minor, patch)
        return new_version
    
    def update_version_in_file(self, new_version: str):
        """更新__init__.py中的版本号"""
        content = self.init_file.read_text(encoding='utf-8')
        
        # 更新版本号
        new_content = re.sub(
            r'(__version__\s*=\s*["\'])[^"\']+(["\'])',
            f'\\g<1>{new_version}\\g<2>',
            content
        )
        
        if new_content == content:
            raise ValueError("Failed to update version in __init__.py")
        
        self.init_file.write_text(new_content, encoding='utf-8')
        print(f"✅ Updated version in {self.init_file}")
    
    def update_changelog(self, new_version: str, bump_type: str):
        """更新CHANGELOG.md"""
        if not self.changelog_file.exists():
            print(f"⚠️  CHANGELOG.md not found at {self.changelog_file}")
            return
        
        content = self.changelog_file.read_text(encoding='utf-8')
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 查找[未发布]部分
        unreleased_pattern = r'## \[未发布\].*?(?=## \[|\Z)'
        match = re.search(unreleased_pattern, content, re.DOTALL)
        
        if match:
            # 创建新的版本条目
            version_entry = f"\n## [{new_version}] - {today}\n\n"
            
            # 根据bump类型添加默认内容
            if bump_type == "major":
                version_entry += "### 变更\n- 🎉 重大版本更新\n\n"
            elif bump_type == "minor":
                version_entry += "### 新增\n- ✨ 新功能更新\n\n"
            else:  # patch
                version_entry += "### 修复\n- 🐛 问题修复\n\n"
            
            # 在[未发布]后插入新版本
            unreleased_end = match.end()
            new_content = (
                content[:unreleased_end] + 
                version_entry + 
                content[unreleased_end:]
            )
            
            self.changelog_file.write_text(new_content, encoding='utf-8')
            print(f"✅ Updated CHANGELOG.md with version {new_version}")
        else:
            print("⚠️  Could not find [未发布] section in CHANGELOG.md")
    
    def create_git_tag(self, version: str):
        """创建Git标签"""
        import subprocess
        
        try:
            # 检查是否有未提交的更改
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.stdout.strip():
                print("⚠️  There are uncommitted changes. Please commit them first.")
                return False
            
            # 创建标签
            tag_name = f"v{version}"
            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", f"Release {version}"],
                check=True,
                cwd=self.project_root
            )
            
            print(f"✅ Created git tag: {tag_name}")
            print(f"💡 Push the tag with: git push origin {tag_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create git tag: {e}")
            return False
        except FileNotFoundError:
            print("⚠️  Git not found. Skipping tag creation.")
            return False
    
    def validate_version(self, version: str) -> bool:
        """验证版本号格式"""
        try:
            self.parse_version(version)
            return True
        except ValueError:
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="QuickStock SDK版本管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s current                 # 显示当前版本
  %(prog)s bump patch              # 升级补丁版本 (1.0.0 -> 1.0.1)
  %(prog)s bump minor              # 升级次版本 (1.0.0 -> 1.1.0)
  %(prog)s bump major              # 升级主版本 (1.0.0 -> 2.0.0)
  %(prog)s set 1.2.3               # 设置指定版本
  %(prog)s bump patch --no-tag     # 升级版本但不创建Git标签
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # current命令
    subparsers.add_parser('current', help='显示当前版本')
    
    # bump命令
    bump_parser = subparsers.add_parser('bump', help='升级版本')
    bump_parser.add_argument(
        'type',
        choices=['major', 'minor', 'patch'],
        help='升级类型'
    )
    bump_parser.add_argument(
        '--no-tag',
        action='store_true',
        help='不创建Git标签'
    )
    
    # set命令
    set_parser = subparsers.add_parser('set', help='设置指定版本')
    set_parser.add_argument('version', help='版本号 (例如: 1.2.3)')
    set_parser.add_argument(
        '--no-tag',
        action='store_true',
        help='不创建Git标签'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        vm = VersionManager()
        
        if args.command == 'current':
            current = vm.get_current_version()
            print(f"当前版本: {current}")
            
        elif args.command == 'bump':
            current = vm.get_current_version()
            new_version = vm.bump_version(args.type)
            
            print(f"版本升级: {current} -> {new_version}")
            
            # 更新文件
            vm.update_version_in_file(new_version)
            vm.update_changelog(new_version, args.type)
            
            # 创建Git标签
            if not args.no_tag:
                vm.create_git_tag(new_version)
            
            print(f"🎉 版本已升级到 {new_version}")
            
        elif args.command == 'set':
            if not vm.validate_version(args.version):
                print(f"❌ 无效的版本号格式: {args.version}")
                sys.exit(1)
            
            current = vm.get_current_version()
            print(f"版本设置: {current} -> {args.version}")
            
            # 更新文件
            vm.update_version_in_file(args.version)
            
            # 创建Git标签
            if not args.no_tag:
                vm.create_git_tag(args.version)
            
            print(f"🎉 版本已设置为 {args.version}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()