"""
自定义错误类

提供清晰的错误分类，便于用户理解和处理SDK使用过程中的异常
"""


class QuickStockError(Exception):
    """
    SDK基础异常类
    所有SDK自定义异常的父类
    """
    pass


class DataSourceError(QuickStockError):
    """
    数据源异常
    用于处理与数据源相关的错误，如连接失败、API调用失败等
    """
    pass


class ValidationError(QuickStockError):
    """
    验证异常
    用于处理参数验证失败的情况，如无效的股票代码、日期格式错误等
    """
    pass


class AuthenticationError(DataSourceError):
    """
    认证异常
    用于处理登录失败等认证相关错误
    """
    pass


class NetworkError(DataSourceError):
    """
    网络异常
    用于处理网络连接问题
    """
    pass


class DataNotFoundError(DataSourceError):
    """
    数据未找到异常
    用于处理请求的数据不存在的情况
    """
    pass
