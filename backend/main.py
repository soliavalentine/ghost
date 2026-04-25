from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.audit import router

app = FastAPI(
    title="Ghost — Hiring Bias Audit API",
    description=(
        "Three-way ATS emulation and bias gap analysis grounded in "
        "Bertrand & Mullainathan (2004) and Kline, Rose & Walters (2022)."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "https://*.vercel.app",
        "https://ghost-hiring-audit.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "service": "Ghost Bias Audit API",
        "docs": "/docs",
        "health": "/api/health",
        "audit": "POST /api/audit",
        "disparity_map": "GET /api/disparity-map",
    }
