"""
ChemMaster 导出 API 端点
支持 LaTeX 和 Word 格式导出
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from ..core.chemistry import FormulaParser
from ..core.reaction_engine import ReactionEngine
from ..plugins.latex_plugin import LatexExporter
from ..plugins.word_plugin import WordExporter

router = APIRouter(prefix="/api/export", tags=["export"])


# 请求模型
class FormulaRequest(BaseModel):
    formula: str
    format: str = "mhchem"  # mhchem, standard


class EquationRequest(BaseModel):
    equation: str
    format: str = "mhchem"
    balance: bool = True


class BatchRequest(BaseModel):
    equations: List[str]
    format: str = "mhchem"
    balance: bool = True


# 响应模型
class FormulaResponse(BaseModel):
    original: str
    unicode: str
    latex: str
    format: str


class EquationResponse(BaseModel):
    original: str
    balanced: str
    unicode: str
    latex: str
    format: str
    is_balanced: bool


class BatchResponse(BaseModel):
    results: List[EquationResponse]
    count: int


# 初始化引擎
formula_parser = FormulaParser()
reaction_engine = ReactionEngine()
latex_exporter = LatexExporter()
word_exporter = WordExporter()


@router.post("/formula", response_model=FormulaResponse)
async def export_formula(request: FormulaRequest):
    """
    导出化学式

    Args:
        formula: 化学式，如 "H2SO4"
        format: 输出格式 ("mhchem", "standard")

    Returns:
        包含各种格式的响应
    """
    try:
        formula = request.formula.strip()

        # 解析化学式
        elements = formula_parser.parse(formula)

        # 转换格式
        unicode_format = formula_parser.to_subscript(formula)
        latex_format = formula_parser.to_latex(formula, request.format)

        return FormulaResponse(
            original=formula,
            unicode=unicode_format,
            latex=latex_format,
            format=request.format
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/equation", response_model=EquationResponse)
async def export_equation(request: EquationRequest):
    """
    导出化学方程式

    Args:
        equation: 化学方程式，如 "Fe + O2 -> Fe2O3"
        format: 输出格式
        balance: 是否自动平衡

    Returns:
        包含各种格式的响应
    """
    try:
        equation = request.equation.strip()

        # 处理方程式
        result = reaction_engine.process_equation(equation)

        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        return EquationResponse(
            original=result['original'],
            balanced=result['balanced'],
            unicode=result['subscript'],
            latex=result['latex'],
            format=request.format,
            is_balanced=result['is_balanced']
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/batch", response_model=BatchResponse)
async def export_batch(request: BatchRequest):
    """
    批量导出方程式

    Args:
        equations: 方程式列表
        format: 输出格式
        balance: 是否自动平衡

    Returns:
        批量处理结果
    """
    try:
        results = []

        for equation in request.equations:
            equation = equation.strip()
            if not equation:
                continue

            result = reaction_engine.process_equation(equation)

            if 'error' not in result:
                results.append(EquationResponse(
                    original=result['original'],
                    balanced=result['balanced'],
                    unicode=result['subscript'],
                    latex=result['latex'],
                    format=request.format,
                    is_balanced=result['is_balanced']
                ))

        return BatchResponse(
            results=results,
            count=len(results)
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/word/formula")
async def export_word_formula(request: FormulaRequest):
    """
    导出化学式到 Word 格式

    Returns:
        Word 可用的各种格式
    """
    try:
        formula = request.formula.strip()

        return {
            'original': formula,
            'unicode': word_exporter.formula_to_word(formula),
            'html': f'<span>{word_exporter.formula_to_word(formula)}</span>',
            'office_js': word_exporter.generate_office_js_code(formula)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/word/equation")
async def export_word_equation(request: EquationRequest):
    """
    导出方程式到 Word 格式

    Returns:
        Word 可用的各种格式
    """
    try:
        equation = request.equation.strip()

        return {
            'original': equation,
            'unicode': word_exporter.equation_to_word(equation, request.balance),
            'html': word_exporter.generate_html_content([equation], request.balance),
            'rtf': word_exporter.generate_rtf_content([equation], request.balance)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/latex/formula")
async def export_latex_formula(request: FormulaRequest):
    """
    导出化学式到 LaTeX 格式

    Returns:
        LaTeX 格式代码
    """
    try:
        formula = request.formula.strip()

        return {
            'original': formula,
            'latex': latex_exporter.formula_to_latex(formula, request.format),
            'package': request.format,
            'usage': f'$${latex_exporter.formula_to_latex(formula, request.format)}$$'
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/latex/equation")
async def export_latex_equation(request: EquationRequest):
    """
    导出方程式到 LaTeX 格式

    Returns:
        LaTeX 格式代码
    """
    try:
        equation = request.equation.strip()

        return {
            'original': equation,
            'latex': latex_exporter.equation_to_latex(equation, request.format, request.balance),
            'package': request.format,
            'balanced': request.balance,
            'usage': f'$${latex_exporter.equation_to_latex(equation, request.format, request.balance)}$$'
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/latex/document")
async def export_latex_document(request: BatchRequest):
    """
    生成完整的 LaTeX 文档

    Returns:
        完整的 LaTeX 文档代码
    """
    try:
        content_parts = []
        for eq in request.equations:
            eq = eq.strip()
            if eq:
                latex = latex_exporter.equation_to_latex(eq, request.format, request.balance)
                content_parts.append(f'$${latex}$$')

        content = "\n\n".join(content_parts)
        document = latex_exporter.generate_latex_document(content)

        return {
            'document': document,
            'equations': request.equations,
            'format': request.format
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
