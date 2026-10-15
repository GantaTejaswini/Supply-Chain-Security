
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "release_gate.py"
ARTIFACT = ROOT / "artifacts" / "demo-package.zip"
TAMPERED = ROOT / "artifacts" / "demo-package-tampered.zip"

SKIP_PROVENANCE_TESTS = (
    os.environ.get("SKIP_PROVENANCE_TESTS", "").lower() == "true"
)


def run_gate(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GATE), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.skipif(
    SKIP_PROVENANCE_TESTS,
    reason="Pull-request builds do not generate provenance attestations.",
)
def test_original_artifact_is_approved():
    result = run_gate()

    assert result.returncode == 0, result.stdout + result.stderr
    assert "RELEASE APPROVED" in result.stdout


def test_tampered_artifact_is_blocked():
    assert TAMPERED.is_file(), "Run the tampering test setup first."

    result = run_gate(str(TAMPERED))

    assert result.returncode != 0
    assert "RELEASE BLOCKED" in result.stdout
    assert (
        "FAIL: Artifact SHA-256 integrity verification" in result.stdout
    ), result.stdout + result.stderr


def test_artifact_and_signature_bundle_exist():
    assert ARTIFACT.is_file()
    assert (ROOT / "cosign.pub").is_file()
    assert (
        ROOT / "artifacts" / "demo-package.zip.bundle.json"
    ).is_file()
