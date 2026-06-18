"""
方程式增强模块
支持：气标(↑)、沉淀(↓)、反应条件、可逆反应等
"""

import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum


class ReactionType(Enum):
    """反应类型枚举"""
    COMBUSTION = "combustion"           # 燃烧反应
    NEUTRALIZATION = "neutralization"   # 中和反应
    DISPLACEMENT = "displacement"       # 置换反应
    DOUBLE_DISPLACEMENT = "double_displacement"  # 复分解反应
    DECOMPOSITION = "decomposition"     # 分解反应
    SYNTHESIS = "synthesis"             # 化合反应
    REDOX = "redox"                     # 氧化还原反应
    PRECIPITATION = "precipitation"     # 沉淀反应
    GAS_EVOLUTION = "gas_evolution"     # 气体生成反应
    UNKNOWN = "unknown"


@dataclass
class ReactionCondition:
    """反应条件"""
    temperature: Optional[str] = None      # 温度
    pressure: Optional[str] = None         # 压强
    catalyst: Optional[str] = None         # 催化剂
    solvent: Optional[str] = None          # 溶剂
    heating: bool = False                  # 加热
    ignition: bool = False                 # 点燃
    electrolysis: bool = False             # 电解
    illumination: bool = False             # 光照
    high_temperature: bool = False         # 高温
    high_pressure: bool = False            # 高压


@dataclass
class CompoundState:
    """化合物状态"""
    is_gas: bool = False       # 是否为气体
    is_liquid: bool = False    # 是否为液体
    is_solid: bool = False     # 是否为固体
    is_aqueous: bool = False   # 是否在溶液中
    is_precipitate: bool = False  # 是否为沉淀


