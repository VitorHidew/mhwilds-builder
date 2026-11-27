from pathlib import Path


PROJECT_DIR = Path(__file__).parents[1]


def read(path: str) -> str:
    return (PROJECT_DIR / path).read_text(encoding="utf-8")


def test_obsolete_project_overwriters_are_not_distributed():
    assert not (PROJECT_DIR / "setup_project.py").exists()
    assert not (PROJECT_DIR / "fetch_mhdb_data.py").exists()
    assert (PROJECT_DIR / "sync_mhdb.py").is_file()


def test_private_runtime_files_are_ignored():
    gitignore = read(".gitignore")
    for pattern in (
        ".env",
        "app/storage/*.json",
        "app/storage/.session_secret",
        ".session_secret",
        "saved_builds.json",
        "saved_damage.json",
        "talisman_inventory.json",
    ):
        assert pattern in gitignore


def test_container_runs_without_root_and_without_embedded_secret():
    dockerfile = read("Dockerfile")
    compose = read("compose.yaml")

    assert "USER mhwilds" in dockerfile
    assert "MHWILDS_SESSION_SECRET" not in dockerfile
    assert "${MHWILDS_SESSION_SECRET:?" in compose
    assert "read_only: true" in compose
    assert "no-new-privileges:true" in compose
    assert "cap_drop:" in compose and "- ALL" in compose


def test_github_automation_covers_tests_container_and_security():
    ci = read(".github/workflows/ci.yml")
    codeql = read(".github/workflows/codeql.yml")
    dependabot = read(".github/dependabot.yml")

    assert "python -m pytest" in ci
    assert "node --check static/js/app.js" in ci
    assert "docker build" in ci
    assert "github/codeql-action/init@v4" in codeql
    assert "python" in codeql and "javascript-typescript" in codeql
    assert "package-ecosystem: pip" in dependabot
    assert "package-ecosystem: docker" in dependabot
    assert "package-ecosystem: github-actions" in dependabot


def test_repository_has_portfolio_and_security_documentation():
    for path in (
        "README.md",
        "LICENSE",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "THIRD_PARTY_NOTICES.md",
        "docs/ARCHITECTURE.md",
        "docs/DATA-SOURCES.md",
        "docs/GITHUB-CHECKLIST.md",
    ):
        assert (PROJECT_DIR / path).is_file(), path

