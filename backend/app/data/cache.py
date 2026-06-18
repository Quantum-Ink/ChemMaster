"""
ChemMaster 混合缓存系统
内存 LRU（快速）+ SQLite TTL（持久化）
用于缓存 PubChem API 响应，减少网络请求
"""

import json
import time
import logging
from collections import OrderedDict
from typing import Any, Optional

logger = logging.getLogger("chemmaster.cache")


class HybridCache:
    """
    两级缓存：内存 LRU + SQLite 持久化

    读取流程：内存命中 → 返回 / SQLite命中 → 写入内存并返回 / 未命中 → 返回 None
    写入流程：同时写入内存和 SQLite
    """

    def __init__(self, max_memory: int = 512, default_ttl: int = 3600):
        """
        Args:
            max_memory: 内存 LRU 最大条目数
            default_ttl: 默认过期时间（秒），1小时
        """
        self._memory: OrderedDict[str, dict] = OrderedDict()
        self._max_memory = max_memory
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

    async def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        先查内存 LRU，再查 SQLite
        """
        # 1. 查内存
        if key in self._memory:
            entry = self._memory[key]
            if entry["expires_at"] > time.time():
                self._memory.move_to_end(key)
                self._hits += 1
                return entry["value"]
            else:
                del self._memory[key]

        # 2. 查 SQLite
        try:
            from .database import Database
            db = await Database.get_instance()
            row = await db.fetch_one(
                "SELECT value, expires_at FROM api_cache WHERE key = ?",
                (key,)
            )
            if row and row["expires_at"] and row["expires_at"] > time.time():
                value = json.loads(row["value"])
                self._set_memory(key, value, row["expires_at"])
                self._hits += 1
                return value
        except Exception as e:
            logger.warning(f"Cache SQLite read error: {e}")

        self._misses += 1
        return None

    async def set(self, key: str, value: Any, ttl: int = None) -> None:
        """
        设置缓存值
        同时写入内存和 SQLite
        """
        ttl = ttl or self._default_ttl
        expires_at = time.time() + ttl

        # 写入内存
        self._set_memory(key, value, expires_at)

        # 写入 SQLite
        try:
            from .database import Database
            db = await Database.get_instance()
            await db.execute(
                "INSERT OR REPLACE INTO api_cache (key, value, source, cached_at, expires_at) "
                "VALUES (?, ?, 'api', datetime('now'), ?)",
                (key, json.dumps(value, ensure_ascii=False), expires_at)
            )
        except Exception as e:
            logger.warning(f"Cache SQLite write error: {e}")

    async def delete(self, key: str) -> None:
        """删除缓存条目"""
        self._memory.pop(key, None)
        try:
            from .database import Database
            db = await Database.get_instance()
            await db.execute("DELETE FROM api_cache WHERE key = ?", (key,))
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")

    async def clear_expired(self) -> int:
        """清理过期缓存，返回清理数量"""
        now = time.time()
        count = 0

        # 清理内存
        expired_keys = [
            k for k, v in self._memory.items()
            if v["expires_at"] <= now
        ]
        for k in expired_keys:
            del self._memory[k]
            count += len(expired_keys)

        # 清理 SQLite
        try:
            from .database import Database
            db = await Database.get_instance()
            await db.execute(
                "DELETE FROM api_cache WHERE expires_at IS NOT NULL AND expires_at < ?",
                (now,)
            )
        except Exception as e:
            logger.warning(f"Cache cleanup error: {e}")

        return count

    def _set_memory(self, key: str, value: Any, expires_at: float):
        """写入内存 LRU"""
        self._memory[key] = {"value": value, "expires_at": expires_at}
        self._memory.move_to_end(key)
        # LRU 淘汰
        while len(self._memory) > self._max_memory:
            self._memory.popitem(last=False)

    def get_stats(self) -> dict:
        """返回缓存统计"""
        total = self._hits + self._misses
        return {
            "memory_entries": len(self._memory),
            "max_memory": self._max_memory,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{self._hits / total * 100:.1f}%" if total > 0 else "N/A",
        }


# 全局缓存实例
cache = HybridCache(max_memory=512, default_ttl=3600)
