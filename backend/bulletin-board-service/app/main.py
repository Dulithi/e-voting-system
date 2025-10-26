import sys
from pathlib import Path

# Add backend directory to Python path for shared module
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from app.api.routes.bulletin import router as bulletin_router

app = FastAPI(title="Bulletin Board Service", version="1.0.0", docs_url="/api/docs")

app.include_router(bulletin_router, prefix="/api/bulletin", tags=["Bulletin Board"])

@app.get("/health")
async def health():
    return {"status": "healthy"}
