"""
ChemMaster SQLite 数据库管理器
提供异步连接、表创建、种子数据加载
确保无网络环境下基本化学功能完全可用
"""

import aiosqlite
import logging
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger("chemmaster.db")

# 数据库文件路径（位于项目根目录）
DB_DIR = Path(__file__).parent.parent.parent.parent
DB_PATH = DB_DIR / "chemmaster.db"


class Database:
    """
    SQLite 数据库单例管理器
    使用 aiosqlite 提供异步接口
    """

    _instance: Optional["Database"] = None
    _db: Optional[aiosqlite.Connection] = None

    @classmethod
    async def get_instance(cls) -> "Database":
        """获取数据库单例（首次调用时自动初始化）"""
        if cls._instance is None:
            cls._instance = cls()
            await cls._instance._initialize()
        return cls._instance

    async def _initialize(self):
        """初始化数据库连接和表结构"""
        logger.info(f"Initializing database at {DB_PATH}")
        self._db = await aiosqlite.connect(str(DB_PATH))
        self._db.row_factory = aiosqlite.Row
        await self._create_tables()
        logger.info("Database initialized")

    async def _create_tables(self):
        """创建所有数据表"""
        await self._db.executescript("""
            -- 元素周期表
            CREATE TABLE IF NOT EXISTS elements (
                symbol TEXT PRIMARY KEY,
                name_zh TEXT NOT NULL,
                name_en TEXT NOT NULL,
                atomic_number INTEGER NOT NULL UNIQUE,
                atomic_mass REAL NOT NULL,
                electron_config TEXT,
                category TEXT,
                period INTEGER,
                group_num INTEGER
            );

            -- 化合物库
            CREATE TABLE IF NOT EXISTS compounds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                name_zh TEXT,
                formula TEXT NOT NULL,
                smiles TEXT,
                molecular_weight REAL,
                cas_number TEXT,
                description TEXT,
                source TEXT DEFAULT 'local',
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(formula, name)
            );

            -- 反应方程式库
            CREATE TABLE IF NOT EXISTS reactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equation TEXT NOT NULL UNIQUE,
                reactants TEXT,
                products TEXT,
                reaction_type TEXT,
                conditions TEXT,
                source TEXT DEFAULT 'local'
            );

            -- API 响应缓存（LRU + TTL）
            CREATE TABLE IF NOT EXISTS api_cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                source TEXT,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at REAL
            );

            -- 索引
            CREATE INDEX IF NOT EXISTS idx_compounds_formula
                ON compounds(formula);
            CREATE INDEX IF NOT EXISTS idx_compounds_name
                ON compounds(name);
            CREATE INDEX IF NOT EXISTS idx_compounds_smiles
                ON compounds(smiles);
            CREATE INDEX IF NOT EXISTS idx_cache_expires
                ON api_cache(expires_at);
        """)
        await self._db.commit()

    # ---- 基础操作 ----

    async def execute(self, sql: str, params: tuple = ()) -> None:
        """执行 SQL（INSERT/UPDATE/DELETE）"""
        await self._db.execute(sql, params)
        await self._db.commit()

    async def fetch_one(self, sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """查询单条记录"""
        async with self._db.execute(sql, params) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def fetch_all(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """查询多条记录"""
        async with self._db.execute(sql, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def executemany(self, sql: str, rows: list) -> None:
        """批量执行"""
        await self._db.executemany(sql, rows)
        await self._db.commit()

    # ---- 统计 ----

    async def count(self, table: str) -> int:
        """统计表记录数"""
        row = await self.fetch_one(f"SELECT COUNT(*) as cnt FROM {table}")
        return row["cnt"] if row else 0

    async def close(self):
        """关闭数据库连接"""
        if self._db:
            await self._db.close()
            logger.info("Database connection closed")
