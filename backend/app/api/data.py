"""
ChemMaster 数据管理 API
提供数据库状态查询、模式切换、元素/化合物查询等端点
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from ..data.database import Database
from ..data.offline_store import OfflineStore
from ..data.cache import cache

router = APIRouter(prefix="/api/data", tags=["data"])


# ====== 数据库状态 ======

@router.get("/status")
async def get_data_status():
    """
    返回数据层状态：离线/在线模式、数据库统计、缓存统计
    """
    db = await Database.get_instance()
    store = OfflineStore(db)
    stats = await store.get_stats()
    cache_stats = cache.get_stats()

    return {
        "mode": "dual",  # dual / offline / online
        "database": stats,
        "cache": cache_stats,
    }


# ====== 元素查询（纯离线） ======

@router.get("/elements")
async def get_all_elements():
    """获取所有元素（离线数据）"""
    db = await Database.get_instance()
    store = OfflineStore(db)
    return await store.get_all_elements()


@router.get("/elements/{symbol}")
async def get_element(symbol: str):
    """按符号查元素，如 /api/data/elements/Fe"""
    db = await Database.get_instance()
    store = OfflineStore(db)
    result = await store.get_element(symbol)
    if not result:
        raise HTTPException(404, f"Element '{symbol}' not found")
    return result


# ====== 化合物查询（离线优先） ======

@router.get("/compounds/search")
async def search_compounds(
    q: str = Query(..., description="搜索关键词（名称/分子式/CAS号）"),
):
    """
    搜索化合物
    优先查本地数据库，未命中返回空列表（前端可决定是否查在线）
    """
    db = await Database.get_instance()
    store = OfflineStore(db)

    # 先精确匹配
    result = await store.search_compound_by_name(q)
    if result:
        return [result]

    result = await store.search_compound_by_formula(q)
    if result:
        return [result]

    result = await store.search_compounds_by_cas(q)
    if result:
        return [result]

    # 模糊搜索
    results = await store.search_compounds_fuzzy(q)
    return results


@router.get("/compounds/{compound_id}")
async def get_compound(compound_id: int):
    """按 ID 获取化合物"""
    db = await Database.get_instance()
    result = await db.fetch_one(
        "SELECT * FROM compounds WHERE id = ?", (compound_id,)
    )
    if not result:
        raise HTTPException(404, "Compound not found")
    return result


# ====== 反应方程式查询 ======

@router.get("/reactions/search")
async def search_reactions(
    q: str = Query(..., description="搜索关键词"),
):
    """搜索反应方程式"""
    db = await Database.get_instance()
    store = OfflineStore(db)
    return await store.search_reactions(q)


# ====== 缓存管理 ======

@router.post("/cache/clear")
async def clear_cache():
    """清理过期缓存"""
    count = await cache.clear_expired()
    return {"cleared": count}


@router.get("/cache/stats")
async def get_cache_stats():
    """获取缓存统计"""
    return cache.get_stats()
