import sys
from pathlib import Path

# Add backend directory to Python path for shared module
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.election import router as election_router
from app.api.routes.trustee import router as trustee_router

app = FastAPI(title="Election Service", version="1.0.0", docs_url="/api/docs")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Admin web frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(election_router, prefix="/api/election", tags=["Election"])
app.include_router(trustee_router, prefix="/api/trustee", tags=["Trustee"])

@app.get("/health")
async def health():
    return {"status": "healthy"}