class EquationEnhancer:
    """方程式增强器"""

    # 常见气体物质
    GASES = {
        'H2', 'O2', 'N2', 'Cl2', 'F2', 'CO2', 'CO', 'SO2', 'SO3',
        'NO', 'NO2', 'N2O', 'NH3', 'HCl', 'HBr', 'HI', 'HF',
        'CH4', 'C2H6', 'C2H4', 'C2H2', 'H2S'
    }

    # 常见沉淀物质（难溶物）
    PRECIPITATES = {
        'AgCl', 'AgBr', 'AgI', 'Ag2S', 'Ag2CO3', 'Ag2SO4',
        'BaSO4', 'BaCO3', 'BaSO3', 'Ba3(PO4)2',
        'CaCO3', 'CaSO3', 'Ca3(PO4)2', 'CaF2',
        'PbCl2', 'PbI2', 'PbS', 'PbSO4', 'PbCO3',
        'CuS', 'Cu(OH)2', 'CuCO3',
        'Fe(OH)3', 'Fe(OH)2', 'FeS',
        'Al(OH)3', 'Al2O3',
        'Mg(OH)2', 'MgCO3',
        'ZnS', 'Zn(OH)2', 'ZnCO3',
        'HgS', 'Hg2Cl2'
    }

    # 常见液态物质
    LIQUIDS = {'H2O', 'H2O2', 'H2SO4', 'HNO3', 'HCl', 'NaOH', 'KOH'}

    # 常见反应条件关键词
    CONDITION_KEYWORDS = {
        '点燃': ReactionCondition(ignition=True),
        '燃烧': ReactionCondition(ignition=True),
        '加热': ReactionCondition(heating=True),
        '△': ReactionCondition(heating=True),
        '高温': ReactionCondition(high_temperature=True),
        '高压': ReactionCondition(high_pressure=True),
        '催化剂': ReactionCondition(catalyst='催化剂'),
        'MnO2': ReactionCondition(catalyst='MnO2'),
        'V2O5': ReactionCondition(catalyst='V2O5'),
        'Fe': ReactionCondition(catalyst='Fe'),
        'Pt': ReactionCondition(catalyst='Pt'),
        'Pd': ReactionCondition(catalyst='Pd'),
        'Ni': ReactionCondition(catalyst='Ni'),
        '电解': ReactionCondition(electrolysis=True),
        '光照': ReactionCondition(illumination=True),
        '通电': ReactionCondition(electrolysis=True),
    }

    # 常见酸
    ACIDS = {'HCl', 'H2SO4', 'HNO3', 'H3PO4', 'H2CO3', 'H2SO3', 'HF', 'HBr', 'HI'}

    # 常见碱
    BASES = {'NaOH', 'KOH', 'Ca(OH)2', 'Ba(OH)2', 'Mg(OH)2', 'Al(OH)3', 'Fe(OH)3', 'Cu(OH)2'}

    # 常见盐
    SALTS = {
        'NaCl', 'KCl', 'CaCl2', 'BaCl2', 'MgCl2', 'AlCl3', 'FeCl3', 'FeCl2',
        'CuCl2', 'ZnCl2', 'AgCl', 'Na2SO4', 'K2SO4', 'CaSO4', 'BaSO4',
        'Na2CO3', 'K2CO3', 'CaCO3', 'NaHCO3', 'NaNO3', 'KNO3', 'AgNO3'
    }

    def __init__(self):
        self._cached_states: Dict[str, CompoundState] = {}

    def get_compound_state(self, formula: str, context: str = "") -> CompoundState:
        """
        获取化合物状态

        Args:
            formula: 化学式
            context: 上下文信息（如反应物/生成物）

        Returns:
            化合物状态
        """
        if formula in self._cached_states:
            return self._cached_states[formula]

        state = CompoundState()

        # 检查是否为气体
        if formula in self.GASES:
            state.is_gas = True

        # 检查是否为沉淀
        if formula in self.PRECIPITATES:
            state.is_precipitate = True
            state.is_solid = True

        # 检查是否为液体
        if formula in self.LIQUIDS:
            state.is_liquid = True

        # 默认为固体（如果是盐类）
        if formula in self.SALTS and not state.is_gas and not state.is_liquid:
            state.is_solid = True

        self._cached_states[formula] = state
        return state

    def detect_reaction_type(self, reactants: List[str], products: List[str]) -> ReactionType:
        """
        检测反应类型

        Args:
            reactants: 反应物列表
            products: 生成物列表

        Returns:
            反应类型
        """
        # 燃烧反应：反应物有 O2，且有有机物或单质
        if 'O2' in reactants:
            has_organic = any(self._is_organic(r) for r in reactants if r != 'O2')
            has_combustion_products = 'CO2' in products or 'H2O' in products
            if has_organic or has_combustion_products:
                return ReactionType.COMBUSTION

        # 中和反应：酸 + 碱 → 盐 + 水
        has_acid = any(r in self.ACIDS for r in reactants)
        has_base = any(r in self.BASES for r in reactants)
        has_water = 'H2O' in products
        if has_acid and has_base and has_water:
            return ReactionType.NEUTRALIZATION

        # 沉淀反应：生成沉淀
        has_precipitate = any(p in self.PRECIPITATES for p in products)
        if has_precipitate:
            return ReactionType.PRECIPITATION

        # 气体生成反应：生成气体
        has_gas_product = any(p in self.GASES for p in products)
        if has_gas_product and len(reactants) > 1:
            return ReactionType.GAS_EVOLUTION

        # 置换反应：单质 + 化合物 → 新单质 + 新化合物
        has_element = any(self._is_element(r) for r in reactants)
        has_compound = any(not self._is_element(r) for r in reactants)
        if has_element and has_compound:
            return ReactionType.DISPLACEMENT

        # 复分解反应：两种化合物交换成分
        if len(reactants) == 2 and all(not self._is_element(r) for r in reactants):
            return ReactionType.DOUBLE_DISPLACEMENT

        # 化合反应：多种物质生成一种
        if len(products) == 1 and len(reactants) > 1:
            return ReactionType.SYNTHESIS

        # 分解反应：一种物质生成多种
        if len(reactants) == 1 and len(products) > 1:
            return ReactionType.DECOMPOSITION

        return ReactionType.UNKNOWN

    def _is_element(self, formula: str) -> bool:
        """判断是否为单质"""
        # 简单判断：只包含一种元素
        elements = set()
        i = 0
        while i < len(formula):
            if formula[i].isupper():
                elem = formula[i]
                i += 1
                while i < len(formula) and formula[i].islower():
                    elem += formula[i]
                    i += 1
                elements.add(elem)
            else:
                i += 1
        return len(elements) == 1

    def _is_organic(self, formula: str) -> bool:
        """判断是否为有机物（含有 C-H 键）"""
        has_c = 'C' in formula
        has_h = 'H' in formula
        # 排除碳酸盐等无机含碳化合物
        inorganic = ['CO2', 'CO', 'CO3', 'HCO3', 'CaCO3', 'Na2CO3', 'NaHCO3']
        return has_c and has_h and not any(i in formula for i in inorganic)

    def detect_conditions(self, equation: str) -> ReactionCondition:
        """
        检测反应条件

        Args:
            equation: 反应方程式（可包含条件描述）

        Returns:
            反应条件
        """
        condition = ReactionCondition()

        for keyword, cond in self.CONDITION_KEYWORDS.items():
            if keyword in equation:
                if cond.temperature:
                    condition.temperature = cond.temperature
                if cond.pressure:
                    condition.pressure = cond.pressure
                if cond.catalyst:
                    condition.catalyst = cond.catalyst
                if cond.solvent:
                    condition.solvent = cond.solvent
                if cond.heating:
                    condition.heating = True
                if cond.ignition:
                    condition.ignition = True
                if cond.electrolysis:
                    condition.electrolysis = True
                if cond.illumination:
                    condition.illumination = True
                if cond.high_temperature:
                    condition.high_temperature = True
                if cond.high_pressure:
                    condition.high_pressure = True

        return condition

    def format_condition(self, condition: ReactionCondition) -> str:
        """
        格式化反应条件

        Args:
            condition: 反应条件

        Returns:
            格式化的条件字符串
        """
        parts = []

        if condition.ignition:
            parts.append("点燃")
        if condition.heating:
            parts.append("△")
        if condition.high_temperature:
            parts.append("高温")
        if condition.high_pressure:
            parts.append("高压")
        if condition.electrolysis:
            parts.append("通电")
        if condition.illumination:
            parts.append("光照")
        if condition.catalyst:
            parts.append(condition.catalyst)
        if condition.temperature:
            parts.append(condition.temperature)
        if condition.pressure:
            parts.append(condition.pressure)
        if condition.solvent:
            parts.append(f"({condition.solvent})")

        return "、".join(parts) if parts else ""

    def enhance_equation(self, equation: str) -> Dict:
        """
        增强方程式，添加状态符号和反应条件

        Args:
            equation: 原始方程式

        Returns:
            增强后的方程式信息
        """
        # 解析方程式
        separators = ['->', '→', '⟶', '<=>', '⇌', '⇋']
        separator = None
        for sep in separators:
            if sep in equation:
                separator = sep
                break

        if not separator:
            return {'error': 'Invalid equation format'}

        parts = equation.split(separator)
        if len(parts) != 2:
            return {'error': 'Invalid equation format'}

        # 解析反应物和生成物
        reactants = [r.strip() for r in parts[0].split('+')]
        products = [p.strip() for p in parts[1].split('+')]

        # 提取系数和化学式
        def parse_term(term: str) -> Tuple[int, str]:
            match = re.match(r'^(\d+)\s*(.+)$', term)
            if match:
                return int(match.group(1)), match.group(2)
            return 1, term

        # 获取每个物质的状态
        reactant_states = {}
        product_states = {}

        for r in reactants:
            coeff, formula = parse_term(r)
            state = self.get_compound_state(formula, 'reactant')
            reactant_states[formula] = state

        for p in products:
            coeff, formula = parse_term(p)
            state = self.get_compound_state(formula, 'product')
            product_states[formula] = state

        # 检测反应类型
        reactant_formulas = [parse_term(r)[1] for r in reactants]
        product_formulas = [parse_term(p)[1] for p in products]
        reaction_type = self.detect_reaction_type(reactant_formulas, product_formulas)

        # 检测反应条件
        condition = self.detect_conditions(equation)

        # 生成带状态符号的方程式
        def format_with_state(term: str, states: Dict[str, CompoundState]) -> str:
            coeff, formula = parse_term(term)
            state = states.get(formula, CompoundState())

            state_symbol = ""
            if state.is_gas:
                state_symbol = "↑"
            elif state.is_precipitate:
                state_symbol = "↓"

            if coeff > 1:
                return f"{coeff}{formula}{state_symbol}"
            return f"{formula}{state_symbol}"

        enhanced_reactants = [format_with_state(r, reactant_states) for r in reactants]
        enhanced_products = [format_with_state(p, product_states) for p in products]

        # 构建增强后的方程式
        condition_str = self.format_condition(condition)

        if condition_str:
            enhanced_equation = f"{' + '.join(enhanced_reactants)} --{condition_str}--> {' + '.join(enhanced_products)}"
        else:
            enhanced_equation = f"{' + '.join(enhanced_reactants)} {separator} {' + '.join(enhanced_products)}"

        return {
            'original': equation,
            'enhanced': enhanced_equation,
            'reactants': {
                'formulas': reactant_formulas,
                'states': {f: {
                    'is_gas': s.is_gas,
                    'is_liquid': s.is_liquid,
                    'is_solid': s.is_solid,
                    'is_precipitate': s.is_precipitate
                } for f, s in reactant_states.items()}
            },
            'products': {
                'formulas': product_formulas,
                'states': {f: {
                    'is_gas': s.is_gas,
                    'is_liquid': s.is_liquid,
                    'is_solid': s.is_solid,
                    'is_precipitate': s.is_precipitate
                } for f, s in product_states.items()}
            },
            'reaction_type': reaction_type.value,
            'condition': {
                'temperature': condition.temperature,
                'pressure': condition.pressure,
                'catalyst': condition.catalyst,
                'heating': condition.heating,
                'ignition': condition.ignition,
                'electrolysis': condition.electrolysis,
                'illumination': condition.illumination,
                'formatted': condition_str
            },
            'has_gas_symbol': any(s.is_gas for s in product_states.values()),
            'has_precipitate_symbol': any(s.is_precipitate for s in product_states.values())
        }

    def to_latex_enhanced(self, enhanced_data: Dict) -> str:
        """
        将增强后的方程式转换为 LaTeX 格式

        Args:
            enhanced_data: enhance_equation 返回的数据

        Returns:
            LaTeX 格式字符串
        """
        if 'error' in enhanced_data:
            return ""

        def format_term_latex(term: str, states: Dict) -> str:
            coeff, formula = parse_term(term)
            state = states.get(formula, {})

            # LaTeX 化学式
            latex_formula = f"\\ce{{{formula}}}"

            # 状态符号
            state_latex = ""
            if state.get('is_gas'):
                state_latex = "\\uparrow"
            elif state.get('is_precipitate'):
                state_latex = "\\downarrow"

            if coeff > 1:
                return f"{coeff}{latex_formula}{state_latex}"
            return f"{latex_formula}{state_latex}"

        def parse_term(term: str) -> Tuple[int, str]:
            match = re.match(r'^(\d+)\s*(.+)$', term)
            if match:
                return int(match.group(1)), match.group(2)
            return 1, term

        # 构建 LaTeX
        reactants_latex = []
        for formula in enhanced_data['reactants']['formulas']:
            reactants_latex.append(format_term_latex(formula, enhanced_data['reactants']['states']))

        products_latex = []
        for formula in enhanced_data['products']['formulas']:
            products_latex.append(format_term_latex(formula, enhanced_data['products']['states']))

        # 条件
        condition = enhanced_data.get('condition', {})
        condition_str = condition.get('formatted', '')

        if condition_str:
            return f"\\ce{{{' + '.join(reactants_latex)} ->[{condition_str}] {' + '.join(products_latex)}}}"
        else:
            return f"\\ce{{{' + '.join(reactants_latex)} -> {' + '.join(products_latex)}}}"

    def to_word_enhanced(self, enhanced_data: Dict) -> str:
        """
        将增强后的方程式转换为 Word 可用的 Unicode 格式

        Args:
            enhanced_data: enhance_equation 返回的数据

        Returns:
            Unicode 格式字符串
        """
        if 'error' in enhanced_data:
            return ""

        def format_term_unicode(term: str, states: Dict) -> str:
            coeff, formula = parse_term(term)
            state = states.get(formula, {})

            # Unicode 下标
            subscript_map = {'0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
                           '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'}

            unicode_formula = ""
            i = 0
            while i < len(formula):
                if formula[i].isdigit():
                    unicode_formula += subscript_map.get(formula[i], formula[i])
                else:
                    unicode_formula += formula[i]
                i += 1

            # 状态符号
            state_symbol = ""
            if state.get('is_gas'):
                state_symbol = "↑"
            elif state.get('is_precipitate'):
                state_symbol = "↓"

            if coeff > 1:
                return f"{coeff}{unicode_formula}{state_symbol}"
            return f"{unicode_formula}{state_symbol}"

        def parse_term(term: str) -> Tuple[int, str]:
            match = re.match(r'^(\d+)\s*(.+)$', term)
            if match:
                return int(match.group(1)), match.group(2)
            return 1, term

        # 构建 Unicode
        reactants_unicode = []
        for formula in enhanced_data['reactants']['formulas']:
            reactants_unicode.append(format_term_unicode(formula, enhanced_data['reactants']['states']))

        products_unicode = []
        for formula in enhanced_data['products']['formulas']:
            products_unicode.append(format_term_unicode(formula, enhanced_data['products']['states']))

        # 条件
        condition = enhanced_data.get('condition', {})
        condition_str = condition.get('formatted', '')

        if condition_str:
            return f"{' + '.join(reactants_unicode)} —{condition_str}→ {' + '.join(products_unicode)}"
        else:
            return f"{' + '.join(reactants_unicode)} → {' + '.join(products_unicode)}"


# 全局实例
equation_enhancer = EquationEnhancer()


# 便捷函数
def enhance_equation(equation: str) -> Dict:
    """增强方程式"""
    return equation_enhancer.enhance_equation(equation)


def equation_to_latex(equation: str) -> str:
    """方程式转 LaTeX"""
    data = equation_enhancer.enhance_equation(equation)
    return equation_enhancer.to_latex_enhanced(data)


def equation_to_word(equation: str) -> str:
    """方程式转 Word 格式"""
    data = equation_enhancer.enhance_equation(equation)
    return equation_enhancer.to_word_enhanced(data)
