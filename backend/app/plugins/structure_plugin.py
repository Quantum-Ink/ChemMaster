"""
ChemMaster 结构导出插件
提供化学结构的多格式导出功能
"""

from typing import Dict, Optional, List
from ..core.rdkit_engine import (
    RDKitEngine,
    validate_smiles,
    get_mol_info,
    smiles_to_svg,
    smiles_to_png_base64,
    smiles_to_chemfig
)
from .base import ChemPlugin, PluginCategory, PluginEndpoint


class StructureExporter:
    """结构导出器"""

    def __init__(self):
        self.engine = RDKitEngine()

    def to_svg(self, smiles: str, width: int = 400, height: int = 300,
               show_atom_indices: bool = False) -> Dict:
        """
        导出为 SVG 格式

        Args:
            smiles: SMILES 字符串
            width: 图片宽度
            height: 图片高度
            show_atom_indices: 是否显示原子索引

        Returns:
            导出结果字典
        """
        if not validate_smiles(smiles):
            return {"error": "Invalid SMILES", "valid": False}

        svg = smiles_to_svg(smiles, width, height, show_atom_indices)
        canonical = self.engine.get_canonical_smiles(smiles)

        return {
            "valid": True,
            "format": "svg",
            "data": svg,
            "smiles": smiles,
            "canonical_smiles": canonical,
            "width": width,
            "height": height
        }

    def to_png(self, smiles: str, width: int = 400, height: int = 300) -> Dict:
        """
        导出为 PNG 格式

        Args:
            smiles: SMILES 字符串
            width: 图片宽度
            height: 图片高度

        Returns:
            导出结果字典
        """
        if not validate_smiles(smiles):
            return {"error": "Invalid SMILES", "valid": False}

        png_base64 = smiles_to_png_base64(smiles, width, height)
        canonical = self.engine.get_canonical_smiles(smiles)

        return {
            "valid": True,
            "format": "png",
            "data": png_base64,
            "mime": "image/png",
            "smiles": smiles,
            "canonical_smiles": canonical,
            "width": width,
            "height": height
        }

    def to_latex(self, smiles: str) -> Dict:
        """
        导出为 LaTeX chemfig 格式

        Args:
            smiles: SMILES 字符串

        Returns:
            导出结果字典
        """
        if not validate_smiles(smiles):
            return {"error": "Invalid SMILES", "valid": False}

        chemfig = smiles_to_chemfig(smiles)
        canonical = self.engine.get_canonical_smiles(smiles)

        return {
            "valid": True,
            "format": "latex",
            "data": chemfig,
            "smiles": smiles,
            "canonical_smiles": canonical
        }

    def to_word(self, smiles: str, width: int = 400, height: int = 300) -> Dict:
        """
        导出为 Word 可用格式

        Args:
            smiles: SMILES 字符串
            width: 图片宽度
            height: 图片高度

        Returns:
            导出结果字典
        """
        if not validate_smiles(smiles):
            return {"error": "Invalid SMILES", "valid": False}

        # 生成 SVG
        svg = smiles_to_svg(smiles, width, height)

        # 生成 PNG
        png_base64 = smiles_to_png_base64(smiles, width, height)

        # 获取分子信息
        info = get_mol_info(smiles)

        canonical = self.engine.get_canonical_smiles(smiles)

        return {
            "valid": True,
            "format": "word",
            "svg": svg,
            "png": png_base64,
            "info": info,
            "smiles": smiles,
            "canonical_smiles": canonical,
            "width": width,
            "height": height
        }

    def to_all_formats(self, smiles: str, width: int = 400, height: int = 300) -> Dict:
        """
        导出所有格式

        Args:
            smiles: SMILES 字符串
            width: 图片宽度
            height: 图片高度

        Returns:
            所有格式的导出结果
        """
        if not validate_smiles(smiles):
            return {"error": "Invalid SMILES", "valid": False}

        return {
            "valid": True,
            "smiles": smiles,
            "canonical_smiles": self.engine.get_canonical_smiles(smiles),
            "svg": self.to_svg(smiles, width, height),
            "png": self.to_png(smiles, width, height),
            "latex": self.to_latex(smiles),
            "word": self.to_word(smiles, width, height)
        }

    def get_common_structures(self) -> Dict[str, str]:
        """
        获取常见有机物结构

        Returns:
            常见有机物字典
        """
        return self.engine.get_common_structures()


class StructurePlugin:
    """结构插件"""

    def __init__(self):
        self.name = "structure"
        self.description = "化学结构导出插件"
        self.exporter = StructureExporter()

    def export(self, smiles: str, format: str = "svg", **kwargs) -> Dict:
        """
        导出化学结构

        Args:
            smiles: SMILES 字符串
            format: 导出格式
            **kwargs: 其他参数

        Returns:
            导出结果
        """
        if format == "svg":
            return self.exporter.to_svg(smiles, **kwargs)
        elif format == "png":
            return self.exporter.to_png(smiles, **kwargs)
        elif format == "latex":
            return self.exporter.to_latex(smiles)
        elif format == "word":
            return self.exporter.to_word(smiles, **kwargs)
        elif format == "all":
            return self.exporter.to_all_formats(smiles, **kwargs)
        else:
            return {"error": f"Unsupported format: {format}", "valid": False}


# 创建全局实例
structure_exporter = StructureExporter()
structure_plugin = StructurePlugin()


# 便捷函数
def export_structure(smiles: str, format: str = "svg", **kwargs) -> Dict:
    """导出化学结构（支持 svg/png/latex/word/all 格式）"""
    return structure_plugin.export(smiles, format, **kwargs)


# ====== 标准插件类（继承 ChemPlugin） ======

class StructureChemPlugin(ChemPlugin):
    """化学结构导出插件（标准插件接口）"""

    name = "structure_export"
    version = "1.0.0"
    description = "将化学结构导出为 SVG/PNG/LaTeX/Word 等多种格式"
    category = PluginCategory.EXPORT

    def __init__(self):
        super().__init__()
        self.exporter = StructureExporter()

    def initialize(self) -> bool:
        return True

    def get_endpoints(self) -> List[PluginEndpoint]:
        return []  # 端点已在 structure.py API 中注册，此处不重复

    def export(self, smiles: str, format: str = "svg", **kwargs) -> Dict:
        """导出化学结构"""
        return structure_plugin.export(smiles, format, **kwargs)
