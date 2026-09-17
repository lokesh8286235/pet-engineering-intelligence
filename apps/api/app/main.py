import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from .analyzer import analyze_repository
from .models import AnalyzeRequest, AnalysisResult

app = FastAPI(title="PET API", version="0.1.0", description="Personal Engineering Toolkit API")


def _cors_origins() -> list[str]:
    """Return configured browser origins, rejecting wildcard credentials access."""
    raw_origins = os.getenv("PET_CORS_ORIGINS", "http://localhost:3000")
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    if "*" in origins:
        raise ValueError("PET_CORS_ORIGINS must list specific origins; '*' is not allowed with credentials")
    return origins or ["http://localhost:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
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
def health(response: Response) -> dict[str, str]:
    response.headers["Cache-Control"] = "no-store"
    return {"status": "ok", "service": "pet-api"}


@app.post("/v1/analyze", response_model=AnalysisResult)
def analyze(request: AnalyzeRequest) -> AnalysisResult:
    try:
        _validate_allowed_root(request.path)
        return analyze_repository(request.path, request.max_files)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
