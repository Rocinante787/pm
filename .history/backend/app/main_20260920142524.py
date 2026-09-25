from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.auth import router as auth_router
from app.board import router as board_router
from app.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Project Management API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(auth_router)
app.include_router(board_router)

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Determine static assets directory
backend_dir = Path(__file__).resolve().parent.parent
frontend_out = backend_dir.parent / "frontend" / "out"
backend_static = backend_dir / "static"

if frontend_out.exists() and (frontend_out / "index.html").exists():
    static_dir = frontend_out
elif backend_static.exists() and (backend_static / "index.html").exists():
    static_dir = backend_static
else:
    static_dir = None

if static_dir:
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
