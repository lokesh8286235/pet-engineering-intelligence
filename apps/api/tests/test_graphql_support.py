from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_recognizes_graphql_source_files(tmp_path: Path):
    (tmp_path / "schema.graphql").write_text(
        "type Query {\n  health: String!\n}\n",
        encoding="utf-8",
    )

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.source_files == 1
    assert result.languages["GraphQL"] == 1
    assert result.signals[0].kind == "GraphQL"


def test_analyzer_recognizes_gql_extension(tmp_path: Path):
    (tmp_path / "schema.gql").write_text("type Query { health: String! }\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.languages["GraphQL"] == 1
