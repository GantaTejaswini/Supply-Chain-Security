\# Supply-Chain Security Project



\## 1. Overview



This project demonstrates a software supply-chain security workflow. It creates a sample software artifact, generates a Software Bill of Materials (SBOM), scans dependency manifests, signs the artifact using Cosign, and verifies its integrity before release.



The release gate approves an artifact only when both its SHA-256 integrity check and Cosign signature verification succeed.



\## 2. Objectives



\- Generate a software package.

\- Calculate and verify SHA-256 checksums.

\- Generate a CycloneDX SBOM using Syft.

\- Scan dependency manifests using Trivy.

\- Sign software artifacts using Cosign.

\- Verify digital signatures using a public key.

\- Block modified or tampered artifacts.

\- Automate security checks using Python and pytest.



\## 3. Technologies Used



\- Python 3.12

\- pytest

\- Git

\- Trivy

\- Syft

\- Cosign

\- SHA-256

\- CycloneDX



\## 4. Project Structure



```text

Supply-Chain-Security/

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

│   ├── create\_artifact.py

│   ├── verify\_artifact.py

│   └── release\_gate.py

├── tests/

│   └── test\_release\_gate.py

├── .gitignore

├── cosign.pub

├── requirements-dev.txt

└── README.md

```



The private key `cosign.key` is stored locally and must never be committed to Git or shared publicly.



\## 5. Prerequisites



Install Python 3.12, Git, Trivy, Syft, and Cosign. Ensure the relevant executable commands are accessible from PowerShell.



\## 6. Environment Setup



Open PowerShell in the project directory:



```powershell

cd E:\\Supply-Chain-Security

```



Activate the virtual environment:



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



Install dependencies:



```powershell

python -m pip install -r requirements-dev.txt

```



\## 7. Create the Artifact



Generate the sample ZIP package and SHA-256 evidence:



```powershell

python scripts\\create\_artifact.py

```



Verify artifact integrity:



```powershell

python scripts\\verify\_artifact.py

```



The verification succeeds when the actual SHA-256 digest matches the recorded digest.



\## 8. Generate the SBOM



Generate a CycloneDX SBOM for the installed Python environment:



```powershell

\& "$env:USERPROFILE\\Downloads\\syft\_1.54.1\_windows\_amd64\\syft.exe" scan dir:.venv\\Lib\\site-packages -o cyclonedx-json=artifacts\\sbom-python-env.cyclonedx.json

```



The SBOM records discovered software components and their metadata. Regenerate it when dependencies change.



\## 9. Scan Dependencies with Trivy



Run the dependency-manifest security scan:



```powershell

trivy fs --timeout 15m --detection-priority comprehensive --file-patterns 'pip:requirements-.\*\\.txt' --scanners vuln,misconfig,secret --skip-dirs .venv --skip-dirs .git --format json --output reports\\trivy-fs-report.json .

```



The results are saved to:



```text

reports/trivy-fs-report.json

```



This is a manifest-focused scan, not a guarantee that the entire project is vulnerability-free.



\## 10. Sign the Artifact



If you do not already have a signing key pair, generate one:



```powershell

cosign-windows-amd64 generate-key-pair

```



Keep the private key and its password confidential.



Sign the artifact:



```powershell

cosign-windows-amd64 sign-blob --key cosign.key --bundle artifacts\\demo-package.zip.bundle.json artifacts\\demo-package.zip

```



Verify the signature:



```powershell

cosign-windows-amd64 verify-blob --key cosign.pub --bundle artifacts\\demo-package.zip.bundle.json artifacts\\demo-package.zip

```



Expected successful output:



```text

Verified OK

```



\## 11. Run the Release Gate



Execute the release gate:



```powershell

python scripts\\release\_gate.py

```



Expected result:



```text

RELEASE APPROVED: All security checks passed.

```



The release gate performs two checks:



1\. SHA-256 artifact integrity verification.

2\. Cosign signature verification.



If either check fails, the release is blocked.



\## 12. Test Tamper Detection



Create a modified copy of the artifact:



```powershell

python -c "from pathlib import Path; p=Path('artifacts/demo-package.zip'); Path('artifacts/demo-package-tampered.zip').write\_bytes(p.read\_bytes()+b'TAMPERED')"

```



Run the release gate against the modified copy:



```powershell

python scripts\\release\_gate.py artifacts\\demo-package-tampered.zip

```



Expected result:



```text

RELEASE BLOCKED: One or more security checks failed.

```



This demonstrates that modified artifacts fail the integrity and signature checks.



\## 13. Automated Testing



Run the automated test suite:



```powershell

python -m pytest -v

```



The tests verify:



1\. The original artifact is approved.

2\. A tampered artifact is blocked.

3\. The artifact, public key, and signature bundle exist.



Expected result for the current test suite:



```text

3 passed

```



\## 14. Final Validation



Run the following commands before submitting the project:



```powershell

python -m compileall -q scripts tests

python -m pytest -v

python scripts\\release\_gate.py

git status --short

```



\## 15. Security Considerations



\- Never commit or share `cosign.key` or its password.

\- Keep the public key and signature bundle available for verification.

\- Rebuild the hash evidence and signature bundle whenever the artifact changes.

\- Regenerate the SBOM and repeat dependency scans after dependency changes.

\- Review scan reports instead of assuming that a successful scan guarantees zero vulnerabilities.

\- The current project demonstrates local security checks; production CI/CD integration and deployment hardening are additional extensions.



\## 16. Conclusion



The Supply-Chain Security project demonstrates software artifact creation, integrity verification, SBOM generation, dependency scanning, cryptographic signing, automated release gating, and tamper detection.



These controls help establish whether an artifact matches its recorded evidence and has a valid signature before it is approved for release.

