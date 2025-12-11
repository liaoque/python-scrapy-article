# QuickStock SDK 发布配置使用说明

## 概述

`release_config` 目录包含了QuickStock SDK的完整发布配置，与主项目代码分离，便于管理和维护。所有tushare相关的依赖和配置已被移除。

## 主要特性

✅ **独立配置**: 与主项目代码完全分离  
✅ **无Tushare依赖**: 移除了所有tushare相关内容  
✅ **自动化发布**: 支持测试PyPI和生产PyPI  
✅ **版本管理**: 自动版本升级和Git标签  
✅ **代码质量**: 集成格式化、检查和测试  

## 快速使用

### 1. 构建包

```bash
cd release_config
python -m build
```

### 2. 测试发布

```bash
cd release_config
python scripts/release.py --dry-run --skip-tests --skip-lint
```

### 3. 版本管理

```bash
# 查看当前版本
cd release_config
python scripts/version_manager.py current

# 升级版本
python scripts/version_manager.py bump patch
```

### 4. 使用Makefile（推荐）

```bash
cd release_config

# 查看所有可用命令
make help

# 构建包
make build

# 发布到测试PyPI
make release-test

# 发布到生产PyPI
make release
```

## 核心依赖

- `pandas>=1.3.0` - 数据处理
- `numpy>=1.20.0` - 数值计算  
- `requests>=2.25.0` - HTTP请求
- `aiohttp>=3.8.0` - 异步HTTP
- `pyyaml>=5.4.0` - 配置文件
- `python-dateutil>=2.8.0` - 日期处理

## 可选依赖

- `baostock>=0.8.0` - Baostock数据源支持

## 文件说明

- `setup.py` - 包配置文件
- `requirements.txt` - 核心依赖
- `requirements-dev.txt` - 开发依赖
- `package_README.md` - 包的README文件
- `scripts/` - 发布和版本管理脚本
- `Makefile` - 常用命令快捷方式

## 注意事项

1. 所有tushare相关的依赖和配置已被完全移除
2. 发布配置与主项目代码分离，避免混淆
3. 使用独立的README文件用于包描述
4. 支持Python 3.7+版本

## 测试验证

构建成功后，可以验证包的完整性：

```bash
cd release_config
twine check dist/*
```

这个配置已经过测试，可以成功构建和发布QuickStock SDK包。