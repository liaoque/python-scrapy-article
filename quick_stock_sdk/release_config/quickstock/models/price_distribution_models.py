"""
涨跌分布统计数据模型

定义涨跌分布统计相关的数据模型和请求对象
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Define DataRequest locally to avoid circular imports
@dataclass
class DataRequest:
    """数据请求模型基类"""
    data_type: str  # stock_basic, stock_daily, index_basic等
    ts_code: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    freq: Optional[str] = None  # 1min, 5min, 1d, 1w, 1m
    fields: Optional[List[str]] = None
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DistributionRange:
    """
    分布区间定义
    
    定义涨跌幅分布统计的区间范围，用于将股票按涨跌幅分类统计。
    
    Attributes:
        name: 区间名称 (如: "0-3%")
        min_value: 最小值 (包含)
        max_value: 最大值 (不包含)
        is_positive: 是否为正区间 (True表示涨幅区间，False表示跌幅区间)
        display_name: 显示名称
    """
    name: str                    # 区间名称 (如: "0-3%")
    min_value: float            # 最小值 (包含)
    max_value: float            # 最大值 (不包含)
    is_positive: bool           # 是否为正区间
    display_name: str           # 显示名称
    
    def __post_init__(self):
        """数据验证"""
        self.validate()
    
    def validate(self) -> bool:
        """验证区间定义"""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Range name is required and must be a string")
        
        if not isinstance(self.min_value, (int, float)):
            raise ValueError("min_value must be numeric")
        
        if not isinstance(self.max_value, (int, float)):
            raise ValueError("max_value must be numeric")
        
        if self.min_value >= self.max_value:
            raise ValueError("min_value must be less than max_value")
        
        if not isinstance(self.is_positive, bool):
            raise ValueError("is_positive must be boolean")
        
        if not self.display_name or not isinstance(self.display_name, str):
            raise ValueError("display_name is required and must be a string")
        
        return True
    
    def contains(self, value: float) -> bool:
        """检查值是否在区间内"""
        return self.min_value <= value < self.max_value
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'name': self.name,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'is_positive': self.is_positive,
            'display_name': self.display_name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DistributionRange':
        """从字典创建实例"""
        return cls(**data)
    
    @classmethod
    def create_default_ranges(cls) -> List['DistributionRange']:
        """创建默认分布区间"""
        return [
            # 正涨幅区间
            cls("0-3%", 0.0, 3.0, True, "0-3%"),
            cls("3-5%", 3.0, 5.0, True, "3-5%"),
            cls("5-7%", 5.0, 7.0, True, "5-7%"),
            cls("7-10%", 7.0, 10.0, True, "7-10%"),
            cls(">=10%", 10.0, float('inf'), True, ">=10%"),
            
            # 负涨幅区间
            cls("0到-3%", -3.0, 0.0, False, "0到-3%"),
            cls("-3到-5%", -5.0, -3.0, False, "-3到-5%"),
            cls("-5到-7%", -7.0, -5.0, False, "-5到-7%"),
            cls("-7到-10%", -10.0, -7.0, False, "-7到-10%"),
            cls("<=-10%", float('-inf'), -10.0, False, "<=-10%"),
        ]


@dataclass
class PriceDistributionRequest(DataRequest):
    """
    涨跌分布统计请求模型
    
    用于请求指定交易日的股票涨跌幅分布统计数据。SDK会实时从数据源获取数据并进行统计分析。
    
    Attributes:
        trade_date: 交易日期 (必填，格式: YYYYMMDD 或 YYYY-MM-DD)
        include_st: 是否包含ST股票 (默认: True)
        market_filter: 市场过滤器，可选值: ['shanghai', 'shenzhen', 'star', 'beijing', 'total', 'non_st', 'st']
        distribution_ranges: 自定义分布区间 (可选，格式: {区间名称: (最小值, 最大值)})
        force_refresh: 是否强制从外部数据源刷新数据 (默认: False)
        timeout: 请求超时时间，单位秒 (默认: 30)
    """
    # 重写父类字段以确保正确的字段顺序
    data_type: str = "price_distribution_stats"  # 数据类型
    ts_code: Optional[str] = None                # 股票代码（继承自父类）
    start_date: Optional[str] = None             # 开始日期（继承自父类）
    end_date: Optional[str] = None               # 结束日期（继承自父类）
    freq: Optional[str] = None                   # 频率（继承自父类）
    fields: Optional[List[str]] = None           # 字段（继承自父类）
    extra_params: Dict[str, Any] = field(default_factory=dict)  # 额外参数（继承自父类）
    
    # 涨跌分布统计特有字段
    trade_date: str = ""                         # 交易日期 (YYYYMMDD)
    include_st: bool = True                      # 是否包含ST股票
    market_filter: Optional[List[str]] = None    # 市场过滤器
    distribution_ranges: Optional[Dict[str, Tuple[float, float]]] = None  # 自定义区间
    force_refresh: bool = False                  # 是否强制刷新
    timeout: int = 30                            # 请求超时时间（秒）
    
    def __post_init__(self):
        """数据验证和标准化"""
        self.data_type = "price_distribution_stats"
        self.normalize()
        self.validate()
    
    def validate(self) -> bool:
        """验证请求参数"""
        from ..core.errors import ValidationError
        
        # 验证交易日期格式并标准化
        if not self.trade_date or self.trade_date == "":
            raise ValidationError("Trade date is required")
        
        # 支持 YYYY-MM-DD 和 YYYYMMDD 格式
        if re.match(r'^\d{4}-\d{2}-\d{2}$', self.trade_date):
            # 转换为 YYYYMMDD 格式
            self.trade_date = self.trade_date.replace('-', '')
        elif not re.match(r'^\d{8}$', self.trade_date):
            raise ValidationError(f"Invalid trade date format: {self.trade_date}. Expected YYYYMMDD or YYYY-MM-DD")
        
        # 验证日期有效性
        try:
            datetime.strptime(self.trade_date, '%Y%m%d')
        except ValueError:
            raise ValidationError(f"Invalid date: {self.trade_date}")
        
        # 验证日期不能是未来日期
        today = datetime.now().strftime('%Y%m%d')
        if self.trade_date > today:
            raise ValidationError(f"Trade date cannot be in the future: {self.trade_date}")
        
        # 验证市场过滤器
        if self.market_filter is not None:
            valid_markets = {'shanghai', 'shenzhen', 'star', 'beijing', 'total', 'non_st', 'st'}
            invalid_markets = set(self.market_filter) - valid_markets
            if invalid_markets:
                raise ValidationError(f"Invalid market filters: {invalid_markets}. Valid options: {valid_markets}")
        
        # 验证自定义区间
        if self.distribution_ranges is not None:
            for range_name, (min_val, max_val) in self.distribution_ranges.items():
                if not isinstance(min_val, (int, float)) or not isinstance(max_val, (int, float)):
                    raise ValidationError(f"Invalid range values for {range_name}: must be numeric")
                if min_val >= max_val:
                    raise ValidationError(f"Invalid range {range_name}: min_value must be less than max_value")
        
        # 验证超时时间
        if not isinstance(self.timeout, int) or self.timeout <= 0:
            raise ValidationError(f"Timeout must be a positive integer: {self.timeout}")
        
        return True
    
    def normalize(self):
        """标准化请求参数"""
        # 确保市场过滤器是列表
        if self.market_filter is not None and not isinstance(self.market_filter, list):
            if isinstance(self.market_filter, str):
                self.market_filter = [self.market_filter]
            else:
                self.market_filter = [str(self.market_filter)]
        
        # 去重市场过滤器，保持原始顺序
        if self.market_filter:
            seen = set()
            deduplicated = []
            for item in self.market_filter:
                if item not in seen:
                    seen.add(item)
                    deduplicated.append(item)
            self.market_filter = deduplicated
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'data_type': self.data_type,
            'ts_code': self.ts_code,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'freq': self.freq,
            'fields': self.fields,
            'extra_params': self.extra_params,
            'trade_date': self.trade_date,
            'include_st': self.include_st,
            'market_filter': self.market_filter,
            'distribution_ranges': self.distribution_ranges,
            'force_refresh': self.force_refresh,
            'timeout': self.timeout
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PriceDistributionRequest':
        """从字典创建实例"""
        return cls(**data)
    
    def get_formatted_date(self) -> str:
        """获取格式化的日期字符串 (YYYY-MM-DD)"""
        return f"{self.trade_date[:4]}-{self.trade_date[4:6]}-{self.trade_date[6:8]}"
    
    def is_market_included(self, market: str) -> bool:
        """检查指定市场是否包含在过滤器中"""
        if self.market_filter is None:
            return True
        return market in self.market_filter
    
    def get_distribution_ranges(self) -> List[DistributionRange]:
        """获取分布区间列表"""
        if self.distribution_ranges:
            ranges = []
            for name, (min_val, max_val) in self.distribution_ranges.items():
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
            return self._get_default_ranges()
    
    def _get_default_ranges(self) -> List[DistributionRange]:
        """获取默认分布区间"""
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


@dataclass
class PriceDistributionStats:
    """
    涨跌分布统计结果模型
    
    封装指定交易日的股票涨跌幅分布统计结果，包括各区间的股票数量和占比。
    
    Attributes:
        trade_date: 交易日期 (格式: YYYYMMDD)
        total_stocks: 总股票数
        positive_ranges: 正涨幅区间统计 (区间名称 -> 股票数量)
        positive_percentages: 正涨幅区间占比 (区间名称 -> 百分比)
        negative_ranges: 负涨幅区间统计 (区间名称 -> 股票数量)
        negative_percentages: 负涨幅区间占比 (区间名称 -> 百分比)
        market_breakdown: 按市场分类的分布统计
        created_at: 创建时间 (ISO格式)
        updated_at: 更新时间 (ISO格式)
        processing_time: 处理耗时 (单位: 秒)
        data_quality_score: 数据质量分数 (0-1之间)
    """
    trade_date: str                          # 交易日期
    total_stocks: int                        # 总股票数
    
    # 涨幅分布
    positive_ranges: Dict[str, int]          # 正涨幅区间统计
    positive_percentages: Dict[str, float]   # 正涨幅区间占比
    
    # 跌幅分布  
    negative_ranges: Dict[str, int]          # 负涨幅区间统计
    negative_percentages: Dict[str, float]   # 负涨幅区间占比
    
    # 市场板块分布
    market_breakdown: Dict[str, Dict[str, Any]]  # 按市场分类的分布
    
    # 元数据
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    processing_time: float = 0.0
    data_quality_score: float = 1.0
    
    def __post_init__(self):
        """数据验证和初始化"""
        self.validate()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def validate(self) -> bool:
        """验证统计数据的一致性"""
        # 验证交易日期格式
        if not self.trade_date or not re.match(r'^\d{8}$', self.trade_date):
            raise ValueError(f"Invalid trade date format: {self.trade_date}")
        
        # 验证总股票数
        if not isinstance(self.total_stocks, int) or self.total_stocks < 0:
            raise ValueError(f"Invalid total_stocks: {self.total_stocks}")
        
        # 验证涨幅分布数据
        if not isinstance(self.positive_ranges, dict):
            raise ValueError("positive_ranges must be a dictionary")
        
        if not isinstance(self.positive_percentages, dict):
            raise ValueError("positive_percentages must be a dictionary")
        
        # 验证跌幅分布数据
        if not isinstance(self.negative_ranges, dict):
            raise ValueError("negative_ranges must be a dictionary")
        
        if not isinstance(self.negative_percentages, dict):
            raise ValueError("negative_percentages must be a dictionary")
        
        # 验证市场板块分布
        if not isinstance(self.market_breakdown, dict):
            raise ValueError("market_breakdown must be a dictionary")
        
        # 验证数值类型
        for range_name, count in self.positive_ranges.items():
            if not isinstance(count, int) or count < 0:
                raise ValueError(f"Invalid positive range count for {range_name}: {count}")
        
        for range_name, count in self.negative_ranges.items():
            if not isinstance(count, int) or count < 0:
                raise ValueError(f"Invalid negative range count for {range_name}: {count}")
        
        for range_name, percentage in self.positive_percentages.items():
            if not isinstance(percentage, (int, float)) or percentage < 0 or percentage > 100:
                raise ValueError(f"Invalid positive percentage for {range_name}: {percentage}")
        
        for range_name, percentage in self.negative_percentages.items():
            if not isinstance(percentage, (int, float)) or percentage < 0 or percentage > 100:
                raise ValueError(f"Invalid negative percentage for {range_name}: {percentage}")
        
        # 验证处理时间和质量分数
        if not isinstance(self.processing_time, (int, float)) or self.processing_time < 0:
            raise ValueError(f"Invalid processing_time: {self.processing_time}")
        
        if not isinstance(self.data_quality_score, (int, float)) or not (0 <= self.data_quality_score <= 1):
            raise ValueError(f"Invalid data_quality_score: {self.data_quality_score}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'trade_date': self.trade_date,
            'total_stocks': self.total_stocks,
            'positive_ranges': self.positive_ranges,
            'positive_percentages': self.positive_percentages,
            'negative_ranges': self.negative_ranges,
            'negative_percentages': self.negative_percentages,
            'market_breakdown': self.market_breakdown,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'processing_time': self.processing_time,
            'data_quality_score': self.data_quality_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PriceDistributionStats':
        """从字典创建实例"""
        return cls(**data)
    
    def get_formatted_date(self) -> str:
        """获取格式化的日期字符串 (YYYY-MM-DD)"""
        return f"{self.trade_date[:4]}-{self.trade_date[4:6]}-{self.trade_date[6:8]}"
    
    def get_total_positive_count(self) -> int:
        """获取总正涨幅股票数"""
        return sum(self.positive_ranges.values())
    
    def get_total_negative_count(self) -> int:
        """获取总负涨幅股票数"""
        return sum(self.negative_ranges.values())
    
    def get_summary(self) -> Dict[str, Any]:
        """获取统计摘要"""
        positive_count = self.get_total_positive_count()
        negative_count = self.get_total_negative_count()
        
        return {
            'trade_date': self.trade_date,
            'total_stocks': self.total_stocks,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'positive_percentage': round(positive_count / self.total_stocks * 100, 2) if self.total_stocks > 0 else 0,
            'negative_percentage': round(negative_count / self.total_stocks * 100, 2) if self.total_stocks > 0 else 0,
            'processing_time': self.processing_time,
            'data_quality_score': self.data_quality_score
        }
    
    def get_market_summary(self, market: str) -> Optional[Dict[str, Any]]:
        """获取指定市场的统计摘要"""
        if market not in self.market_breakdown:
            return None
        
        market_data = self.market_breakdown[market]
        return {
            'market': market,
            'total_stocks': market_data.get('total_stocks', 0),
            'positive_ranges': market_data.get('positive_ranges', {}),
            'negative_ranges': market_data.get('negative_ranges', {}),
            'positive_count': sum(market_data.get('positive_ranges', {}).values()),
            'negative_count': sum(market_data.get('negative_ranges', {}).values())
        }
    
    def compare_with(self, other: 'PriceDistributionStats') -> Dict[str, Any]:
        """与另一个统计结果比较"""
        if not isinstance(other, PriceDistributionStats):
            raise ValueError("Can only compare with another PriceDistributionStats instance")
        
        comparison = {
            'base_date': self.trade_date,
            'compare_date': other.trade_date,
            'total_stocks_diff': other.total_stocks - self.total_stocks,
            'positive_changes': {},
            'negative_changes': {}
        }
        
        # 比较正涨幅分布变化
        for range_name in self.positive_ranges:
            if range_name in other.positive_ranges:
                diff = other.positive_ranges[range_name] - self.positive_ranges[range_name]
                comparison['positive_changes'][range_name] = diff
        
        # 比较负涨幅分布变化
        for range_name in self.negative_ranges:
            if range_name in other.negative_ranges:
                diff = other.negative_ranges[range_name] - self.negative_ranges[range_name]
                comparison['negative_changes'][range_name] = diff
        
        return comparison


# 默认分布区间配置
DEFAULT_DISTRIBUTION_RANGES = {
    # 正涨幅区间
    "0-3%": (0.0, 3.0),
    "3-5%": (3.0, 5.0),
    "5-7%": (5.0, 7.0),
    "7-10%": (7.0, 10.0),
    ">=10%": (10.0, float('inf')),
    
    # 负涨幅区间
    "0到-3%": (-3.0, 0.0),
    "-3到-5%": (-5.0, -3.0),
    "-5到-7%": (-7.0, -5.0),
    "-7到-10%": (-10.0, -7.0),
    "<=-10%": (float('-inf'), -10.0)
}

# 市场分类配置
MARKET_TYPES = {
    'total': '总体市场',
    'non_st': '非ST股票',
    'shanghai': '上海证券交易所',
    'shenzhen': '深圳证券交易所',
    'star': '科创板',
    'beijing': '北京证券交易所',
    'st': 'ST股票'
}