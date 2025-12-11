"""
涨跌分布计算器

实现股票涨跌幅区间分类和统计计算的核心算法
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from ..core.errors import ValidationError
from ..models import DistributionRange


class DistributionCalculationError(ValidationError):
    """分布计算异常"""
    
    def __init__(self, message: str, calculation_data: Dict[str, Any] = None):
        """
        初始化分布计算异常
        
        Args:
            message: 错误消息
            calculation_data: 相关计算数据
        """
        super().__init__(message)
        self.calculation_data = calculation_data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'calculation_data': self.calculation_data
        }


@dataclass
class DistributionResult:
    """分布计算结果"""
    range_name: str                     # 区间名称
    stock_count: int                    # 股票数量
    stock_codes: List[str]              # 股票代码列表
    percentage: float                   # 占比
    range_definition: DistributionRange # 区间定义
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'range_name': self.range_name,
            'stock_count': self.stock_count,
            'stock_codes': self.stock_codes,
            'percentage': self.percentage,
            'range_definition': self.range_definition.to_dict() if self.range_definition else None
        }


class DistributionCalculator:
    """
    涨跌分布计算器
    
    实现股票涨跌幅区间分类逻辑和统计数据计算
    """
    

    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化分布计算器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.default_ranges = self._create_default_ranges()
    
    def _create_default_ranges(self) -> List[DistributionRange]:
        """创建默认区间定义"""
        return DistributionRange.create_default_ranges()
    
    def classify_by_ranges(self, stock_data: pd.DataFrame, 
                          ranges: Optional[List[DistributionRange]] = None) -> Dict[str, List[str]]:
        """
        按区间分类股票
        
        Args:
            stock_data: 股票数据DataFrame，必须包含'ts_code'和'pct_chg'列
            ranges: 区间定义列表，如果为None则使用默认区间
            
        Returns:
            按区间分类的股票代码字典 {区间名称: [股票代码列表]}
            
        Raises:
            DistributionCalculationError: 数据验证失败或计算错误
        """
        # 验证输入数据
        self._validate_stock_data(stock_data)
        
        # 使用默认区间或自定义区间
        ranges = ranges or self.default_ranges
        self.validate_ranges(ranges)
        
        # 初始化分类结果
        classified_stocks = {range_def.name: [] for range_def in ranges}
        
        try:
            # 遍历每只股票进行分类
            for _, row in stock_data.iterrows():
                ts_code = row['ts_code']
                pct_chg = row['pct_chg']
                
                # 跳过无效的涨跌幅数据
                if pd.isna(pct_chg) or not isinstance(pct_chg, (int, float)) or not np.isfinite(pct_chg):
                    self.logger.warning(f"Invalid pct_chg for {ts_code}: {pct_chg}")
                    continue
                
                # 找到对应的区间
                target_range = self._find_range_for_value(pct_chg, ranges)
                if target_range:
                    classified_stocks[target_range.name].append(ts_code)
                else:
                    self.logger.warning(f"No range found for {ts_code} with pct_chg {pct_chg}")
            
            self.logger.info(f"Successfully classified {len(stock_data)} stocks into {len(ranges)} ranges")
            return classified_stocks
            
        except Exception as e:
            raise DistributionCalculationError(
                f"Error during stock classification: {str(e)}",
                {
                    'stock_count': len(stock_data),
                    'range_count': len(ranges),
                    'error_type': type(e).__name__
                }
            )
    
    def calculate_statistics(self, classified_stocks: Dict[str, List[str]], 
                           ranges: Optional[List[DistributionRange]] = None) -> Dict[str, DistributionResult]:
        """
        计算统计数据
        
        Args:
            classified_stocks: 按区间分类的股票字典
            ranges: 区间定义列表
            
        Returns:
            统计结果字典 {区间名称: DistributionResult}
            
        Raises:
            DistributionCalculationError: 计算错误
        """
        ranges = ranges or self.default_ranges
        range_dict = {r.name: r for r in ranges}
        
        # 计算总股票数
        total_stocks = sum(len(stocks) for stocks in classified_stocks.values())
        
        if total_stocks == 0:
            self.logger.warning("No stocks to calculate statistics")
            return {}
        
        statistics = {}
        
        try:
            for range_name, stock_codes in classified_stocks.items():
                stock_count = len(stock_codes)
                percentage = (stock_count / total_stocks) * 100 if total_stocks > 0 else 0.0
                
                # 获取区间定义
                range_definition = range_dict.get(range_name)
                
                statistics[range_name] = DistributionResult(
                    range_name=range_name,
                    stock_count=stock_count,
                    stock_codes=stock_codes.copy(),  # 创建副本避免外部修改
                    percentage=round(percentage, 2),
                    range_definition=range_definition
                )
            
            self.logger.info(f"Calculated statistics for {len(statistics)} ranges, total stocks: {total_stocks}")
            return statistics
            
        except Exception as e:
            raise DistributionCalculationError(
                f"Error during statistics calculation: {str(e)}",
                {
                    'total_stocks': total_stocks,
                    'range_count': len(classified_stocks),
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
            return {key: 0.0 for key in counts.keys()}
        
        percentages = {}
        for key, count in counts.items():
            percentage = (count / total) * 100
            percentages[key] = round(percentage, 2)
        
        return percentages
    
    def validate_ranges(self, ranges: List[DistributionRange]) -> bool:
        """
        验证区间定义
        
        Args:
            ranges: 区间定义列表
            
        Returns:
            是否有效
            
        Raises:
            DistributionCalculationError: 区间定义无效
        """
        if not ranges:
            raise DistributionCalculationError("Ranges list cannot be empty")
        
        if not isinstance(ranges, list):
            raise DistributionCalculationError("Ranges must be a list")
        
        # 验证每个区间
        range_names = set()
        positive_ranges = []
        negative_ranges = []
        
        for i, range_def in enumerate(ranges):
            if not isinstance(range_def, DistributionRange):
                raise DistributionCalculationError(
                    f"Range at index {i} is not a DistributionRange instance",
                    {'range_index': i, 'range_type': type(range_def).__name__}
                )
            
            # 检查名称唯一性
            if range_def.name in range_names:
                raise DistributionCalculationError(
                    f"Duplicate range name: {range_def.name}",
                    {'range_name': range_def.name}
                )
            range_names.add(range_def.name)
            
            # 验证区间值
            if not isinstance(range_def.min_value, (int, float)) or not isinstance(range_def.max_value, (int, float)):
                raise DistributionCalculationError(
                    f"Range values must be numeric for range: {range_def.name}",
                    {'range_name': range_def.name, 'min_value': range_def.min_value, 'max_value': range_def.max_value}
                )
            
            # 分类正负区间
            if range_def.is_positive:
                positive_ranges.append(range_def)
            else:
                negative_ranges.append(range_def)
        
        # 验证正区间覆盖性和连续性
        if positive_ranges:
            self._validate_range_coverage(positive_ranges, is_positive=True)
        
        # 验证负区间覆盖性和连续性
        if negative_ranges:
            self._validate_range_coverage(negative_ranges, is_positive=False)
        
        self.logger.info(f"Validated {len(ranges)} ranges ({len(positive_ranges)} positive, {len(negative_ranges)} negative)")
        return True
    
    def _validate_range_coverage(self, ranges: List[DistributionRange], is_positive: bool):
        """验证区间覆盖性"""
        if not ranges:
            return
        
        # 按最小值排序
        sorted_ranges = sorted(ranges, key=lambda r: r.min_value)
        
        # 检查区间逻辑
        for range_def in sorted_ranges:
            if is_positive:
                # 正区间：min_value <= max_value，且都应该 >= 0
                if range_def.min_value > range_def.max_value and range_def.max_value != float('inf'):
                    raise DistributionCalculationError(
                        f"Invalid positive range: min_value ({range_def.min_value}) > max_value ({range_def.max_value})",
                        {'range_name': range_def.name}
                    )
                if range_def.min_value < 0:
                    raise DistributionCalculationError(
                        f"Positive range should have non-negative min_value: {range_def.name}",
                        {'range_name': range_def.name, 'min_value': range_def.min_value}
                    )
            else:
                # 负区间：min_value <= max_value，但值都应该 <= 0
                if range_def.min_value > range_def.max_value and range_def.min_value != float('-inf'):
                    raise DistributionCalculationError(
                        f"Invalid negative range: min_value ({range_def.min_value}) > max_value ({range_def.max_value})",
                        {'range_name': range_def.name}
                    )
                if range_def.max_value > 0:
                    raise DistributionCalculationError(
                        f"Negative range should have non-positive max_value: {range_def.name}",
                        {'range_name': range_def.name, 'max_value': range_def.max_value}
                    )
    
    def _find_range_for_value(self, value: float, ranges: List[DistributionRange]) -> Optional[DistributionRange]:
        """
        为给定值找到对应的区间
        
        Args:
            value: 涨跌幅值
            ranges: 区间定义列表
            
        Returns:
            匹配的区间定义，如果没有找到则返回None
        """
        for range_def in ranges:
            if self._value_in_range(value, range_def):
                return range_def
        return None
    
    def _value_in_range(self, value: float, range_def: DistributionRange) -> bool:
        """
        判断值是否在区间内
        
        Args:
            value: 要判断的值
            range_def: 区间定义
            
        Returns:
            是否在区间内
        """
        return range_def.contains(value)
    
    def _validate_stock_data(self, stock_data: pd.DataFrame):
        """验证股票数据"""
        if not isinstance(stock_data, pd.DataFrame):
            raise DistributionCalculationError(
                "Stock data must be a pandas DataFrame",
                {'data_type': type(stock_data).__name__}
            )
        
        if stock_data.empty:
            raise DistributionCalculationError("Stock data cannot be empty")
        
        # 检查必需列
        required_columns = ['ts_code', 'pct_chg']
        missing_columns = [col for col in required_columns if col not in stock_data.columns]
        if missing_columns:
            raise DistributionCalculationError(
                f"Missing required columns: {missing_columns}",
                {
                    'required_columns': required_columns,
                    'available_columns': list(stock_data.columns),
                    'missing_columns': missing_columns
                }
            )
        
        # 检查数据类型
        if not stock_data['ts_code'].dtype == 'object':
            self.logger.warning("ts_code column should be string type")
        
        # 检查空值
        null_ts_codes = stock_data['ts_code'].isnull().sum()
        if null_ts_codes > 0:
            raise DistributionCalculationError(
                f"Found {null_ts_codes} null values in ts_code column",
                {'null_count': null_ts_codes}
            )
        
        # 检查重复股票代码
        duplicate_codes = stock_data['ts_code'].duplicated().sum()
        if duplicate_codes > 0:
            self.logger.warning(f"Found {duplicate_codes} duplicate stock codes")
    
    def get_range_summary(self, statistics: Dict[str, DistributionResult]) -> Dict[str, Any]:
        """
        获取区间统计摘要
        
        Args:
            statistics: 统计结果字典
            
        Returns:
            统计摘要
        """
        if not statistics:
            return {
                'total_ranges': 0,
                'total_stocks': 0,
                'positive_ranges': 0,
                'negative_ranges': 0,
                'largest_range': None,
                'smallest_range': None
            }
        
        total_stocks = sum(result.stock_count for result in statistics.values())
        positive_ranges = sum(1 for result in statistics.values() 
                            if result.range_definition and result.range_definition.is_positive)
        negative_ranges = len(statistics) - positive_ranges
        
        # 找到最大和最小的区间
        largest_range = max(statistics.values(), key=lambda x: x.stock_count)
        smallest_range = min(statistics.values(), key=lambda x: x.stock_count)
        
        return {
            'total_ranges': len(statistics),
            'total_stocks': total_stocks,
            'positive_ranges': positive_ranges,
            'negative_ranges': negative_ranges,
            'largest_range': {
                'name': largest_range.range_name,
                'count': largest_range.stock_count,
                'percentage': largest_range.percentage
            },
            'smallest_range': {
                'name': smallest_range.range_name,
                'count': smallest_range.stock_count,
                'percentage': smallest_range.percentage
            }
        }


# 便利函数
def create_default_ranges() -> List[DistributionRange]:
    """
    创建默认的涨跌幅区间定义
    
    Returns:
        默认区间列表
    """
    return DistributionRange.create_default_ranges()


def classify_stocks_by_change(stock_data: pd.DataFrame, 
                            ranges: Optional[List[DistributionRange]] = None) -> Dict[str, List[str]]:
    """
    便利函数：按涨跌幅分类股票
    
    Args:
        stock_data: 股票数据
        ranges: 区间定义
        
    Returns:
        分类结果
    """
    calculator = DistributionCalculator()
    return calculator.classify_by_ranges(stock_data, ranges)


def calculate_distribution_stats(stock_data: pd.DataFrame, 
                               ranges: Optional[List[DistributionRange]] = None) -> Dict[str, DistributionResult]:
    """
    便利函数：计算完整的分布统计
    
    Args:
        stock_data: 股票数据
        ranges: 区间定义
        
    Returns:
        统计结果
    """
    calculator = DistributionCalculator()
    classified = calculator.classify_by_ranges(stock_data, ranges)
    return calculator.calculate_statistics(classified, ranges)