"""
ChemMaster 离子方程式 API
支持离子方程式配平、分子方程式→离子方程式转换、离子分析
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from ..core.ion_engine import (
    balance_ion_equation,
    convert_to_ionic,
    parse_ion,
    IonParser,
    IonEquationBalancer,
    MolecularToIonicConverter,
)

router = APIRouter(prefix="/api/ion", tags=["ion"])

# 初始化引擎
ion_parser = IonParser()
ion_balancer = IonEquationBalancer()
converter = MolecularToIonicConverter()


# ====== 请求模型 ======

class IonEquationRequest(BaseModel):
    """离子方程式请求"""
    equation: str           # 离子方程式，如 "H+ + OH- -> H2O"
    format: str = "mhchem"  # 输出格式


class MolecularToIonRequest(BaseModel):
    """分子方程式→离子方程式转换请求"""
    equation: str           # 分子方程式，如 "NaOH + HCl -> NaCl + H2O"


class IonAnalysisRequest(BaseModel):
    """离子分析请求"""
    equation: str           # 方程式（分子或离子）


# ====== 响应模型 ======

class IonBalanceResponse(BaseModel):
    """离子配平响应"""
    original: str
    balanced: str
    unicode: str
    latex: str
    is_balanced: bool
    charge_balanced: bool
    reactant_charges: int
    product_charges: int


class IonConvertResponse(BaseModel):
    """离子转换响应"""
    original: str
    full_ionic: str
    net_ionic: str
    spectator_ions: List[str]
    balanced_molecular: str


class IonInfoResponse(BaseModel):
    """离子信息响应"""
    formula: str
    symbol: str
    charge: int
    is_cation: bool
    unicode: str
    latex: str


# ====== API 端点 ======

@router.post("/balance", response_model=IonBalanceResponse)
async def balance_ion(request: IonEquationRequest):
    """
    配平离子方程式

    支持格式：
    - H+ + OH- -> H2O
    - Fe + Cu^2+ -> Fe^2+ + Cu
    - MnO4- + H+ + Fe^2+ -> Mn^2+ + Fe^3+ + H2O
    """
    try:
        equation = request.equation.strip()
        result = balance_ion_equation(equation)

        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        return IonBalanceResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/convert", response_model=IonConvertResponse)
async def convert_molecular_to_ion(request: MolecularToIonRequest):
    """
    将分子方程式转换为离子方程式

    自动拆分强电解质，识别旁观离子，生成净离子方程式。

    示例：
    - NaOH + HCl -> NaCl + H2O → H+ + OH- = H2O
    - Na2SO4 + BaCl2 -> BaSO4 + 2NaCl → Ba^2+ + SO4^2- = BaSO4
    """
    try:
        equation = request.equation.strip()
        result = convert_to_ionic(equation)

        return IonConvertResponse(
            original=result.original,
            full_ionic=result.full_ionic,
            net_ionic=result.net_ionic,
            spectator_ions=result.spectator_ions,
            balanced_molecular=result.balanced_molecular,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/analyze")
async def analyze_ion(request: IonAnalysisRequest):
    """
    分析方程式中的离子

    返回：
    - 离子列表及电荷
    - 旁观离子
    - 完整离子方程式
    - 净离子方程式
    - 电荷守恒验证
    """
    try:
        equation = request.equation.strip()

        # 判断是离子方程式还是分子方程式
        has_ion = any(c in equation for c in ['+', '-']) and not equation.startswith('2') and not equation.startswith('3')

        # 尝试转换
        try:
            result = convert_to_ionic(equation)
            return {
                "type": "molecular",
                "original": equation,
                "full_ionic": result.full_ionic,
                "net_ionic": result.net_ionic,
                "spectator_ions": result.spectator_ions,
                "balanced_molecular": result.balanced_molecular,
            }
        except:
            pass

        # 尝试作为离子方程式配平
        try:
            result = balance_ion_equation(equation)
            if 'error' not in result:
                return {
                    "type": "ionic",
                    "original": equation,
                    "balanced": result['balanced'],
                    "unicode": result['unicode'],
                    "latex": result['latex'],
                    "charge_balanced": result['charge_balanced'],
                    "reactant_charges": result['reactant_charges'],
                    "product_charges": result['product_charges'],
                }
        except:
            pass

        raise HTTPException(status_code=400, detail="无法解析该方程式")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/info/{ion_str}")
async def get_ion_info(ion_str: str):
    """
    获取离子信息

    示例：/api/ion/info/H+ → {symbol: "H", charge: 1, ...}
    """
    try:
        ion = parse_ion(ion_str)

        return IonInfoResponse(
            formula=ion.formula,
            symbol=ion.symbol,
            charge=ion.charge,
            is_cation=ion.is_cation,
            unicode=ion_parser.to_unicode(ion),
            latex=ion_parser.to_latex(ion),
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"无法解析离子: {ion_str}")
