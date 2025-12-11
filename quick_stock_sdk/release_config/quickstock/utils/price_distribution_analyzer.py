"""
涨跌分布分析器

整合分布计算器和统计聚合器，实现完整的分布分析流程，
包括市场板块分布计算功能和缓存机制集成
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd

from ..core.errors import ValidationError
from ..models.price_distribution_models import (
    PriceDistributionRequest, 
    PriceDistributionStats, 
    DistributionRange
)
from .distribution_calculator import DistributionCalculator, DistributionResult
from .statistics_aggregator import StatisticsAggregator, MarketStatistics
from .price_distribution_performance import PriceDistributionPerformanceOptimizer


class PriceDistributionAnalysisError(ValidationError):
    """分布分析异常"""
    
    def __init__(self, message: str, analysis_data: Dict[str, Any] = None):
        """
        初始化分布分析异常
        
        Args:
            message: 错误消息
            analysis_data: 相关分析数据
        """
        super().__init__(message)
        self.analysis_data = analysis_data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'analysis_data': self.analysis_data
        }


class PriceDistributionAnalyzer:
    """
    涨跌分布分析器
    
    整合计算器和聚合器，实现完整的分布分析流程
    """
    
    def __init__(self, performance_optimizer: Optional[PriceDistributionPerformanceOptimizer] = None,
                 logger: Optional[logging.Logger] = None):
        """
        初始化分布分析器
        
        Args:
            performance_optimizer: 性能优化器
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.calculator = DistributionCalculator(logger)
        self.aggregator = StatisticsAggregator(logger)
        self.performance_optimizer = performance_optimizer
        self.default_ranges = self._create_default_ranges()
        
        # 性能统计
        self._performance_stats = {
            'total_analyses': 0,
            'average_processing_time': 0.0,
            'total_processing_time': 0.0
        }
    
    def _create_default_ranges(self) -> List[DistributionRange]:
        """创建默认区间"""
        return [
            # 正涨幅区间
            DistributionRange("0-3%", 0.0, 3.0, True, "0-3%"),
            DistributionRange("3-5%", 3.0, 5.0, True, "3-5%"),
            DistributionRange("5-7%", 5.0, 7.0, True, "5-7%"),
            DistributionRange("7-10%", 7.0, 10.0, True, "7-10%"),
            DistributionRange(">=10%", 10.0, float('inf'), True, ">=10%"),
            
            # 负涨幅区间
            DistributionRange("0到-3%", -3.0, 0.0, False, "0到-3%"),
            DistributionRange("-3到-5%", -5.0, -3.0, False, "-3到-5%"),
            DistributionRange("-5到-7%", -7.0, -5.0, False, "-5到-7%"),
            DistributionRange("-7到-10%", -10.0, -7.0, False, "-7到-10%"),
            DistributionRange("<=-10%", float('-inf'), -10.0, False, "<=-10%"),
        ]
    
    async def analyze_distribution(self, stock_data: pd.DataFrame, 
                                 ranges: Optional[List[DistributionRange]] = None) -> Dict[str, Any]:
        """
        分析涨跌分布
        
        Args:
            stock_data: 股票数据DataFrame，必须包含'ts_code'和'pct_chg'列
            ranges: 区间定义列表，如果为None则使用默认区间
            
        Returns:
            分布分析结果字典
            
        Raises:
            PriceDistributionAnalysisError: 分析过程中发生错误
        """
        start_time = time.time()
        
        try:
            # 验证输入数据
            self._validate_stock_data(stock_data)
            
            # 使用默认区间或自定义区间
            ranges = ranges or self.default_ranges
            
            # 执行分布计算
            self.logger.info(f"Starting distribution analysis for {len(stock_data)} stocks")
            
            # 1. 按区间分类股票
            classified_stocks = self.calculator.classify_by_ranges(stock_data, ranges)
            
            # 2. 计算统计数据
            distribution_results = self.calculator.calculate_statistics(classified_stocks, ranges)
            
            # 3. 生成分析结果
            analysis_result = self._build_analysis_result(
                stock_data, distribution_results, ranges, start_time
            )
            
            # 更新性能统计
            processing_time = time.time() - start_time
            self._update_performance_stats(processing_time)
            
            self.logger.info(f"Distribution analysis completed in {processing_time:.3f}s")
            return analysis_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            raise PriceDistributionAnalysisError(
                f"Distribution analysis failed: {str(e)}",
                {
                    'stock_count': len(stock_data) if stock_data is not None else 0,
                    'range_count': len(ranges) if ranges else 0,
                    'processing_time': processing_time,
                    'error_type': type(e).__name__
                }
            )
    
    async def calculate_market_breakdown(self, classified_data: Dict[str, pd.DataFrame],
                                       ranges: Optional[List[DistributionRange]] = None) -> Dict[str, Dict[str, Any]]:
        """
        计算市场板块分布
        
        Args:
            classified_data: 按市场分类的股票数据 {市场名称: DataFrame}
            ranges: 区间定义列表
            
        Returns:
            市场板块分布结果 {市场名称: 分布统计}
            
        Raises:
            PriceDistributionAnalysisError: 计算过程中发生错误
        """
        start_time = time.time()
        
        try:
            # 验证输入数据
            if not classified_data:
                raise PriceDistributionAnalysisError("No classified market data provided")
            
            # 使用默认区间或自定义区间
            ranges = ranges or self.default_ranges
            
            market_breakdown = {}
            
            # 为每个市场计算分布统计
            for market_name, market_data in classified_data.items():
                if market_data.empty:
                    self.logger.warning(f"No data for market: {market_name}")
                    continue
                
                # 计算市场分布
                self.logger.debug(f"Calculating distribution for market {market_name}: {len(market_data)} stocks")
                
                # 1. 按区间分类股票
                classified_stocks = self.calculator.classify_by_ranges(market_data, ranges)
                
                # 2. 计算统计数据
                distribution_results = self.calculator.calculate_statistics(classified_stocks, ranges)
                
                # 3. 构建市场统计结果
                market_stats = self._build_market_stats(
                    market_name, market_data, distribution_results
                )
                
                market_breakdown[market_name] = market_stats
            
            processing_time = time.time() - start_time
            self.logger.info(f"Market breakdown calculation completed in {processing_time:.3f}s for {len(market_breakdown)} markets")
            
            return market_breakdown
            
        except Exception as e:
            processing_time = time.time() - start_time
            raise PriceDistributionAnalysisError(
                f"Market breakdown calculation failed: {str(e)}",
                {
                    'market_count': len(classified_data) if classified_data else 0,
                    'processing_time': processing_time,
                    'error_type': type(e).__name__
                }
            )
    
    async def analyze_complete_distribution(self, request: PriceDistributionRequest,
                                          stock_data: pd.DataFrame,
                                          classified_data: Dict[str, pd.DataFrame]) -> PriceDistributionStats:
        """
        执行完整的分布分析
        
        Args:
            request: 分布统计请求
            stock_data: 完整股票数据
            classified_data: 按市场分类的股票数据
            
        Returns:
            完整的分布统计结果
            
        Raises:
            PriceDistributionAnalysisError: 分析过程中发生错误
        """
        start_time = time.time()
        
        try:
            # 获取分布区间
            ranges = request.get_distribution_ranges()
            
            # 1. 计算总体分布
            self.logger.info(f"Analyzing overall distribution for {len(stock_data)} stocks")
            overall_analysis = await self.analyze_distribution(
                stock_data, ranges
            )
            
            # 2. 计算市场板块分布
            self.logger.info(f"Calculating market breakdown for {len(classified_data)} markets")
            market_breakdown = await self.calculate_market_breakdown(
                classified_data, ranges
            )
            
            # 3. 聚合市场统计数据
            market_distribution_results = {}
            for market_name, market_stats in market_breakdown.items():
                # 转换为DistributionResult格式
                distribution_results = {}
                for range_name in ranges:
                    range_name_str = range_name.name
                    stock_count = market_stats.get('positive_ranges', {}).get(range_name_str, 0) + \
                                market_stats.get('negative_ranges', {}).get(range_name_str, 0)
                    percentage = market_stats.get('positive_percentages', {}).get(range_name_str, 0.0) + \
                               market_stats.get('negative_percentages', {}).get(range_name_str, 0.0)
                    stock_codes = market_stats.get('stock_codes', {}).get(range_name_str, [])
                    
                    distribution_results[range_name_str] = DistributionResult(
                        range_name=range_name_str,
                        stock_count=stock_count,
                        stock_codes=stock_codes,
                        percentage=percentage,
                        range_definition=range_name
                    )
                
                market_distribution_results[market_name] = distribution_results
            
            # 4. 使用聚合器处理市场统计
            aggregated_market_stats = self.aggregator.aggregate_market_stats(market_distribution_results)
            
            # 5. 构建最终结果
            processing_time = time.time() - start_time
            
            # 分离正负区间统计
            positive_ranges = {}
            positive_percentages = {}
            negative_ranges = {}
            negative_percentages = {}
            
            for range_name, result in overall_analysis.get('distribution_results', {}).items():
                if result.range_definition and result.range_definition.is_positive:
                    positive_ranges[range_name] = result.stock_count
                    positive_percentages[range_name] = result.percentage
                else:
                    negative_ranges[range_name] = result.stock_count
                    negative_percentages[range_name] = result.percentage
            
            # 转换市场板块数据格式
            market_breakdown_formatted = {}
            for market_name, market_stats in aggregated_market_stats.items():
                market_breakdown_formatted[market_name] = {
                    'total_stocks': market_stats.total_stocks,
                    'positive_ranges': market_stats.positive_ranges,
                    'positive_percentages': market_stats.positive_percentages,
                    'negative_ranges': market_stats.negative_ranges,
                    'negative_percentages': market_stats.negative_percentages,
                    'stock_codes': market_stats.stock_codes
                }
            
            # 创建最终统计结果
            stats = PriceDistributionStats(
                trade_date=request.trade_date,
                total_stocks=len(stock_data),
                positive_ranges=positive_ranges,
                positive_percentages=positive_percentages,
                negative_ranges=negative_ranges,
                negative_percentages=negative_percentages,
                market_breakdown=market_breakdown_formatted,
                processing_time=processing_time,
                data_quality_score=self._calculate_data_quality_score(stock_data, overall_analysis)
            )
            
            # 6. 验证数据一致性
            validation_result = self.aggregator.validate_data_consistency(stats)
            if not validation_result['is_valid']:
                self.logger.warning(f"Data consistency validation failed: {validation_result['errors']}")
            
            self.logger.info(f"Complete distribution analysis finished in {processing_time:.3f}s")
            return stats
            
        except Exception as e:
            processing_time = time.time() - start_time
            raise PriceDistributionAnalysisError(
                f"Complete distribution analysis failed: {str(e)}",
                {
                    'trade_date': request.trade_date,
                    'total_stocks': len(stock_data) if stock_data is not None else 0,
                    'market_count': len(classified_data) if classified_data else 0,
                    'processing_time': processing_time,
                    'error_type': type(e).__name__
                }
            )
    
    def _validate_stock_data(self, stock_data: pd.DataFrame):
        """验证股票数据"""
        if not isinstance(stock_data, pd.DataFrame):
            raise PriceDistributionAnalysisError(
                "Stock data must be a pandas DataFrame",
                {'data_type': type(stock_data).__name__}
            )
        
        if stock_data.empty:
            raise PriceDistributionAnalysisError("Stock data cannot be empty")
        
        # 检查必需列
        required_columns = ['ts_code', 'pct_chg']
        missing_columns = [col for col in required_columns if col not in stock_data.columns]
        if missing_columns:
            raise PriceDistributionAnalysisError(
                f"Missing required columns: {missing_columns}",
                {
                    'required_columns': required_columns,
                    'available_columns': list(stock_data.columns),
                    'missing_columns': missing_columns
                }
            )
    
    def _build_analysis_result(self, stock_data: pd.DataFrame, 
                             distribution_results: Dict[str, DistributionResult],
                             ranges: List[DistributionRange],
                             start_time: float) -> Dict[str, Any]:
        """构建分析结果"""
        processing_time = time.time() - start_time
        
        # 计算统计摘要
        range_summary = self.calculator.get_range_summary(distribution_results)
        
        return {
            'total_stocks': len(stock_data),
            'distribution_results': distribution_results,
            'range_summary': range_summary,
            'processing_time': processing_time,
            'data_quality_score': self._calculate_data_quality_score(stock_data, {'distribution_results': distribution_results}),
            'ranges_used': [r.to_dict() for r in ranges],
            'analysis_metadata': {
                'analyzer_version': '1.0.0',
                'analysis_timestamp': time.time(),
                'stock_count': len(stock_data),
                'range_count': len(ranges)
            }
        }
    
    def _build_market_stats(self, market_name: str, market_data: pd.DataFrame,
                          distribution_results: Dict[str, DistributionResult]) -> Dict[str, Any]:
        """构建市场统计结果"""
        # 分离正负区间
        positive_ranges = {}
        positive_percentages = {}
        negative_ranges = {}
        negative_percentages = {}
        stock_codes = {}
        
        for range_name, result in distribution_results.items():
            stock_codes[range_name] = result.stock_codes
            
            if result.range_definition and result.range_definition.is_positive:
                positive_ranges[range_name] = result.stock_count
                positive_percentages[range_name] = result.percentage
            else:
                negative_ranges[range_name] = result.stock_count
                negative_percentages[range_name] = result.percentage
        
        return {
            'market_name': market_name,
            'total_stocks': len(market_data),
            'positive_ranges': positive_ranges,
            'positive_percentages': positive_percentages,
            'negative_ranges': negative_ranges,
            'negative_percentages': negative_percentages,
            'stock_codes': stock_codes
        }
    
    def _calculate_data_quality_score(self, stock_data: pd.DataFrame, 
                                    analysis_result: Dict[str, Any]) -> float:
        """计算数据质量分数"""
        try:
            score = 1.0
            
            # 检查空值比例
            null_pct_chg = stock_data['pct_chg'].isnull().sum() / len(stock_data)
            if null_pct_chg > 0:
                score -= null_pct_chg * 0.3  # 空值影响30%权重
            
            # 检查异常值比例（涨跌幅超过±20%的股票）
            extreme_values = stock_data[
                (stock_data['pct_chg'].abs() > 20) & 
                (stock_data['pct_chg'].notna())
            ]
            extreme_ratio = len(extreme_values) / len(stock_data)
            if extreme_ratio > 0.1:  # 超过10%的股票有极端涨跌幅
                score -= (extreme_ratio - 0.1) * 0.2  # 超出部分影响20%权重
            
            # 检查分布结果的完整性
            distribution_results = analysis_result.get('distribution_results', {})
            if not distribution_results:
                score -= 0.5  # 没有分布结果扣50%
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.warning(f"Failed to calculate data quality score: {e}")
            return 0.8  # 默认分数
    
    def _update_performance_stats(self, processing_time: float):
        """更新性能统计"""
        self._performance_stats['total_analyses'] += 1
        self._performance_stats['total_processing_time'] += processing_time
        self._performance_stats['average_processing_time'] = (
            self._performance_stats['total_processing_time'] / 
            self._performance_stats['total_analyses']
        )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        return self._performance_stats.copy()
    
    def reset_performance_stats(self):
        """重置性能统计"""
        self._performance_stats = {
            'total_analyses': 0,
            'average_processing_time': 0.0,
            'total_processing_time': 0.0
        }
    
    async def validate_analysis_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证分析结果
        
        Args:
            result: 分析结果
            
        Returns:
            验证结果字典
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'checks_performed': []
        }
        
        try:
            # 检查基本结构
            validation_result['checks_performed'].append('basic_structure')
            required_keys = ['total_stocks', 'distribution_results', 'processing_time']
            for key in required_keys:
                if key not in result:
                    validation_result['errors'].append(f"Missing required key: {key}")
                    validation_result['is_valid'] = False
            
            # 检查股票总数一致性
            validation_result['checks_performed'].append('stock_count_consistency')
            if 'distribution_results' in result:
                calculated_total = sum(
                    res.stock_count for res in result['distribution_results'].values()
                )
                reported_total = result.get('total_stocks', 0)
                
                if calculated_total != reported_total:
                    validation_result['errors'].append(
                        f"Stock count mismatch: calculated {calculated_total}, reported {reported_total}"
                    )
                    validation_result['is_valid'] = False
            
            # 检查处理时间合理性
            validation_result['checks_performed'].append('processing_time')
            processing_time = result.get('processing_time', 0)
            if processing_time < 0:
                validation_result['errors'].append("Processing time cannot be negative")
                validation_result['is_valid'] = False
            elif processing_time > 300:  # 5分钟
                validation_result['warnings'].append(
                    f"Processing time seems unusually long: {processing_time} seconds"
                )
            
            # 检查数据质量分数
            validation_result['checks_performed'].append('data_quality_score')
            quality_score = result.get('data_quality_score', 1.0)
            if not (0 <= quality_score <= 1):
                validation_result['errors'].append(
                    f"Data quality score out of range: {quality_score}"
                )
                validation_result['is_valid'] = False
            
            return validation_result
            
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Validation process failed: {str(e)}")
            return validation_result
    
    def get_performance_optimization_stats(self) -> Dict[str, Any]:
        """
        获取性能优化统计信息
        
        Returns:
            性能优化统计字典
        """
        stats = {
            'analyzer_stats': self.get_performance_stats(),
            'performance_optimizer_available': self.performance_optimizer is not None
        }
        
        if self.performance_optimizer:
            stats['optimizer_stats'] = self.performance_optimizer.get_performance_stats()
        
        return stats

    async def analyze_distribution_with_performance_optimization(self, stock_data: pd.DataFrame, 
                                                               ranges: Optional[List[DistributionRange]] = None,
                                                               operation_name: str = "distribution_analysis") -> Dict[str, Any]:
        """
        使用性能优化的分布分析
        
        Args:
            stock_data: 股票数据
            ranges: 分布区间列表
            operation_name: 操作名称
            
        Returns:
            分析结果字典
        """
        if not self.performance_optimizer:
            # 如果没有性能优化器，使用标准方法
            return await self.analyze_distribution(stock_data, ranges)
        
        try:
            # 使用性能优化器进行分析
            optimized_result = await self.performance_optimizer.optimize_distribution_analysis(
                stock_data=stock_data,
                ranges=ranges or self.default_ranges,
                operation_name=operation_name
            )
            
            return optimized_result
            
        except Exception as e:
            self.logger.warning(f"Performance optimization failed, falling back to standard analysis: {e}")
            return await self.analyze_distribution(stock_data, ranges)

    async def analyze_complete_distribution_with_performance_optimization(self, 
                                                                        request: PriceDistributionRequest,
                                                                        stock_data: pd.DataFrame,
                                                                        classified_data: Dict[str, pd.DataFrame]) -> PriceDistributionStats:
        """
        使用性能优化的完整分布分析
        
        Args:
            request: 分布统计请求
            stock_data: 完整股票数据
            classified_data: 按市场分类的股票数据
            
        Returns:
            完整的分布统计结果
        """
        if not self.performance_optimizer:
            # 如果没有性能优化器，使用标准方法
            return await self.analyze_complete_distribution(request, stock_data, classified_data)
        
        try:
            start_time = time.time()
            
            # 使用性能优化器进行完整分析
            ranges = self._get_ranges_from_request(request)
            
            # 优化总体分析
            total_optimized_result = await self.performance_optimizer.optimize_distribution_analysis(
                stock_data=stock_data,
                ranges=ranges,
                operation_name=f"complete_analysis_{request.trade_date}"
            )
            
            # 优化市场分解分析
            market_optimized_results = {}
            for market_name, market_data in classified_data.items():
                if len(market_data) > 0:
                    market_result = await self.performance_optimizer.optimize_distribution_analysis(
                        stock_data=market_data,
                        ranges=ranges,
                        operation_name=f"market_analysis_{market_name}_{request.trade_date}"
                    )
                    market_optimized_results[market_name] = market_result
            
            # 构建最终结果
            stats = self._build_price_distribution_stats_from_optimized_results(
                request, stock_data, total_optimized_result, market_optimized_results, ranges
            )
            
            processing_time = time.time() - start_time
            stats.processing_time = processing_time
            
            # 更新性能统计
            self._update_performance_stats(processing_time)
            
            return stats
            
        except Exception as e:
            self.logger.warning(f"Performance optimization failed, falling back to standard analysis: {e}")
            return await self.analyze_complete_distribution(request, stock_data, classified_data)

    def _get_ranges_from_request(self, request: PriceDistributionRequest) -> List[DistributionRange]:
        """从请求中获取区间定义"""
        if request.distribution_ranges:
            ranges = []
            for name, (min_val, max_val) in request.distribution_ranges.items():
                is_positive = min_val >= 0
                ranges.append(DistributionRange(
                    name=name,
                    min_value=min_val,
                    max_value=max_val,
                    is_positive=is_positive,
                    display_name=name
                ))
            return ranges
        else:
            return self.default_ranges

    def _build_price_distribution_stats_from_optimized_results(self, 
                                                             request: PriceDistributionRequest,
                                                             stock_data: pd.DataFrame,
                                                             total_optimized_result: Dict[str, Any],
                                                             market_optimized_results: Dict[str, Dict[str, Any]],
                                                             ranges: List[DistributionRange]) -> PriceDistributionStats:
        """从优化结果构建PriceDistributionStats"""
        
        # 从优化结果中提取总体统计
        total_stats = total_optimized_result.get('distribution_stats', {})
        
        positive_ranges = {}
        negative_ranges = {}
        positive_percentages = {}
        negative_percentages = {}
        
        for range_def in ranges:
            range_name = range_def.name
            range_stats = total_stats.get(range_name, {'count': 0, 'percentage': 0.0})
            
            if range_def.is_positive:
                positive_ranges[range_name] = range_stats['count']
                positive_percentages[range_name] = range_stats['percentage']
            else:
                negative_ranges[range_name] = range_stats['count']
                negative_percentages[range_name] = range_stats['percentage']
        
        # 构建市场分解
        market_breakdown = {}
        for market_name, market_result in market_optimized_results.items():
            market_stats = market_result.get('distribution_stats', {})
            market_total = market_result.get('total_stocks', 0)
            
            market_positive_ranges = {}
            market_negative_ranges = {}
            market_positive_percentages = {}
            market_negative_percentages = {}
            market_stock_codes = {}
            
            for range_def in ranges:
                range_name = range_def.name
                range_stats = market_stats.get(range_name, {'count': 0, 'percentage': 0.0})
                
                if range_def.is_positive:
                    market_positive_ranges[range_name] = range_stats['count']
                    market_positive_percentages[range_name] = range_stats['percentage']
                else:
                    market_negative_ranges[range_name] = range_stats['count']
                    market_negative_percentages[range_name] = range_stats['percentage']
                
                # 获取股票代码（如果可用）
                if 'stock_codes' in range_stats:
                    market_stock_codes[range_name] = range_stats['stock_codes']
            
            market_breakdown[market_name] = {
                'total_stocks': market_total,
                'positive_ranges': market_positive_ranges,
                'negative_ranges': market_negative_ranges,
                'positive_percentages': market_positive_percentages,
                'negative_percentages': market_negative_percentages,
                'stock_codes': market_stock_codes
            }
        
        # 计算数据质量分数
        data_quality_score = self._calculate_data_quality_score_from_optimized_result(
            stock_data, total_optimized_result
        )
        
        return PriceDistributionStats(
            trade_date=request.trade_date,
            total_stocks=len(stock_data),
            positive_ranges=positive_ranges,
            negative_ranges=negative_ranges,
            positive_percentages=positive_percentages,
            negative_percentages=negative_percentages,
            market_breakdown=market_breakdown,
            processing_time=0.0,  # 将在调用方设置
            data_quality_score=data_quality_score
        )

    def _calculate_data_quality_score_from_optimized_result(self, stock_data: pd.DataFrame, 
                                                          optimized_result: Dict[str, Any]) -> float:
        """从优化结果计算数据质量分数"""
        try:
            # 基础分数
            base_score = 1.0
            
            # 检查数据完整性
            total_processed = optimized_result.get('total_stocks', 0)
            if total_processed < len(stock_data):
                completeness_ratio = total_processed / len(stock_data)
                base_score *= completeness_ratio
            
            # 检查处理时间（性能指标）
            processing_time = optimized_result.get('processing_time', 0)
            if processing_time > 10:  # 超过10秒认为性能较差
                time_penalty = max(0.1, 1.0 - (processing_time - 10) / 100)
                base_score *= time_penalty
            
            # 检查错误率
            error_count = optimized_result.get('error_count', 0)
            if error_count > 0:
                error_penalty = max(0.1, 1.0 - error_count / len(stock_data))
                base_score *= error_penalty
            
            return max(0.0, min(1.0, base_score))
            
        except Exception:
            return 0.8  # 默认分数


