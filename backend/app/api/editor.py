from fastapi import APIRouter
from app.core.rdkit_engine import mol_info, mol_svg
from app.core.chemistry import parse_formula

router = APIRouter()

# ======================
# 分子分析（V9）
# ======================
@router.get("/editor/analyze")
def analyze(smiles: str):
    return mol_info(smiles)

# ======================
# SVG结构（V8/V11）
# ======================
@router.get("/editor/svg")
def svg(smiles: str):
    return {"svg": mol_svg(smiles)}

# ======================
# 化学式解析（V1）
# ======================
@router.get("/editor/formula")
def formula(q: str):
    return parse_formula(q)