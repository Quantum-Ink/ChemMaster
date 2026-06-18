"""
ChemMaster 化学式解析核心模块
支持：化学式解析、下标转换、LaTeX 格式化
"""

import re
from typing import Dict, List, Tuple, Optional


class FormulaParser:
    """化学式解析器"""

    # 常见元素符号
    ELEMENTS = {
        'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
        'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca',
        'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
        'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr',
        'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn',
        'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd',
        'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
        'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
        'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th',
        'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm',
        'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds',
        'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og'
    }

    # Unicode 下标字符映射
    SUBSCRIPT_MAP = {
        '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
        '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
    }

    # Unicode 上标字符映射
    SUPERSCRIPT_MAP = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
        '+': '⁺', '-': '⁻'
    }

    def parse(self, formula: str) -> Dict[str, int]:
        """
        解析化学式，返回元素计数

        Args:
            formula: 化学式字符串，如 "H2SO4", "Ca(OH)2"

        Returns:
            元素计数字典，如 {"H": 2, "S": 1, "O": 4}
        """
        result = {}
        i = 0
        n = len(formula)

        while i < n:
            if formula[i] in '([':
                # 处理括号（圆括号或方括号）
                bracket_content, end_idx = self._extract_bracket(formula, i)
                # 获取括号后的数字
                multiplier, new_idx = self._extract_number(formula, end_idx)
                # 递归解析括号内容
                inner_elements = self.parse(bracket_content)
                # 乘以倍数
                for elem, count in inner_elements.items():
                    result[elem] = result.get(elem, 0) + count * multiplier
                i = new_idx
            elif formula[i].isupper():
                # 处理元素符号
                elem, i = self._extract_element(formula, i)
                count, i = self._extract_number(formula, i)
                result[elem] = result.get(elem, 0) + count
            else:
                i += 1

        return result

    def _extract_bracket(self, formula: str, start: int) -> Tuple[str, int]:
        """提取括号内容（支持圆括号和方括号）"""
        open_char = formula[start]
        close_char = ')' if open_char == '(' else ']'
        depth = 0
        i = start
        while i < len(formula):
            if formula[i] == open_char:
                depth += 1
            elif formula[i] == close_char:
                depth -= 1
                if depth == 0:
                    return formula[start + 1:i], i + 1
            i += 1
        raise ValueError(f"Unmatched bracket at position {start}")

    def _extract_element(self, formula: str, start: int) -> Tuple[str, int]:
        """提取元素符号"""
        if start >= len(formula):
            return "", start

        # 元素符号：大写字母 + 可选小写字母
        elem = formula[start]
        i = start + 1
        while i < len(formula) and formula[i].islower():
            elem += formula[i]
            i += 1

        if elem not in self.ELEMENTS:
            raise ValueError(f"Unknown element: {elem}")

        return elem, i

    def _extract_number(self, formula: str, start: int) -> Tuple[int, int]:
        """提取数字"""
        num_str = ""
        i = start
        while i < len(formula) and formula[i].isdigit():
            num_str += formula[i]
            i += 1

        return (int(num_str) if num_str else 1), i

    def to_subscript(self, formula: str) -> str:
        """
        将化学式转换为 Unicode 下标格式

        Args:
            formula: 原始化学式 "H2SO4"

        Returns:
            带下标的化学式 "H₂SO₄"
        """
        result = ""
        i = 0
        n = len(formula)

        while i < n:
            if formula[i] == '(':
                result += '('
                i += 1
            elif formula[i] in ')]':
                result += formula[i]
                i += 1
                # 括号后的数字转为下标
                while i < n and formula[i].isdigit():
                    result += self.SUBSCRIPT_MAP.get(formula[i], formula[i])
                    i += 1
            elif formula[i].isupper():
                # 元素符号
                result += formula[i]
                i += 1
                while i < n and formula[i].islower():
                    result += formula[i]
                    i += 1
                # 元素后的数字转为下标
                while i < n and formula[i].isdigit():
                    result += self.SUBSCRIPT_MAP.get(formula[i], formula[i])
                    i += 1
            elif formula[i] in '+-':
                # 电荷符号
                while i < n and (formula[i] in '+-' or formula[i].isdigit()):
                    if formula[i].isdigit():
                        result += self.SUPERSCRIPT_MAP.get(formula[i], formula[i])
                    else:
                        result += self.SUPERSCRIPT_MAP.get(formula[i], formula[i])
                    i += 1
            else:
                result += formula[i]
                i += 1

        return result

    def to_latex(self, formula: str, package: str = "mhchem") -> str:
        """
        将化学式转换为 LaTeX 格式

        Args:
            formula: 原始化学式
            package: LaTeX 包格式 ("mhchem" 或 "standard")

        Returns:
            LaTeX 格式字符串
        """
        if package == "mhchem":
            return f"\\ce{{{formula}}}"
        else:
            # 标准 LaTeX 格式
            result = ""
            i = 0
            n = len(formula)

            while i < n:
                if formula[i].isupper():
                    result += formula[i]
                    i += 1
                    while i < n and formula[i].islower():
                        result += formula[i]
                        i += 1
                    # 数字转为下标
                    if i < n and formula[i].isdigit():
                        num = ""
                        while i < n and formula[i].isdigit():
                            num += formula[i]
                            i += 1
                        result += f"_{{{num}}}"
                elif formula[i] in '+-':
                    # 电荷转为上标
                    charge = ""
                    while i < n and (formula[i] in '+-' or formula[i].isdigit()):
                        charge += formula[i]
                        i += 1
                    result += f"^{{{charge}}}"
                else:
                    result += formula[i]
                    i += 1

            return result


