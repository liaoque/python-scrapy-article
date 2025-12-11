# QuickStock SDK 发布配置

这个目录包含了QuickStock SDK的发布配置文件和脚本，与主项目代码分离，便于管理和维护。

QuickStock SDK是一个轻量级的金融数据获取工具，专注于实时数据获取，不包含缓存或数据库持久化功能。

## 目录结构

```
release_config/
├── README.md                    # 本文件
├── setup.py                     # 包配置文件
├── pyproject.toml              # 现代Python包配置
├── requirements.txt            # 核心依赖
├── requirements-dev.txt        # 开发依赖
├── MANIFEST.in                 # 包含文件配置
├── Makefile                    # 常用命令
├── .pre-commit-config.yaml     # 代码质量检查
├── .github/workflows/          # GitHub Actions配置
│   └── release.yml
└── scripts/                    # 发布脚本
    ├── version_manager.py      # 版本管理
    ├── release.py              # 发布管理
    └── extract_changelog.py    # 提取更新日志
```

## 特性

- ✅ **独立配置**: 与主项目代码分离，避免混淆
- ✅ **无Tushare依赖**: 移除了所有tushare相关的依赖和配置
- ✅ **自动化发布**: 支持测试PyPI和生产PyPI发布
- ✅ **版本管理**: 自动版本升级和标签创建
- ✅ **代码质量**: 集成代码格式化、检查和测试
- ✅ **CI/CD**: GitHub Actions自动化流程
- ✅ **实时数据**: 直接从数据源获取最新数据，确保数据实时性

## 快速开始

### 1. 安装依赖

```bash
# 安装开发依赖
pip install -r release_config/requirements-dev.txt

# 或使用Makefile
cd release_config && make deps
```

### 2. 构建包

```bash
# 进入发布配置目录
cd release_config

# 构建包
make build

# 或直接使用Python
python -m build
```

### 3. 发布到测试PyPI

```bash
cd release_config
make release-test

# 或使用脚本
python scripts/release.py --test-pypi
```

### 4. 发布到生产PyPI

```bash
cd release_config
make release

# 或使用脚本
python scripts/release.py --production
```

## 版本管理

### 查看当前版本

```bash
cd release_config
make version

# 或使用脚本
python scripts/version_manager.py current
```

### 升级版本

```bash
# 升级补丁版本 (1.0.0 -> 1.0.1)
cd release_config && make bump-patch

# 升级次版本 (1.0.0 -> 1.1.0)
cd release_config && make bump-minor

# 升级主版本 (1.0.0 -> 2.0.0)
cd release_config && make bump-major
```

## 代码质量

### 格式化代码

```bash
cd release_config
make format
```

### 检查代码质量

```bash
cd release_config
make lint
```

### 运行测试

```bash
cd release_config
make test
```

## 发布流程

### 完整发布流程

1. **准备发布**
   ```bash
   cd release_config
   make pre-release  # 格式化、检查、测试、构建
   ```

2. **测试发布**
   ```bash
   make release-test  # 发布到测试PyPI
   ```

3. **验证测试版本**
   ```bash
   # 在新环境中测试安装
   pip install --index-url https://test.pypi.org/simple/ \
              --extra-index-url https://pypi.org/simple/ \
              quickstock
   ```

4. **生产发布**
   ```bash
   make release  # 发布到生产PyPI
   ```

### 自动化发布

推送版本标签会触发GitHub Actions自动发布：

```bash
# 升级版本并创建标签
cd release_config
make bump-patch  # 这会自动创建Git标签

# 推送标签触发自动发布
git push origin v1.0.1
```

## 配置说明

### 核心依赖 (requirements.txt)

- `pandas>=1.3.0` - 数据处理
- `numpy>=1.20.0` - 数值计算
- `requests>=2.25.0` - HTTP请求
- `aiohttp>=3.8.0` - 异步HTTP
- `pyyaml>=5.4.0` - 配置文件
- `python-dateutil>=2.8.0` - 日期处理

### 可选依赖

- `baostock>=0.8.0` - Baostock数据源支持

### 开发依赖 (requirements-dev.txt)

- 测试框架: pytest, pytest-asyncio, pytest-cov
- 代码质量: black, flake8, mypy, isort
- 文档生成: sphinx
- 构建工具: build, twine, wheel

## 环境变量

发布到PyPI需要配置API令牌：

```bash
# 配置PyPI令牌
pip install keyring
keyring set https://upload.pypi.org/legacy/ __token__

# 配置测试PyPI令牌
keyring set https://test.pypi.org/legacy/ __token__
```

## 常见问题

### 构建失败

```bash
# 清理并重新构建
cd release_config
make clean
make build
```

### 上传失败

检查PyPI凭据配置，确保API令牌正确设置。

### 版本冲突

如果版本号已存在于PyPI：

```bash
cd release_config
make bump-patch  # 升级到下一个版本
make release
```

## 最佳实践

1. **定期发布**: 建议每2-4周发布一次
2. **测试优先**: 始终先发布到测试PyPI
3. **版本语义**: 遵循语义化版本规范
4. **文档同步**: 保持CHANGELOG.md更新
5. **代码质量**: 发布前运行完整的质量检查

## 支持的Python版本

- Python 3.7+
- 在CI中测试Python 3.7, 3.8, 3.9, 3.10, 3.11

## 许可证

MIT License - 详见项目根目录的LICENSE文件。