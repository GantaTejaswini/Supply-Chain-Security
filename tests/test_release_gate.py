
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

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


def test_signature_failure_blocks_release():
    from scripts import release_gate

    with (
        patch.object(release_gate, "ROOT", ROOT),
        patch.object(release_gate, "DEFAULT_ARTIFACT", ARTIFACT),
        patch.object(release_gate, "PUBLIC_KEY", ROOT / "cosign.pub"),
        patch.object(
            release_gate,
            "BUNDLE",
            ROOT / "artifacts" / "demo-package.zip.bundle.json",
        ),
        patch.object(release_gate.shutil, "which") as mock_which,
        patch.object(release_gate, "run_check") as mock_check,
        patch.object(sys, "argv", [str(GATE)]),
    ):
        mock_which.side_effect = ["cosign", "gh"]
        mock_check.side_effect = [True, False, True]

        result = release_gate.main()

    assert result == 1
    assert [call.args[1] for call in mock_check.call_args_list] == [
        "Artifact SHA-256 integrity verification",
        "Cosign signature verification",
        "GitHub build-provenance verification",
    ]


def test_provenance_failure_blocks_release():
    from scripts import release_gate

    with (
        patch.object(release_gate, "ROOT", ROOT),
        patch.object(release_gate, "DEFAULT_ARTIFACT", ARTIFACT),
        patch.object(release_gate, "PUBLIC_KEY", ROOT / "cosign.pub"),
        patch.object(
            release_gate,
            "BUNDLE",
            ROOT / "artifacts" / "demo-package.zip.bundle.json",
        ),
        patch.object(release_gate.shutil, "which") as mock_which,
        patch.object(release_gate, "run_check") as mock_check,
        patch.object(sys, "argv", [str(GATE)]),
    ):
        mock_which.side_effect = ["cosign", "gh"]
        mock_check.side_effect = [True, True, False]

        result = release_gate.main()

    assert result == 1
    assert [call.args[1] for call in mock_check.call_args_list] == [
        "Artifact SHA-256 integrity verification",
        "Cosign signature verification",
        "GitHub build-provenance verification",
    ]
