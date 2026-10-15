# Security Pipeline Guide
## 1. Purpose
The pipeline checks software artifacts and their supporting security evidence before release approval.
## 2. Security Controls
| Control | Purpose |
|---|---|
| SHA-256 | Detects changes to artifact contents relative to the recorded digest. |
| SBOM validation | Checks the generated Software Bill of Materials against the project's validation rules. |
| Trivy | Scans supported project files for vulnerabilities, misconfigurations, and secrets. |
| Bandit | Performs static security analysis of Python code when configured in the workflow. |
| Cosign | Signs artifacts and verifies signatures against a public key. |
| GitHub Attestations | Provides verifiable build-provenance evidence. |
| pytest | Tests security-gate decisions and failure handling. |
The exact controls executed in CI are determined by `.github/workflows/ci.yml`.
## 3. Release Approval
The release gate in `scripts/release_gate.py` requires:
1. The target artifact to exist.
2. The public key and signature bundle to exist.
3. Cosign and GitHub CLI to be available.
4. SHA-256 integrity verification to succeed.
5. Cosign signature verification to succeed.
6. GitHub attestation verification to succeed for the configured repository and signer workflow.
If a required check fails, the release gate returns a failure status and blocks approval.
## 4. Failure Testing
The release-gate tests cover successful approval and failure scenarios, including tampered artifacts and simulated signature or provenance verification failures.
These tests demonstrate the gate's fail-closed decision logic. Mocked failure tests do not replace cryptographic verification against real invalid signatures or forged attestations.
## 5. Operational Guidance
- Never commit the Cosign private key or its password.
- Keep the public key available to authorized verifiers.
- Rebuild artifact hashes and signatures whenever artifact contents change.
- Generate and validate a fresh SBOM when dependencies change.
- Review scanner findings and the configured vulnerability policy.
- Verify provenance for the exact artifact being released.
- Review the GitHub Actions results before approving a release.
## 6. Limitations
Successful checks provide evidence for the controls that actually ran. They do not guarantee that the software is entirely free of vulnerabilities or that every aspect of the build environment is secure.
The current project focuses on security tooling and CI/CD. Frontend and backend services are separate future development work.
