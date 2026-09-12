import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .analyzer import analyze_repository
from .models import AnalyzeRequest, AnalysisResult

app = FastAPI(title="PET API", version="0.1.0", description="Personal Engineering Toolkit API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _validate_allowed_root(path: str) -> None:
    """Restrict API scans when an operator configures a repository root."""
    configured_root = os.getenv("PET_REPOSITORY_ROOT")
    if not configured_root:
        return

    root = Path(configured_root).expanduser().resolve()
    candidate = Path(path).expanduser().resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("path must be within PET_REPOSITORY_ROOT") from exc


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "pet-api"}


@app.post("/v1/analyze", response_model=AnalysisResult)
def analyze(request: AnalyzeRequest) -> AnalysisResult:
    try:
        _validate_allowed_root(request.path)
        return analyze_repository(request.path, request.max_files)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
