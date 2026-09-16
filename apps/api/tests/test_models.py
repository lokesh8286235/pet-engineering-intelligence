import pytest
from pydantic import ValidationError

from app.models import AnalysisResult, AnalyzeRequest, FileSignal, Risk


def test_analyze_request_trims_path():
    request = AnalyzeRequest(path="  /workspace/repo  ")
    assert request.path == "/workspace/repo"


def test_analyze_request_rejects_blank_path():
    with pytest.raises(ValidationError):
        AnalyzeRequest(path="   ")


def test_analyze_request_rejects_boolean_max_files():
    with pytest.raises(ValidationError):
        AnalyzeRequest(path="/workspace/repo", max_files=True)


def test_file_signal_normalizes_text_fields():
    signal = FileSignal(path="  app.py  ", kind="  python  ", size_bytes=1, lines=1)
    assert signal.path == "app.py"
    assert signal.kind == "python"


def test_file_signal_rejects_blank_text_fields():
    with pytest.raises(ValidationError):
        FileSignal(path="   ", kind="python", size_bytes=1, lines=1)

    with pytest.raises(ValidationError):
        FileSignal(path="app.py", kind="   ", size_bytes=1, lines=1)


def test_file_signal_rejects_negative_metrics():
    with pytest.raises(ValidationError):
        FileSignal(path="app.py", kind="python", size_bytes=-1, lines=1)

    with pytest.raises(ValidationError):
        FileSignal(path="app.py", kind="python", size_bytes=1, lines=-1)


def test_file_signal_rejects_boolean_metrics():
    with pytest.raises(ValidationError):
        FileSignal(path="app.py", kind="python", size_bytes=True, lines=1)

    with pytest.raises(ValidationError):
        FileSignal(path="app.py", kind="python", size_bytes=1, lines=False)


def test_risk_requires_meaningful_text():
    with pytest.raises(ValidationError):
        Risk(severity="", category="quality", message="problem")

    with pytest.raises(ValidationError):
        Risk(severity="medium", category="quality", message="")


def test_risk_normalizes_text_and_evidence():
    risk = Risk(
        severity="  medium  ",
        category="  quality  ",
        message="  problem  ",
        evidence=["  evidence line 1  ", "evidence line 2"],
    )

    assert risk.severity == "medium"
    assert risk.category == "quality"
    assert risk.message == "problem"
    assert risk.evidence == ["evidence line 1", "evidence line 2"]


def test_risk_rejects_blank_text_and_evidence():
    with pytest.raises(ValidationError):
        Risk(severity="   ", category="quality", message="problem")

    with pytest.raises(ValidationError):
        Risk(severity="medium", category="quality", message="problem", evidence=["   "])


def test_analysis_result_enforces_health_score_bounds():
    base = dict(
        repository="demo",
        files=1,
        source_files=1,
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


def test_analysis_result_rejects_boolean_counts():
    base = dict(
        repository="demo",
        files=1,
        source_files=1,
        lines=10,
        languages={"python": 10},
        signals=[],
        risks=[],
        health_score=100,
    )

    for field in ("files", "source_files", "lines"):
        with pytest.raises(ValidationError):
            AnalysisResult(**base, **{field: True})


def test_analysis_result_rejects_boolean_health_score():
    base = dict(
        repository="demo",
        files=1,
        source_files=1,
        lines=10,
        languages={"python": 10},
        signals=[],
        risks=[],
    )

    with pytest.raises(ValidationError):
        AnalysisResult(**base, health_score=True)


def test_analysis_result_normalizes_language_names():
    result = AnalysisResult(
        repository="demo",
        files=1,
        source_files=1,
        lines=10,
        languages={"  Python  ": 10},
        signals=[],
        risks=[],
        health_score=100,
    )

    assert result.languages == {"Python": 10}


def test_analysis_result_rejects_invalid_language_counts():
    base = dict(
        repository="demo",
        files=1,
        source_files=1,
        lines=10,
        signals=[],
        risks=[],
        health_score=100,
    )

    with pytest.raises(ValidationError):
        AnalysisResult(**base, languages={"Python": -1})

    with pytest.raises(ValidationError):
        AnalysisResult(**base, languages={"Python": True})

    with pytest.raises(ValidationError):
        AnalysisResult(**base, languages={"   ": 1})


def test_analysis_result_rejects_duplicate_normalized_language_names():
    base = dict(
        repository="demo",
        files=1,
        source_files=1,
        lines=10,
        signals=[],
        risks=[],
        health_score=100,
    )

    with pytest.raises(ValidationError):
        AnalysisResult(**base, languages={"Python": 10, " Python ": 5})
