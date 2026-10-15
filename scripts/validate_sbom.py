import json
import sys
from pathlib import Path
DEFAULT_SBOM_PATH = Path("artifacts/sbom-project.cyclonedx.json")
EXPECTED_FORMAT = "CycloneDX"
EXPECTED_SPEC_VERSION = "1.6"
def load_sbom(path: Path) -> dict:
    """Load an SBOM and validate its format, version, and components."""
    if not path.is_file():
        raise FileNotFoundError(f"Required SBOM file is missing: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            f"Cannot read valid SBOM JSON from {path}: {error}"
        ) from error
    if not isinstance(data, dict):
        raise ValueError("SBOM must contain a JSON object.")
    if data.get("bomFormat") != EXPECTED_FORMAT:
        raise ValueError(
            f"SBOM format must be {EXPECTED_FORMAT}, "
            f"got {data.get('bomFormat')!r}."
        )
    version = data.get("specVersion")
    if version != EXPECTED_SPEC_VERSION:
        raise ValueError(
            f"Expected CycloneDX {EXPECTED_SPEC_VERSION}, got {version!r}."
        )
    components = data.get("components")
    if not isinstance(components, list) or not components:
        raise ValueError("SBOM must contain a non-empty components list.")
    for index, component in enumerate(components):
        if not isinstance(component, dict):
            raise ValueError(
                f"SBOM component at index {index} must be an object."
            )
        name = component.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"SBOM component at index {index} must have a non-empty name."
            )
    return data
def main() -> int:
    if len(sys.argv) > 2:
        print(
            "Usage: python scripts/validate_sbom.py [SBOM_PATH]",
            file=sys.stderr,
        )
        return 2
    path = Path(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_SBOM_PATH
    try:
        sbom = load_sbom(path)
    except (FileNotFoundError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2
    print("PASS: SBOM validation succeeded.")
    print(f"Format: {sbom['bomFormat']}")
    print(f"Specification: {sbom['specVersion']}")
    print(f"Components: {len(sbom['components'])}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
