"""
ChemMaster 主应用入口
注册所有 API 路由和中间件，并自动发现加载插件
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.editor import router as editor
from app.api.export import router as export
from app.api.structure import router as structure
from app.services.plugin_manager import plugin_manager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chemmaster")


# ---- 应用生命周期 ----

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动/关闭时执行的逻辑"""
    # 启动时：自动发现并加载所有插件
    logger.info("Discovering plugins...")
    results = plugin_manager.discover_and_load(app)
    for name, success in results.items():
        status = "OK" if success else "FAILED"
        logger.info(f"  Plugin '{name}': {status}")
    logger.info(f"Loaded {sum(results.values())}/{len(results)} plugins")

    yield  # 应用运行中

    # 关闭时：清理插件资源
    logger.info("Cleaning up plugins...")
    for info in plugin_manager.list_plugins():
        plugin_manager.unregister(info["name"])


# ---- 创建 FastAPI 应用 ----

app = FastAPI(
    title="ChemMaster V13 Unified Platform",
    lifespan=lifespan,
)

# CORS 中间件：允许前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- 注册核心路由 ----

app.include_router(editor)
app.include_router(export)
app.include_router(structure)


# ---- 插件管理端点 ----

@app.get("/plugins", tags=["plugins"])
def list_plugins():
    """返回所有已加载插件的信息"""
    return plugin_manager.get_all_status()


@app.get("/plugins/{category}", tags=["plugins"])
def list_plugins_by_category(category: str):
    """按分类返回插件列表"""
    plugins = plugin_manager.get_plugins_by_category(category)
    return [p.get_status() for p in plugins]


# ---- 健康检查 ----

@app.get("/")
def root():
    """健康检查端点"""
    return {"status": "V13 Running"}
