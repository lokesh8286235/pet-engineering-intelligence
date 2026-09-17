from pathlib import Path

import pytest

from app.analyzer import analyze_repository


def test_analyzer_rejects_boolean_file_limit(tmp_path: Path):
    with pytest.raises(ValueError, match="max_files must be between 1 and 10000"):
        analyze_repository(str(tmp_path), max_files=True)
