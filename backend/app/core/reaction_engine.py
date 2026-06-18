"""
ChemMaster 化学方程式平衡引擎
使用矩阵法（高斯消元）平衡化学方程式
"""

import re
import numpy as np
from typing import List, Dict, Tuple, Optional
from fractions import Fraction

from .chemistry import FormulaParser, ReactionParser


class EquationBalancer:
    """化学方程式平衡器（矩阵法）"""

    def __init__(self):
        self.formula_parser = FormulaParser()
        self.reaction_parser = ReactionParser()

    def balance(self, equation: str) -> str:
        """
        平衡化学方程式

        Args:
            equation: 未平衡的方程式，如 "Fe + O2 -> Fe2O3"

        Returns:
            平衡后的方程式，如 "4Fe + 3O2 -> 2Fe2O3"
        """
        # 解析方程式
        reactants, products = self.reaction_parser.parse_equation(equation)

        # 获取所有元素
        all_elements = set()
        for term in reactants + products:
            coeff, formula = self._extract_coefficient(term)
            elements = self.formula_parser.parse(formula)
            all_elements.update(elements.keys())

        elements_list = sorted(all_elements)
        num_elements = len(elements_list)
        num_compounds = len(reactants) + len(products)

        if num_compounds == 0:
            raise ValueError("Empty equation")

        # 构建矩阵
        # 行：元素，列：化合物（反应物为正，生成物为负）
        matrix = np.zeros((num_elements, num_compounds), dtype=float)

        for j, term in enumerate(reactants):
            coeff, formula = self._extract_coefficient(term)
            elements = self.formula_parser.parse(formula)
            for i, elem in enumerate(elements_list):
                if elem in elements:
                    matrix[i][j] = elements[elem]

        for j, term in enumerate(products):
            coeff, formula = self._extract_coefficient(term)
            elements = self.formula_parser.parse(formula)
            for i, elem in enumerate(elements_list):
                if elem in elements:
                    matrix[i][j + len(reactants)] = -elements[elem]

        # 使用高斯消元求解零空间
        coefficients = self._solve_null_space(matrix)

        if coefficients is None:
            raise ValueError("Cannot balance this equation")

        # 转换为整数系数
        coefficients = self._to_integer_coefficients(coefficients)

        # 构建平衡后的方程式
        balanced_reactants = []
        for j, term in enumerate(reactants):
            coeff, formula = self._extract_coefficient(term)
            new_coeff = int(coefficients[j])
            if new_coeff == 1:
                balanced_reactants.append(formula)
            else:
                balanced_reactants.append(f"{new_coeff}{formula}")

        balanced_products = []
        for j, term in enumerate(products):
            coeff, formula = self._extract_coefficient(term)
            new_coeff = int(coefficients[j + len(reactants)])
            if new_coeff == 1:
                balanced_products.append(formula)
            else:
                balanced_products.append(f"{new_coeff}{formula}")

        # 保留原始分隔符
        separator = self._get_separator(equation)
        return ' + '.join(balanced_reactants) + f' {separator} ' + ' + '.join(balanced_products)

    def _extract_coefficient(self, term: str) -> Tuple[int, str]:
        """提取化学式前的系数"""
        match = re.match(r'^(\d+)\s*(.+)$', term.strip())
        if match:
            return int(match.group(1)), match.group(2)
        return 1, term.strip()

    def _get_separator(self, equation: str) -> str:
        """获取方程式中的分隔符"""
        separators = ['->', '→', '⟶', '<=>', '⇌', '⇋']
        for sep in separators:
            if sep in equation:
                return sep
        return '->'

    def _solve_null_space(self, matrix: np.ndarray) -> Optional[np.ndarray]:
        """
        使用高斯消元求解矩阵的零空间

        Args:
            matrix: 系数矩阵 (元素数 x 化合物数)

        Returns:
            零空间基向量，或 None 如果无解
        """
        # 矩阵形状：元素数 x 化合物数
        num_elements, num_compounds = matrix.shape

        # 创建增广矩阵 [A | 0]
        A = matrix.copy().astype(float)

        # 高斯消元（行简化）
        pivot_cols = []
        pivot_row = 0

        for col in range(num_compounds):
            # 找主元
            found = False
            for row in range(pivot_row, num_elements):
                if abs(A[row, col]) > 1e-10:
                    # 交换行
                    A[[pivot_row, row]] = A[[row, pivot_row]]
                    found = True
                    break

            if not found:
                continue

            # 归一化
            pivot_val = A[pivot_row, col]
            A[pivot_row] = A[pivot_row] / pivot_val

            # 消元
            for row in range(num_elements):
                if row != pivot_row and abs(A[row, col]) > 1e-10:
                    factor = A[row, col]
                    A[row] = A[row] - factor * A[pivot_row]

            pivot_cols.append(col)
            pivot_row += 1

        # 找自由变量（非主元列）
        free_vars = [i for i in range(num_compounds) if i not in pivot_cols]

        if not free_vars:
            return None

        # 构建零空间基向量
        solution = np.zeros(num_compounds)
        free_var_idx = free_vars[0]
        solution[free_var_idx] = 1.0

        # 回代求解主元变量
        for i, col in enumerate(pivot_cols):
            # 从简化行阶梯形中读取系数
            solution[col] = -A[i, free_var_idx]

        return solution

    def _to_integer_coefficients(self, coefficients: np.ndarray) -> np.ndarray:
        """
        将浮点系数转换为最小整数系数

        Args:
            coefficients: 浮点系数数组

        Returns:
            整数系数数组
        """
        # 转换为分数
        fractions = [Fraction(c).limit_denominator(1000) for c in coefficients]

        # 找最小公倍数
        denominators = [f.denominator for f in fractions]
        lcm = denominators[0]
        for d in denominators[1:]:
            lcm = lcm * d // self._gcd(lcm, d)

        # 转换为整数
        int_coefficients = np.array([int(f * lcm) for f in fractions])

        # 确保所有系数为正
        if np.any(int_coefficients < 0):
            int_coefficients = -int_coefficients

        # 约分
        gcd = int(np.gcd.reduce(np.abs(int_coefficients)))
        if gcd > 0:
            int_coefficients = int_coefficients // gcd

        return int_coefficients

    def _gcd(self, a: int, b: int) -> int:
        """计算最大公约数"""
        while b:
            a, b = b, a % b
        return a

    def is_balanced(self, equation: str) -> bool:
        """
        检查方程式是否已平衡

        Args:
            equation: 化学方程式

        Returns:
            是否平衡
        """
        reactant_counts, product_counts = self.reaction_parser.get_element_counts(equation)
        return reactant_counts == product_counts


