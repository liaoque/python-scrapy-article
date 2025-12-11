"""
统计聚合器

实现按市场板块聚合统计数据、百分比计算和数据一致性验证的功能
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from ..core.errors import ValidationError
from ..models import DistributionRange, PriceDistributionStats
from .distribution_calculator import DistributionResult


class StatisticsAggregationError(ValidationError):
    """统计聚合异常"""
    
    def __init__(self, message: str, aggregation_data: Dict[str, Any] = None):
        """
        初始化统计聚合异常
        
        Args:
            message: 错误消息
            aggregation_data: 相关聚合数据
        """
        super().__init__(message)
        self.aggregation_data = aggregation_data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'aggregation_data': self.aggregation_data
        }


@dataclass
class MarketStatistics:
    """市场统计数据"""
    market_name: str                        # 市场名称
    total_stocks: int                       # 总股票数
    positive_ranges: Dict[str, int]         # 正涨幅区间统计
    positive_percentages: Dict[str, float]  # 正涨幅区间占比
    negative_ranges: Dict[str, int]         # 负涨幅区间统计
    negative_percentages: Dict[str, float]  # 负涨幅区间占比
    stock_codes: Dict[str, List[str]]       # 按区间分类的股票代码
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'market_name': self.market_name,
            'total_stocks': self.total_stocks,
            'positive_ranges': self.positive_ranges,
            'positive_percentages': self.positive_percentages,
            'negative_ranges': self.negative_ranges,
            'negative_percentages': self.negative_percentages,
            'stock_codes': self.stock_codes
        }


class StatisticsAggregator:
    """
    统计聚合器
    
    负责统计数据的聚合、百分比计算和数据一致性验证
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化统计聚合器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def aggregate_market_stats(self, market_data: Dict[str, Dict[str, DistributionResult]]) -> Dict[str, MarketStatistics]:
        """
        聚合市场统计数据
        
        Args:
            market_data: 按市场分类的分布统计结果
                        {市场名称: {区间名称: DistributionResult}}
        
        Returns:
            聚合后的市场统计数据 {市场名称: MarketStatistics}
            
        Raises:
            StatisticsAggregationError: 聚合过程中发生错误
        """
        if not market_data:
            self.logger.warning("No market data provided for aggregation")
            return {}
        
        aggregated_stats = {}
        
        try:
            for market_name, distribution_results in market_data.items():
                if not distribution_results:
                    self.logger.warning(f"No distribution results for market: {market_name}")
                    continue
                
                # 计算市场总股票数
                total_stocks = sum(result.stock_count for result in distribution_results.values())
                
                # 分离正负区间
                positive_ranges = {}
                negative_ranges = {}
                positive_percentages = {}
                negative_percentages = {}
                stock_codes = {}
                
                for range_name, result in distribution_results.items():
                    stock_codes[range_name] = result.stock_codes.copy()
                    
                    if result.range_definition and result.range_definition.is_positive:
                        positive_ranges[range_name] = result.stock_count
                        positive_percentages[range_name] = result.percentage
                    else:
                        negative_ranges[range_name] = result.stock_count
                        negative_percentages[range_name] = result.percentage
                
                # 验证百分比一致性
                self._validate_percentages(positive_ranges, positive_percentages, total_stocks, market_name, "positive")
                self._validate_percentages(negative_ranges, negative_percentages, total_stocks, market_name, "negative")
                
                # 创建市场统计对象
                market_stats = MarketStatistics(
                    market_name=market_name,
                    total_stocks=total_stocks,
                    positive_ranges=positive_ranges,
                    positive_percentages=positive_percentages,
                    negative_ranges=negative_ranges,
                    negative_percentages=negative_percentages,
                    stock_codes=stock_codes
                )
                
                aggregated_stats[market_name] = market_stats
                
                self.logger.info(f"Aggregated statistics for market {market_name}: {total_stocks} stocks, "
                               f"{len(positive_ranges)} positive ranges, {len(negative_ranges)} negative ranges")
            
            return aggregated_stats
            
        except Exception as e:
            raise StatisticsAggregationError(
                f"Error during market statistics aggregation: {str(e)}",
                {
                    'market_count': len(market_data),
                    'error_type': type(e).__name__
                }
            )
    
    def calculate_percentages(self, counts: Dict[str, int], total: int) -> Dict[str, float]:
        """
        计算百分比
        
        Args:
            counts: 计数字典 {区间名称: 数量}
            total: 总数
            
        Returns:
            百分比字典 {区间名称: 百分比}
        """
        if total == 0:
            self.logger.warning("Total count is zero, returning zero percentages")
            return {key: 0.0 for key in counts.keys()}
        
        percentages = {}
        for key, count in counts.items():
            if not isinstance(count, int) or count < 0:
                self.logger.warning(f"Invalid count for {key}: {count}, setting to 0")
                count = 0
            
            percentage = (count / total) * 100
            percentages[key] = round(percentage, 2)
        
        # 验证百分比总和
        total_percentage = sum(percentages.values())
        if abs(total_percentage - 100.0) > 0.1:  # 允许0.1%的舍入误差
            self.logger.warning(f"Percentage total ({total_percentage:.2f}%) deviates from 100%")
        
        return percentages
    
    def generate_summary(self, stats: PriceDistributionStats) -> Dict[str, Any]:
        """
        生成统计摘要
        
        Args:
            stats: 涨跌分布统计结果
            
        Returns:
            统计摘要字典
        """
        if not stats:
            return {}
        
        try:
            # 基本统计信息
            positive_total = sum(stats.positive_ranges.values())
            negative_total = sum(stats.negative_ranges.values())
            
            # 计算涨跌股票占比
            positive_pct = (positive_total / stats.total_stocks * 100) if stats.total_stocks > 0 else 0.0
            negative_pct = (negative_total / stats.total_stocks * 100) if stats.total_stocks > 0 else 0.0
            
            # 找到最大和最小的区间
            all_ranges = {**stats.positive_ranges, **stats.negative_ranges}
            if all_ranges:
                max_range = max(all_ranges.items(), key=lambda x: x[1])
                min_range = min(all_ranges.items(), key=lambda x: x[1])
            else:
                max_range = ("N/A", 0)
                min_range = ("N/A", 0)
            
            # 市场板块统计
            market_summary = {}
            for market, market_data in stats.market_breakdown.items():
                market_total = market_data.get('total_stocks', 0)
                market_positive = sum(market_data.get('positive_ranges', {}).values())
                market_negative = sum(market_data.get('negative_ranges', {}).values())
                
                market_summary[market] = {
                    'total_stocks': market_total,
                    'positive_stocks': market_positive,
                    'negative_stocks': market_negative,
                    'positive_percentage': (market_positive / market_total * 100) if market_total > 0 else 0.0,
                    'negative_percentage': (market_negative / market_total * 100) if market_total > 0 else 0.0
                }
            
            summary = {
                'trade_date': stats.trade_date,
                'total_stocks': stats.total_stocks,
                'positive_stocks': positive_total,
                'negative_stocks': negative_total,
                'positive_percentage': round(positive_pct, 2),
                'negative_percentage': round(negative_pct, 2),
                'largest_range': {
                    'name': max_range[0],
                    'count': max_range[1],
                    'percentage': round((max_range[1] / stats.total_stocks * 100) if stats.total_stocks > 0 else 0.0, 2)
                },
                'smallest_range': {
                    'name': min_range[0],
                    'count': min_range[1],
                    'percentage': round((min_range[1] / stats.total_stocks * 100) if stats.total_stocks > 0 else 0.0, 2)
                },
                'market_breakdown': market_summary,
                'processing_time': stats.processing_time,
                'data_quality_score': stats.data_quality_score,
                'created_at': stats.created_at
            }
            
            self.logger.info(f"Generated summary for {stats.total_stocks} stocks on {stats.trade_date}")
            return summary
            
        except Exception as e:
            raise StatisticsAggregationError(
                f"Error generating statistics summary: {str(e)}",
                {
                    'trade_date': stats.trade_date if stats else None,
                    'total_stocks': stats.total_stocks if stats else None,
                    'error_type': type(e).__name__
                }
            )
    
    def validate_data_consistency(self, stats: PriceDistributionStats) -> Dict[str, Any]:
        """
        验证数据一致性
        
        Args:
            stats: 涨跌分布统计结果
            
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
            # 检查1: 总股票数一致性
            positive_total = sum(stats.positive_ranges.values())
            negative_total = sum(stats.negative_ranges.values())
            calculated_total = positive_total + negative_total
            
            validation_result['checks_performed'].append('total_stocks_consistency')
            if calculated_total != stats.total_stocks:
                error_msg = f"Total stocks mismatch: calculated {calculated_total}, reported {stats.total_stocks}"
                validation_result['errors'].append(error_msg)
                validation_result['is_valid'] = False
            
            # 检查2: 百分比一致性
            validation_result['checks_performed'].append('percentage_consistency')
            for range_name, count in stats.positive_ranges.items():
                expected_pct = (count / stats.total_stocks * 100) if stats.total_stocks > 0 else 0.0
                actual_pct = stats.positive_percentages.get(range_name, 0.0)
                
                if abs(expected_pct - actual_pct) > 0.01:  # 允许0.01%的误差
                    error_msg = f"Percentage mismatch for {range_name}: expected {expected_pct:.2f}%, got {actual_pct:.2f}%"
                    validation_result['errors'].append(error_msg)
                    validation_result['is_valid'] = False
            
            for range_name, count in stats.negative_ranges.items():
                expected_pct = (count / stats.total_stocks * 100) if stats.total_stocks > 0 else 0.0
                actual_pct = stats.negative_percentages.get(range_name, 0.0)
                
                if abs(expected_pct - actual_pct) > 0.01:  # 允许0.01%的误差
                    error_msg = f"Percentage mismatch for {range_name}: expected {expected_pct:.2f}%, got {actual_pct:.2f}%"
                    validation_result['errors'].append(error_msg)
                    validation_result['is_valid'] = False
            
            # 检查3: 市场板块数据一致性
            validation_result['checks_performed'].append('market_breakdown_consistency')
            market_total_stocks = 0
            for market, market_data in stats.market_breakdown.items():
                market_stocks = market_data.get('total_stocks', 0)
                market_positive = sum(market_data.get('positive_ranges', {}).values())
                market_negative = sum(market_data.get('negative_ranges', {}).values())
                market_calculated = market_positive + market_negative
                
                if market_calculated != market_stocks:
                    error_msg = f"Market {market} total mismatch: calculated {market_calculated}, reported {market_stocks}"
                    validation_result['errors'].append(error_msg)
                    validation_result['is_valid'] = False
                
                market_total_stocks += market_stocks
            
            # 注意：市场总数可能不等于总股票数，因为可能有重叠或分类不完整的情况
            if market_total_stocks > 0 and abs(market_total_stocks - stats.total_stocks) > stats.total_stocks * 0.1:
                warning_msg = f"Market breakdown total ({market_total_stocks}) significantly differs from total stocks ({stats.total_stocks})"
                validation_result['warnings'].append(warning_msg)
            
            # 检查4: 数据质量分数合理性
            validation_result['checks_performed'].append('data_quality_score')
            if not (0 <= stats.data_quality_score <= 1):
                error_msg = f"Data quality score out of range: {stats.data_quality_score}"
                validation_result['errors'].append(error_msg)
                validation_result['is_valid'] = False
            
            # 检查5: 处理时间合理性
            validation_result['checks_performed'].append('processing_time')
            if stats.processing_time < 0:
                error_msg = f"Processing time cannot be negative: {stats.processing_time}"
                validation_result['errors'].append(error_msg)
                validation_result['is_valid'] = False
            elif stats.processing_time > 300:  # 5分钟
                warning_msg = f"Processing time seems unusually long: {stats.processing_time} seconds"
                validation_result['warnings'].append(warning_msg)
            
            self.logger.info(f"Data consistency validation completed: {len(validation_result['errors'])} errors, "
                           f"{len(validation_result['warnings'])} warnings")
            
            return validation_result
            
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Validation process failed: {str(e)}")
            return validation_result
    
    def merge_market_statistics(self, market_stats_list: List[MarketStatistics]) -> MarketStatistics:
        """
        合并多个市场统计数据
        
        Args:
            market_stats_list: 市场统计数据列表
            
        Returns:
            合并后的市场统计数据
            
        Raises:
            StatisticsAggregationError: 合并过程中发生错误
        """
        if not market_stats_list:
            raise StatisticsAggregationError("No market statistics provided for merging")
        
        if len(market_stats_list) == 1:
            return market_stats_list[0]
        
        try:
            # 合并市场名称
            market_names = [stats.market_name for stats in market_stats_list]
            merged_name = f"merged_{'_'.join(market_names)}"
            
            # 合并总股票数
            total_stocks = sum(stats.total_stocks for stats in market_stats_list)
            
            # 合并正涨幅区间
            merged_positive_ranges = {}
            merged_negative_ranges = {}
            merged_stock_codes = {}
            
            for stats in market_stats_list:
                for range_name, count in stats.positive_ranges.items():
                    merged_positive_ranges[range_name] = merged_positive_ranges.get(range_name, 0) + count
                
                for range_name, count in stats.negative_ranges.items():
                    merged_negative_ranges[range_name] = merged_negative_ranges.get(range_name, 0) + count
                
                for range_name, codes in stats.stock_codes.items():
                    if range_name not in merged_stock_codes:
                        merged_stock_codes[range_name] = []
                    merged_stock_codes[range_name].extend(codes)
            
            # 去重股票代码
            for range_name in merged_stock_codes:
                merged_stock_codes[range_name] = list(set(merged_stock_codes[range_name]))
            
            # 重新计算百分比
            merged_positive_percentages = self.calculate_percentages(merged_positive_ranges, total_stocks)
            merged_negative_percentages = self.calculate_percentages(merged_negative_ranges, total_stocks)
            
            merged_stats = MarketStatistics(
                market_name=merged_name,
                total_stocks=total_stocks,
                positive_ranges=merged_positive_ranges,
                positive_percentages=merged_positive_percentages,
                negative_ranges=merged_negative_ranges,
                negative_percentages=merged_negative_percentages,
                stock_codes=merged_stock_codes
            )
            
            self.logger.info(f"Merged {len(market_stats_list)} market statistics into {merged_name}")
            return merged_stats
            
        except Exception as e:
            raise StatisticsAggregationError(
                f"Error merging market statistics: {str(e)}",
                {
                    'market_count': len(market_stats_list),
                    'error_type': type(e).__name__
                }
            )
    
    def _validate_percentages(self, counts: Dict[str, int], percentages: Dict[str, float], 
                            total: int, market_name: str, range_type: str):
        """验证百分比计算的准确性"""
        for range_name, count in counts.items():
            expected_pct = (count / total * 100) if total > 0 else 0.0
            actual_pct = percentages.get(range_name, 0.0)
            
            if abs(expected_pct - actual_pct) > 0.01:  # 允许0.01%的误差
                raise StatisticsAggregationError(
                    f"Percentage validation failed for {market_name} {range_type} range {range_name}: "
                    f"expected {expected_pct:.2f}%, got {actual_pct:.2f}%",
                    {
                        'market_name': market_name,
                        'range_type': range_type,
                        'range_name': range_name,
                        'expected_percentage': expected_pct,
                        'actual_percentage': actual_pct,
                        'count': count,
                        'total': total
                    }
                )
    
    def calculate_range_statistics(self, distribution_results: Dict[str, DistributionResult]) -> Dict[str, Any]:
        """
        计算区间统计信息
        
        Args:
            distribution_results: 分布计算结果
            
        Returns:
            区间统计信息
        """
        if not distribution_results:
            return {}
        
        total_stocks = sum(result.stock_count for result in distribution_results.values())
        positive_count = sum(1 for result in distribution_results.values() 
                           if result.range_definition and result.range_definition.is_positive)
        negative_count = len(distribution_results) - positive_count
        
        # 找到最大和最小的区间
        max_result = max(distribution_results.values(), key=lambda x: x.stock_count)
        min_result = min(distribution_results.values(), key=lambda x: x.stock_count)
        
        return {
            'total_ranges': len(distribution_results),
            'total_stocks': total_stocks,
            'positive_ranges': positive_count,
            'negative_ranges': negative_count,
            'largest_range': {
                'name': max_result.range_name,
                'count': max_result.stock_count,
                'percentage': max_result.percentage
            },
            'smallest_range': {
                'name': min_result.range_name,
                'count': min_result.stock_count,
                'percentage': min_result.percentage
            },
            'average_stocks_per_range': round(total_stocks / len(distribution_results), 2) if distribution_results else 0
        }


# 便利函数
def aggregate_market_data(market_data: Dict[str, Dict[str, DistributionResult]], 
                         logger: Optional[logging.Logger] = None) -> Dict[str, MarketStatistics]:
    """
    便利函数：聚合市场数据
    
    Args:
        market_data: 市场分布数据
        logger: 日志记录器
        
    Returns:
        聚合后的市场统计
    """
    aggregator = StatisticsAggregator(logger)
    return aggregator.aggregate_market_stats(market_data)


def calculate_distribution_percentages(counts: Dict[str, int], total: int) -> Dict[str, float]:
    """
    便利函数：计算分布百分比
    
    Args:
        counts: 计数字典
        total: 总数
        
    Returns:
        百分比字典
    """
    aggregator = StatisticsAggregator()
    return aggregator.calculate_percentages(counts, total)


def validate_statistics_consistency(stats: PriceDistributionStats) -> Dict[str, Any]:
    """
    便利函数：验证统计数据一致性
    
    Args:
        stats: 统计数据
        
    Returns:
        验证结果
    """
    aggregator = StatisticsAggregator()
    return aggregator.validate_data_consistency(stats)