---
title: "SLSA — Supply-chain Levels for Software Artifacts"
date: 2026-06-03
draft: false
showReadingTime: false
---

SLSA (pronounced "salsa") is a framework for securing the software supply chain. Developed by Google, now under the OpenSSF. The core question it answers: how do you know the artifact you are deploying is actually what was built from the source you think it was?

The answer is **provenance**: cryptographically signed metadata that records what built an artifact, from what source, when, and under what conditions. SLSA defines levels of increasing rigour around how that provenance is generated and verified.

---

## Why it matters

The software supply chain is an attack surface. SolarWinds, XZ Utils, Log4Shell — different attack vectors but the same underlying problem: something got into the build or the dependency that should not have been there, and nobody noticed until it was too late.

SLSA does not prevent all supply chain attacks. It makes certain classes of attack verifiably harder and gives consumers of an artifact a way to check that it was built the way it claims to have been.

---

## The levels

SLSA defines three build levels (reorganised from the original four in SLSA v1.0):

**L1 — Provenance exists**
The build produces signed provenance documenting what produced the artifact. Any build system, any format. Protects against accidental tampering and gives a starting point for verification.

**L2 — Hosted build, signed provenance**
Build runs on a hosted CI platform (GitHub Actions, Cloud Build, etc.). Provenance is generated and signed by the build platform, not the developer's machine. Harder to falsify — an attacker needs to compromise the build platform, not just a developer laptop.

**L3 — Hardened build**
Ephemeral, isolated build environment. Non-falsifiable provenance — the build platform itself signs the provenance in a way that even a compromised build script cannot forge. Parameterless builds where the inputs are fully declared.

---

## Provenance in practice

Provenance is a JSON document (SLSA uses the [in-toto Attestation Framework](https://github.com/in-toto/attestation)) that records:

- The source repository and commit
- The build platform and workflow
- The artifact digest(s)
- The builder identity

It is signed using [Sigstore](https://www.sigstore.dev/) / cosign, which provides keyless signing backed by OIDC identity. No key management required for the common case.

---

## Tooling

**SLSA GitHub Generator**: reusable GitHub Actions workflows that generate SLSA L3 provenance for common artifact types (Go binaries, container images, Maven/Gradle packages). The easiest path to L3 on GitHub Actions.

**cosign**: signs and verifies container images and provenance attestations. Part of the Sigstore project.

**slsa-verifier**: CLI tool to verify SLSA provenance against an artifact. Used by consumers to check that an artifact meets a required SLSA level.

**Dependency Track / Grype / Trivy**: SBOM and vulnerability scanning tools that complement SLSA (SLSA is about build integrity, SBOM is about knowing what is in the artifact — related but distinct).

---

## SLSA and container images

Container images are a natural fit. The image digest is the artifact, provenance attests to the build that produced it, cosign attaches the attestation to the registry.

```bash
# verify an image has SLSA provenance
slsa-verifier verify-image \
  ghcr.io/myorg/myimage@sha256:abc123 \
  --source-uri github.com/myorg/myrepo \
  --source-tag v1.0.0
```

For the [tooling images](/thinking/shared-tooling-images/) pattern — images published to a registry that teams depend on — SLSA provenance is worth adding. It gives consumers a verifiable chain from source to image.

---

## Practical adoption

**L1** is low friction. Generate provenance as part of the build, attach it to the release. Most CI platforms make this straightforward.

**L2** requires a hosted build platform (most teams already use one) and using the platform's signing rather than rolling your own.

**L3** requires workflow changes — ephemeral environments, parameterless builds, using the SLSA GitHub Generator or equivalent. More investment but achievable for a standard GitHub Actions project.

Start at L1. Provenance exists, the chain is documented, the habit is established. L2 and L3 follow naturally as the pipeline matures — you are not making a big architectural decision, you are incrementally tightening what you already have.

In practice: never seen L1, L2, or L3 required explicitly by a client or platform. It is still "good idea in theory" territory for most teams. That said, the underlying practices — signed builds, traceable artifacts, reproducible pipelines — show up as requirements all the time, just not always under the SLSA name.

Which points to what SLSA actually is: a name and a framework for practices that are already good ideas. Automate the build, sign the output, record the provenance. Quality follows from automation — it frees up time to iterate, makes review easier, and ensures consistency without manual discipline. SLSA formalises that and gives you a vocabulary to talk about it with others. The levels are a ladder, not a checklist to complete before you can ship.

---

## Related

- [Shared Tooling Images](/thinking/shared-tooling-images/): SLSA provenance applies directly to published tooling images
- [GitHub Actions](/public-notes/cicd/github/): where SLSA GitHub Generator workflows run
