"""
ChemMaster 主应用入口
注册所有 API 路由和中间件
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.editor import router as editor
from app.api.export import router as export
from app.api.structure import router as structure

app = FastAPI(title="ChemMaster V13 Unified Platform")

# CORS 中间件：允许前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# 注册路由
app.include_router(editor)
app.include_router(export)
app.include_router(structure)


@app.get("/")
def root():
    """健康检查端点"""
    return {"status": "V13 Running"}