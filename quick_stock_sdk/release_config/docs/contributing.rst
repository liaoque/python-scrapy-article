Contributing to QuickStock SDK
==============================

我们欢迎任何形式的贡献！无论是一个小小的文档修复还是一个新的功能，我们都感激不尽。

如何贡献
--------

1. Fork 仓库
2. 创建您的特性分支 (git checkout -b feature/AmazingFeature)
3. 提交您的更改 (git commit -m 'Add some AmazingFeature')
4. 推送到分支 (git push origin feature/AmazingFeature)
5. 开启一个 Pull Request

报告问题
-------

如果您发现了 bug 或者有任何改进建议，请在 GitHub 上开启一个 Issue。

开发环境设置
----------

1. 克隆仓库:

.. code-block:: bash

    git clone https://github.com/your-repo/quickstock.git
    cd quickstock

2. 安装开发依赖:

.. code-block:: bash

    pip install -r requirements-dev.txt

3. 运行测试:

.. code-block:: bash

    pytest

编码规范
-------

- 遵循 PEP 8 编码规范
- 添加适当的文档字符串
- 编写测试用例
- 保持向后兼容性

文档
----

文档使用 Sphinx 编写，源文件位于 ``docs/`` 目录中。要构建文档，请运行:

.. code-block:: bash

    cd docs
    make html

然后打开 ``_build/html/index.html`` 查看生成的文档。