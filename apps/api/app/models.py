from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    path: str = Field(min_length=1, description="Local repository path")
    max_files: int = Field(default=2500, ge=1, le=10000, strict=True)

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("path must not be blank")
        return value


class FileSignal(BaseModel):
    path: str = Field(min_length=1)
    kind: str = Field(min_length=1)
    size_bytes: int = Field(ge=0, strict=True)
    lines: int = Field(ge=0, strict=True)

    @field_validator("path", "kind")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("value must not be blank")
        return value


class Risk(BaseModel):
    severity: str = Field(min_length=1)
    category: str = Field(min_length=1)
    message: str = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list)

    @field_validator("severity", "category", "message")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("risk text fields must not be blank")
        return value

    @field_validator("evidence")
    @classmethod
    def validate_evidence(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value]
        if any(not item for item in normalized):
            raise ValueError("risk evidence must not contain blank values")
        return normalized


class AnalysisResult(BaseModel):
    repository: str = Field(min_length=1)
    files: int = Field(ge=0, strict=True)
    source_files: int = Field(ge=0, strict=True)
    lines: int = Field(ge=0, strict=True)
    languages: dict[str, int]
    signals: list[FileSignal]
    risks: list[Risk]
    health_score: int = Field(ge=0, le=100, strict=True)

    @field_validator("repository")
    @classmethod
    def validate_repository(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("repository must not be blank")
        return value

    @field_validator("languages")
    @classmethod
    def validate_languages(cls, value: dict[str, int]) -> dict[str, int]:
        normalized: dict[str, int] = {}
        for language, count in value.items():
            language = language.strip()
            if not language:
                raise ValueError("language names must not be blank")
            if language in normalized:
                raise ValueError("language names must be unique after trimming")
            if type(count) is not int or count < 0:
                raise ValueError("language counts must be non-negative integers")
            normalized[language] = count
        return normalized
