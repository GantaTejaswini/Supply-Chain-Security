# Supply-Chain Security Project
A Python-based software supply-chain security project that demonstrates artifact integrity verification, Software Bill of Materials (SBOM) validation, vulnerability scanning, cryptographic signing, build-provenance verification, and automated release decisions.
## 1. Project Objectives
- Create a sample software artifact.
- Calculate and verify SHA-256 checksums.
- Generate and validate CycloneDX SBOMs.
- Scan dependency manifests for vulnerabilities, misconfigurations, and exposed secrets.
- Sign artifacts using Cosign.
- Verify signatures using a public key and signature bundle.
- Verify GitHub Actions build provenance.
- Block releases when required security checks fail.
- Automate security testing with pytest.
- Run security checks through GitHub Actions.
## 2. Technology Stack
- Python
- pytest
- Git and GitHub Actions
- Syft
- Trivy
- Cosign
- GitHub CLI (`gh`)
- SHA-256
- CycloneDX
- Bandit
## 3. Project Structure
```text
Supply-Chain-Security/
├── .github/
│   └── workflows/
│       └── ci.yml
├── artifacts/
│   ├── demo-package.zip
│   ├── demo-package.zip.bundle.json
│   ├── sbom.cyclonedx.json
│   └── sbom-python-env.cyclonedx.json
├── docs/
├── reports/
│   ├── artifact-sha256.txt
│   └── trivy-fs-report.json
├── scripts/
│   ├── create_artifact.py
│   ├── release_gate.py
│   ├── validate_sbom.py
│   ├── verify_artifact.py
│   └── vulnerability_gate.py
├── tests/
│   ├── test_release_gate.py
│   ├── test_sbom_validator.py
│   └── test_vulnerability_gate.py
├── .gitignore
├── cosign.pub
├── requirements-dev.txt
└── README.md
```
Generated artifacts and reports can vary depending on the pipeline execution.
## 4. Prerequisites
Install and configure:
- Python 3.12
- Git
- Syft
- Trivy
- Cosign
- GitHub CLI (`gh`)
The required command-line tools must be available in PowerShell. Python dependencies are listed in `requirements-dev.txt`.
## 5. Set Up the Python Environment
Open PowerShell in the project directory:
```powershell
cd E:\Supply-Chain-Security
```
Create the virtual environment if it does not already exist:
```powershell
python -m venv .venv
```
Activate it:
```powershell
.\.venv\Scripts\Activate.ps1
```
Install development dependencies:
```powershell
python -m pip install -r requirements-dev.txt
```
## 6. Create and Verify an Artifact
Create the sample package and its SHA-256 evidence:
```powershell
python scripts\create_artifact.py
```
Verify its integrity:
```powershell
python scripts\verify_artifact.py
```
The integrity check compares the artifact's calculated SHA-256 digest with the expected digest recorded by the project.
A matching digest establishes that the artifact matches the recorded hash. It does not, by itself, prove who created the artifact.
## 7. Generate and Validate an SBOM
An SBOM lists software components and related metadata.
Generate a CycloneDX SBOM for the Python virtual environment using your installed Syft executable. For example, if Syft is in the Downloads directory:
```powershell
& "$env:USERPROFILE\Downloads\syft_1.54.1_windows_amd64\syft.exe" scan dir:.venv\Lib\site-packages -o cyclonedx-json=artifacts\sbom-python-env.cyclonedx.json
```
Use the actual Syft executable path on your machine.
Validate an SBOM with the project validator:
```powershell
python scripts\validate_sbom.py artifacts\sbom-python-env.cyclonedx.json
```
Regenerate and revalidate the SBOM when dependencies change. An SBOM describes discovered components; it does not guarantee that those components are vulnerability-free.
## 8. Scan Dependencies
Run a Trivy filesystem scan:
```powershell
trivy fs --timeout 15m --detection-priority comprehensive --file-patterns 'pip:requirements-.*\.txt' --scanners vuln,misconfig,secret --skip-dirs .venv --skip-dirs .git --format json --output reports\trivy-fs-report.json .
```
Review the resulting report:
```powershell
Get-Content .\reports\trivy-fs-report.json -TotalCount 40
```
Run the project's vulnerability gate according to its configured inputs and options:
```powershell
python scripts\vulnerability_gate.py --help
```
Use the arguments shown by the script's help output for your local report and policy configuration.
A successful scan is not proof that no vulnerabilities exist. Review findings, scanner coverage, and the policy used to decide whether findings block a release.
## 9. Sign and Verify an Artifact
Cosign signing uses a private key. Keep the private key and its password confidential.
If you need to create a key pair and do not already have one:
```powershell
cosign-windows-amd64 generate-key-pair
```
Use the actual Cosign executable name available on your machine.
Sign the artifact:
```powershell
cosign-windows-amd64 sign-blob --key cosign.key --bundle artifacts\demo-package.zip.bundle.json artifacts\demo-package.zip
```
Verify its signature:
```powershell
cosign-windows-amd64 verify-blob --key cosign.pub --bundle artifacts\demo-package.zip.bundle.json artifacts\demo-package.zip
```
A successful signature verification confirms that the signature matches the artifact and the supplied public key. It does not independently establish the trustworthiness of the build process.
## 10. Release Gate
Run:
```powershell
python scripts\release_gate.py
```
The release gate checks the following requirements:
1. **Artifact integrity:** SHA-256 verification must succeed.
2. **Signature verification:** Cosign must verify the artifact using the public key and signature bundle.
3. **Build provenance:** GitHub CLI must verify the artifact's GitHub attestation against the configured repository and signer workflow.
The gate fails closed: if a required check fails or a required tool or file is missing, the release is blocked.
**Important:** A locally generated artifact does not automatically have a GitHub build attestation. To pass provenance verification, use an artifact with a matching, verifiable attestation from the configured repository and workflow.
## 11. Test Tamper Detection
Create a modified copy of the artifact:
```powershell
python -c "from pathlib import Path; p=Path('artifacts/demo-package.zip'); Path('artifacts/demo-package-tampered.zip').write_bytes(p.read_bytes()+b'TAMPERED')"
```
Run the release gate against the modified copy:
```powershell
python scripts\release_gate.py artifacts\demo-package-tampered.zip
```
The modified artifact should not be approved. The integrity and signature checks should detect that the supplied bytes do not match the original evidence.
Remove the test copy when finished:
```powershell
Remove-Item .\artifacts\demo-package-tampered.zip
```
## 12. Run Automated Tests
Run all tests:
```powershell
python -m pytest -v
```
The test suite covers release-gate decisions, SBOM validation, and vulnerability-gate behavior, including failure cases.
Test counts can change as new tests are added. Use the actual pytest summary as the authoritative result.
## 13. Continuous Integration
The GitHub Actions workflow is located at:
```text
.github/workflows/ci.yml
```
The pipeline automates configured security checks and tests. Depending on the workflow configuration and execution context, it can include static analysis, SBOM generation and validation, vulnerability scanning, artifact signing, GitHub build attestations, release-gate checks, and artifact uploads.
Inspect the workflow and the latest GitHub Actions run to confirm which jobs executed and passed.
## 14. Final Local Validation
Run:
```powershell
python -m compileall -q scripts tests
python -m pytest -v
git status --short
```
Run the release gate separately when you have the artifact, signature bundle, public key, Cosign, GitHub CLI, and a verifiable GitHub attestation available:
```powershell
python scripts\release_gate.py
```
## 15. Security Considerations
- Never commit or share `cosign.key` or its password.
- Keep signing credentials secure and restrict access to them.
- Keep the public key and signature bundle available to authorized verifiers.
- Recreate the hash evidence and signature bundle whenever the artifact changes.
- Regenerate the SBOM and repeat relevant security scans after dependency changes.
- Review vulnerability findings instead of assuming that a successful scan guarantees zero vulnerabilities.
- Verify the provenance of the exact artifact being released.
- Protect CI credentials and use least-privilege workflow permissions.
- Treat local test results and CI results as evidence of the checks performed, not as proof of complete security.
## 16. Current Scope and Future Work
This project currently focuses on supply-chain security checks, command-line tooling, automated tests, and CI/CD integration.
A web frontend, an HTTP backend, deployment features, and additional production hardening are separate extensions and should not be considered implemented until they are built and tested.
## 17. Conclusion
The project demonstrates a security-focused artifact lifecycle: package creation, integrity verification, SBOM validation, vulnerability scanning, cryptographic signing, provenance verification, and release gating.
Together, these controls provide multiple layers of evidence to help prevent modified or insufficiently verified artifacts from being approved for release.
