"""
股票代码分类工具

提供股票代码的市场分类和ST股票检测功能
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from ..core.errors import ValidationError


class StockClassificationError(ValidationError):
    """股票分类异常"""
    
    def __init__(self, message: str, code: str = None, classification_details: Dict[str, Any] = None):
        """
        初始化股票分类异常
        
        Args:
            message: 错误消息
            code: 导致错误的股票代码
            classification_details: 分类详细信息
        """
        super().__init__(message)
        self.code = code
        self.classification_details = classification_details or {}
        self.timestamp = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'code': self.code,
            'classification_details': self.classification_details,
            'timestamp': self.timestamp
        }


class UnknownStockCodeError(StockClassificationError):
    """未知股票代码格式异常"""
    
    def __init__(self, code: str, analysis_result: Dict[str, Any] = None):
        """
        初始化未知股票代码异常
        
        Args:
            code: 未知的股票代码
            analysis_result: 代码分析结果
        """
        self.analysis_result = analysis_result or {}
        message = f"无法识别的股票代码格式: {code}"
        
        super().__init__(message, code, {
            'analysis_result': self.analysis_result,
            'possible_markets': self._suggest_possible_markets(code),
            'suggestions': self._generate_suggestions(code)
        })
    
    def _suggest_possible_markets(self, code: str) -> List[str]:
        """建议可能的市场"""
        suggestions = []
        
        # 提取数字部分进行分析
        digits = re.findall(r'\d+', code)
        if digits and len(digits[0]) == 6:
            digit_code = digits[0]
            
            # 基于数字规则推测
            if digit_code.startswith('60') or digit_code.startswith('68'):
                suggestions.append('shanghai')
            elif digit_code.startswith('00') or digit_code.startswith('30'):
                suggestions.append('shenzhen')
            elif digit_code.startswith('688'):
                suggestions.append('star')
            elif digit_code.startswith('8') or digit_code.startswith('4'):
                suggestions.append('beijing')
        
        return suggestions
    
    def _generate_suggestions(self, code: str) -> List[str]:
        """生成修正建议"""
        suggestions = []
        
        # 基本格式建议
        if not re.search(r'\d{6}', code):
            suggestions.append("股票代码应包含6位数字")
        
        # 交易所标识建议
        if not re.search(r'\.(SH|SZ|BJ)', code.upper()):
            suggestions.append("可能缺少交易所标识 (.SH, .SZ, .BJ)")
        
        # 格式示例
        suggestions.append("标准格式示例: 000001.SZ, 600000.SH, 688001.SH, 430001.BJ")
        
        return suggestions


class MissingStockNameError(StockClassificationError):
    """缺失股票名称异常"""
    
    def __init__(self, code: str, context: str = None):
        """
        初始化缺失股票名称异常
        
        Args:
            code: 股票代码
            context: 上下文信息
        """
        message = f"股票代码 {code} 缺少名称信息，无法进行ST检测"
        super().__init__(message, code, {
            'context': context,
            'fallback_options': [
                '使用外部数据源获取股票名称',
                '跳过ST检测，按普通股票处理',
                '手动提供股票名称信息'
            ]
        })


@dataclass
class ClassificationResult:
    """分类结果"""
    ts_code: str                    # 股票代码
    market: str                     # 市场分类
    is_st: bool                     # 是否ST股票
    confidence: float               # 分类置信度 (0.0-1.0)
    classification_details: Dict[str, Any]  # 分类详细信息
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'ts_code': self.ts_code,
            'market': self.market,
            'is_st': self.is_st,
            'confidence': self.confidence,
            'classification_details': self.classification_details
        }


class StockCodeClassifier:
    """股票代码分类器
    
    提供股票代码的市场分类和ST股票检测功能
    """
    
    # 市场分类规则
    MARKET_RULES = {
        'shanghai': {
            'patterns': [r'^60\d{4}', r'^68[0-7]\d{3}', r'^900\d{3}'],
            'description': '上海证券交易所',
            'exchange_suffix': '.SH'
        },
        'star': {
            'patterns': [r'^688\d{3}'],
            'description': '科创板',
            'exchange_suffix': '.SH'
        },
        'shenzhen': {
            'patterns': [r'^00\d{4}', r'^30[0-7]\d{3}', r'^200\d{3}'],
            'description': '深圳证券交易所',
            'exchange_suffix': '.SZ'
        },
        'beijing': {
            'patterns': [r'^[48]\d{5}'],
            'description': '北京证券交易所',
            'exchange_suffix': '.BJ'
        }
    }
    
    # ST股票检测模式
    ST_PATTERNS = [
        r'\*ST',      # *ST开头
        r'ST',        # ST开头
        r'退市',      # 退市股票
        r'暂停',      # 暂停交易
        r'N\*ST',     # 新上市的*ST股票
        r'NST'        # 新上市的ST股票
    ]
    
    def __init__(self, enable_fallback: bool = True, logger: Optional[logging.Logger] = None):
        """
        初始化股票代码分类器
        
        Args:
            enable_fallback: 是否启用回退分类策略
            logger: 日志记录器
        """
        self.enable_fallback = enable_fallback
        self.logger = logger or logging.getLogger(__name__)
        
        # 编译正则表达式以提高性能
        self._compiled_market_patterns = {}
        self._compiled_st_patterns = []
        
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译正则表达式模式"""
        # 编译市场分类模式
        for market, rules in self.MARKET_RULES.items():
            self._compiled_market_patterns[market] = [
                re.compile(pattern) for pattern in rules['patterns']
            ]
        
        # 编译ST检测模式
        self._compiled_st_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.ST_PATTERNS
        ]
    
    def classify_market(self, ts_code: str) -> str:
        """
        根据股票代码分类市场
        
        Args:
            ts_code: 股票代码 (如: "000001.SZ", "600000.SH")
            
        Returns:
            市场分类: 'shanghai' | 'shenzhen' | 'star' | 'beijing'
            
        Raises:
            UnknownStockCodeError: 无法识别的股票代码格式
        """
        result = self._classify_market_with_details(ts_code)
        return result['market']
    
    def _classify_market_with_details(self, ts_code: str) -> Dict[str, Any]:
        """
        分类市场并返回详细信息
        
        Args:
            ts_code: 股票代码
            
        Returns:
            包含市场分类和详细信息的字典
        """
        if not ts_code or not isinstance(ts_code, str):
            raise UnknownStockCodeError(str(ts_code), {'reason': 'Invalid input type'})
        
        # 标准化代码格式
        normalized_code = self._normalize_code(ts_code)
        
        # 提取数字部分
        code_match = re.match(r'^(\d{6})', normalized_code)
        if not code_match:
            raise UnknownStockCodeError(ts_code, {
                'reason': 'No 6-digit code found',
                'normalized_code': normalized_code
            })
        
        stock_code = code_match.group(1)
        
        # 按优先级匹配市场规则
        for market in ['star', 'shanghai', 'shenzhen', 'beijing']:
            patterns = self._compiled_market_patterns[market]
            for pattern in patterns:
                if pattern.match(stock_code):
                    self.logger.debug(f"Code {ts_code} classified as {market}")
                    return {
                        'market': market,
                        'fallback_used': False,
                        'confidence': 1.0,
                        'matched_rules': [pattern.pattern for pattern in patterns if pattern.match(stock_code)]
                    }
        
        # 如果启用回退策略，尝试基于交易所后缀推断
        if self.enable_fallback:
            fallback_market = self._fallback_market_classification(ts_code)
            if fallback_market:
                self.logger.warning(f"Using fallback classification for {ts_code}: {fallback_market}")
                return {
                    'market': fallback_market,
                    'fallback_used': True,
                    'confidence': 0.5,
                    'matched_rules': []
                }
        
        # 无法分类
        raise UnknownStockCodeError(ts_code, {
            'reason': 'No matching market rules',
            'stock_code': stock_code,
            'available_markets': list(self.MARKET_RULES.keys())
        })
    
    def is_st_stock(self, stock_name: str) -> bool:
        """
        判断是否为ST股票
        
        Args:
            stock_name: 股票名称
            
        Returns:
            是否为ST股票
            
        Raises:
            MissingStockNameError: 缺少股票名称信息
        """
        if not stock_name or not isinstance(stock_name, str):
            raise MissingStockNameError("", "Stock name is required for ST detection")
        
        stock_name = stock_name.strip()
        if not stock_name:
            raise MissingStockNameError("", "Empty stock name provided")
        
        # 检查ST模式
        for pattern in self._compiled_st_patterns:
            if pattern.search(stock_name):
                self.logger.debug(f"Stock {stock_name} identified as ST stock")
                return True
        
        return False
    
    def classify_stock(self, ts_code: str, stock_name: str = None) -> ClassificationResult:
        """
        对股票进行完整分类
        
        Args:
            ts_code: 股票代码
            stock_name: 股票名称 (可选，用于ST检测)
            
        Returns:
            分类结果
        """
        classification_details = {
            'input_code': ts_code,
            'input_name': stock_name,
            'classification_time': None,
            'fallback_used': False
        }
        
        try:
            # 市场分类
            market_result = self._classify_market_with_details(ts_code)
            market = market_result['market']
            confidence = market_result['confidence']
            classification_details['fallback_used'] = market_result['fallback_used']
            classification_details['market_rules_matched'] = market_result['matched_rules']
            
        except UnknownStockCodeError as e:
            # 如果启用回退策略，尝试默认分类
            if self.enable_fallback:
                market = self._get_default_market_classification(ts_code)
                # 如果是真正无法分类的代码，置信度为0
                confidence = 0.0 if market == 'unknown' else 0.5
                classification_details['fallback_used'] = True
                classification_details['fallback_reason'] = str(e)
                classification_details['market_rules_matched'] = []
                self.logger.warning(f"Using fallback classification for {ts_code}: {market}")
            else:
                raise
        
        # ST股票检测
        is_st = False
        st_confidence = 1.0
        
        if stock_name:
            try:
                is_st = self.is_st_stock(stock_name)
            except MissingStockNameError:
                st_confidence = 0.0
                classification_details['st_detection_failed'] = True
        else:
            st_confidence = 0.0
            classification_details['no_stock_name'] = True
        
        # 计算综合置信度
        overall_confidence = min(confidence, st_confidence) if stock_name else confidence
        
        classification_details.update({
            'market_confidence': confidence,
            'st_confidence': st_confidence,
            'st_patterns_matched': self._get_matched_st_patterns(stock_name) if stock_name else []
        })
        
        return ClassificationResult(
            ts_code=ts_code,
            market=market,
            is_st=is_st,
            confidence=overall_confidence,
            classification_details=classification_details
        )
    
    def batch_classify(self, stocks: List[Dict[str, str]]) -> List[ClassificationResult]:
        """
        批量分类股票
        
        Args:
            stocks: 股票信息列表，每个元素包含 'ts_code' 和可选的 'name'
            
        Returns:
            分类结果列表
        """
        results = []
        
        for stock_info in stocks:
            ts_code = stock_info.get('ts_code', '')
            stock_name = stock_info.get('name', stock_info.get('stock_name', ''))
            
            try:
                result = self.classify_stock(ts_code, stock_name)
                results.append(result)
            except Exception as e:
                # 创建失败结果
                error_result = ClassificationResult(
                    ts_code=ts_code,
                    market='unknown',
                    is_st=False,
                    confidence=0.0,
                    classification_details={
                        'error': str(e),
                        'error_type': type(e).__name__,
                        'input_code': ts_code,
                        'input_name': stock_name
                    }
                )
                
                results.append(error_result)
                self.logger.error(f"Failed to classify {ts_code}: {e}")
        
        return results
    
    def get_market_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        获取市场分类规则
        
        Returns:
            市场分类规则字典
        """
        return self.MARKET_RULES.copy()
    
    def get_st_patterns(self) -> List[str]:
        """
        获取ST股票检测模式
        
        Returns:
            ST检测模式列表
        """
        return self.ST_PATTERNS.copy()
    
    def validate_classification_rules(self) -> Dict[str, Any]:
        """
        验证分类规则的完整性和正确性
        
        Returns:
            验证结果
        """
        validation_result = {
            'is_valid': True,
            'issues': [],
            'statistics': {
                'total_markets': len(self.MARKET_RULES),
                'total_patterns': sum(len(rules['patterns']) for rules in self.MARKET_RULES.values()),
                'total_st_patterns': len(self.ST_PATTERNS)
            }
        }
        
        # 检查市场规则
        for market, rules in self.MARKET_RULES.items():
            if not rules.get('patterns'):
                validation_result['issues'].append(f"Market {market} has no patterns")
                validation_result['is_valid'] = False
            
            if not rules.get('description'):
                validation_result['issues'].append(f"Market {market} has no description")
            
            # 验证正则表达式
            for pattern in rules.get('patterns', []):
                try:
                    re.compile(pattern)
                except re.error as e:
                    validation_result['issues'].append(f"Invalid regex in {market}: {pattern} - {e}")
                    validation_result['is_valid'] = False
        
        # 检查ST模式
        for pattern in self.ST_PATTERNS:
            try:
                re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                validation_result['issues'].append(f"Invalid ST regex: {pattern} - {e}")
                validation_result['is_valid'] = False
        
        return validation_result
    
    def validate_stock_code_format(self, ts_code: str) -> Dict[str, Any]:
        """
        验证股票代码格式的详细信息
        
        Args:
            ts_code: 股票代码
            
        Returns:
            验证结果详情
        """
        validation_result = {
            'is_valid': False,
            'code': ts_code,
            'issues': [],
            'suggestions': [],
            'format_analysis': {},
            'possible_corrections': []
        }
        
        if not ts_code or not isinstance(ts_code, str):
            validation_result['issues'].append('代码不能为空且必须是字符串')
            validation_result['suggestions'].append('请提供有效的股票代码字符串')
            return validation_result
        
        code_clean = ts_code.strip()
        if not code_clean:
            validation_result['issues'].append('代码不能为空白字符')
            return validation_result
        
        # 格式分析
        analysis = {
            'length': len(code_clean),
            'has_digits': bool(re.search(r'\d', code_clean)),
            'has_letters': bool(re.search(r'[a-zA-Z]', code_clean)),
            'has_dot': '.' in code_clean,
            'digit_count': len(re.findall(r'\d', code_clean)),
            'letter_count': len(re.findall(r'[a-zA-Z]', code_clean)),
            'special_chars': re.findall(r'[^0-9a-zA-Z.]', code_clean),
            'starts_with_digit': code_clean[0].isdigit() if code_clean else False,
            'starts_with_letter': code_clean[0].isalpha() if code_clean else False
        }
        validation_result['format_analysis'] = analysis
        
        # 基本格式检查
        if analysis['length'] < 6:
            validation_result['issues'].append(f"代码长度不足: {analysis['length']} < 6")
        elif analysis['length'] > 20:
            validation_result['issues'].append(f"代码长度过长: {analysis['length']} > 20")
        
        if not analysis['has_digits']:
            validation_result['issues'].append('代码必须包含数字')
        elif analysis['digit_count'] < 6:
            validation_result['issues'].append(f"数字位数不足: {analysis['digit_count']} < 6")
        
        if analysis['special_chars']:
            validation_result['issues'].append(f"包含无效字符: {', '.join(set(analysis['special_chars']))}")
        
        # 检查是否有严重的格式问题
        has_serious_issues = (
            analysis['length'] < 6 or 
            analysis['length'] > 20 or
            not analysis['has_digits'] or
            analysis['digit_count'] < 6 or
            analysis['special_chars']
        )
        
        # 检查是否缺少交易所标识（对于标准格式验证）
        lacks_exchange_suffix = (
            analysis['digit_count'] == 6 and 
            not analysis['has_dot'] and
            not re.match(r'^[0-9]{6}\.(SH|SZ|BJ)$', code_clean.upper())
        )
        
        if has_serious_issues:
            # 有严重问题，直接标记为无效
            validation_result['is_valid'] = False
            
            # 生成修正建议
            corrections = self._generate_format_corrections(code_clean)
            validation_result['possible_corrections'] = corrections
            
            # 生成使用建议
            suggestions = self._generate_usage_suggestions(code_clean, analysis)
            validation_result['suggestions'].extend(suggestions)
        elif lacks_exchange_suffix:
            # 缺少交易所标识，标记为无效但提供修正建议
            validation_result['is_valid'] = False
            validation_result['issues'].append('缺少交易所标识')
            
            # 生成修正建议
            corrections = self._generate_format_corrections(code_clean)
            validation_result['possible_corrections'] = corrections
            
            # 生成使用建议
            suggestions = self._generate_usage_suggestions(code_clean, analysis)
            validation_result['suggestions'].extend(suggestions)
        else:
            # 尝试识别格式并提供建议
            try:
                # 尝试分类以检查是否有效
                self.classify_market(ts_code)
                validation_result['is_valid'] = True
                validation_result['suggestions'].append('代码格式有效')
            except UnknownStockCodeError as e:
                validation_result['issues'].append(f'无法识别的格式: {str(e)}')
                
                # 生成修正建议
                corrections = self._generate_format_corrections(code_clean)
                validation_result['possible_corrections'] = corrections
                
                # 生成使用建议
                suggestions = self._generate_usage_suggestions(code_clean, analysis)
                validation_result['suggestions'].extend(suggestions)
        
        return validation_result
    
    def validate_stock_name_for_st_detection(self, stock_name: str) -> Dict[str, Any]:
        """
        验证股票名称是否适合ST检测
        
        Args:
            stock_name: 股票名称
            
        Returns:
            验证结果
        """
        validation_result = {
            'is_valid': False,
            'name': stock_name,
            'issues': [],
            'suggestions': [],
            'st_analysis': {},
            'confidence': 0.0
        }
        
        if not stock_name or not isinstance(stock_name, str):
            validation_result['issues'].append('股票名称不能为空且必须是字符串')
            validation_result['suggestions'].append('请提供有效的股票名称')
            return validation_result
        
        name_clean = stock_name.strip()
        if not name_clean:
            validation_result['issues'].append('股票名称不能为空白字符')
            return validation_result
        
        # ST分析
        st_analysis = {
            'length': len(name_clean),
            'has_st_prefix': bool(re.search(r'^(\*?ST|N\*?ST)', name_clean, re.IGNORECASE)),
            'has_st_anywhere': bool(re.search(r'ST', name_clean, re.IGNORECASE)),
            'has_delisting_keywords': bool(re.search(r'(退市|暂停)', name_clean)),
            'matched_patterns': [],
            'is_likely_st': False
        }
        
        # 检查匹配的ST模式
        for pattern in self._compiled_st_patterns:
            if pattern.search(name_clean):
                st_analysis['matched_patterns'].append(pattern.pattern)
        
        st_analysis['is_likely_st'] = len(st_analysis['matched_patterns']) > 0
        validation_result['st_analysis'] = st_analysis
        
        # 验证结果
        if len(name_clean) >= 2:  # 至少2个字符
            validation_result['is_valid'] = True
            validation_result['confidence'] = 1.0
            validation_result['suggestions'].append('股票名称格式有效，可以进行ST检测')
        else:
            validation_result['issues'].append('股票名称过短，可能影响ST检测准确性')
            validation_result['confidence'] = 0.5
        
        # 提供ST检测相关建议
        if st_analysis['is_likely_st']:
            validation_result['suggestions'].append(f"检测到ST股票特征，匹配模式: {', '.join(st_analysis['matched_patterns'])}")
        else:
            validation_result['suggestions'].append('未检测到ST股票特征')
        
        return validation_result
    
    def get_classification_confidence(self, ts_code: str, stock_name: str = None) -> Dict[str, Any]:
        """
        获取分类置信度的详细分析
        
        Args:
            ts_code: 股票代码
            stock_name: 股票名称
            
        Returns:
            置信度分析结果
        """
        confidence_analysis = {
            'overall_confidence': 0.0,
            'market_confidence': 0.0,
            'st_confidence': 0.0,
            'factors': [],
            'recommendations': []
        }
        
        try:
            # 市场分类置信度
            market_result = self._classify_market_with_details(ts_code)
            confidence_analysis['market_confidence'] = market_result['confidence']
            
            if market_result['fallback_used']:
                confidence_analysis['factors'].append('使用了回退分类策略，置信度降低')
                confidence_analysis['recommendations'].append('建议使用标准格式的股票代码')
            else:
                confidence_analysis['factors'].append('成功匹配市场分类规则')
            
        except Exception as e:
            confidence_analysis['factors'].append(f'市场分类失败: {str(e)}')
            confidence_analysis['recommendations'].append('检查股票代码格式是否正确')
        
        # ST检测置信度
        if stock_name:
            try:
                st_validation = self.validate_stock_name_for_st_detection(stock_name)
                confidence_analysis['st_confidence'] = st_validation['confidence']
                
                if st_validation['is_valid']:
                    confidence_analysis['factors'].append('股票名称有效，可以进行ST检测')
                else:
                    confidence_analysis['factors'].append('股票名称可能影响ST检测准确性')
                    confidence_analysis['recommendations'].append('提供完整的股票名称以提高ST检测准确性')
            except Exception as e:
                confidence_analysis['factors'].append(f'ST检测失败: {str(e)}')
                confidence_analysis['st_confidence'] = 0.0
        else:
            confidence_analysis['factors'].append('未提供股票名称，无法进行ST检测')
            confidence_analysis['recommendations'].append('提供股票名称以启用ST检测功能')
        
        # 计算综合置信度
        if stock_name:
            confidence_analysis['overall_confidence'] = min(
                confidence_analysis['market_confidence'], 
                confidence_analysis['st_confidence']
            )
        else:
            confidence_analysis['overall_confidence'] = confidence_analysis['market_confidence']
        
        return confidence_analysis
    
    def _generate_format_corrections(self, code: str) -> List[Dict[str, Any]]:
        """生成格式修正建议"""
        corrections = []
        
        # 提取数字部分
        digits = re.findall(r'\d+', code)
        if digits and len(digits[0]) == 6:
            main_digits = digits[0]
            
            # 基于数字规则推断交易所
            if main_digits.startswith('60') or main_digits.startswith('68'):
                corrections.append({
                    'type': 'add_exchange',
                    'original': code,
                    'corrected': f"{main_digits}.SH",
                    'confidence': 0.8,
                    'reason': '基于代码规则推断为上海交易所'
                })
            elif main_digits.startswith('688'):
                corrections.append({
                    'type': 'add_exchange',
                    'original': code,
                    'corrected': f"{main_digits}.SH",
                    'confidence': 0.9,
                    'reason': '基于代码规则推断为科创板'
                })
            elif main_digits.startswith('00') or main_digits.startswith('30'):
                corrections.append({
                    'type': 'add_exchange',
                    'original': code,
                    'corrected': f"{main_digits}.SZ",
                    'confidence': 0.8,
                    'reason': '基于代码规则推断为深圳交易所'
                })
            elif main_digits.startswith('8') or main_digits.startswith('4'):
                corrections.append({
                    'type': 'add_exchange',
                    'original': code,
                    'corrected': f"{main_digits}.BJ",
                    'confidence': 0.7,
                    'reason': '基于代码规则推断为北京交易所'
                })
        
        # 大小写修正
        if re.match(r'^[0-9]{6}\.(sh|sz|bj)$', code.lower()):
            corrections.append({
                'type': 'case_correction',
                'original': code,
                'corrected': code.upper(),
                'confidence': 0.95,
                'reason': '修正交易所后缀大小写'
            })
        
        # 格式转换
        if code.upper().startswith(('SH.', 'SZ.', 'BJ.')):
            parts = code.upper().split('.')
            if len(parts) == 2 and len(parts[1]) == 6:
                corrections.append({
                    'type': 'format_conversion',
                    'original': code,
                    'corrected': f"{parts[1]}.{parts[0]}",
                    'confidence': 0.9,
                    'reason': '转换为标准格式'
                })
        
        return sorted(corrections, key=lambda x: x['confidence'], reverse=True)
    
    def _generate_usage_suggestions(self, code: str, analysis: Dict[str, Any]) -> List[str]:
        """生成使用建议"""
        suggestions = []
        
        if analysis['digit_count'] == 6 and not analysis['has_dot']:
            suggestions.append('代码包含6位数字但缺少交易所标识，请添加 .SH、.SZ 或 .BJ')
        
        if analysis['length'] < 6:
            suggestions.append('代码长度不足，标准股票代码为6位数字加交易所标识')
        
        if analysis['special_chars']:
            suggestions.append('代码包含无效字符，只允许数字、字母和点号')
        
        if not analysis['has_digits']:
            suggestions.append('股票代码必须包含数字部分')
        
        # 格式示例
        suggestions.append('标准格式示例: 000001.SZ (深圳), 600000.SH (上海), 688001.SH (科创板), 430001.BJ (北京)')
        
        return suggestions
    
    def _normalize_code(self, ts_code: str) -> str:
        """标准化股票代码格式"""
        # 去除空格并转换为大写
        normalized = ts_code.strip().upper()
        
        # 处理不同格式
        # Baostock格式: sz.000001 -> 000001 (优先处理，因为包含点号)
        if normalized.startswith(('SZ.', 'SH.', 'BJ.')):
            normalized = normalized.split('.')[1]
        # 标准格式: 000001.SZ -> 000001
        elif '.' in normalized:
            normalized = normalized.split('.')[0]
        
        return normalized
    
    def _fallback_market_classification(self, ts_code: str) -> Optional[str]:
        """回退市场分类策略"""
        # 基于交易所后缀推断
        if '.SH' in ts_code.upper():
            # 进一步区分上海主板和科创板
            code_part = ts_code.split('.')[0]
            if code_part.startswith('688'):
                return 'star'
            else:
                return 'shanghai'
        elif '.SZ' in ts_code.upper():
            return 'shenzhen'
        elif '.BJ' in ts_code.upper():
            return 'beijing'
        
        return None
    
    def _get_default_market_classification(self, ts_code: str) -> str:
        """获取默认市场分类"""
        # 尝试回退分类
        fallback = self._fallback_market_classification(ts_code)
        if fallback:
            return fallback
        
        # 最后的默认值
        return 'unknown'
    
    def _get_matched_rules(self, ts_code: str, market: str) -> List[str]:
        """获取匹配的规则"""
        matched_rules = []
        
        if market in self.MARKET_RULES:
            normalized_code = self._normalize_code(ts_code)
            code_match = re.match(r'^(\d{6})', normalized_code)
            
            if code_match:
                stock_code = code_match.group(1)
                patterns = self._compiled_market_patterns[market]
                original_patterns = self.MARKET_RULES[market]['patterns']
                
                for i, pattern in enumerate(patterns):
                    if pattern.match(stock_code):
                        matched_rules.append(original_patterns[i])
        
        return matched_rules
    
    def _get_matched_st_patterns(self, stock_name: str) -> List[str]:
        """获取匹配的ST模式"""
        if not stock_name:
            return []
        
        matched_patterns = []
        for i, pattern in enumerate(self._compiled_st_patterns):
            if pattern.search(stock_name):
                matched_patterns.append(self.ST_PATTERNS[i])
        
        return matched_patterns


# 便利函数
def classify_market(ts_code: str) -> str:
    """
    便利函数：分类股票市场
    
    Args:
        ts_code: 股票代码
        
    Returns:
        市场分类
    """
    classifier = StockCodeClassifier()
    return classifier.classify_market(ts_code)


def is_st_stock(stock_name: str) -> bool:
    """
    便利函数：检测ST股票
    
    Args:
        stock_name: 股票名称
        
    Returns:
        是否为ST股票
    """
    classifier = StockCodeClassifier()
    return classifier.is_st_stock(stock_name)


def classify_stock(ts_code: str, stock_name: str = None) -> ClassificationResult:
    """
    便利函数：完整股票分类
    
    Args:
        ts_code: 股票代码
        stock_name: 股票名称
        
    Returns:
        分类结果
    """
    classifier = StockCodeClassifier()
    return classifier.classify_stock(ts_code, stock_name)