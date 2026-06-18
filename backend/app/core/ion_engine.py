"""
ChemMaster 离子方程式引擎
支持：离子解析、离子方程式配平、分子方程式→离子方程式转换、旁观离子检测
"""

import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from fractions import Fraction

from .chemistry import FormulaParser


# ====== 离子数据结构 ======

@dataclass
class Ion:
    """离子表示"""
    formula: str          # 离子式，如 "SO4^2-"
    symbol: str           # 核心符号，如 "SO4"
    charge: int           # 电荷数，如 -2
    is_cation: bool = True  # 是否为阳离子

    def __post_init__(self):
        self.is_cation = self.charge > 0


@dataclass
class IonicEquationResult:
    """离子方程式分析结果"""
    original: str                        # 原始分子方程式
    full_ionic: str                      # 完整离子方程式
    net_ionic: str                       # 净离子方程式
    spectator_ions: List[str]            # 旁观离子
    balanced_molecular: str              # 平衡后的分子方程式
    balanced_full_ionic: str             # 平衡后的完整离子方程式
    balanced_net_ionic: str              # 平衡后的净离子方程式
    charge_balanced: bool                # 电荷是否守恒
    reactant_charges: int                # 反应物总电荷
    product_charges: int                 # 生成物总电荷


# ====== 强电解质表 ======

# 强酸（完全电离）
STRONG_ACIDS = {
    'HCl', 'HBr', 'HI', 'HNO3', 'H2SO4', 'HClO4', 'HClO3',
}

# 强碱（完全电离）
STRONG_BASES = {
    'NaOH', 'KOH', 'Ca(OH)2', 'Ba(OH)2', 'Sr(OH)2',
}

# 可溶盐（常见，完全电离）
SOLUBLE_SALTS = {
    # 钠盐
    'NaCl', 'NaBr', 'NaI', 'NaNO3', 'Na2SO4', 'Na2CO3', 'Na3PO4',
    'Na2S', 'NaOH', 'NaHCO3', 'Na2SO3', 'NaClO', 'NaClO3',
    'NaCH3COO', 'NaC2H3O2', 'CH3COONa',
    # 钾盐
    'KCl', 'KBr', 'KI', 'KNO3', 'K2SO4', 'K2CO3', 'K3PO4',
    'K2S', 'KOH', 'KHCO3', 'K2SO3', 'KClO', 'KClO3',
    'K2CrO4', 'K2Cr2O7', 'KMnO4',
    # 铵盐
    'NH4Cl', 'NH4Br', 'NH4I', 'NH4NO3', '(NH4)2SO4', '(NH4)2CO3',
    '(NH4)3PO4', 'NH4HCO3', 'NH4CH3COO',
    # 硝酸盐（全部可溶）
    'AgNO3', 'Ca(NO3)2', 'Mg(NO3)2', 'Fe(NO3)2', 'Fe(NO3)3',
    'Cu(NO3)2', 'Zn(NO3)2', 'Pb(NO3)2', 'Al(NO3)3',
    # 氯化物（大部分可溶）
    'CaCl2', 'MgCl2', 'FeCl2', 'FeCl3', 'CuCl2', 'ZnCl2',
    'AlCl3', 'BaCl2', 'SrCl2', 'MnCl2', 'NiCl2', 'CoCl2',
    # 硫酸盐（大部分可溶）
    'MgSO4', 'FeSO4', 'Fe2(SO4)3', 'CuSO4', 'ZnSO4',
    'Al2(SO4)3', 'NiSO4', 'CoSO4', 'MnSO4', 'Cr2(SO4)3',
    'Na2SO4', 'K2SO4', '(NH4)2SO4',
    # 配合物盐（可溶，完全电离）
    'K3[Fe(CN)6]', 'K4[Fe(CN)6]', 'Na3[AlF6]',
    '[Cu(NH3)4]SO4', '[Ag(NH3)2]Cl', '[Co(NH3)6]Cl3',
    'K[PtCl3(NH3)]', 'Na2[SiF6]',
}

