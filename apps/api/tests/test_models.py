import pytest
from pydantic import ValidationError

from app.models import AnalysisResult, FileSignal, Risk


def test_file_signal_rejects_negative_metrics():
    with pytest.raises(ValidationError):
        FileSignal(path="app.py", kind="python", size_bytes=-1, lines=1)

    with pytest.raises(ValidationError):
        FileSignal(path="app.py", kind="python", size_bytes=1, lines=-1)


def test_risk_requires_meaningful_text():
    with pytest.raises(ValidationError):
        Risk(severity="", category="quality", message="problem")

    with pytest.raises(ValidationError):
        Risk(severity="medium", category="quality", message="")


def test_analysis_result_enforces_health_score_bounds():
    base = dict(
        repository="demo",
        files=1,
        lines=10,
        languages={"python": 10},
        signals=[],
        risks=[],
    )

    with pytest.raises(ValidationError):
        AnalysisResult(**base, health_score=-1)

    with pytest.raises(ValidationError):
        AnalysisResult(**base, health_score=101)

    result = AnalysisResult(**base, health_score=100)
    assert result.health_score == 100
