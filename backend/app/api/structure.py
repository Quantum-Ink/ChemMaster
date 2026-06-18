"""
ChemMaster 结构处理 API
提供化学结构的验证、渲染和导出功能
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List

from ..core.rdkit_engine import (
    validate_smiles,
    get_mol_info,
    smiles_to_svg,
    smiles_to_png_base64,
    smiles_to_chemfig,
    get_common_structures
)

router = APIRouter(prefix="/api/structure", tags=["structure"])


# 请求模型
class SmilesRequest(BaseModel):
    smiles: str


class RenderRequest(BaseModel):
    smiles: str
    width: int = 400
    height: int = 300
    show_atom_indices: bool = False


class ExportRequest(BaseModel):
    smiles: str
    format: str = "svg"  # svg, png, latex
    width: int = 400
    height: int = 300


# 响应模型
class ValidationResult(BaseModel):
    valid: bool
    smiles: Optional[str] = None
    canonical_smiles: Optional[str] = None
    error: Optional[str] = None


class MolInfoResult(BaseModel):
    valid: bool
    canonical_smiles: Optional[str] = None
    formula: Optional[str] = None
    molecular_weight: Optional[float] = None
    num_atoms: Optional[int] = None
    num_bonds: Optional[int] = None
    num_rings: Optional[int] = None
    is_aromatic: Optional[bool] = None
    atoms: Optional[List[dict]] = None
    bonds: Optional[List[dict]] = None
    error: Optional[str] = None


class ExportResult(BaseModel):
    format: str
    data: str
    smiles: str
    canonical_smiles: str


@router.post("/validate", response_model=ValidationResult)
async def validate(request: SmilesRequest):
    """
    验证 SMILES 字符串是否有效

    Args:
        smiles: SMILES 字符串

    Returns:
        验证结果
    """
    try:
        smiles = request.smiles.strip()
        if not smiles:
            return ValidationResult(valid=False, error="Empty SMILES")

        is_valid = validate_smiles(smiles)

        if is_valid:
            from ..core.rdkit_engine import rdkit_engine
            canonical = rdkit_engine.get_canonical_smiles(smiles)
            return ValidationResult(
                valid=True,
                smiles=smiles,
                canonical_smiles=canonical
            )
        else:
            return ValidationResult(valid=False, error="Invalid SMILES")

    except Exception as e:
        return ValidationResult(valid=False, error=str(e))


@router.post("/info", response_model=MolInfoResult)
async def get_info(request: SmilesRequest):
    """
    获取分子信息

    Args:
        smiles: SMILES 字符串

    Returns:
        分子信息
    """
    try:
        smiles = request.smiles.strip()
        info = get_mol_info(smiles)

        if "error" in info:
            return MolInfoResult(valid=False, error=info["error"])

        return MolInfoResult(**info)

    except Exception as e:
        return MolInfoResult(valid=False, error=str(e))


@router.post("/render/svg")
async def render_svg(request: RenderRequest):
    """
    渲染 SVG 格式的分子结构图

    Args:
        smiles: SMILES 字符串
        width: 图片宽度
        height: 图片高度
        show_atom_indices: 是否显示原子索引

    Returns:
        SVG 图片
    """
    try:
        smiles = request.smiles.strip()
        svg = smiles_to_svg(
            smiles,
            width=request.width,
            height=request.height,
            show_atom_indices=request.show_atom_indices
        )

        if svg is None:
            raise HTTPException(status_code=400, detail="Failed to render SVG")

        return Response(content=svg, media_type="image/svg+xml")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/render/png")
async def render_png(request: RenderRequest):
    """
    渲染 PNG 格式的分子结构图

    Args:
        smiles: SMILES 字符串
        width: 图片宽度
        height: 图片高度

    Returns:
        PNG 图片（base64 编码）
    """
    try:
        smiles = request.smiles.strip()
        png_base64 = smiles_to_png_base64(
            smiles,
            width=request.width,
            height=request.height
        )

        if png_base64 is None:
            raise HTTPException(status_code=400, detail="Failed to render PNG")

        return {
            "format": "png",
            "data": png_base64,
            "mime": "image/png"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export", response_model=ExportResult)
async def export(request: ExportRequest):
    """
    导出分子结构

    Args:
        smiles: SMILES 字符串
        format: 导出格式 (svg, png, latex)
        width: 图片宽度（SVG/PNG）
        height: 图片高度（SVG/PNG）

    Returns:
        导出结果
    """
    try:
        smiles = request.smiles.strip()

        # 验证 SMILES
        if not validate_smiles(smiles):
            raise HTTPException(status_code=400, detail="Invalid SMILES")

        # 获取规范化的 SMILES
        from ..core.rdkit_engine import rdkit_engine
        canonical = rdkit_engine.get_canonical_smiles(smiles)

        # 根据格式导出
        if request.format == "svg":
            data = smiles_to_svg(smiles, request.width, request.height)
            if data is None:
                raise HTTPException(status_code=400, detail="Failed to generate SVG")
        elif request.format == "png":
            data = smiles_to_png_base64(smiles, request.width, request.height)
            if data is None:
                raise HTTPException(status_code=400, detail="Failed to generate PNG")
        elif request.format == "latex":
            data = smiles_to_chemfig(smiles)
            if data is None:
                raise HTTPException(status_code=400, detail="Failed to generate LaTeX")
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")

        return ExportResult(
            format=request.format,
            data=data,
            smiles=smiles,
            canonical_smiles=canonical
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/common")
async def get_common():
    """
    获取常见有机物结构

    Returns:
        常见有机物字典
    """
    return get_common_structures()


@router.post("/batch/validate")
async def batch_validate(smiles_list: List[str]):
    """
    批量验证 SMILES

    Args:
        smiles_list: SMILES 列表

    Returns:
        验证结果列表
    """
    results = []
    for smiles in smiles_list:
        is_valid = validate_smiles(smiles.strip())
        results.append({
            "smiles": smiles,
            "valid": is_valid
        })
    return results


@router.post("/batch/info")
async def batch_info(smiles_list: List[str]):
    """
    批量获取分子信息

    Args:
        smiles_list: SMILES 列表

    Returns:
        分子信息列表
    """
    results = []
    for smiles in smiles_list:
        info = get_mol_info(smiles.strip())
        results.append(info)
    return results


# ========== 3D 结构端点 ==========

class Smiles3DRequest(BaseModel):
    smiles: str


class PubChem3DRequest(BaseModel):
    name: str


class SDF3DResult(BaseModel):
    sdf: str
    smiles: Optional[str] = None
    formula: Optional[str] = None
    info: Optional[dict] = None


@router.post("/3d", response_model=SDF3DResult)
async def get_3d_structure(request: Smiles3DRequest):
    """
    从 SMILES 生成 3D SDF 结构

    Args:
        smiles: SMILES 字符串

    Returns:
        3D SDF 数据
    """
    try:
        smiles = request.smiles.strip()
        if not smiles:
            raise HTTPException(status_code=400, detail="Empty SMILES")

        from ..core.rdkit_engine import rdkit_engine
        from ..core.molecule_renderer import molecule_renderer

        # 验证 SMILES
        if not rdkit_engine.validate_smiles(smiles):
            raise HTTPException(status_code=400, detail="Invalid SMILES")

        # 生成 3D SDF
        sdf = molecule_renderer.smiles_to_3d_sdf(smiles)
        if sdf is None:
            raise HTTPException(status_code=500, detail="Failed to generate 3D structure")

        # 获取分子信息
        info = rdkit_engine.get_mol_info(smiles)
        canonical = rdkit_engine.get_canonical_smiles(smiles)

        return SDF3DResult(
            sdf=sdf,
            smiles=canonical,
            formula=info.get('formula', ''),
            info={
                'formula': info.get('formula', ''),
                'molecular_weight': info.get('molecular_weight', 0),
                'num_atoms': info.get('num_atoms', 0),
                'num_bonds': info.get('num_bonds', 0),
                'num_rings': info.get('num_rings', 0),
                'is_aromatic': info.get('is_aromatic', False)
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pubchem/3d")
async def get_pubchem_3d(request: PubChem3DRequest):
    """
    从 PubChem 获取化合物 3D 结构

    Args:
        name: 化合物名称（英文）

    Returns:
        3D SDF 数据 + 化合物信息
    """
    try:
        name = request.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Empty compound name")

        from ..core.pubchem_api import pubchem_api

        # 搜索化合物
        compound = pubchem_api.search_by_name(name)
        if compound is None:
            raise HTTPException(status_code=404, detail=f"Compound not found: {name}")

        # 获取 3D 结构
        sdf = pubchem_api.get_3d_structure(compound.cid)
        if sdf is None:
            raise HTTPException(status_code=404, detail="3D structure not available from PubChem")

        return {
            "sdf": sdf,
            "name": compound.iupac_name or name,
            "smiles": compound.smiles,
            "formula": compound.molecular_formula,
            "info": {
                "formula": compound.molecular_formula,
                "molecular_weight": compound.molecular_weight,
                "iupac_name": compound.iupac_name,
                "num_atoms": None,
                "description": compound.description[:200] if compound.description else ""
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pubchem/search/{name}")
async def pubchem_search(name: str):
    """
    搜索 PubChem 化合物

    Args:
        name: 化合物名称

    Returns:
        化合物信息
    """
    try:
        from ..core.pubchem_api import pubchem_api

        compound = pubchem_api.search_by_name(name)
        if compound is None:
            raise HTTPException(status_code=404, detail=f"Compound not found: {name}")

        return {
            "cid": compound.cid,
            "name": compound.iupac_name or name,
            "smiles": compound.smiles,
            "formula": compound.molecular_formula,
            "molecular_weight": compound.molecular_weight,
            "description": compound.description[:200] if compound.description else "",
            "synonyms": compound.synonyms[:5] if compound.synonyms else []
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
