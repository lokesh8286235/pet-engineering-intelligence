from pathlib import Path

import pytest

from app.analyzer import analyze_repository


def test_analyzer_counts_languages_and_lines(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hello')\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path))
    assert result.files == 2
    assert result.lines == 2
    assert result.languages["Python"] == 1
    assert result.languages["Markdown"] == 1


def test_analyzer_counts_mdx_as_markdown_documentation(tmp_path: Path):
    (tmp_path / "docs.mdx").write_text("# Docs\n\n<Component />\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path))
    assert result.files == 1
    assert result.languages["Markdown"] == 1
    assert not any(r.category == "documentation" for r in result.risks)


def test_analyzer_does_not_count_trailing_newline_as_source_line(tmp_path: Path):
    (tmp_path / "main.py").write_text("one\ntwo\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path))
    assert result.lines == 2
    assert result.signals[0].lines == 2


def test_analyzer_returns_files_in_deterministic_order(tmp_path: Path):
    (tmp_path / "z.py").write_text("z = 1\n", encoding="utf-8")
    (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "m.py").write_text("m = 1\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path), max_files=2)
    assert [signal.path for signal in result.signals] == ["a.py", "nested/m.py"]


def test_analyzer_flags_missing_tests(tmp_path: Path):
    (tmp_path / "main.py").write_text("x = 1\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path))
    assert any(r.category == "testing" and r.severity == "high" for r in result.risks)


def test_analyzer_detects_conventional_test_files_without_substring_false_positives(tmp_path: Path):
    (tmp_path / "contest.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "test_parser.py").write_text("def test_parser(): pass\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path))
    assert not any(r.category == "testing" for r in result.risks)


def test_analyzer_detects_standalone_test_and_spec_files(tmp_path: Path):
    (tmp_path / "test.py").write_text("def test_root(): pass\n", encoding="utf-8")
    (tmp_path / "spec.py").write_text("def test_spec(): pass\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path))
    assert not any(r.category == "testing" for r in result.risks)


def test_analyzer_detects_dotted_test_and_spec_files(tmp_path: Path):
    (tmp_path / "parser.test.js").write_text("test('parser', () => {});\n", encoding="utf-8")
    (tmp_path / "parser.spec.ts").write_text("it('parser', () => {});\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path))
    assert not any(r.category == "testing" for r in result.risks)


def test_analyzer_detects_nested_spec_files(tmp_path: Path):
    spec_dir = tmp_path / "specs"
    spec_dir.mkdir()
    (spec_dir / "parser.py").write_text("def test_parser(): pass\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path))
    assert not any(r.category == "testing" for r in result.risks)


def test_analyzer_detects_js_tests_in_dunder_tests_directory(tmp_path: Path):
    test_dir = tmp_path / "__tests__"
    test_dir.mkdir()
    (test_dir / "parser.js").write_text("test('parser', () => {});\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path))
    assert not any(r.category == "testing" for r in result.risks)


def test_analyzer_counts_modern_javascript_and_typescript_module_extensions(tmp_path: Path):
    (tmp_path / "worker.mjs").write_text("export const worker = true;\n", encoding="utf-8")
    (tmp_path / "config.cjs").write_text("module.exports = {};\n", encoding="utf-8")
    (tmp_path / "types.mts").write_text("export type ID = string;\n", encoding="utf-8")
    (tmp_path / "legacy.cts").write_text("export const value = 1;\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 4
    assert result.languages["JavaScript"] == 2
    assert result.languages["TypeScript"] == 2
    assert all(signal.kind in {"JavaScript", "TypeScript"} for signal in result.signals)


def test_analyzer_skips_symlinks(tmp_path: Path):
    target = tmp_path / "outside.py"
    target.write_text("secret = True\n", encoding="utf-8")
    link = tmp_path / "linked.py"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        return
    result = analyze_repository(str(tmp_path))
    assert all(signal.path != "linked.py" for signal in result.signals)


def test_analyzer_skips_binary_files(tmp_path: Path):
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "image.bin").write_bytes(b"\x89PNG\r\n\x1a\n\x00binary")
    result = analyze_repository(str(tmp_path))
    assert result.files == 1
    assert all(signal.path != "image.bin" for signal in result.signals)


def test_binary_files_do_not_consume_scan_limit(tmp_path: Path):
    (tmp_path / "00-image.bin").write_bytes(b"\x00binary")
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path), max_files=1)
    assert result.files == 1
    assert result.signals[0].path == "app.py"


def test_analyzer_skips_sensitive_files(tmp_path: Path):
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    for name in (".env", ".env.local", "credentials.json", "server.pem"):
        (tmp_path / name).write_text("SECRET=should-not-be-scanned\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path))
    assert result.files == 1
    assert all(signal.path not in {".env", ".env.local", "credentials.json", "server.pem"} for signal in result.signals)


def test_analyzer_skips_common_ssh_private_keys(tmp_path: Path):
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    for name in ("id_rsa", "id_ed25519", "id_ecdsa", "id_dsa"):
        (tmp_path / name).write_text("-----BEGIN OPENSSH PRIVATE KEY-----\nSECRET\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.signals[0].path == "app.py"


def test_analyzer_skips_common_package_auth_files(tmp_path: Path):
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    for name in (".netrc", ".npmrc", ".pypirc"):
        (tmp_path / name).write_text("TOKEN=should-not-be-scanned\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.signals[0].path == "app.py"


def test_analyzer_skips_nested_cloud_credential_files(tmp_path: Path):
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    aws = tmp_path / ".aws"
    aws.mkdir()
    (aws / "credentials").write_text("aws_secret=should-not-be-scanned\n", encoding="utf-8")
    docker = tmp_path / ".docker"
    docker.mkdir()
    (docker / "config.json").write_text("{\"auths\": {}}\n", encoding="utf-8")
    gcloud = tmp_path / ".config" / "gcloud"
    gcloud.mkdir(parents=True)
    (gcloud / "application_default_credentials.json").write_text("{\"client_secret\": \"should-not-be-scanned\"}\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.signals[0].path == "app.py"


def test_analyzer_skips_python_tooling_cache_directories(tmp_path: Path):
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    for dirname in (".pytest_cache", ".mypy_cache", ".ruff_cache"):
        cache = tmp_path / dirname
        cache.mkdir()
        (cache / "generated.py").write_text("generated = True\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.signals[0].path == "app.py"


def test_analyzer_skips_python_coverage_artifact_directories(tmp_path: Path):
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    for dirname in (".tox", ".nox", "coverage", "htmlcov"):
        artifact_dir = tmp_path / dirname
        artifact_dir.mkdir()
        (artifact_dir / "generated.py").write_text("generated = True\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.signals[0].path == "app.py"


def test_analyzer_skips_generated_frontend_build_cache_directories(tmp_path: Path):
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    for dirname in (".turbo", ".vercel"):
        cache = tmp_path / dirname
        cache.mkdir()
        (cache / "generated.js").write_text("module.exports = {};\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.signals[0].path == "app.py"


def test_analyzer_skips_generated_terraform_directory_case_insensitively(tmp_path: Path):
    generated = tmp_path / ".Terraform"
    generated.mkdir()
    (generated / "provider.js").write_text("module.exports = {};\n", encoding="utf-8")
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.signals[0].path == "app.py"


def test_analyzer_ignores_large_documentation_files_for_maintainability_risk(tmp_path: Path):
    (tmp_path / "README.md").write_text("line\n" * 801, encoding="utf-8")
    result = analyze_repository(str(tmp_path))
    assert not any(r.category == "maintainability" for r in result.risks)


def test_analyzer_rejects_non_positive_file_limits(tmp_path: Path):
    with pytest.raises(ValueError, match="max_files must be between 1 and 10000"):
        analyze_repository(str(tmp_path), max_files=0)


def test_analyzer_rejects_excessive_file_limits(tmp_path: Path):
    with pytest.raises(ValueError, match="max_files must be between 1 and 10000"):
        analyze_repository(str(tmp_path), max_files=10_001)


def test_analyzer_does_not_report_limit_when_exactly_at_file_count(tmp_path: Path):
    for name in ("a.py", "b.py"):
        (tmp_path / name).write_text("x = 1\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path), max_files=2)

    assert result.files == 2
    assert not any(r.category == "analysis" for r in result.risks)


def test_analyzer_reports_limit_only_when_more_valid_files_exist(tmp_path: Path):
    for name in ("a.py", "b.py", "c.py"):
        (tmp_path / name).write_text("x = 1\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path), max_files=2)

    assert result.files == 2
    risk = next(r for r in result.risks if r.category == "analysis")
    assert risk.severity == "low"
    assert risk.message == "Analysis scan truncated at configured file limit"


def test_analyzer_skips_file_that_grows_past_scan_limit(tmp_path: Path):
    from app import analyzer

    path = tmp_path / "app.py"
    path.write_text("x = 1\n", encoding="utf-8")
    original = analyzer._read_text

    def grow_then_read(target: Path) -> str | None:
        target.write_bytes(b"x" * (analyzer.MAX_FILE_BYTES + 1))
        return original(target)

    analyzer._read_text = grow_then_read
    try:
        result = analyze_repository(str(tmp_path))
    finally:
        analyzer._read_text = original

    assert result.files == 0


def test_analyzer_skips_invalid_utf8_files(tmp_path: Path):
    (tmp_path / "app.py").write_bytes(b"x = 1\n\xff\xfe\xfa")
    result = analyze_repository(str(tmp_path))
    assert result.files == 0


def test_analyzer_skips_nul_bytes_beyond_binary_sample(tmp_path: Path):
    content = b"# text\n" + (b"x" * 9000) + b"\x00"
    (tmp_path / "app.py").write_bytes(content)

    result = analyze_repository(str(tmp_path))

    assert result.files == 0


def test_analyzer_skips_ignored_directories_case_insensitively(tmp_path: Path):
    ignored = tmp_path / "Node_Modules"
    ignored.mkdir()
    (ignored / "dependency.js").write_text("module.exports = {};\n", encoding="utf-8")
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.signals[0].path == "app.py"
