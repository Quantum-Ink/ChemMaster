"""
ChemMaster LaTeX 导出插件
支持 mhchem 包和标准 LaTeX 格式
"""

from typing import Dict, List, Optional
from ..core.chemistry import FormulaParser, ReactionParser
from ..core.reaction_engine import EquationBalancer, ReactionEngine


class LatexExporter:
    """LaTeX 导出器"""

    def __init__(self):
        self.formula_parser = FormulaParser()
        self.reaction_parser = ReactionParser()
        self.reaction_engine = ReactionEngine()

    def formula_to_latex(self, formula: str, package: str = "mhchem") -> str:
        """
        将化学式转换为 LaTeX 格式

        Args:
            formula: 化学式，如 "H2SO4"
            package: LaTeX 包格式 ("mhchem" 或 "standard")

        Returns:
            LaTeX 格式字符串
        """
        return self.formula_parser.to_latex(formula, package)

    def equation_to_latex(self, equation: str, package: str = "mhchem", balance: bool = True) -> str:
        """
        将化学方程式转换为 LaTeX 格式

        Args:
            equation: 化学方程式
            package: LaTeX 包格式
            balance: 是否自动平衡

        Returns:
            LaTeX 格式字符串
        """
        if balance:
            return self.reaction_engine.format_for_latex(equation, package)
        else:
            return self.reaction_parser.to_latex(equation, package)

    def generate_latex_document(self, content: str, title: str = "Chemical Formulas") -> str:
        """
        生成完整的 LaTeX 文档

        Args:
            content: LaTeX 内容
            title: 文档标题

        Returns:
            完整的 LaTeX 文档字符串
        """
        return f"""\\documentclass{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath}}
\\usepackage{{mhchem}}

\\title{{{title}}}
\\author{{ChemMaster}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

{content}

\\end{{document}}"""

    def generate_reaction_table(self, equations: List[str], balance: bool = True) -> str:
        """
        生成反应方程式表格

        Args:
            equations: 方程式列表
            balance: 是否自动平衡

        Returns:
            LaTeX 表格字符串
        """
        latex_table = """\\begin{{table}}[h]
\\centering
\\begin{{tabular}}{{|c|c|c|}}
\\hline
\\textbf{{序号}} & \\textbf{{原始方程式}} & \\textbf{{平衡后}} \\\\
\\hline
"""

        for i, eq in enumerate(equations, 1):
            original_latex = self.reaction_parser.to_latex(eq, "mhchem")
            if balance:
                balanced_latex = self.reaction_engine.format_for_latex(eq, "mhchem")
            else:
                balanced_latex = original_latex

            latex_table += f"{i} & $${original_latex}$$ & $${balanced_latex}$$ \\\\\\\\\n\\hline\n"

        latex_table += """\\end{tabular}
\\caption{化学反应方程式}
\\end{table}"""

        return latex_table

    def generate_mhchem_package(self) -> str:
        """
        生成 mhchem 包的使用说明

        Returns:
            mhchem 包使用示例
        """
        return """% mhchem 包使用示例
% 在导言区添加：\\usepackage{mhchem}

% 基本化学式
\\ce{H2O}          % 水
\\ce{H2SO4}        % 硫酸
\\ce{NaCl}         % 氯化钠

% 带下标的化学式
\\ce{CO2}          % 二氧化碳
\\ce{C6H12O6}      % 葡萄糖

% 离子
\\ce{H+}           % 氢离子
\\ce{OH-}          % 氢氧根离子
\\ce{SO4^2-}       % 硫酸根离子
\\ce{NH4+}         % 铵根离子

% 反应方程式
\\ce{2H2 + O2 -> 2H2O}           % 燃烧反应
\\ce{HCl + NaOH -> NaCl + H2O}  % 中和反应
\\ce{Fe + CuSO4 -> FeSO4 + Cu}  % 置换反应

% 可逆反应
\\ce{N2 + 3H2 <=> 2NH3}         % 合成氨

% 气体和沉淀
\\ce{CaCO3 v}                    % 沉淀
\\ce{CO2 ^}                      % 气体

% 条件
\\ce{2H2O ->[\\text{电解}] 2H2 + O2}  % 电解水"""


def export_formula_to_latex(formula: str, package: str = "mhchem") -> Dict:
    """
    导出化学式到 LaTeX 格式

    Args:
        formula: 化学式
        package: LaTeX 包格式

    Returns:
        包含 LaTeX 代码的字典
    """
    exporter = LatexExporter()

    return {
        'original': formula,
        'latex': exporter.formula_to_latex(formula, package),
        'package': package,
        'usage': f'$${exporter.formula_to_latex(formula, package)}$$'
    }


def export_equation_to_latex(equation: str, package: str = "mhchem", balance: bool = True) -> Dict:
    """
    导出方程式到 LaTeX 格式

    Args:
        equation: 化学方程式
        package: LaTeX 包格式
        balance: 是否自动平衡

    Returns:
        包含 LaTeX 代码的字典
    """
    exporter = LatexExporter()

    return {
        'original': equation,
        'latex': exporter.equation_to_latex(equation, package, balance),
        'package': package,
        'balanced': balance,
        'usage': f'$${exporter.equation_to_latex(equation, package, balance)}$$'
    }
