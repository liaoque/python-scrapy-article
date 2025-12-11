# QuickStock SDK Release Makefile
# 提供发布相关的命令

.PHONY: help install install-dev test test-cov lint format clean build release-test release

# 项目根目录
PROJECT_ROOT := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PARENT_DIR := $(shell dirname $(PROJECT_ROOT))

# 默认目标
help:
	@echo "QuickStock SDK Release - 可用命令:"
	@echo ""
	@echo "环境设置:"
	@echo "  install      - 安装包（生产模式）"
	@echo "  install-dev  - 安装包（开发模式）"
	@echo "  deps         - 安装依赖"
	@echo ""
	@echo "代码质量:"
	@echo "  test         - 运行测试"
	@echo "  test-cov     - 运行测试并生成覆盖率报告"
	@echo "  lint         - 运行代码检查"
	@echo "  format       - 格式化代码"
	@echo ""
	@echo "构建和发布:"
	@echo "  clean        - 清理构建产物"
	@echo "  build        - 构建包"
	@echo "  release-test - 发布到测试PyPI"
	@echo "  release      - 发布到生产PyPI"
	@echo ""
	@echo "版本管理:"
	@echo "  version      - 显示当前版本"
	@echo "  bump-patch   - 升级补丁版本"
	@echo "  bump-minor   - 升级次版本"
	@echo "  bump-major   - 升级主版本"

# 安装
install:
	cd $(PROJECT_ROOT) && pip install .

install-dev:
	cd $(PROJECT_ROOT) && pip install -e ".[dev]"

deps:
	pip install -r $(PROJECT_ROOT)/requirements-dev.txt

# 测试
test:
	cd $(PROJECT_ROOT) && python -m pytest tests/ -v

test-cov:
	cd $(PROJECT_ROOT) && python -m pytest tests/ -v --cov=quickstock --cov-report=html --cov-report=term-missing

# 代码质量
lint:
	cd $(PARENT_DIR) && flake8 quickstock/ tests/ release_config/scripts/ --max-line-length=88 --extend-ignore=E203,W503
	cd $(PARENT_DIR) && mypy quickstock/ --ignore-missing-imports

format:
	cd $(PARENT_DIR) && black quickstock/ tests/ release_config/scripts/
	cd $(PARENT_DIR) && isort quickstock/ tests/ release_config/scripts/

format-check:
	cd $(PARENT_DIR) && black --check --diff quickstock/ tests/ release_config/scripts/
	cd $(PARENT_DIR) && isort --check-only --diff quickstock/ tests/ release_config/scripts/

# 构建和发布
clean:
	python $(PROJECT_ROOT)/scripts/release.py --clean-only

build:
	cd $(PROJECT_ROOT) && python -m build

check-build:
	cd $(PROJECT_ROOT) && twine check dist/*

release-test:
	python $(PROJECT_ROOT)/scripts/release.py --test-pypi

release:
	python $(PROJECT_ROOT)/scripts/release.py --production

release-dry:
	python $(PROJECT_ROOT)/scripts/release.py --dry-run

# 版本管理
version:
	python $(PROJECT_ROOT)/scripts/version_manager.py current

bump-patch:
	python $(PROJECT_ROOT)/scripts/version_manager.py bump patch

bump-minor:
	python $(PROJECT_ROOT)/scripts/version_manager.py bump minor

bump-major:
	python $(PROJECT_ROOT)/scripts/version_manager.py bump major

# 完整的发布前检查
pre-release: clean format lint test build check-build
	@echo "✅ 发布前检查完成"
	@echo "💡 运行 'make release-test' 来发布到测试PyPI"