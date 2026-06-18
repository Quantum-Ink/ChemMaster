"""
ChemMaster 编辑器 API 端点
提供化学式解析、分子信息查询和结构渲染功能
"""

from fastapi import APIRouter, HTTPException

from ..core.rdkit_engine import get_mol_info, smiles_to_svg, validate_smiles
from ..core.chemistry import parse_formula

router = APIRouter(prefix="/editor", tags=["editor"])


@router.get("/analyze")
def analyze(smiles: str):
    """分析分子结构，返回原子、键、分子量等信息"""
    if not validate_smiles(smiles):
        raise HTTPException(status_code=400, detail="Invalid SMILES")
    return get_mol_info(smiles)


@router.get("/svg")
def svg(smiles: str):
    """将 SMILES 转换为 SVG 矢量图"""
    result = smiles_to_svg(smiles)
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to render SVG")
    return {"svg": result}


@router.get("/formula")
def formula(q: str):
    """解析化学式，返回元素计数"""
    try:
        return parse_formula(q)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))