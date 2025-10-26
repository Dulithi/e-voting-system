import sys
from pathlib import Path

# Add backend directory to Python path for shared module
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from app.api.routes.code_sheet import router as cs_router

app = FastAPI(title="Code Sheet Service", version="1.0.0", docs_url="/api/docs")

app.include_router(cs_router, prefix="/api/code-sheet", tags=["Code Sheet"])

@app.get("/health")
async def health():
    return {"status": "healthy"}
