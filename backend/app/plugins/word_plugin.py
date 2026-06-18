"""
ChemMaster Word 导出插件
支持 Unicode 下标格式和 Office.js 集成
"""

from typing import Dict, List, Optional
from ..core.chemistry import FormulaParser, ReactionParser
from ..core.reaction_engine import EquationBalancer, ReactionEngine


class WordExporter:
    """Word 导出器"""

    def __init__(self):
        self.formula_parser = FormulaParser()
        self.reaction_parser = ReactionParser()
        self.reaction_engine = ReactionEngine()

    def formula_to_word(self, formula: str) -> str:
        """
        将化学式转换为 Word 可用的 Unicode 下标格式

        Args:
            formula: 化学式，如 "H2SO4"

        Returns:
            Unicode 下标格式，如 "H₂SO₄"
        """
        return self.formula_parser.to_subscript(formula)

    def equation_to_word(self, equation: str, balance: bool = True) -> str:
        """
        将化学方程式转换为 Word 可用的格式

        Args:
            equation: 化学方程式
            balance: 是否自动平衡

        Returns:
            Unicode 下标格式的方程式
        """
        if balance:
            return self.reaction_engine.format_for_word(equation)
        else:
            return self.reaction_parser.to_subscript(equation)

    def generate_word_content(self, equations: List[str], balance: bool = True) -> str:
        """
        生成可直接粘贴到 Word 的内容

        Args:
            equations: 方程式列表
            balance: 是否自动平衡

        Returns:
            Word 可用的内容字符串
        """
        content_lines = []
        for i, eq in enumerate(equations, 1):
            formatted = self.equation_to_word(eq, balance)
            content_lines.append(f"{i}. {formatted}")

        return "\n".join(content_lines)

    def generate_html_content(self, equations: List[str], balance: bool = True) -> str:
        """
        生成 HTML 格式的内容（可在 Word 中粘贴）

        Args:
            equations: 方程式列表
            balance: 是否自动平衡

        Returns:
            HTML 格式字符串
        """
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Times New Roman', serif; }
        .equation { margin: 10px 0; font-size: 14pt; }
        .number { font-weight: bold; margin-right: 10px; }
    </style>
</head>
<body>
    <h2>化学反应方程式</h2>
"""

        for i, eq in enumerate(equations, 1):
            formatted = self.equation_to_word(eq, balance)
            html += f'    <div class="equation"><span class="number">{i}.</span>{formatted}</div>\n'

        html += """</body>
</html>"""

        return html

    def generate_rtf_content(self, equations: List[str], balance: bool = True) -> str:
        """
        生成 RTF 格式的内容（Word 原生格式）

        Args:
            equations: 方程式列表
            balance: 是否自动平衡

        Returns:
            RTF 格式字符串
        """
        rtf = """{\\rtf1\\ansi\\deff0
{\\fonttbl{\\f0 Times New Roman;}}
{\\colortbl;\\red0\\green0\\blue0;}
\\f0\\fs24
"""

        for i, eq in enumerate(equations, 1):
            formatted = self.equation_to_word(eq, balance)
            rtf += f"{i}. {formatted}\\par\n"

        rtf += "}"

        return rtf

    def generate_office_js_code(self, formula: str) -> str:
        """
        生成 Office.js 插入代码

        Args:
            formula: 化学式

        Returns:
            Office.js 代码字符串
        """
        formatted = self.formula_to_word(formula)

        return f"""
// Office.js 代码 - 插入化学式到 Word
async function insertFormula() {{
    await Word.run(async (context) => {{
        const body = context.document.body;
        body.insertParagraph("{formatted}", Word.InsertLocation.end);
        await context.sync();
    }});
}}

// 调用
insertFormula();
"""


def export_formula_to_word(formula: str) -> Dict:
    """
    导出化学式到 Word 格式

    Args:
        formula: 化学式

    Returns:
        包含各种格式的字典
    """
    exporter = WordExporter()

    return {
        'original': formula,
        'unicode': exporter.formula_to_word(formula),
        'html': f'<span>{exporter.formula_to_word(formula)}</span>',
        'office_js': exporter.generate_office_js_code(formula)
    }


def export_equation_to_word(equation: str, balance: bool = True) -> Dict:
    """
    导出方程式到 Word 格式

    Args:
        equation: 化学方程式
        balance: 是否自动平衡

    Returns:
        包含各种格式的字典
    """
    exporter = WordExporter()

    return {
        'original': equation,
        'unicode': exporter.equation_to_word(equation, balance),
        'balanced': balance,
        'html': exporter.generate_html_content([equation], balance),
        'rtf': exporter.generate_rtf_content([equation], balance)
    }