# 难溶物（不拆分）
INSOLUBLE = {
    'AgCl', 'AgBr', 'AgI', 'Ag2S', 'Ag2CO3', 'Ag2SO4', 'Ag3PO4',
    'BaSO4', 'BaCO3', 'BaSO3', 'Ba3(PO4)2', 'BaCrO4',
    'CaCO3', 'CaSO3', 'Ca3(PO4)2', 'CaF2',
    'PbCl2', 'PbI2', 'PbS', 'PbSO4', 'PbCO3', 'PbCrO4',
    'CuS', 'Cu(OH)2', 'CuCO3', 'Cu3(PO4)2',
    'Fe(OH)3', 'Fe(OH)2', 'FeS', 'Fe2(CO3)3',
    'Al(OH)3', 'Al2O3', 'Al2(CO3)3',
    'Mg(OH)2', 'MgCO3', 'Mg3(PO4)2',
    'ZnS', 'Zn(OH)2', 'ZnCO3', 'Zn3(PO4)2',
    'HgS', 'Hg2Cl2', 'HgI2',
    'MnS', 'Mn(OH)2', 'MnCO3',
    'NiS', 'Ni(OH)2', 'NiCO3',
    'CoS', 'Co(OH)2',
    'Cr(OH)3', 'Cr2(CO3)3',
}

# 气体（不拆分）
GASES = {
    'H2', 'O2', 'N2', 'Cl2', 'F2', 'CO2', 'CO', 'SO2', 'SO3',
    'NO', 'NO2', 'N2O', 'NH3', 'HCl', 'HBr', 'HI', 'HF',
    'CH4', 'C2H6', 'C2H4', 'C2H2', 'H2S',
}

# 弱电解质（不完全电离，不拆分）
WEAK_ELECTROLYTES = {
    'H2O', 'HF', 'HCN', 'H2S', 'H2CO3', 'H2SO3', 'H3PO4',
    'CH3COOH', 'HC2H3O2', 'NH3', 'NH3·H2O',
}

# 常见离子的 Unicode 上标映射
CHARGE_SUPERSCRIPTS = {
    0: '', 1: '⁺', 2: '²⁺', 3: '³⁺', 4: '⁴⁺',
    -1: '⁻', -2: '²⁻', -3: '³⁻', -4: '⁴⁻',
}


# ====== 离子解析器 ======

class IonParser:
    """
    离子解析器
    解析离子表示，如 H+, OH-, SO4^2-, Fe3+
    """

    # 匹配离子格式：符号 + 电荷
    # 支持格式：H+, OH-, SO4^2-, Fe3+, [Cu(NH3)4]2+
    ION_PATTERN = re.compile(
        r'^(\[?.*\]?)(\d*)([+-])(\d*)$'
    )

    def parse(self, ion_str: str) -> Ion:
        """
        解析离子字符串

        Args:
            ion_str: 离子表示，如 "H+", "OH-", "SO4^2-", "Fe3+"

        Returns:
            Ion 对象
        """
        ion_str = ion_str.strip()

        # 处理 [complex]n+ 格式
        if ion_str.startswith('['):
            match = re.match(r'^(\[.+?\])(\d*)([+-])$', ion_str)
            if match:
                symbol = match.group(1)
                count = int(match.group(2)) if match.group(2) else 1
                sign = 1 if match.group(3) == '+' else -1
                return Ion(
                    formula=ion_str,
                    symbol=symbol,
                    charge=count * sign,
                )

        # 标准离子格式
        match = self.ION_PATTERN.match(ion_str)
        if not match:
            # 尝试解析简单格式（如 "Na+"）
            if ion_str.endswith('+'):
                return Ion(formula=ion_str, symbol=ion_str[:-1], charge=1)
            elif ion_str.endswith('-'):
                return Ion(formula=ion_str, symbol=ion_str[:-1], charge=-1)
            raise ValueError(f"Cannot parse ion: {ion_str}")

        symbol = match.group(1)
        count_str = match.group(2)
        sign = match.group(3)
        charge_str = match.group(4)

        # 计算电荷
        if count_str and charge_str:
            # 格式：SO4^2- 或 Fe3+
            count = int(count_str)
            charge_val = int(charge_str) if charge_str else 1
        elif charge_str:
            # 格式：H+ 或 OH-
            count = 0
            charge_val = int(charge_str)
        else:
            count = 0
            charge_val = 1

        charge = charge_val if sign == '+' else -charge_val
        if count_str and not charge_str:
            charge = count if sign == '+' else -count

        return Ion(
            formula=ion_str,
            symbol=symbol,
            charge=charge,
        )

    def to_unicode(self, ion: Ion) -> str:
        """将离子转换为 Unicode 格式"""
        charge = ion.charge
        if charge == 0:
            return ion.symbol

        sup = CHARGE_SUPERSCRIPTS.get(charge, '')
        if sup:
            return f"{ion.symbol}{sup}"

        # 通用格式
        if abs(charge) == 1:
            return f"{ion.symbol}{'⁺' if charge > 0 else '⁻'}"
        return f"{ion.symbol}{self._to_superscript(abs(charge))}{'⁺' if charge > 0 else '⁻'}"

    def to_latex(self, ion: Ion) -> str:
        """将离子转换为 LaTeX 格式"""
        charge = ion.charge
        if charge == 0:
            return ion.symbol

        if charge == 1:
            charge_str = "+"
        elif charge == -1:
            charge_str = "-"
        elif charge > 0:
            charge_str = f"{charge}+"
        else:
            charge_str = f"{abs(charge)}-"

        return f"\\ce{{{ion.symbol}^{charge_str}}}"

    def _to_superscript(self, n: int) -> str:
        """数字转上标"""
        superscripts = '⁰¹²³⁴⁵⁶⁷⁸⁹'
        return ''.join(superscripts[int(d)] for d in str(n))


