
from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
REPORT_DIR = ROOT / "reports"

ARTIFACT_PATH = ARTIFACT_DIR / "demo-package.zip"
REPORT_PATH = REPORT_DIR / "artifact-sha256.txt"

PACKAGE_CONTENT = (
    "Synthetic package for the FreshersUniverse PRD 09 project.\n"
    "This package contains no production code or credentials.\n"
).encode("utf-8")


def main():
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Fixed metadata helps produce a reproducible ZIP artifact.
    info = ZipInfo(
        "package/README.txt",
        date_time=(2024, 1, 1, 0, 0, 0),
    )
    info.compress_type = ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16

    with ZipFile(ARTIFACT_PATH, "w") as archive:
        archive.writestr(info, PACKAGE_CONTENT)

    digest = sha256(ARTIFACT_PATH.read_bytes()).hexdigest()

    report = (
        f"Artifact: {ARTIFACT_PATH.relative_to(ROOT).as_posix()}\n"
        f"SHA-256: {digest}\n"
    )

    REPORT_PATH.write_text(report, encoding="utf-8")

    print("Synthetic artifact created successfully.")
    print(f"Artifact: {ARTIFACT_PATH}")
    print(f"SHA-256:  {digest}")
    print(f"Evidence: {REPORT_PATH}")


if __name__ == "__main__":
    main()
