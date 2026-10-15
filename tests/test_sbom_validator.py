import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_sbom.py"


def run_validator(sbom_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(sbom_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def write_sbom(tmp_path: Path, data) -> Path:
    path = tmp_path / "sbom.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def valid_sbom() -> dict:
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "components": [
            {"type": "library", "name": "example-package", "version": "1.0"}
        ],
    }


def test_valid_sbom_passes(tmp_path):
    result = run_validator(write_sbom(tmp_path, valid_sbom()))

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: SBOM validation succeeded." in result.stdout
    assert "Specification: 1.6" in result.stdout


def test_cyclonedx_17_fails(tmp_path):
    sbom = valid_sbom()
    sbom["specVersion"] = "1.7"

    result = run_validator(write_sbom(tmp_path, sbom))

    assert result.returncode == 2
    assert "Expected CycloneDX 1.6, got '1.7'." in result.stderr


def test_invalid_json_fails(tmp_path):
    path = tmp_path / "sbom.json"
    path.write_text("{invalid json", encoding="utf-8")

    result = run_validator(path)

    assert result.returncode == 2
    assert "Cannot read valid SBOM JSON" in result.stderr


def test_missing_file_fails(tmp_path):
    result = run_validator(tmp_path / "missing.json")

    assert result.returncode == 2
    assert "Required SBOM file is missing" in result.stderr


def test_wrong_format_fails(tmp_path):
    sbom = valid_sbom()
    sbom["bomFormat"] = "OtherFormat"

    result = run_validator(write_sbom(tmp_path, sbom))

    assert result.returncode == 2
    assert "SBOM format must be CycloneDX" in result.stderr


def test_unsupported_version_fails(tmp_path):
    sbom = valid_sbom()
    sbom["specVersion"] = "9.9"

    result = run_validator(write_sbom(tmp_path, sbom))

    assert result.returncode == 2
    assert "Expected CycloneDX 1.6" in result.stderr


def test_empty_components_fails(tmp_path):
    sbom = valid_sbom()
    sbom["components"] = []

    result = run_validator(write_sbom(tmp_path, sbom))

    assert result.returncode == 2
    assert "non-empty components list" in result.stderr


def test_component_without_name_fails(tmp_path):
    sbom = valid_sbom()
    sbom["components"] = [{"type": "library"}]

    result = run_validator(write_sbom(tmp_path, sbom))

    assert result.returncode == 2
    assert "non-empty name" in result.stderr