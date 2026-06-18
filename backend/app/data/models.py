"""
ChemMaster 数据模型
定义化学数据的 Pydantic 模型，用于 API 请求/响应和数据库映射
"""

from pydantic import BaseModel
from typing import Optional, List


class Element(BaseModel):
    """元素信息"""
    symbol: str                  # 元素符号，如 "H"
    name_zh: str                 # 中文名，如 "氢"
    name_en: str                 # 英文名，如 "Hydrogen"
    atomic_number: int           # 原子序数
    atomic_mass: float           # 相对原子质量
    electron_config: Optional[str] = None  # 电子排布
    category: Optional[str] = None         # 元素分类


class Compound(BaseModel):
    """化合物信息"""
    id: Optional[int] = None
    name: Optional[str] = None       # 英文名
    name_zh: Optional[str] = None    # 中文名
    formula: str                     # 分子式
    smiles: Optional[str] = None     # SMILES 表示
    molecular_weight: Optional[float] = None  # 分子量
    cas_number: Optional[str] = None          # CAS 号
    description: Optional[str] = None         # 描述
    source: str = "local"            # 数据来源：local / pubchem
    cached_at: Optional[str] = None


class Reaction(BaseModel):
    """反应方程式"""
    id: Optional[int] = None
    equation: str                    # 方程式
    reactants: Optional[str] = None  # 反应物（JSON）
    products: Optional[str] = None   # 生成物（JSON）
    reaction_type: Optional[str] = None  # 反应类型
    conditions: Optional[str] = None     # 反应条件
    source: str = "local"


class CacheEntry(BaseModel):
    """缓存条目"""
    key: str
    value: str
    source: Optional[str] = None
    cached_at: Optional[str] = None
    expires_at: Optional[float] = None


class DataMode(BaseModel):
    """数据模式状态"""
    mode: str = "auto"       # auto / offline / online
    offline_available: bool = True
    online_available: bool = False
    cache_entries: int = 0
    db_compounds: int = 0
