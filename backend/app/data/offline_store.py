"""
ChemMaster 离线数据存储
提供本地 SQLite 化学数据查询
确保无网络环境下基本功能可用
"""

import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger("chemmaster.offline")


class OfflineStore:
    """
    离线化学数据存储
    封装所有本地 SQLite 查询操作
    """

    def __init__(self, db):
        self.db = db

    # ====== 元素查询 ======

    async def get_element(self, symbol: str) -> Optional[Dict[str, Any]]:
        """按符号查元素，如 'H' → 氢"""
        return await self.db.fetch_one(
            "SELECT * FROM elements WHERE symbol = ?", (symbol,)
        )

    async def get_all_elements(self) -> List[Dict[str, Any]]:
        """获取所有元素"""
        return await self.db.fetch_all(
            "SELECT * FROM elements ORDER BY atomic_number"
        )

    # ====== 化合物查询 ======

    async def search_compound_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """按名称查化合物（支持中英文）"""
        return await self.db.fetch_one(
            "SELECT * FROM compounds WHERE name = ? OR name_zh = ?",
            (name, name)
        )

    async def search_compound_by_formula(self, formula: str) -> Optional[Dict[str, Any]]:
        """按分子式查化合物"""
        return await self.db.fetch_one(
            "SELECT * FROM compounds WHERE formula = ?", (formula,)
        )

    async def search_compound_by_smiles(self, smiles: str) -> Optional[Dict[str, Any]]:
        """按 SMILES 查化合物"""
        return await self.db.fetch_one(
            "SELECT * FROM compounds WHERE smiles = ?", (smiles,)
        )

    async def search_compounds_by_cas(self, cas: str) -> Optional[Dict[str, Any]]:
        """按 CAS 号查化合物"""
        return await self.db.fetch_one(
            "SELECT * FROM compounds WHERE cas_number = ?", (cas,)
        )

    async def search_compounds_fuzzy(self, keyword: str) -> List[Dict[str, Any]]:
        """模糊搜索化合物"""
        return await self.db.fetch_all(
            "SELECT * FROM compounds WHERE name LIKE ? OR name_zh LIKE ? OR formula LIKE ? LIMIT 20",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        )

    async def save_compound(self, compound: Dict[str, Any]) -> None:
        """保存化合物到本地（来自在线查询结果）"""
        try:
            await self.db.execute(
                "INSERT OR IGNORE INTO compounds "
                "(name, name_zh, formula, smiles, molecular_weight, cas_number, description, source) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, 'pubchem')",
                (
                    compound.get("name"),
                    compound.get("name_zh"),
                    compound.get("formula", compound.get("molecular_formula")),
                    compound.get("smiles"),
                    compound.get("molecular_weight"),
                    compound.get("cas_number"),
                    compound.get("description"),
                )
            )
            logger.debug(f"Saved compound: {compound.get('name')}")
        except Exception as e:
            logger.warning(f"Failed to save compound: {e}")

    # ====== 反应方程式 ======

    async def get_reaction(self, equation: str) -> Optional[Dict[str, Any]]:
        """查反应方程式"""
        return await self.db.fetch_one(
            "SELECT * FROM reactions WHERE equation = ?", (equation,)
        )

    async def search_reactions(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索反应方程式"""
        return await self.db.fetch_all(
            "SELECT * FROM reactions WHERE equation LIKE ? LIMIT 20",
            (f"%{keyword}%",)
        )

    async def save_reaction(self, reaction: Dict[str, Any]) -> None:
        """保存反应方程式"""
        try:
            await self.db.execute(
                "INSERT OR IGNORE INTO reactions "
                "(equation, reactants, products, reaction_type, conditions, source) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    reaction.get("equation"),
                    reaction.get("reactants"),
                    reaction.get("products"),
                    reaction.get("reaction_type"),
                    reaction.get("conditions"),
                    reaction.get("source", "local"),
                )
            )
        except Exception as e:
            logger.warning(f"Failed to save reaction: {e}")

    # ====== 统计 ======

    async def get_stats(self) -> Dict[str, int]:
        """返回离线数据库统计"""
        return {
            "elements": await self.db.count("elements"),
            "compounds": await self.db.count("compounds"),
            "reactions": await self.db.count("reactions"),
            "cache_entries": await self.db.count("api_cache"),
        }
