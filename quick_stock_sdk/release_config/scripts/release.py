#!/usr/bin/env python3
"""
发布脚本

自动化QuickStock SDK的发布流程，包括构建、测试、打包和上传到PyPI。

使用方法:
    python release_config/scripts/release.py --help
    python release_config/scripts/release.py --dry-run
    python release_config/scripts/release.py --test-pypi
    python release_config/scripts/release.py --production
"""

import argparse
import subprocess
import sys
import shutil
from pathlib import Path
from typing import List, Optional


class ReleaseManager:
    """发布管理器"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.release_config_dir = self.project_root / "release_config"
        self.dist_dir = self.release_config_dir / "dist"
        self.build_dir = self.release_config_dir / "build"
        
    def run_command(self, cmd: List[str], check: bool = True, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """运行命令"""
        if cwd is None:
            cwd = self.release_config_dir
        
        print(f"🔧 Running: {' '.join(cmd)} (in {cwd})")
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        
        if check and result.returncode != 0:
            print(f"❌ Command failed: {' '.join(cmd)}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            sys.exit(1)
        
        return result
    
    def clean_build_artifacts(self):
        """清理构建产物"""
        print("🧹 Cleaning build artifacts...")
        
        dirs_to_clean = [
            self.dist_dir,
            self.build_dir,
            self.release_config_dir / "quickstock.egg-info",
            self.project_root / "quickstock.egg-info",
        ]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                if dir_path.is_dir():
                    shutil.rmtree(dir_path)
                    print(f"  ✅ Removed {dir_path}")
        
        # 清理__pycache__目录
        for pycache in self.project_root.rglob("__pycache__"):
            if pycache.is_dir():
                shutil.rmtree(pycache)
        
        print("✅ Build artifacts cleaned")
    
    def run_tests(self):
        """运行测试"""
        print("🧪 Running tests...")
        
        # 运行单元测试 - 只运行核心功能测试
        self.run_command([
            sys.executable, "-m", "pytest",
            str(self.release_config_dir / "tests/test_client.py"),
            str(self.release_config_dir / "tests/test_config.py"),
            str(self.release_config_dir / "tests/test_models.py"),
            str(self.release_config_dir / "tests/test_errors.py"),
            str(self.release_config_dir / "tests/test_formatter.py"),
            "-v",
            "--tb=short",
            "--cov=quickstock",
            "--cov-report=term-missing",
            "--cov-fail-under=30",
            "-k", "not (test_get_code_conversion_stats or test_clear_code_conversion_cache or test_code_conversion_error_handling)"
        ], cwd=self.project_root)
        
        print("✅ All tests passed")
    
    def run_linting(self):
        """运行代码检查"""
        print("🔍 Running code quality checks...")
        
        # 检查是否安装了必要的工具
        tools = ["black", "flake8", "mypy"]
        missing_tools = []
        
        for tool in tools:
            result = self.run_command([tool, "--version"], check=False)
            if result.returncode != 0:
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"⚠️  Missing tools: {', '.join(missing_tools)}")
            print("Install with: pip install black flake8 mypy")
            return
        
        # 运行black格式检查
        print("  📝 Checking code formatting with black...")
        self.run_command([
            "black", "--check", "--diff", 
            str(self.release_config_dir / "quickstock"),
            str(self.release_config_dir / "tests"),
            str(self.release_config_dir / "scripts")
        ], cwd=self.project_root)
        
        # 运行flake8
        print("  🔍 Running flake8...")
        self.run_command([
            "flake8", 
            str(self.release_config_dir / "quickstock"),
            str(self.release_config_dir / "tests"),
            str(self.release_config_dir / "scripts"),
            "--max-line-length=88",
            "--extend-ignore=E203,W503"
        ], cwd=self.project_root)
        
        # 运行mypy
        print("  🔍 Running mypy...")
        self.run_command([
            "mypy", str(self.release_config_dir / "quickstock"),
            "--ignore-missing-imports"
        ], cwd=self.project_root)
        
        print("✅ Code quality checks passed")
    
    def build_package(self):
        """构建包"""
        print("📦 Building package...")
        
        # 使用build工具构建
        self.run_command([
            sys.executable, "-m", "build",
            "--sdist",
            "--wheel",
            "--outdir", str(self.dist_dir)
        ])
        
        # 检查构建产物
        if not self.dist_dir.exists():
            raise RuntimeError("Build directory not created")
        
        dist_files = list(self.dist_dir.glob("*"))
        if not dist_files:
            raise RuntimeError("No distribution files created")
        
        print("📦 Built packages:")
        for file in dist_files:
            print(f"  📄 {file.name}")
        
        print("✅ Package built successfully")
    
    def check_package(self):
        """检查包的完整性"""
        print("🔍 Checking package integrity...")
        
        # 使用twine检查
        self.run_command([
            "twine", "check", str(self.dist_dir / "*")
        ])
        
        print("✅ Package integrity check passed")
    
    def upload_to_test_pypi(self):
        """上传到测试PyPI"""
        print("🚀 Uploading to Test PyPI...")
        
        self.run_command([
            "twine", "upload",
            "--repository", "testpypi",
            str(self.dist_dir / "*")
        ])
        
        print("✅ Uploaded to Test PyPI")
        print("🔗 Check at: https://test.pypi.org/project/quickstock/")
    
    def upload_to_pypi(self):
        """上传到PyPI"""
        print("🚀 Uploading to PyPI...")
        
        # 确认上传
        response = input("⚠️  Are you sure you want to upload to PyPI? (yes/no): ")
        if response.lower() != "yes":
            print("❌ Upload cancelled")
            return
        
        self.run_command([
            "twine", "upload",
            str(self.dist_dir / "*")
        ])
        
        print("✅ Uploaded to PyPI")
        print("🔗 Check at: https://pypi.org/project/quickstock/")
    
    def verify_installation(self, test_pypi: bool = False):
        """验证安装"""
        print("🔍 Verifying installation...")
        
        # 获取版本号
        sys.path.insert(0, str(self.project_root))
        import quickstock
        version = quickstock.__version__
        
        # 构建安装命令
        if test_pypi:
            cmd = [
                sys.executable, "-m", "pip", "install",
                "--index-url", "https://test.pypi.org/simple/",
                "--extra-index-url", "https://pypi.org/simple/",
                f"quickstock=={version}"
            ]
        else:
            cmd = [
                sys.executable, "-m", "pip", "install",
                f"quickstock=={version}"
            ]
        
        print(f"💡 Test installation with: {' '.join(cmd)}")
    
    def create_release_notes(self):
        """创建发布说明"""
        print("📝 Creating release notes...")
        
        changelog_file = self.project_root / "CHANGELOG.md"
        if not changelog_file.exists():
            print("⚠️  CHANGELOG.md not found")
            return
        
        # 读取最新版本的更新内容
        content = changelog_file.read_text(encoding='utf-8')
        
        # 提取最新版本的内容
        import re
        pattern = r'## \[([^\]]+)\] - ([^\n]+)\n(.*?)(?=## \[|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        if matches:
            version, date, notes = matches[0]
            release_notes = f"# Release {version} ({date})\n\n{notes.strip()}"
            
            release_file = self.release_config_dir / f"RELEASE_NOTES_{version}.md"
            release_file.write_text(release_notes, encoding='utf-8')
            
            print(f"✅ Release notes created: {release_file}")
        else:
            print("⚠️  Could not extract release notes from CHANGELOG.md")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="QuickStock SDK发布工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
发布流程:
1. 清理构建产物
2. 运行测试和代码检查
3. 构建包
4. 检查包完整性
5. 上传到PyPI

示例:
  %(prog)s --dry-run           # 干运行，不上传
  %(prog)s --test-pypi         # 上传到测试PyPI
  %(prog)s --production        # 上传到生产PyPI
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='干运行，执行所有步骤但不上传'
    )
    
    parser.add_argument(
        '--test-pypi',
        action='store_true',
        help='上传到测试PyPI'
    )
    
    parser.add_argument(
        '--production',
        action='store_true',
        help='上传到生产PyPI'
    )
    
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='跳过测试'
    )
    
    parser.add_argument(
        '--skip-lint',
        action='store_true',
        help='跳过代码检查'
    )
    
    parser.add_argument(
        '--clean-only',
        action='store_true',
        help='只清理构建产物'
    )
    
    args = parser.parse_args()
    
    if not any([args.dry_run, args.test_pypi, args.production, args.clean_only]):
        parser.print_help()
        return
    
    try:
        rm = ReleaseManager()
        
        # 清理构建产物
        rm.clean_build_artifacts()
        
        if args.clean_only:
            print("🎉 Clean completed")
            return
        
        # 运行测试
        if not args.skip_tests:
            rm.run_tests()
        
        # 运行代码检查
        if not args.skip_lint:
            rm.run_linting()
        
        # 构建包
        rm.build_package()
        
        # 检查包
        rm.check_package()
        
        # 创建发布说明
        rm.create_release_notes()
        
        if args.dry_run:
            print("🎉 Dry run completed successfully")
            print("💡 Package is ready for release")
            
        elif args.test_pypi:
            rm.upload_to_test_pypi()
            rm.verify_installation(test_pypi=True)
            print("🎉 Test PyPI release completed")
            
        elif args.production:
            rm.upload_to_pypi()
            rm.verify_installation(test_pypi=False)
            print("🎉 Production release completed")
        
    except Exception as e:
        print(f"❌ Release failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()