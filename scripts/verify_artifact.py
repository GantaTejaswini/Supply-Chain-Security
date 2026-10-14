
import argparse
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = ROOT / "artifacts" / "demo-package.zip"
REPORT_PATH = ROOT / "reports" / "artifact-sha256.txt"


def calculate_sha256(file_path: Path) -> str:
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def read_expected_sha256() -> str:
    if not REPORT_PATH.is_file():
        raise FileNotFoundError(
            f"Evidence report not found: {REPORT_PATH}"
        )

    report = REPORT_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"^SHA-256:\s*([0-9a-fA-F]{64})\s*$",
        report,
        flags=re.MULTILINE,
    )

    if match is None:
        raise ValueError(
            "Evidence report does not contain a valid SHA-256 digest."
        )

    return match.group(1).lower()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify an artifact against its recorded SHA-256 digest."
    )
    parser.add_argument(
        "artifact",
        nargs="?",
        type=Path,
        default=DEFAULT_ARTIFACT,
        help="Artifact path to verify (default: demo-package.zip)",
    )
    args = parser.parse_args()

    artifact_path = args.artifact
    if not artifact_path.is_absolute():
        artifact_path = ROOT / artifact_path

    try:
        if not artifact_path.is_file():
            raise FileNotFoundError(
                f"Artifact not found: {artifact_path}"
            )

        expected = read_expected_sha256()
        actual = calculate_sha256(artifact_path)

        print(f"Artifact: {artifact_path}")
        print(f"Expected SHA-256: {expected}")
        print(f"Actual SHA-256:   {actual}")

        if actual != expected:
            print("FAIL: Artifact integrity verification failed.")
            return 1

        print("PASS: Artifact integrity verification succeeded.")
        return 0

    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