class ReactionParser:
    """反应方程式解析器"""

    def __init__(self):
        self.formula_parser = FormulaParser()

    def parse_equation(self, equation: str) -> Tuple[List[str], List[str]]:
        """
        解析反应方程式

        Args:
            equation: 如 "H2 + O2 -> H2O"

        Returns:
            (反应物列表, 生成物列表)
        """
        # 分割反应物和生成物
        separators = ['->', '→', '⟶', '<=>', '⇌', '⇋']
        for sep in separators:
            if sep in equation:
                parts = equation.split(sep)
                if len(parts) == 2:
                    reactants = [r.strip() for r in parts[0].split('+')]
                    products = [p.strip() for p in parts[1].split('+')]
                    return reactants, products

        raise ValueError(f"Invalid equation format: {equation}")

    def get_element_counts(self, equation: str) -> Tuple[Dict[str, int], Dict[str, int]]:
        """
        获取反应方程式中各元素的原子数

        Returns:
            (反应物元素计数, 生成物元素计数)
        """
        reactants, products = self.parse_equation(equation)

        reactant_counts = {}
        for r in reactants:
            # 处理系数
            coeff, formula = self._extract_coefficient(r)
            elements = self.formula_parser.parse(formula)
            for elem, count in elements.items():
                reactant_counts[elem] = reactant_counts.get(elem, 0) + count * coeff

        product_counts = {}
        for p in products:
            coeff, formula = self._extract_coefficient(p)
            elements = self.formula_parser.parse(formula)
            for elem, count in elements.items():
                product_counts[elem] = product_counts.get(elem, 0) + count * coeff

        return reactant_counts, product_counts

    def _extract_coefficient(self, term: str) -> Tuple[int, str]:
        """提取化学式前的系数"""
        match = re.match(r'^(\d+)\s*(.+)$', term)
        if match:
            return int(match.group(1)), match.group(2)
        return 1, term

    def to_subscript(self, equation: str) -> str:
        """将方程式转换为带下标的格式"""
        result = equation
        separators = ['->', '→', '⟶', '<=>', '⇌', '⇋']

        for sep in separators:
            if sep in result:
                parts = result.split(sep)
                if len(parts) == 2:
                    reactants = [r.strip() for r in parts[0].split('+')]
                    products = [p.strip() for p in parts[1].split('+')]

                    # 转换每个化学式
                    formatted_reactants = []
                    for r in reactants:
                        coeff, formula = self._extract_coefficient(r)
                        formatted = self.formula_parser.to_subscript(formula)
                        if coeff > 1:
                            formatted = f"{coeff}{formatted}"
                        formatted_reactants.append(formatted)

                    formatted_products = []
                    for p in products:
                        coeff, formula = self._extract_coefficient(p)
                        formatted = self.formula_parser.to_subscript(formula)
                        if coeff > 1:
                            formatted = f"{coeff}{formatted}"
                        formatted_products.append(formatted)

                    return ' + '.join(formatted_reactants) + f' {sep} ' + ' + '.join(formatted_products)

        return result

    def to_latex(self, equation: str, package: str = "mhchem") -> str:
        """将方程式转换为 LaTeX 格式"""
        if package == "mhchem":
            # mhchem 直接支持方程式
            return f"\\ce{{{equation}}}"
        else:
            # 标准格式
            reactants, products = self.parse_equation(equation)
            latex_reactants = []
            for r in reactants:
                coeff, formula = self._extract_coefficient(r)
                latex_formula = self.formula_parser.to_latex(formula, package)
                if coeff > 1:
                    latex_formula = f"{coeff}{latex_formula}"
                latex_reactants.append(latex_formula)

            latex_products = []
            for p in products:
                coeff, formula = self._extract_coefficient(p)
                latex_formula = self.formula_parser.to_latex(formula, package)
                if coeff > 1:
                    latex_formula = f"{coeff}{latex_formula}"
                latex_products.append(latex_formula)

            return ' + '.join(latex_reactants) + ' \\rightarrow ' + ' + '.join(latex_products)


# 便捷函数
def parse_formula(formula: str) -> Dict[str, int]:
    """解析化学式"""
    parser = FormulaParser()
    return parser.parse(formula)


def formula_to_subscript(formula: str) -> str:
    """化学式转下标格式"""
    parser = FormulaParser()
    return parser.to_subscript(formula)


def formula_to_latex(formula: str) -> str:
    """化学式转 LaTeX 格式"""
    parser = FormulaParser()
    return parser.to_latex(formula)
