"""
财务报告服务

提供财务报告、业绩预告和业绩快报的核心业务逻辑
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd

from ..models import (
    DataRequest, FinancialReport, EarningsForecast, FlashReport,
    FinancialReportsRequest, EarningsForecastRequest, FlashReportsRequest
)
from ..core.data_manager import DataManager
from ..core.errors import (
    ValidationError, DataSourceError, FinancialDataError,
    ReportNotFoundError, ForecastDataError, FlashReportError,
    FinancialDataValidationError, RateLimitError, NetworkError
)
from ..utils.performance_monitor import get_performance_monitor
from ..utils.memory_optimizer import ChunkedDataProcessor, DataFrameOptimizer, memory_efficient_processing


class FinancialReportsService:
    """
    财务报告服务
    
    提供财务报告相关数据的核心业务逻辑，包括：
    - 实时获取和返回财务报告数据
    - 实时获取和返回业绩预告数据  
    - 实时获取和返回业绩快报数据
    - 多股票批量查询
    - 错误处理和重试机制
    """
    
    # 批处理配置
    BATCH_CONFIG = {
        'max_batch_size': 50,       # 最大批处理大小
        'batch_timeout': 60,        # 批处理超时时间（秒）
        'concurrent_limit': 5       # 并发请求限制
    }
    
    # 重试配置
    RETRY_CONFIG = {
        'max_retries': 3,           # 最大重试次数
        'base_delay': 1.0,          # 基础延迟时间（秒）
        'max_delay': 30.0,          # 最大延迟时间（秒）
        'backoff_factor': 2.0       # 退避因子
    }
    
    def __init__(self, data_manager: DataManager, 
                 logger: Optional[logging.Logger] = None):
        """
        初始化财务报告服务
        
        Args:
            data_manager: 数据管理器
            logger: 日志记录器
        """
        self.data_manager = data_manager
        self.logger = logger or logging.getLogger(__name__)
        
        # 初始化性能监控和内存优化
        self.performance_monitor = get_performance_monitor()
        self.data_processor = ChunkedDataProcessor(chunk_size=1000, memory_limit_mb=200.0)
        
        # 初始化统计信息
        self._stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'batch_requests': 0,
            'retry_attempts': 0,
            'total_processing_time': 0.0,
            'last_request_time': None
        }
        
        # 初始化信号量用于并发控制
        self._semaphore = asyncio.Semaphore(self.BATCH_CONFIG['concurrent_limit'])
    
    async def get_financial_reports(self, request: FinancialReportsRequest) -> List[FinancialReport]:
        """
        获取财务报告数据
        
        Args:
            request: 财务报告请求
            
        Returns:
            财务报告数据列表
            
        Raises:
            FinancialDataError: 财务数据相关错误
            ReportNotFoundError: 报告未找到
        """
        # 使用性能监控
        async with self.performance_monitor.measure_operation(
            f"get_financial_reports_{request.ts_code}"
        ) as monitor:
            start_time = datetime.now()
            self._update_request_stats()
            
            try:
                self.logger.info(f"开始获取财务报告: {request.ts_code}, {request.start_date}-{request.end_date}")
                
                # 1. 验证请求参数
                request.validate()
                
                # 2. 从数据源获取数据（带重试机制）
                raw_data = await self._fetch_with_retry(
                    self._fetch_financial_reports_data, request
                )
                
                # 3. 使用内存优化的数据处理
                with memory_efficient_processing("处理财务报告数据"):
                    # 优化原始数据的内存使用
                    if not raw_data.empty:
                        raw_data = DataFrameOptimizer.optimize_dtypes(raw_data)
                    
                    # 数据验证和转换
                    financial_reports = self._process_financial_reports_data(raw_data, request)
                
                # 4. 记录成功统计
                processing_time = (datetime.now() - start_time).total_seconds()
                self._update_success_stats(processing_time)
                
                self.logger.info(f"成功获取{len(financial_reports)}条财务报告，处理时间: {processing_time:.2f}s")
                return financial_reports
                
            except Exception as e:
                self._update_failure_stats()
                if isinstance(e, (FinancialDataError, ReportNotFoundError)):
                    raise
                else:
                    self.logger.error(f"获取财务报告失败: {e}")
                    raise FinancialDataError(
                        f"获取财务报告失败: {str(e)}",
                        error_code="FINANCIAL_REPORTS_ERROR",
                        details={'request': request.to_dict(), 'error': str(e)}
                    )
    
    async def get_earnings_forecast(self, request: EarningsForecastRequest) -> List[EarningsForecast]:
        """
        获取业绩预告数据
        
        Args:
            request: 业绩预告请求
            
        Returns:
            业绩预告数据列表
            
        Raises:
            FinancialDataError: 财务数据相关错误
            ForecastDataError: 预告数据错误
        """
        start_time = datetime.now()
        self._update_request_stats()
        
        try:
            self.logger.info(f"开始获取业绩预告: {request.ts_code}, {request.start_date}-{request.end_date}")
            
            # 1. 验证请求参数
            request.validate()
            
            # 2. 从数据源获取数据（带重试机制）
            raw_data = await self._fetch_with_retry(
                self._fetch_earnings_forecast_data, request
            )
            
            # 3. 数据验证和转换
            earnings_forecasts = self._process_earnings_forecast_data(raw_data, request)
            
            # 4. 记录成功统计
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_success_stats(processing_time)
            
            self.logger.info(f"成功获取{len(earnings_forecasts)}条业绩预告，处理时间: {processing_time:.2f}s")
            return earnings_forecasts
            
        except Exception as e:
            self._update_failure_stats()
            if isinstance(e, (FinancialDataError, ForecastDataError)):
                raise
            else:
                self.logger.error(f"获取业绩预告失败: {e}")
                raise ForecastDataError(
                    request.ts_code,
                    f"获取业绩预告失败: {str(e)}"
                )
    
    async def get_earnings_flash_reports(self, request: FlashReportsRequest) -> List[FlashReport]:
        """
        获取业绩快报数据
        
        Args:
            request: 业绩快报请求
            
        Returns:
            业绩快报数据列表
            
        Raises:
            FinancialDataError: 财务数据相关错误
            FlashReportError: 快报数据错误
        """
        start_time = datetime.now()
        self._update_request_stats()
        
        try:
            self.logger.info(f"开始获取业绩快报: {request.ts_code}, {request.start_date}-{request.end_date}")
            
            # 1. 验证请求参数
            request.validate()
            
            # 2. 从数据源获取数据（带重试机制）
            raw_data = await self._fetch_with_retry(
                self._fetch_flash_reports_data, request
            )
            
            # 3. 数据验证和转换
            flash_reports = self._process_flash_reports_data(raw_data, request)
            
            # 4. 记录成功统计
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_success_stats(processing_time)
            
            self.logger.info(f"成功获取{len(flash_reports)}条业绩快报，处理时间: {processing_time:.2f}s")
            return flash_reports
            
        except Exception as e:
            self._update_failure_stats()
            if isinstance(e, (FinancialDataError, FlashReportError)):
                raise
            else:
                self.logger.error(f"获取业绩快报失败: {e}")
                raise FlashReportError(
                    request.ts_code,
                    f"获取业绩快报失败: {str(e)}"
                )    

    async def get_batch_financial_data(self, stock_codes: List[str], 
                                     data_types: List[str] = None,
                                     start_date: str = None, 
                                     end_date: str = None,
                                     **kwargs) -> Dict[str, Any]:
        """
        批量获取多股票的财务数据
        
        Args:
            stock_codes: 股票代码列表
            data_types: 数据类型列表，可选值: ['financial_reports', 'earnings_forecast', 'flash_reports']
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数
            
        Returns:
            批量财务数据结果字典
            
        Raises:
            FinancialDataError: 财务数据相关错误
        """
        start_time = datetime.now()
        self._update_request_stats()
        self._stats['batch_requests'] += 1
        
        try:
            self.logger.info(f"开始批量获取财务数据: {len(stock_codes)}只股票")
            
            # 1. 参数验证
            if not stock_codes:
                raise ValidationError("股票代码列表不能为空")
            
            if len(stock_codes) > self.BATCH_CONFIG['max_batch_size']:
                raise ValidationError(f"批量大小超过限制: {len(stock_codes)} > {self.BATCH_CONFIG['max_batch_size']}")
            
            if data_types is None:
                data_types = ['financial_reports', 'earnings_forecast', 'flash_reports']
            
            # 验证数据类型
            valid_types = ['financial_reports', 'earnings_forecast', 'flash_reports']
            invalid_types = set(data_types) - set(valid_types)
            if invalid_types:
                raise ValidationError(f"无效的数据类型: {invalid_types}")
            
            # 2. 分批处理股票代码
            batch_results = {}
            failed_stocks = {}
            
            # 将股票代码分成小批次
            batch_size = min(10, len(stock_codes))  # 每批最多10只股票
            stock_batches = [stock_codes[i:i + batch_size] for i in range(0, len(stock_codes), batch_size)]
            
            # 3. 并发处理各批次
            for batch_idx, stock_batch in enumerate(stock_batches):
                self.logger.debug(f"处理第{batch_idx + 1}/{len(stock_batches)}批股票: {stock_batch}")
                
                # 为每个股票创建任务
                tasks = []
                for stock_code in stock_batch:
                    task = self._process_single_stock_batch(
                        stock_code, data_types, start_date, end_date, **kwargs
                    )
                    tasks.append(task)
                
                # 并发执行任务
                batch_timeout = self.BATCH_CONFIG['batch_timeout']
                try:
                    results = await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True),
                        timeout=batch_timeout
                    )
                    
                    # 处理结果
                    for i, result in enumerate(results):
                        stock_code = stock_batch[i]
                        if isinstance(result, Exception):
                            failed_stocks[stock_code] = str(result)
                            self.logger.warning(f"股票{stock_code}处理失败: {result}")
                        else:
                            batch_results[stock_code] = result
                            
                except asyncio.TimeoutError:
                    self.logger.error(f"批次{batch_idx + 1}处理超时")
                    for stock_code in stock_batch:
                        if stock_code not in batch_results:
                            failed_stocks[stock_code] = "处理超时"
            
            # 4. 构建返回结果
            processing_time = (datetime.now() - start_time).total_seconds()
            result = {
                'success_count': len(batch_results),
                'failed_count': len(failed_stocks),
                'total_count': len(stock_codes),
                'processing_time': processing_time,
                'data': batch_results,
                'failed_stocks': failed_stocks,
                'data_types': data_types,
                'date_range': {
                    'start_date': start_date,
                    'end_date': end_date
                }
            }
            
            # 5. 记录统计信息
            if batch_results:
                self._update_success_stats(processing_time)
            if failed_stocks:
                self._update_failure_stats()
            
            self.logger.info(f"批量处理完成: 成功{len(batch_results)}, 失败{len(failed_stocks)}, "
                           f"处理时间: {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            self._update_failure_stats()
            if isinstance(e, (FinancialDataError, ValidationError)):
                raise
            else:
                self.logger.error(f"批量获取财务数据失败: {e}")
                raise FinancialDataError(
                    f"批量获取财务数据失败: {str(e)}",
                    error_code="BATCH_FINANCIAL_DATA_ERROR",
                    details={'stock_codes': stock_codes, 'data_types': data_types}
                )
    
    async def _process_single_stock_batch(self, stock_code: str, data_types: List[str],
                                        start_date: str, end_date: str, **kwargs) -> Dict[str, Any]:
        """
        处理单只股票的批量数据获取
        
        Args:
            stock_code: 股票代码
            data_types: 数据类型列表
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数
            
        Returns:
            单只股票的财务数据
        """
        async with self._semaphore:  # 控制并发数
            stock_data = {}
            
            for data_type in data_types:
                try:
                    if data_type == 'financial_reports':
                        request = FinancialReportsRequest(
                            ts_code=stock_code,
                            start_date=start_date,
                            end_date=end_date,
                            **kwargs
                        )
                        data = await self.get_financial_reports(request)
                        stock_data[data_type] = [item.to_dict() for item in data]
                        
                    elif data_type == 'earnings_forecast':
                        request = EarningsForecastRequest(
                            ts_code=stock_code,
                            start_date=start_date,
                            end_date=end_date,
                            **kwargs
                        )
                        data = await self.get_earnings_forecast(request)
                        stock_data[data_type] = [item.to_dict() for item in data]
                        
                    elif data_type == 'flash_reports':
                        request = FlashReportsRequest(
                            ts_code=stock_code,
                            start_date=start_date,
                            end_date=end_date,
                            **kwargs
                        )
                        data = await self.get_earnings_flash_reports(request)
                        stock_data[data_type] = [item.to_dict() for item in data]
                        
                except Exception as e:
                    self.logger.warning(f"获取{stock_code}的{data_type}数据失败: {e}")
                    stock_data[data_type] = {'error': str(e)}
            
            return stock_data
    
    async def _fetch_with_retry(self, fetch_func, request, max_retries: int = None):
        """
        带指数退避的重试机制
        
        Args:
            fetch_func: 数据获取函数
            request: 请求对象
            max_retries: 最大重试次数
            
        Returns:
            获取的数据
        """
        if max_retries is None:
            max_retries = self.RETRY_CONFIG['max_retries']
        
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return await fetch_func(request)
                
            except Exception as e:
                last_error = e
                self._stats['retry_attempts'] += 1
                
                # 判断是否应该重试
                if not self._should_retry(e) or attempt >= max_retries:
                    break
                
                # 计算延迟时间（指数退避）
                delay = min(
                    self.RETRY_CONFIG['base_delay'] * (self.RETRY_CONFIG['backoff_factor'] ** attempt),
                    self.RETRY_CONFIG['max_delay']
                )
                
                self.logger.warning(f"第{attempt + 1}次尝试失败，{delay:.2f}秒后重试: {e}")
                await asyncio.sleep(delay)
        
        # 所有重试都失败了
        raise last_error
    
    def _should_retry(self, error: Exception) -> bool:
        """
        判断是否应该重试
        
        Args:
            error: 异常对象
            
        Returns:
            是否应该重试
        """
        # 网络相关错误应该重试
        if isinstance(error, (NetworkError, ConnectionError, TimeoutError)):
            return True
        
        # 速率限制错误应该重试
        if isinstance(error, RateLimitError):
            return True
        
        # 数据源临时错误应该重试
        if isinstance(error, DataSourceError):
            error_msg = str(error).lower()
            temporary_keywords = [
                'timeout', 'connection', 'network', 'temporary', 
                'server error', '502', '503', '504'
            ]
            return any(keyword in error_msg for keyword in temporary_keywords)
        
        # 参数验证错误不应该重试
        if isinstance(error, (ValidationError, FinancialDataValidationError)):
            return False
        
        # 其他财务数据错误通常不需要重试
        if isinstance(error, (ReportNotFoundError, ForecastDataError, FlashReportError)):
            return False
        
        # 默认不重试
        return False
    
    async def _fetch_financial_reports_data(self, request: FinancialReportsRequest) -> pd.DataFrame:
        """
        从数据源获取财务报告数据
        
        Args:
            request: 财务报告请求
            
        Returns:
            原始财务报告数据
        """
        # 创建数据请求
        data_request = DataRequest(
            data_type='financial_reports',
            ts_code=request.ts_code,
            start_date=request.start_date,
            end_date=request.end_date,
            extra_params={
                'report_type': request.report_type,
                'fields': request.fields
            }
        )
        
        # 从数据管理器获取数据
        raw_data = await self.data_manager.get_data(data_request)
        
        if raw_data.empty:
            raise ReportNotFoundError(
                request.ts_code,
                request.start_date or request.end_date,
                request.report_type
            )
        
        return raw_data
    
    async def _fetch_earnings_forecast_data(self, request: EarningsForecastRequest) -> pd.DataFrame:
        """
        从数据源获取业绩预告数据
        
        Args:
            request: 业绩预告请求
            
        Returns:
            原始业绩预告数据
        """
        # 创建数据请求
        data_request = DataRequest(
            data_type='earnings_forecast',
            ts_code=request.ts_code,
            start_date=request.start_date,
            end_date=request.end_date,
            extra_params={
                'forecast_type': request.forecast_type,
                'fields': request.fields
            }
        )
        
        # 从数据管理器获取数据
        raw_data = await self.data_manager.get_data(data_request)
        
        if raw_data.empty:
            raise ForecastDataError(
                request.ts_code,
                "未找到业绩预告数据"
            )
        
        return raw_data
    
    async def _fetch_flash_reports_data(self, request: FlashReportsRequest) -> pd.DataFrame:
        """
        从数据源获取业绩快报数据
        
        Args:
            request: 业绩快报请求
            
        Returns:
            原始业绩快报数据
        """
        # 创建数据请求
        data_request = DataRequest(
            data_type='flash_reports',
            ts_code=request.ts_code,
            start_date=request.start_date,
            end_date=request.end_date,
            extra_params={
                'sort_by': getattr(request, 'sort_by', 'publish_date'),
                'fields': request.fields
            }
        )
        
        # 从数据管理器获取数据
        raw_data = await self.data_manager.get_data(data_request)
        
        if raw_data.empty:
            raise FlashReportError(
                request.ts_code,
                "未找到业绩快报数据"
            )
        
        return raw_data
    
    def _process_financial_reports_data(self, raw_data: pd.DataFrame, 
                                      request: FinancialReportsRequest) -> List[FinancialReport]:
        """
        处理财务报告原始数据
        
        Args:
            raw_data: 原始数据
            request: 请求对象
            
        Returns:
            处理后的财务报告列表
        """
        financial_reports = []
        
        for _, row in raw_data.iterrows():
            try:
                # 数据验证和转换
                financial_report = FinancialReport(
                    ts_code=str(row.get('ts_code', '')),
                    report_date=str(row.get('report_date', '')),
                    report_type=str(row.get('report_type', '')),
                    total_revenue=float(row.get('total_revenue', 0.0)),
                    net_profit=float(row.get('net_profit', 0.0)),
                    total_assets=float(row.get('total_assets', 0.0)),
                    total_liabilities=float(row.get('total_liabilities', 0.0)),
                    shareholders_equity=float(row.get('shareholders_equity', 0.0)),
                    operating_cash_flow=float(row.get('operating_cash_flow', 0.0)),
                    eps=float(row.get('eps', 0.0)),
                    roe=float(row.get('roe', 0.0))
                )
                
                financial_reports.append(financial_report)
                
            except Exception as e:
                self.logger.warning(f"处理财务报告数据失败: {e}, 行数据: {row.to_dict()}")
                continue
        
        if not financial_reports:
            raise ReportNotFoundError(
                request.ts_code,
                request.start_date or request.end_date,
                request.report_type
            )
        
        return financial_reports
    
    def _process_earnings_forecast_data(self, raw_data: pd.DataFrame,
                                      request: EarningsForecastRequest) -> List[EarningsForecast]:
        """
        处理业绩预告原始数据
        
        Args:
            raw_data: 原始数据
            request: 请求对象
            
        Returns:
            处理后的业绩预告列表
        """
        earnings_forecasts = []
        
        for _, row in raw_data.iterrows():
            try:
                # 数据验证和转换
                earnings_forecast = EarningsForecast(
                    ts_code=str(row.get('ts_code', '')),
                    forecast_date=str(row.get('forecast_date', '')),
                    forecast_period=str(row.get('forecast_period', '')),
                    forecast_type=str(row.get('forecast_type', '')),
                    net_profit_min=float(row.get('net_profit_min', 0.0)),
                    net_profit_max=float(row.get('net_profit_max', 0.0)),
                    growth_rate_min=float(row.get('growth_rate_min', 0.0)),
                    growth_rate_max=float(row.get('growth_rate_max', 0.0)),
                    forecast_summary=str(row.get('forecast_summary', ''))
                )
                
                earnings_forecasts.append(earnings_forecast)
                
            except Exception as e:
                self.logger.warning(f"处理业绩预告数据失败: {e}, 行数据: {row.to_dict()}")
                continue
        
        if not earnings_forecasts:
            raise ForecastDataError(
                request.ts_code,
                "业绩预告数据处理失败"
            )
        
        return earnings_forecasts
    
    def _process_flash_reports_data(self, raw_data: pd.DataFrame,
                                  request: FlashReportsRequest) -> List[FlashReport]:
        """
        处理业绩快报原始数据
        
        Args:
            raw_data: 原始数据
            request: 请求对象
            
        Returns:
            处理后的业绩快报列表
        """
        flash_reports = []
        
        for _, row in raw_data.iterrows():
            try:
                # 数据验证和转换
                flash_report = FlashReport(
                    ts_code=str(row.get('ts_code', '')),
                    report_date=str(row.get('report_date', '')),
                    publish_date=str(row.get('publish_date', '')),
                    report_period=str(row.get('report_period', '')),
                    total_revenue=float(row.get('total_revenue', 0.0)),
                    net_profit=float(row.get('net_profit', 0.0)),
                    revenue_growth=float(row.get('revenue_growth', 0.0)),
                    profit_growth=float(row.get('profit_growth', 0.0)),
                    eps=float(row.get('eps', 0.0)),
                    report_summary=str(row.get('report_summary', ''))
                )
                
                flash_reports.append(flash_report)
                
            except Exception as e:
                self.logger.warning(f"处理业绩快报数据失败: {e}, 行数据: {row.to_dict()}")
                continue
        
        if not flash_reports:
            raise FlashReportError(
                request.ts_code,
                "业绩快报数据处理失败"
            )
        
        return flash_reports
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        获取性能统计信息
        
        Returns:
            性能统计信息字典
        """
        # 获取性能监控器的统计信息
        monitor_stats = self.performance_monitor.get_performance_summary()
        
        # 合并服务层统计信息
        return {
            'service_stats': self._stats.copy(),
            'performance_monitor': monitor_stats,
            'memory_processor': {
                'chunk_size': self.data_processor.chunk_size,
                'memory_limit_mb': self.data_processor.memory_limit_mb
            }
        }
    
    def reset_performance_stats(self):
        """重置性能统计信息"""
        self._stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'batch_requests': 0,
            'retry_attempts': 0,
            'total_processing_time': 0.0,
            'last_request_time': None
        }
        self.performance_monitor.reset_stats()
    
    def _convert_to_financial_reports(self, data: pd.DataFrame) -> List[FinancialReport]:
        """
        将DataFrame转换为FinancialReport列表
        
        Args:
            data: DataFrame数据
            
        Returns:
            FinancialReport列表
        """
        financial_reports = []
        
        for _, row in data.iterrows():
            try:
                financial_report = FinancialReport.from_dict(row.to_dict())
                financial_reports.append(financial_report)
            except Exception as e:
                self.logger.warning(f"转换财务报告数据失败: {e}")
                continue
        
        return financial_reports
    
    def _convert_to_earnings_forecasts(self, data: pd.DataFrame) -> List[EarningsForecast]:
        """
        将DataFrame转换为EarningsForecast列表
        
        Args:
            data: DataFrame数据
            
        Returns:
            EarningsForecast列表
        """
        earnings_forecasts = []
        
        for _, row in data.iterrows():
            try:
                earnings_forecast = EarningsForecast.from_dict(row.to_dict())
                earnings_forecasts.append(earnings_forecast)
            except Exception as e:
                self.logger.warning(f"转换业绩预告数据失败: {e}")
                continue
        
        return earnings_forecasts
    
    def _convert_to_flash_reports(self, data: pd.DataFrame) -> List[FlashReport]:
        """
        将DataFrame转换为FlashReport列表
        
        Args:
            data: DataFrame数据
            
        Returns:
            FlashReport列表
        """
        flash_reports = []
        
        for _, row in data.iterrows():
            try:
                flash_report = FlashReport.from_dict(row.to_dict())
                flash_reports.append(flash_report)
            except Exception as e:
                self.logger.warning(f"转换业绩快报数据失败: {e}")
                continue
        
        return flash_reports
    
    def _convert_financial_reports_to_dataframe(self, reports: List[FinancialReport]) -> pd.DataFrame:
        """
        将FinancialReport列表转换为DataFrame
        
        Args:
            reports: FinancialReport列表
            
        Returns:
            DataFrame数据
        """
        if not reports:
            return pd.DataFrame()
        
        data = [report.to_dict() for report in reports]
        return pd.DataFrame(data)
    
    def _convert_earnings_forecasts_to_dataframe(self, forecasts: List[EarningsForecast]) -> pd.DataFrame:
        """
        将EarningsForecast列表转换为DataFrame
        
        Args:
            forecasts: EarningsForecast列表
            
        Returns:
            DataFrame数据
        """
        if not forecasts:
            return pd.DataFrame()
        
        data = [forecast.to_dict() for forecast in forecasts]
        return pd.DataFrame(data)
    
    def _convert_flash_reports_to_dataframe(self, reports: List[FlashReport]) -> pd.DataFrame:
        """
        将FlashReport列表转换为DataFrame
        
        Args:
            reports: FlashReport列表
            
        Returns:
            DataFrame数据
        """
        if not reports:
            return pd.DataFrame()
        
        data = [report.to_dict() for report in reports]
        return pd.DataFrame(data)
    
    def _update_request_stats(self):
        """更新请求统计"""
        self._stats['total_requests'] += 1
        self._stats['last_request_time'] = datetime.now()
    
    def _update_success_stats(self, processing_time: float):
        """更新成功统计"""
        self._stats['successful_requests'] += 1
        self._stats['total_processing_time'] += processing_time
    
    def _update_failure_stats(self):
        """更新失败统计"""
        self._stats['failed_requests'] += 1
    
    def get_service_stats(self) -> Dict[str, Any]:
        """
        获取服务统计信息
        
        Returns:
            服务统计数据
        """
        total_requests = self._stats['total_requests']
        successful_requests = self._stats['successful_requests']
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': self._stats['failed_requests'],
            'success_rate': successful_requests / total_requests if total_requests > 0 else 0,
            'batch_requests': self._stats['batch_requests'],
            'retry_attempts': self._stats['retry_attempts'],
            'average_processing_time': (
                self._stats['total_processing_time'] / successful_requests
                if successful_requests > 0 else 0
            ),
            'last_request_time': self._stats['last_request_time'].isoformat() if self._stats['last_request_time'] else None
        }
    
    def reset_stats(self):
        """重置统计信息"""
        self._stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'batch_requests': 0,
            'retry_attempts': 0,
            'total_processing_time': 0.0,
            'last_request_time': None
        }