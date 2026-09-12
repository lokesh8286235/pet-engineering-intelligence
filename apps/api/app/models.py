from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    path: str = Field(min_length=1, description="Local repository path")
    max_files: int = Field(default=2500, ge=1, le=10000)


class FileSignal(BaseModel):
    path: str = Field(min_length=1)
    kind: str = Field(min_length=1)
    size_bytes: int = Field(ge=0)
    lines: int = Field(ge=0)


class Risk(BaseModel):
    severity: str = Field(min_length=1)
    category: str = Field(min_length=1)
    message: str = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    repository: str = Field(min_length=1)
    files: int = Field(ge=0)
    source_files: int = Field(ge=0)
    lines: int = Field(ge=0)
    languages: dict[str, int]
    signals: list[FileSignal]
    risks: list[Risk]
    health_score: int = Field(ge=0, le=100)
