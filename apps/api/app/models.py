from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    path: str = Field(min_length=1, description="Local repository path")
    max_files: int = Field(default=2500, ge=1, le=10000)


class FileSignal(BaseModel):
    path: str
    kind: str
    size_bytes: int
    lines: int


class Risk(BaseModel):
    severity: str
    category: str
    message: str
    evidence: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    repository: str
    files: int
    lines: int
    languages: dict[str, int]
    signals: list[FileSignal]
    risks: list[Risk]
    health_score: int
