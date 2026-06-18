from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.editor import router as editor
from app.api.reaction import router as reaction
from app.api.export import router as export
from app.api.db import router as db

app = FastAPI(title="ChemMaster V13 Unified Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(editor)
app.include_router(reaction)
app.include_router(export)
app.include_router(db)

@app.get("/")
def root():
    return {"status": "V13 Running"}