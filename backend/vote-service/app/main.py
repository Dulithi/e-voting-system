import sys
from pathlib import Path

# Add backend directory to Python path for shared module
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from app.api.routes.vote_submission import router as vote_router

app = FastAPI(title="Vote Submission Service", version="1.0.0", docs_url="/api/docs")

app.include_router(vote_router, prefix="/api/vote-submission", tags=["Vote Submission"])

@app.get("/health")
async def health():
    return {"status": "healthy"}
