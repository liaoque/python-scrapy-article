from setuptools import setup, find_packages

setup(
    name="quick_stock_sdk",
    version="0.1.2",
    packages=find_packages(),
    include_package_data=True,
    description="A quick stock SDK for retrieving stock prices and information",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="liao que",
    author_email="",
    url="",  # 更新为实际的项目URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "requests",
        "pandas",
        "tushare",
        "numpy",
    ],
    tests_require=[
        "pytest",
    ],
    test_suite='tests',
)