class ReactionEngine:
    """反应引擎（高级接口）"""

    def __init__(self):
        self.balancer = EquationBalancer()
        self.reaction_parser = ReactionParser()
        self.formula_parser = FormulaParser()

    def process_equation(self, equation: str) -> Dict:
        """
        处理化学方程式

        Args:
            equation: 输入的方程式

        Returns:
            处理结果字典
        """
        result = {
            'original': equation,
            'balanced': None,
            'is_balanced': False,
            'subscript': None,
            'latex': None,
            'elements': {}
        }

        try:
            # 检查是否已平衡
            result['is_balanced'] = self.balancer.is_balanced(equation)

            # 平衡方程式
            if not result['is_balanced']:
                result['balanced'] = self.balancer.balance(equation)
            else:
                result['balanced'] = equation

            # 转换为下标格式
            result['subscript'] = self.reaction_parser.to_subscript(result['balanced'])

            # 转换为 LaTeX 格式
            result['latex'] = self.reaction_parser.to_latex(result['balanced'])

            # 获取元素信息
            reactant_counts, product_counts = self.reaction_parser.get_element_counts(result['balanced'])
            result['elements'] = {
                'reactants': reactant_counts,
                'products': product_counts
            }

        except Exception as e:
            result['error'] = str(e)

        return result

    def format_for_word(self, equation: str) -> str:
        """
        格式化为 Word 可用的格式（Unicode 下标）

        Args:
            equation: 化学方程式

        Returns:
            带 Unicode 下标的方程式
        """
        balanced = self.balancer.balance(equation)
        return self.reaction_parser.to_subscript(balanced)

    def format_for_latex(self, equation: str, package: str = "mhchem") -> str:
        """
        格式化为 LaTeX 格式

        Args:
            equation: 化学方程式
            package: LaTeX 包格式

        Returns:
            LaTeX 格式的方程式
        """
        balanced = self.balancer.balance(equation)
        return self.reaction_parser.to_latex(balanced, package)


# 便捷函数
def balance_equation(equation: str) -> str:
    """平衡化学方程式"""
    balancer = EquationBalancer()
    return balancer.balance(equation)


def format_equation(equation: str, format_type: str = "subscript") -> str:
    """
    格式化方程式

    Args:
        equation: 化学方程式
        format_type: 格式类型 ("subscript", "latex", "mhchem")

    Returns:
        格式化后的方程式
    """
    engine = ReactionEngine()

    if format_type == "subscript":
        return engine.format_for_word(equation)
    elif format_type == "latex":
        return engine.format_for_latex(equation, "standard")
    elif format_type == "mhchem":
        return engine.format_for_latex(equation, "mhchem")
    else:
        raise ValueError(f"Unknown format type: {format_type}")