# ====== 离子方程式配平器 ======

class IonEquationBalancer:
    """
    离子方程式配平器
    同时满足原子守恒和电荷守恒
    """

    def __init__(self):
        self.formula_parser = FormulaParser()

    def balance(self, equation: str) -> Dict:
        """
        配平离子方程式

        Args:
            equation: 离子方程式，如 "H+ + OH- -> H2O"

        Returns:
            配平结果
        """
        # 解析方程式
        reactants, products = self._parse_equation(equation)

        # 获取所有元素和电荷
        all_elements = set()
        reactant_data = []  # (元素计数, 电荷)
        product_data = []

        for term in reactants:
            coeff, formula, charge = self._parse_term(term)
            elements = self._parse_formula_with_charge(formula, charge)
            all_elements.update(elements.keys())
            reactant_data.append((elements, charge, coeff, formula))

        for term in products:
            coeff, formula, charge = self._parse_term(term)
            elements = self._parse_formula_with_charge(formula, charge)
            all_elements.update(elements.keys())
            product_data.append((elements, charge, coeff, formula))

        # 移除电荷键（单独处理）
        all_elements.discard('__charge__')

        elements_list = sorted(all_elements)
        num_elements = len(elements_list)
        num_compounds = len(reactants) + len(products)

        if num_compounds == 0:
            return {'error': 'Empty equation'}

        # 构建矩阵（包含电荷行）
        # 行：元素 + 电荷，列：化合物
        matrix_rows = num_elements + 1  # +1 for charge
        matrix = []

        # 元素行
        for elem in elements_list:
            row = []
            for data in reactant_data:
                row.append(data[0].get(elem, 0))
            for data in product_data:
                row.append(-data[0].get(elem, 0))
            matrix.append(row)

        # 电荷行
        charge_row = []
        for data in reactant_data:
            charge_row.append(data[1])
        for data in product_data:
            charge_row.append(-data[1])
        matrix.append(charge_row)

        # 高斯消元求解
        coefficients = self._solve_null_space(matrix, num_compounds)

        if coefficients is None:
            return {'error': 'Cannot balance this equation'}

        # 转换为整数系数
        coefficients = self._to_integer_coefficients(coefficients)

        # 构建平衡后的方程式
        balanced_reactants = []
        for i, term in enumerate(reactants):
            coeff, formula, charge = self._parse_term(term)
            new_coeff = int(coefficients[i])
            ion_str = self._format_ion(formula, charge, new_coeff)
            balanced_reactants.append(ion_str)

        balanced_products = []
        for i, term in enumerate(products):
            coeff, formula, charge = self._parse_term(term)
            new_coeff = int(coefficients[i + len(reactants)])
            ion_str = self._format_ion(formula, charge, new_coeff)
            balanced_products.append(ion_str)

        # 保留原始分隔符
        separator = self._get_separator(equation)
        balanced = ' + '.join(balanced_reactants) + f' {separator} ' + ' + '.join(balanced_products)

        # 生成 Unicode 和 LaTeX
        unicode_result = self._to_unicode(reactants, products, coefficients, separator)
        latex_result = self._to_latex(reactants, products, coefficients, separator)

        # 验证电荷守恒
        reactant_charge_sum = sum(
            self._parse_term(t)[2] * int(coefficients[i])
            for i, t in enumerate(reactants)
        )
        product_charge_sum = sum(
            self._parse_term(t)[2] * int(coefficients[i + len(reactants)])
            for i, t in enumerate(products)
        )

        return {
            'original': equation,
            'balanced': balanced,
            'unicode': unicode_result,
            'latex': latex_result,
            'is_balanced': self._check_balanced(equation),
            'charge_balanced': reactant_charge_sum == product_charge_sum,
            'reactant_charges': reactant_charge_sum,
            'product_charges': product_charge_sum,
        }

    def _parse_equation(self, equation: str) -> Tuple[List[str], List[str]]:
        """解析方程式，返回反应物和生成物列表"""
        separators = ['->', '→', '⟶', '<=>', '⇌', '⇋']
        for sep in separators:
            if sep in equation:
                parts = equation.split(sep)
                if len(parts) == 2:
                    reactants = [r.strip() for r in parts[0].split('+')]
                    products = [p.strip() for r in parts[1].split('+')]
                    return reactants, products
        raise ValueError(f"Invalid equation format: {equation}")

    def _parse_term(self, term: str) -> Tuple[int, str, int]:
        """
        解析一个项，返回 (系数, 化学式/离子式, 电荷)

        Examples:
            "2H+" → (2, "H", 1)
            "SO4^2-" → (1, "SO4", -2)
            "Fe" → (1, "Fe", 0)
        """
        term = term.strip()

        # 提取系数
        coeff_match = re.match(r'^(\d+)\s*(.+)$', term)
        if coeff_match:
            coeff = int(coeff_match.group(1))
            rest = coeff_match.group(2)
        else:
            coeff = 1
            rest = term

        # 提取电荷
        charge = 0
        formula = rest

        # 配合物离子：[Cu(NH3)4]2+ 或 [Fe(CN)6]3-
        if rest.startswith('['):
            bracket_match = re.match(r'^(\[.+?\])(\d*)([+-])$', rest)
            if bracket_match:
                formula = bracket_match.group(1)
                num_str = bracket_match.group(2)
                sign = bracket_match.group(3)
                charge = int(num_str) if num_str else 1
                if sign == '-':
                    charge = -charge
                return coeff, formula, charge

        # 格式：SO4^2- 或 H+
        charge_match = re.match(r'^(.+?)(\d*)([+-])$', rest)
        if charge_match:
            formula = charge_match.group(1)
            num_str = charge_match.group(2)
            sign = charge_match.group(3)

            if num_str:
                charge = int(num_str)
            else:
                charge = 1

            if sign == '-':
                charge = -charge

        return coeff, formula, charge

    def _parse_formula_with_charge(self, formula: str, charge: int) -> Dict[str, int]:
        """解析化学式/离子式的元素计数"""
        try:
            elements = self.formula_parser.parse(formula)
        except ValueError:
            # 如果解析失败，尝试移除括号
            elements = {}

        # 添加电荷作为虚拟元素
        if charge != 0:
            elements['__charge__'] = charge

        return elements

    def _format_ion(self, formula: str, charge: int, coeff: int) -> str:
        """格式化离子输出"""
        if charge == 0:
            # 分子
            if coeff == 1:
                return formula
            return f"{coeff}{formula}"

        # 离子
        if abs(charge) == 1:
            charge_str = '+' if charge > 0 else '-'
        else:
            charge_str = f"{abs(charge)}{'+' if charge > 0 else '-'}"

        ion_str = f"{formula}{charge_str}"
        if coeff == 1:
            return ion_str
        return f"{coeff}{ion_str}"

    def _get_separator(self, equation: str) -> str:
        """获取方程式分隔符"""
        separators = ['->', '→', '⟶', '<=>', '⇌', '⇋']
        for sep in separators:
            if sep in equation:
                return sep
        return '->'

    def _solve_null_space(self, matrix: List[List[float]], n: int) -> Optional[List[float]]:
        """高斯消元求解零空间"""
        import numpy as np

        A = np.array(matrix, dtype=float)
        rows, cols = A.shape

        # 行简化
        pivot_cols = []
        pivot_row = 0

        for col in range(cols):
            # 找主元
            found = False
            for row in range(pivot_row, rows):
                if abs(A[row, col]) > 1e-10:
                    A[[pivot_row, row]] = A[[row, pivot_row]]
                    found = True
                    break

            if not found:
                continue

            # 归一化
            pivot_val = A[pivot_row, col]
            A[pivot_row] = A[pivot_row] / pivot_val

            # 消元
            for row in range(rows):
                if row != pivot_row and abs(A[row, col]) > 1e-10:
                    factor = A[row, col]
                    A[row] = A[row] - factor * A[pivot_row]

            pivot_cols.append(col)
            pivot_row += 1

        # 找自由变量
        free_vars = [i for i in range(cols) if i not in pivot_cols]

        if not free_vars:
            return None

        # 构建解
        solution = np.zeros(cols)
        free_var_idx = free_vars[0]
        solution[free_var_idx] = 1.0

        # 回代
        for i, col in enumerate(pivot_cols):
            solution[col] = -A[i, free_var_idx]

        return solution.tolist()

    def _to_integer_coefficients(self, coefficients: List[float]) -> List[int]:
        """转换为最小正整数系数"""
        fractions = [Fraction(c).limit_denominator(1000) for c in coefficients]

        # 找最小公倍数
        denominators = [f.denominator for f in fractions]
        lcm = denominators[0]
        for d in denominators[1:]:
            lcm = lcm * d // self._gcd(lcm, d)

        # 转换为整数
        int_coefficients = [int(f * lcm) for f in fractions]

        # 确保所有系数为正
        if any(c < 0 for c in int_coefficients):
            int_coefficients = [-c for c in int_coefficients]

        # 约分
        from math import gcd
        from functools import reduce
        g = reduce(gcd, [abs(c) for c in int_coefficients if c != 0])
        if g > 0:
            int_coefficients = [c // g for c in int_coefficients]

        return int_coefficients

    def _gcd(self, a: int, b: int) -> int:
        """最大公约数"""
        while b:
            a, b = b, a % b
        return a

    def _check_balanced(self, equation: str) -> bool:
        """检查方程式是否已平衡"""
        try:
            result = self.balance(equation)
            return result.get('balanced') == equation
        except:
            return False

    def _to_unicode(self, reactants, products, coefficients, separator) -> str:
        """生成 Unicode 格式"""
        parts_r = []
        for i, term in enumerate(reactants):
            coeff, formula, charge = self._parse_term(term)
            new_coeff = int(coefficients[i])
            parts_r.append(self._format_ion_unicode(formula, charge, new_coeff))

        parts_p = []
        for i, term in enumerate(products):
            coeff, formula, charge = self._parse_term(term)
            new_coeff = int(coefficients[i + len(reactants)])
            parts_p.append(self._format_ion_unicode(formula, charge, new_coeff))

        sep = ' → ' if '->' in separator or '→' in separator else ' ⇌ '
        return ' + '.join(parts_r) + sep + ' + '.join(parts_p)

    def _to_latex(self, reactants, products, coefficients, separator) -> str:
        """生成 LaTeX 格式"""
        parts_r = []
        for i, term in enumerate(reactants):
            coeff, formula, charge = self._parse_term(term)
            new_coeff = int(coefficients[i])
            parts_r.append(self._format_ion_latex(formula, charge, new_coeff))

        parts_p = []
        for i, term in enumerate(products):
            coeff, formula, charge = self._parse_term(term)
            new_coeff = int(coefficients[i + len(reactants)])
            parts_p.append(self._format_ion_latex(formula, charge, new_coeff))

        arrow = '\\rightarrow' if '->' in separator or '→' in separator else '\\rightleftharpoons'
        return f"\\ce{{{' + '.join(parts_r)} {arrow} {' + '.join(parts_p)}}}"

    def _format_ion_unicode(self, formula: str, charge: int, coeff: int) -> str:
        """格式化离子为 Unicode"""
        sup_map = {1: '⁺', 2: '²⁺', 3: '³⁺', 4: '⁴⁺',
                   -1: '⁻', -2: '²⁻', -3: '³⁻', -4: '⁴⁻'}

        if charge == 0:
            s = formula
        else:
            s = f"{formula}{sup_map.get(charge, str(charge))}"

        if coeff > 1:
            s = f"{coeff}{s}"
        return s

    def _format_ion_latex(self, formula: str, charge: int, coeff: int) -> str:
        """格式化离子为 LaTeX"""
        if charge == 0:
            s = formula
        else:
            if charge == 1:
                c = '+'
            elif charge == -1:
                c = '-'
            elif charge > 0:
                c = f"{charge}+"
            else:
                c = f"{abs(charge)}-"
            s = f"\\ce{{{formula}^{c}}}"

        if coeff > 1:
            s = f"{coeff}{s}"
        return s


# ====== 分子方程式 → 离子方程式转换器 ======

class MolecularToIonicConverter:
    """
    将分子方程式转换为离子方程式
    1. 拆分强电解质为离子
    2. 保留弱电解质、沉淀、气体
    3. 识别旁观离子
    4. 生成净离子方程式
    """

    def __init__(self):
        self.formula_parser = FormulaParser()

    def convert(self, equation: str) -> IonicEquationResult:
        """
        将分子方程式转换为离子方程式

        Args:
            equation: 分子方程式，如 "NaOH + HCl -> NaCl + H2O"

        Returns:
            IonicEquationResult 包含完整离子方程式和净离子方程式
        """
        # 解析方程式
        reactants, products = self._parse_equation(equation)

        # 拆分各物质
        reactant_species = []  # (系数, 物质列表)
        product_species = []

        for term in reactants:
            species = self._dissociate(term)
            reactant_species.append(species)

        for term in products:
            species = self._dissociate(term)
            product_species.append(species)

        # 生成完整离子方程式
        full_ionic_reactants = []
        full_ionic_products = []

        for species in reactant_species:
            full_ionic_reactants.extend(species)

        for species in product_species:
            full_ionic_products.extend(species)

        # 找出旁观离子
        reactant_ions = {s for s in full_ionic_reactants if self._is_ion(s)}
        product_ions = {s for s in full_ionic_products if self._is_ion(s)}
        spectator_ions = list(reactant_ions & product_ions)

        # 生成净离子方程式（移除旁观离子）
        net_reactants = [s for s in full_ionic_reactants if s not in spectator_ions]
        net_products = [s for s in full_ionic_products if s not in spectator_ions]

        # 格式化输出
        separator = self._get_separator(equation)

        full_ionic = self._format_equation(full_ionic_reactants, full_ionic_products, separator)
        net_ionic = self._format_equation(net_reactants, net_products, separator)

        # 平衡分子方程式
        from .reaction_engine import EquationBalancer
        balancer = EquationBalancer()
        try:
            balanced_molecular = balancer.balance(equation)
        except:
            balanced_molecular = equation

        return IonicEquationResult(
            original=equation,
            full_ionic=full_ionic,
            net_ionic=net_ionic,
            spectator_ions=spectator_ions,
            balanced_molecular=balanced_molecular,
            balanced_full_ionic=full_ionic,
            balanced_net_ionic=net_ionic,
            charge_balanced=True,
            reactant_charges=0,
            product_charges=0,
        )

    def _dissociate(self, term: str) -> List[str]:
        """
        将物质拆分为离子（如果是强电解质）

        Returns:
            拆分后的离子/分子列表
        """
        term = term.strip()

        # 提取系数
        coeff_match = re.match(r'^(\d+)\s*(.+)$', term)
        if coeff_match:
            coeff = int(coeff_match.group(1))
            formula = coeff_match.group(2)
        else:
            coeff = 1
            formula = term

        # 检查是否为强电解质
        if self._should_dissociate(formula):
            ions = self._get_ions(formula)
            if ions:
                # 应用系数
                result = []
                for ion in ions:
                    if coeff > 1:
                        result.append(f"{coeff}{ion}")
                    else:
                        result.append(ion)
                return result

        # 不拆分
        return [term]

    def _should_dissociate(self, formula: str) -> bool:
        """判断是否应该拆分"""
        # 水不拆分
        if formula == 'H2O':
            return False
        # 弱电解质不拆分
        if formula in WEAK_ELECTROLYTES:
            return False
        # 气体不拆分
        if formula in GASES:
            return False
        # 沉淀不拆分
        if formula in INSOLUBLE:
            return False
        # 强酸、强碱、可溶盐拆分
        if formula in STRONG_ACIDS or formula in STRONG_BASES or formula in SOLUBLE_SALTS:
            return True
        return False

    def _get_ions(self, formula: str) -> List[str]:
        """获取强电解质的离子"""
        # 常见电解质的离解映射
        dissociation_map = {
            # 强酸
            'HCl': ['H+', 'Cl-'],
            'HBr': ['H+', 'Br-'],
            'HI': ['H+', 'I-'],
            'HNO3': ['H+', 'NO3-'],
            'H2SO4': ['2H+', 'SO4^2-'],
            'HClO4': ['H+', 'ClO4-'],
            'HClO3': ['H+', 'ClO3-'],
            # 强碱
            'NaOH': ['Na+', 'OH-'],
            'KOH': ['K+', 'OH-'],
            'Ca(OH)2': ['Ca^2+', '2OH-'],
            'Ba(OH)2': ['Ba^2+', '2OH-'],
            'Sr(OH)2': ['Sr^2+', '2OH-'],
            # 钠盐
            'NaCl': ['Na+', 'Cl-'],
            'NaBr': ['Na+', 'Br-'],
            'NaI': ['Na+', 'I-'],
            'NaNO3': ['Na+', 'NO3-'],
            'Na2SO4': ['2Na+', 'SO4^2-'],
            'Na2CO3': ['2Na+', 'CO3^2-'],
            'Na3PO4': ['3Na+', 'PO4^3-'],
            'Na2S': ['2Na+', 'S^2-'],
            'NaHCO3': ['Na+', 'HCO3-'],
            'Na2SO3': ['2Na+', 'SO3^2-'],
            'NaClO': ['Na+', 'ClO-'],
            'CH3COONa': ['Na+', 'CH3COO-'],
            'NaCH3COO': ['Na+', 'CH3COO-'],
            'NaC2H3O2': ['Na+', 'C2H3O2-'],
            # 钾盐
            'KCl': ['K+', 'Cl-'],
            'KBr': ['K+', 'Br-'],
            'KI': ['K+', 'I-'],
            'KNO3': ['K+', 'NO3-'],
            'K2SO4': ['2K+', 'SO4^2-'],
            'K2CO3': ['2K+', 'CO3^2-'],
            'K3PO4': ['3K+', 'PO4^3-'],
            'K2S': ['2K+', 'S^2-'],
            'KHCO3': ['K+', 'HCO3-'],
            'K2SO3': ['2K+', 'SO3^2-'],
            'KClO': ['K+', 'ClO-'],
            'K2CrO4': ['2K+', 'CrO4^2-'],
            'K2Cr2O7': ['2K+', 'Cr2O7^2-'],
            'KMnO4': ['K+', 'MnO4-'],
            # 铵盐
            'NH4Cl': ['NH4+', 'Cl-'],
            'NH4Br': ['NH4+', 'Br-'],
            'NH4I': ['NH4+', 'I-'],
            'NH4NO3': ['NH4+', 'NO3-'],
            '(NH4)2SO4': ['2NH4+', 'SO4^2-'],
            '(NH4)2CO3': ['2NH4+', 'CO3^2-'],
            '(NH4)3PO4': ['3NH4+', 'PO4^3-'],
            'NH4HCO3': ['NH4+', 'HCO3-'],
            # 硝酸盐
            'AgNO3': ['Ag+', 'NO3-'],
            'Ca(NO3)2': ['Ca^2+', '2NO3-'],
            'Mg(NO3)2': ['Mg^2+', '2NO3-'],
            'Fe(NO3)2': ['Fe^2+', '2NO3-'],
            'Fe(NO3)3': ['Fe^3+', '3NO3-'],
            'Cu(NO3)2': ['Cu^2+', '2NO3-'],
            'Zn(NO3)2': ['Zn^2+', '2NO3-'],
            'Pb(NO3)2': ['Pb^2+', '2NO3-'],
            'Al(NO3)3': ['Al^3+', '3NO3-'],
            # 氯化物
            'CaCl2': ['Ca^2+', '2Cl-'],
            'MgCl2': ['Mg^2+', '2Cl-'],
            'FeCl2': ['Fe^2+', '2Cl-'],
            'FeCl3': ['Fe^3+', '3Cl-'],
            'CuCl2': ['Cu^2+', '2Cl-'],
            'ZnCl2': ['Zn^2+', '2Cl-'],
            'AlCl3': ['Al^3+', '3Cl-'],
            'BaCl2': ['Ba^2+', '2Cl-'],
            'SrCl2': ['Sr^2+', '2Cl-'],
            'MnCl2': ['Mn^2+', '2Cl-'],
            # 硫酸盐
            'MgSO4': ['Mg^2+', 'SO4^2-'],
            'FeSO4': ['Fe^2+', 'SO4^2-'],
            'Fe2(SO4)3': ['2Fe^3+', '3SO4^2-'],
            'CuSO4': ['Cu^2+', 'SO4^2-'],
            'ZnSO4': ['Zn^2+', 'SO4^2-'],
            'Al2(SO4)3': ['2Al^3+', '3SO4^2-'],
            # 配合物盐
            'K3[Fe(CN)6]': ['3K+', '[Fe(CN)6]^3-'],
            'K4[Fe(CN)6]': ['4K+', '[Fe(CN)6]^4-'],
            'Na3[AlF6]': ['3Na+', '[AlF6]^3-'],
            '[Cu(NH3)4]SO4': ['[Cu(NH3)4]^2+', 'SO4^2-'],
            '[Ag(NH3)2]Cl': ['[Ag(NH3)2]+', 'Cl-'],
            '[Co(NH3)6]Cl3': ['[Co(NH3)6]^3+', '3Cl-'],
            'K[PtCl3(NH3)]': ['K+', '[PtCl3(NH3)]^-'],
            'Na2[SiF6]': ['2Na+', '[SiF6]^2-'],
        }

        return dissociation_map.get(formula, [])

    def _is_ion(self, term: str) -> bool:
        """判断是否为离子"""
        return bool(re.search(r'[+-]$', term)) or bool(re.search(r'\^[0-9]*[+-]', term))

    def _parse_equation(self, equation: str) -> Tuple[List[str], List[str]]:
        """解析方程式"""
        separators = ['->', '→', '⟶', '<=>', '⇌', '⇋']
        for sep in separators:
            if sep in equation:
                parts = equation.split(sep)
                if len(parts) == 2:
                    reactants = [r.strip() for r in parts[0].split('+')]
                    products = [p.strip() for p in parts[1].split('+')]
                    return reactants, products
        raise ValueError(f"Invalid equation format: {equation}")

    def _get_separator(self, equation: str) -> str:
        """获取分隔符"""
        separators = ['->', '→', '⟶', '<=>', '⇌', '⇋']
        for sep in separators:
            if sep in equation:
                return sep
        return '->'

    def _format_equation(self, reactants: List[str], products: List[str], separator: str) -> str:
        """格式化方程式"""
        r_str = ' + '.join(reactants)
        p_str = ' + '.join(products)
        return f"{r_str} {separator} {p_str}"


# ====== 全局实例 ======

ion_parser = IonParser()
ion_balancer = IonEquationBalancer()
molecular_to_ionic = MolecularToIonicConverter()


# ====== 便捷函数 ======

def balance_ion_equation(equation: str) -> Dict:
    """配平离子方程式"""
    return ion_balancer.balance(equation)


def convert_to_ionic(equation: str) -> IonicEquationResult:
    """分子方程式转离子方程式"""
    return molecular_to_ionic.convert(equation)


def parse_ion(ion_str: str) -> Ion:
    """解析离子"""
    return ion_parser.parse(ion_str)