# 便利函数
async def analyze_stock_distribution(stock_data: pd.DataFrame, 
                                   ranges: Optional[List[DistributionRange]] = None,
                                   logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    便利函数：分析股票涨跌分布
    
    Args:
        stock_data: 股票数据
        ranges: 分布区间
        logger: 日志记录器
        
    Returns:
        分布分析结果
    """
    analyzer = PriceDistributionAnalyzer(logger)
    return await analyzer.analyze_distribution(stock_data, ranges)


async def calculate_market_distribution(classified_data: Dict[str, pd.DataFrame],
                                      ranges: Optional[List[DistributionRange]] = None,
                                      logger: Optional[logging.Logger] = None) -> Dict[str, Dict[str, Any]]:
    """
    便利函数：计算市场板块分布
    
    Args:
        classified_data: 按市场分类的股票数据
        ranges: 分布区间
        logger: 日志记录器
        
    Returns:
        市场板块分布结果
    """
    analyzer = PriceDistributionAnalyzer(logger)
    return await analyzer.calculate_market_breakdown(classified_data, ranges)


async def perform_complete_analysis(request: PriceDistributionRequest,
                                  stock_data: pd.DataFrame,
                                  classified_data: Dict[str, pd.DataFrame],
                                  logger: Optional[logging.Logger] = None) -> PriceDistributionStats:
    """
    便利函数：执行完整的分布分析
    
    Args:
        request: 分布统计请求
        stock_data: 完整股票数据
        classified_data: 按市场分类的股票数据
        logger: 日志记录器
        
    Returns:
        完整的分布统计结果
    """
    analyzer = PriceDistributionAnalyzer(logger)
    return await analyzer.analyze_complete_distribution(request, stock_data, classified_data)

