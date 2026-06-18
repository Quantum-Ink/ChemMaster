"""
分子渲染器模块
支持：SVG 矢量图输出、2D/3D 分子可视化
使用 RDKit 进行分子结构渲染
"""

import io
import base64
from typing import Optional, Dict, Any
from dataclasses import dataclass

try:
    from rdkit import Chem
    from rdkit.Chem import Draw, AllChem, Descriptors
    from rdkit.Chem.Draw import rdMolDraw2D
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    print("Warning: RDKit not installed. Molecule rendering features will be limited.")


@dataclass
class RenderOptions:
    """渲染选项"""
    width: int = 300
    height: int = 200
    show_atom_indices: bool = False
    show_bond_indices: bool = False
    show_hydrogens: bool = True
    highlight_atoms: list = None
    highlight_bonds: list = None
    background_color: str = "white"
    atom_colors: dict = None
    bond_colors: dict = None

    def __post_init__(self):
        if self.highlight_atoms is None:
            self.highlight_atoms = []
        if self.highlight_bonds is None:
            self.highlight_bonds = []
        if self.atom_colors is None:
            self.atom_colors = {}
        if self.bond_colors is None:
            self.bond_colors = {}


class MoleculeRenderer:
    """分子渲染器"""

    # 元素颜色映射
    ELEMENT_COLORS = {
        'C': (0.2, 0.2, 0.2),   # 灰色
        'H': (0.8, 0.8, 0.8),   # 浅灰
        'O': (0.8, 0.0, 0.0),   # 红色
        'N': (0.0, 0.0, 0.8),   # 蓝色
        'S': (0.8, 0.8, 0.0),   # 黄色
        'P': (1.0, 0.5, 0.0),   # 橙色
        'F': (0.0, 0.8, 0.0),   # 绿色
        'Cl': (0.0, 0.8, 0.0),  # 绿色
        'Br': (0.6, 0.2, 0.0),  # 棕色
        'I': (0.4, 0.0, 0.8),   # 紫色
    }

    def __init__(self):
        self._mol_cache: Dict[str, Any] = {}

    def smiles_to_mol(self, smiles: str) -> Optional[Any]:
        """
        将 SMILES 转换为 RDKit 分子对象

        Args:
            smiles: SMILES 表示式

        Returns:
            RDKit 分子对象或 None
        """
        if not RDKIT_AVAILABLE:
            return None

        if smiles in self._mol_cache:
            return self._mol_cache[smiles]

        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is not None:
                # 添加氢原子
                mol = Chem.AddHs(mol)
                # 计算 2D 坐标
                AllChem.Compute2DCoords(mol)
                self._mol_cache[smiles] = mol
            return mol
        except Exception as e:
            print(f"Error converting SMILES to molecule: {e}")
            return None

    def mol_to_svg(self, mol: Any, options: RenderOptions = None) -> Optional[str]:
        """
        将分子对象转换为 SVG 格式

        Args:
            mol: RDKit 分子对象
            options: 渲染选项

        Returns:
            SVG 字符串或 None
        """
        if not RDKIT_AVAILABLE or mol is None:
            return None

        if options is None:
            options = RenderOptions()

        try:
            # 创建 SVG 绘图器
            drawer = rdMolDraw2D.MolDraw2DSVG(options.width, options.height)

            # 设置绘图选项
            draw_options = drawer.drawOptions()
            draw_options.addAtomIndices = options.show_atom_indices
            draw_options.addBondIndices = options.show_bond_indices

            # 设置背景颜色
            if options.background_color == "white":
                draw_options.setBackgroundColour((1.0, 1.0, 1.0))
            elif options.background_color == "black":
                draw_options.setBackgroundColour((0.0, 0.0, 0.0))

            # 设置高亮颜色
            highlight_atom_colors = {}
            for atom_idx in options.highlight_atoms:
                highlight_atom_colors[atom_idx] = (1.0, 0.0, 0.0)  # 红色高亮

            highlight_bond_colors = {}
            for bond_idx in options.highlight_bonds:
                highlight_bond_colors[bond_idx] = (1.0, 0.0, 0.0)  # 红色高亮

            # 绘制分子
            if highlight_atom_colors or highlight_bond_colors:
                drawer.DrawMolecule(
                    mol,
                    highlightAtoms=options.highlight_atoms,
                    highlightBonds=options.highlight_bonds,
                    highlightAtomColors=highlight_atom_colors,
                    highlightBondColors=highlight_bond_colors
                )
            else:
                drawer.DrawMolecule(mol)

            drawer.FinishDrawing()
            svg = drawer.GetDrawingText()

            return svg

        except Exception as e:
            print(f"Error rendering molecule to SVG: {e}")
            return None

    def smiles_to_svg(self, smiles: str, options: RenderOptions = None) -> Optional[str]:
        """
        将 SMILES 转换为 SVG 格式

        Args:
            smiles: SMILES 表示式
            options: 渲染选项

        Returns:
            SVG 字符串或 None
        """
        mol = self.smiles_to_mol(smiles)
        if mol is None:
            return None

        return self.mol_to_svg(mol, options)

    def smiles_to_png_base64(self, smiles: str, options: RenderOptions = None) -> Optional[str]:
        """
        将 SMILES 转换为 base64 编码的 PNG 图片

        Args:
            smiles: SMILES 表示式
            options: 渲染选项

        Returns:
            base64 编码的 PNG 图片字符串或 None
        """
        if not RDKIT_AVAILABLE:
            return None

        mol = self.smiles_to_mol(smiles)
        if mol is None:
            return None

        if options is None:
            options = RenderOptions()

        try:
            img = Draw.MolToImage(mol, size=(options.width, options.height))

            # 转换为 base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode()

            return f"data:image/png;base64,{img_base64}"

        except Exception as e:
            print(f"Error rendering molecule to PNG: {e}")
            return None

    def mol_to_3d_sdf(self, mol: Any) -> Optional[str]:
        """
        将分子对象转换为 3D SDF 格式

        Args:
            mol: RDKit 分子对象

        Returns:
            SDF 格式字符串或 None
        """
        if not RDKIT_AVAILABLE or mol is None:
            return None

        try:
            # 添加氢原子
            mol = Chem.AddHs(mol)

            # 生成 3D 构象
            AllChem.EmbedMolecule(mol, randomSeed=42)
            AllChem.MMFFOptimizeMolecule(mol)

            # 转换为 SDF 格式
            sdf = Chem.MolToMolBlock(mol)

            return sdf

        except Exception as e:
            print(f"Error generating 3D SDF: {e}")
            return None

    def smiles_to_3d_sdf(self, smiles: str) -> Optional[str]:
        """
        将 SMILES 转换为 3D SDF 格式

        Args:
            smiles: SMILES 表示式

        Returns:
            SDF 格式字符串或 None
        """
        mol = self.smiles_to_mol(smiles)
        if mol is None:
            return None

        return self.mol_to_3d_sdf(mol)

    def get_molecule_info(self, smiles: str) -> Optional[Dict]:
        """
        获取分子信息

        Args:
            smiles: SMILES 表示式

        Returns:
            分子信息字典或 None
        """
        if not RDKIT_AVAILABLE:
            return None

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None

        try:
            mol_with_h = Chem.AddHs(mol)

            return {
                'smiles': smiles,
                'molecular_formula': Chem.rdMolDescriptors.CalcMolFormula(mol),
                'molecular_weight': Descriptors.ExactMolWt(mol),
                'num_atoms': mol.GetNumAtoms(),
                'num_bonds': mol.GetNumBonds(),
                'num_heavy_atoms': mol.GetNumHeavyAtoms(),
                'num_hydrogens': mol_with_h.GetNumAtoms() - mol.GetNumAtoms(),
                'num_rings': mol.GetRingInfo().NumRings(),
                'num_aromatic_rings': Descriptors.NumAromaticRings(mol),
                'logp': Descriptors.MolLogP(mol),
                'tpsa': Descriptors.TPSA(mol),
                'h_bond_donors': Descriptors.NumHDonors(mol),
                'h_bond_acceptors': Descriptors.NumHAcceptors(mol),
                'rotatable_bonds': Descriptors.NumRotatableBonds(mol),
                'is_aromatic': any(atom.GetIsAromatic() for atom in mol.GetAtoms()),
                'is_chiral': Chem.FindMolChiralCenters(mol) != []
            }

        except Exception as e:
            print(f"Error getting molecule info: {e}")
            return None

    def generate_2d_coords(self, mol: Any) -> Optional[Any]:
        """
        生成 2D 坐标

        Args:
            mol: RDKit 分子对象

        Returns:
            带有 2D 坐标的分子对象或 None
        """
        if not RDKIT_AVAILABLE or mol is None:
            return None

        try:
            mol = Chem.AddHs(mol)
            AllChem.Compute2DCoords(mol)
            return mol
        except Exception as e:
            print(f"Error generating 2D coordinates: {e}")
            return None

    def generate_3d_coords(self, mol: Any) -> Optional[Any]:
        """
        生成 3D 坐标

        Args:
            mol: RDKit 分子对象

        Returns:
            带有 3D 坐标的分子对象或 None
        """
        if not RDKIT_AVAILABLE or mol is None:
            return None

        try:
            mol = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol, randomSeed=42)
            AllChem.MMFFOptimizeMolecule(mol)
            return mol
        except Exception as e:
            print(f"Error generating 3D coordinates: {e}")
            return None

    def draw_reaction(self, reaction_smarts: str, options: RenderOptions = None) -> Optional[str]:
        """
        绘制反应式

        Args:
            reaction_smarts: 反应 SMARTS 表示式
            options: 渲染选项

        Returns:
            SVG 字符串或 None
        """
        if not RDKIT_AVAILABLE:
            return None

        if options is None:
            options = RenderOptions()

        try:
            rxn = AllChem.ReactionFromSmarts(reaction_smarts)
            if rxn is None:
                return None

            drawer = rdMolDraw2D.MolDraw2DSVG(options.width, options.height)
            drawer.DrawReaction(rxn)
            drawer.FinishDrawing()

            return drawer.GetDrawingText()

        except Exception as e:
            print(f"Error drawing reaction: {e}")
            return None

    def create_mol_block(self, smiles: str) -> Optional[str]:
        """
        创建 MOL 文件内容

        Args:
            smiles: SMILES 表示式

        Returns:
            MOL 文件内容或 None
        """
        if not RDKIT_AVAILABLE:
            return None

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None

        try:
            mol = Chem.AddHs(mol)
            AllChem.Compute2DCoords(mol)
            return Chem.MolToMolBlock(mol)
        except Exception as e:
            print(f"Error creating MOL block: {e}")
            return None


# 全局实例
molecule_renderer = MoleculeRenderer()


# 便捷函数
def smiles_to_svg(smiles: str, width: int = 300, height: int = 200) -> Optional[str]:
    """SMILES 转 SVG"""
    options = RenderOptions(width=width, height=height)
    return molecule_renderer.smiles_to_svg(smiles, options)


def smiles_to_png_base64(smiles: str, width: int = 300, height: int = 200) -> Optional[str]:
    """SMILES 转 PNG base64"""
    options = RenderOptions(width=width, height=height)
    return molecule_renderer.smiles_to_png_base64(smiles, options)


def get_molecule_info(smiles: str) -> Optional[Dict]:
    """获取分子信息"""
    return molecule_renderer.get_molecule_info(smiles)
