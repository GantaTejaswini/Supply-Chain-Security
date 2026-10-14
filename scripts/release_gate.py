import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = ROOT / "artifacts" / "demo-package.zip"
PUBLIC_KEY = ROOT / "cosign.pub"
BUNDLE = ROOT / "artifacts" / "demo-package.zip.bundle.json"
VERIFIER = ROOT / "scripts" / "verify_artifact.py"


def run_check(command: list[str], label: str) -> bool:
    print(f"\n[RELEASE GATE] {label}")

    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            text=True,
        )
    except OSError as error:
        print(f"ERROR: Could not execute check: {error}")
        return False

    if result.returncode != 0:
        print(f"FAIL: {label}")
        return False

    print(f"PASS: {label}")
    return True


def main() -> int:
    artifact = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_ARTIFACT

    if not artifact.is_absolute():
        artifact = ROOT / artifact

    if not artifact.is_file():
        print(f"BLOCKED: Artifact not found: {artifact}")
        return 1

    if not PUBLIC_KEY.is_file():
        print(f"BLOCKED: Public key not found: {PUBLIC_KEY}")
        return 1

    if not BUNDLE.is_file():
        print(f"BLOCKED: Signature bundle not found: {BUNDLE}")
        return 1

    integrity_ok = run_check(
        [sys.executable, str(VERIFIER), str(artifact)],
        "Artifact SHA-256 integrity verification",
    )

    signature_ok = run_check(
        [
            "cosign-windows-amd64",
            "verify-blob",
            "--key",
            str(PUBLIC_KEY),
            "--bundle",
            str(BUNDLE),
            str(artifact),
        ],
        "Cosign signature verification",
    )

    if not (integrity_ok and signature_ok):
        print("\nRELEASE BLOCKED: One or more security checks failed.")
        return 1

    print("\nRELEASE APPROVED: All security checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())