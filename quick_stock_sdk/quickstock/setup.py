"""
QuickStock SDK - 易于使用的金融数据获取SDK
"""
import os
import sys
from setuptools import setup, find_packages

# 读取版本信息
def get_version():
    """从src/quickstock/__init__.py文件中获取版本号"""
    version_file = os.path.join(os.path.dirname(__file__), 'src', 'quickstock', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return "1.0.0"

# 读取长描述
def get_long_description():
    """读取README.md作为长描述"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# 读取requirements.txt
def get_requirements():
    """读取requirements.txt中的依赖"""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="quickstock",
    version=get_version(),
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    
    # 项目描述
    description="QuickStock SDK - 易于使用的金融数据获取SDK，用于获取股票、指数和基金数据",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    
    # 作者信息
    author="QuickStock Team",
    author_email="quickstock@example.com",
    
    # 项目链接
    url="https://github.com/quickstock/quickstock-sdk",
    project_urls={
        "Bug Reports": "https://github.com/quickstock/quickstock-sdk/issues",
        "Source": "https://github.com/quickstock/quickstock-sdk",
    },
    
    # 分类信息
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    
    # Python版本要求
    python_requires='>=3.7',
    
    # 关键词
    keywords="stock, finance, data, sdk, baostock, 股票, 金融数据",
    
    # 依赖管理
    install_requires=get_requirements() or [
        "requests>=2.25.0",
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "aiohttp>=3.8.0",
        "python-dateutil>=2.8.0",
    ],
    
    # 可选依赖
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=2.12.0",
        ],
        "baostock": [
            "baostock>=0.8.0",
        ],
    },
    
    # 包数据
    package_data={
        'quickstock': ['py.typed'],
    },
    
    # ZIP安全
    zip_safe=False,
)
