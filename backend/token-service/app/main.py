import sys
from pathlib import Path

# Add backend directory to Python path for shared module
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from app.api.routes.blind_signing import router as blind_router

app = FastAPI(title="Anonymous Token Service", version="1.0.0", docs_url="/api/docs")

app.include_router(blind_router, prefix="/api/blind_signing", tags=["Blind Signing"])

@app.get("/health")
async def health():
    return {"status": "healthy"}
