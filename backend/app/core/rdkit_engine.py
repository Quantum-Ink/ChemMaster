"""
ChemMaster RDKit 引擎模块
提供化学结构处理、渲染和导出功能
"""

from rdkit import Chem
from rdkit.Chem import AllChem, rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D
import base64
from typing import Optional, Dict, Any


class RDKitEngine:
    """RDKit 化学引擎"""

    def __init__(self):
        """初始化 RDKit 引擎"""
        pass

    def validate_smiles(self, smiles: str) -> bool:
        """
        验证 SMILES 字符串是否有效

        Args:
            smiles: SMILES 字符串

        Returns:
            是否有效
        """
        try:
            mol = Chem.MolFromSmiles(smiles)
            return mol is not None
        except Exception:
            return False

    def get_canonical_smiles(self, smiles: str) -> Optional[str]:
        """
        获取规范化的 SMILES

        Args:
            smiles: SMILES 字符串

        Returns:
            规范化的 SMILES，无效则返回 None
        """
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None
            return Chem.MolToSmiles(mol)
        except Exception:
            return None

    def get_mol_info(self, smiles: str) -> Dict[str, Any]:
        """
        获取分子信息

        Args:
            smiles: SMILES 字符串

        Returns:
            分子信息字典
        """
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return {"error": "Invalid SMILES", "valid": False}

            # 获取原子信息
            atoms = []
            for atom in mol.GetAtoms():
                atoms.append({
                    "symbol": atom.GetSymbol(),
                    "index": atom.GetIdx(),
                    "degree": atom.GetDegree(),
                    "formal_charge": atom.GetFormalCharge(),
                    "is_aromatic": atom.GetIsAromatic()
                })

            # 获取键信息
            bonds = []
            for bond in mol.GetBonds():
                bonds.append({
                    "start": bond.GetBeginAtomIdx(),
                    "end": bond.GetEndAtomIdx(),
                    "type": str(bond.GetBondType()),
                    "is_aromatic": bond.GetIsAromatic()
                })

            return {
                "valid": True,
                "canonical_smiles": Chem.MolToSmiles(mol),
                "formula": Chem.rdMolDescriptors.CalcMolFormula(mol),
                "molecular_weight": Chem.rdMolDescriptors.CalcExactMolWt(mol),
                "num_atoms": mol.GetNumAtoms(),
                "num_bonds": mol.GetNumBonds(),
                "num_rings": Chem.rdMolDescriptors.CalcNumRings(mol),
                "is_aromatic": any(a.GetIsAromatic() for a in mol.GetAtoms()),
                "atoms": atoms,
                "bonds": bonds
            }
        except Exception as e:
            return {"error": str(e), "valid": False}

    def smiles_to_svg(self, smiles: str, width: int = 400, height: int = 300,
                      show_atom_indices: bool = False) -> Optional[str]:
        """
        将 SMILES 转换为 SVG 格式

        Args:
            smiles: SMILES 字符串
            width: 图片宽度
            height: 图片高度
            show_atom_indices: 是否显示原子索引

        Returns:
            SVG 字符串，失败返回 None
        """
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None

            # 添加氢原子
            mol = Chem.AddHs(mol)

            # 生成 2D 坐标
            AllChem.Compute2DCoords(mol)
            rdDepictor.Compute2DCoords(mol)

            # 创建 SVG 绘制器
            drawer = rdMolDraw2D.MolDraw2DSVG(width, height)

            # 设置绘制选项
            drawer.drawOptions().addAtomIndices = show_atom_indices
            drawer.drawOptions().bondLineWidth = 2
            drawer.drawOptions().fontSize = 16

            # 绘制分子
            drawer.DrawMolecule(mol)
            drawer.FinishDrawing()

            # 获取 SVG 字符串
            svg = drawer.GetDrawingText()

            return svg
        except Exception as e:
            print(f"Error generating SVG: {e}")
            return None

    def smiles_to_png_base64(self, smiles: str, width: int = 400, height: int = 300) -> Optional[str]:
        """
        将 SMILES 转换为 PNG base64 编码

        Args:
            smiles: SMILES 字符串
            width: 图片宽度
            height: 图片高度

        Returns:
            base64 编码的 PNG，失败返回 None
        """
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None

            # 添加氢原子
            mol = Chem.AddHs(mol)

            # 生成 2D 坐标
            AllChem.Compute2DCoords(mol)

            # 创建 PNG 绘制器
            drawer = rdMolDraw2D.MolDraw2DCairo(width, height)
            drawer.DrawMolecule(mol)
            drawer.FinishDrawing()

            # 获取 PNG 数据
            png_data = drawer.GetDrawingText()

            # 转换为 base64
            return base64.b64encode(png_data).decode('utf-8')
        except Exception as e:
            print(f"Error generating PNG: {e}")
            return None

    def smiles_to_chemfig(self, smiles: str) -> Optional[str]:
        """
        将 SMILES 转换为 LaTeX chemfig 格式

        Args:
            smiles: SMILES 字符串

        Returns:
            chemfig 代码，失败返回 None
        """
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None

            # 简化版：使用 SMILES 直接转换
            # 对于复杂分子，需要更复杂的算法
            canonical = Chem.MolToSmiles(mol)

            # 基本转换规则
            chemfig = self._smiles_to_chemfig_internal(canonical)

            return chemfig
        except Exception as e:
            print(f"Error generating chemfig: {e}")
            return None

    def _smiles_to_chemfig_internal(self, smiles: str) -> str:
        """
        内部方法：SMILES 转 chemfig

        简化实现，处理基本有机物
        """
        # 这里实现基本的转换逻辑
        # 对于复杂分子，需要更完整的解析器

        # 替换常见模式
        replacements = {
            '-': '-',      # 单键
            '=': '=',      # 双键
            '#': '≡',  # 三键
            '(': '(',      # 分支开始
            ')': ')',      # 分支结束
        }

        result = smiles
        for old, new in replacements.items():
            result = result.replace(old, new)

        return f"\\chemfig{{{result}}}"

    def get_common_structures(self) -> Dict[str, str]:
        """
        获取常见有机物结构

        Returns:
            常见有机物字典 {名称: SMILES}
        """
        return {
            "甲烷": "C",
            "乙烷": "CC",
            "丙烷": "CCC",
            "丁烷": "CCCC",
            "乙烯": "C=C",
            "乙炔": "C#C",
            "苯": "c1ccccc1",
            "甲醇": "CO",
            "乙醇": "CCO",
            "甲醛": "C=O",
            "乙醛": "CC=O",
            "丙酮": "CC(=O)C",
            "乙酸": "CC(=O)O",
            "苯酚": "Oc1ccccc1",
            "苯胺": "Nc1ccccc1",
            "硝基苯": "c1ccc(cc1)[N+](=O)[O-]",
            "氯甲烷": "CCl",
            "溴乙烷": "CCBr",
            "碘甲烷": "CI",
            "环己烷": "C1CCCCC1",
            "环戊烷": "C1CCCC1",
            "萘": "c1ccc2ccccc2c1",
            "蒽": "c1ccc2cc3ccccc3cc2c1",
            "吡啶": "c1ccncc1",
            "呋喃": "c1ccoc1",
            "噻吩": "c1ccsc1",
            "吡咯": "c1cc[nH]c1",
            "吲哚": "c1ccc2[nH]ccc2c1",
            "喹啉": "c1ccc2ncccc2c1",
            "葡萄糖": "OC[C@H]1OC(O)[C@H](O)[C@@H](O)[C@@H]1O",
            "蔗糖": "OC[C@H]1OC(O[C@@]2(CO)OC[C@@H](O)[C@H]2O)[C@H](O)[C@@H](O)[C@@H]1O",
            "氨基酸(甘氨酸)": "NCC(=O)O",
            "氨基酸(丙氨酸)": "CC(N)C(=O)O",
            "胆固醇": "CC(C)CCCC(C)C1CCC2C1(CCC3C2CC=C4C3(CCC(C4)O)C)C",
            "阿司匹林": "CC(=O)Oc1ccccc1C(=O)O",
            "咖啡因": "Cn1c(=O)c2c(ncn2C)n(C)c1=O"
        }


# 创建全局引擎实例
rdkit_engine = RDKitEngine()


# 便捷函数
def validate_smiles(smiles: str) -> bool:
    """验证 SMILES"""
    return rdkit_engine.validate_smiles(smiles)


def get_mol_info(smiles: str) -> Dict[str, Any]:
    """获取分子信息"""
    return rdkit_engine.get_mol_info(smiles)


def smiles_to_svg(smiles: str, width: int = 400, height: int = 300) -> Optional[str]:
    """SMILES 转 SVG"""
    return rdkit_engine.smiles_to_svg(smiles, width, height)


def smiles_to_png_base64(smiles: str, width: int = 400, height: int = 300) -> Optional[str]:
    """SMILES 转 PNG base64"""
    return rdkit_engine.smiles_to_png_base64(smiles, width, height)


def smiles_to_chemfig(smiles: str) -> Optional[str]:
    """SMILES 转 chemfig"""
    return rdkit_engine.smiles_to_chemfig(smiles)


def get_common_structures() -> Dict[str, str]:
    """获取常见有机物结构"""
    return rdkit_engine.get_common_structures()
 