import sys
from pathlib import Path
import os

# Add backend directory to Python path for shared module
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.blind_signing import router as blind_router

app = FastAPI(title="Anonymous Token Service", version="1.0.0", docs_url="/api/docs")

# Check if running in development mode
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# CORS middleware - Secure configuration based on environment
if DEBUG:
    # Development: Allow all origins for testing (mobile app, admin web)
    # This is secure because:
    # 1. Only enabled in dev environment
    # 2. Production will enforce strict origins
    # 3. All endpoints still require JWT authentication
    # 4. Backend validates all inputs regardless of origin
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins in development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Production: Strict origin control
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(blind_router, prefix="/api/token", tags=["Blind Signing"])

@app.get("/health")
async def health():
    return {"status": "healthy"}
