"""
ChemMaster 化学模块测试
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.chemistry import FormulaParser, ReactionParser
from backend.app.core.reaction_engine import EquationBalancer


def test_formula_parser():
    """测试化学式解析器"""
    parser = FormulaParser()

    # 测试简单化学式
    assert parser.parse('H2O') == {'H': 2, 'O': 1}
    assert parser.parse('H2SO4') == {'H': 2, 'S': 1, 'O': 4}
    assert parser.parse('NaCl') == {'Na': 1, 'Cl': 1}

    # 测试带括号的化学式
    assert parser.parse('Ca(OH)2') == {'Ca': 1, 'O': 2, 'H': 2}
    assert parser.parse('Mg(OH)2') == {'Mg': 1, 'O': 2, 'H': 2}

    # 测试下标转换
    assert parser.to_subscript('H2O') == 'H₂O'
    assert parser.to_subscript('H2SO4') == 'H₂SO₄'
    assert parser.to_subscript('Ca(OH)2') == 'Ca(OH)₂'
    assert parser.to_subscript('NH4+') == 'NH₄⁺'

    # 测试 LaTeX 转换
    assert parser.to_latex('H2O', 'mhchem') == '\\ce{H2O}'
    assert parser.to_latex('H2SO4', 'mhchem') == '\\ce{H2SO4}'

    print('[PASS] Formula parser tests passed')


def test_reaction_parser():
    """测试反应方程式解析器"""
    parser = ReactionParser()

    # 测试方程式解析
    reactants, products = parser.parse_equation('H2 + O2 -> H2O')
    assert reactants == ['H2', 'O2']
    assert products == ['H2O']

    # 测试元素计数
    reactant_counts, product_counts = parser.get_element_counts('2H2 + O2 -> 2H2O')
    assert reactant_counts == {'H': 4, 'O': 2}
    assert product_counts == {'H': 4, 'O': 2}

    print('[PASS] Reaction parser tests passed')


def test_equation_balancer():
    """测试方程式平衡器"""
    balancer = EquationBalancer()

    # 测试简单平衡
    assert balancer.balance('Fe + O2 -> Fe2O3') == '4Fe + 3O2 -> 2Fe2O3'
    assert balancer.balance('H2 + O2 -> H2O') == '2H2 + O2 -> 2H2O'

    # 测试已平衡的方程式
    assert balancer.is_balanced('2H2 + O2 -> 2H2O') == True
    assert balancer.is_balanced('H2 + O2 -> H2O') == False

    print('[PASS] Equation balancer tests passed')


def test_format_conversion():
    """测试格式转换"""
    parser = FormulaParser()

    # 测试多种化学式
    formulas = [
        ('H2O', 'H₂O', '\\ce{H2O}'),
        ('CO2', 'CO₂', '\\ce{CO2}'),
        ('NaCl', 'NaCl', '\\ce{NaCl}'),
        ('CaCO3', 'CaCO₃', '\\ce{CaCO3}'),
        ('H2SO4', 'H₂SO₄', '\\ce{H2SO4}'),
        ('NaOH', 'NaOH', '\\ce{NaOH}'),
    ]

    for formula, expected_subscript, expected_latex in formulas:
        assert parser.to_subscript(formula) == expected_subscript, f"Failed for {formula}"
        assert parser.to_latex(formula, 'mhchem') == expected_latex, f"Failed for {formula}"

    print('[PASS] Format conversion tests passed')


def main():
    """运行所有测试"""
    print('Running ChemMaster chemistry tests...\n')

    try:
        test_formula_parser()
        test_reaction_parser()
        test_equation_balancer()
        test_format_conversion()

        print('\n[PASS] All tests passed!')
        return 0
    except AssertionError as e:
        print(f'\n[FAIL] Test failed: {e}')
        return 1
    except Exception as e:
        print(f'\n[ERROR] Error: {e}')
        return 1


if __name__ == '__main__':
    exit(main())
