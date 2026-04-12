---
name: public-notes section
description: Learning-in-public notes section — published notes across cloud-infra, observability, security, and tools
type: project
---

The `content/public-notes/` section is live and growing.

**Why:** User wants a "learning in public" notes section tied to their professional profile.

**Published notes (draft: false):**

*Cloud infrastructure*
- `cloud-infrastructure/kubernetes/` — polished prose, 12 architecture diagrams
- `cloud-infrastructure/ansible/` — text only
- `cloud-infrastructure/terraform/` — Terragrunt folded in (stub removed), multi-env patterns, testing/validation
- `cloud-infrastructure/cdk/` — AWS CDK (Java), honest take: slow, CloudFormation drift, cross-stack export/import pain, SSM workaround

*CI/CD*
- `cicd/git/` — workflows, merge vs rebase, branch strategies
- `cicd/gitea/` — renamed from gogs; covers Gogs → Gitea → Forgejo lineage, Forgejo recommended for new deployments, kubectx mention, issue tracker screenshots
- `cicd/argo/` — GitOps, App of Apps, repo structure, bootstrap sequence, self-management

*Observability*
- `observability/prometheus/` — kube-prometheus-stack (with CRD workaround), ServiceMonitor, PromQL, alerting, Metrics Server
- `observability/grafana/` — data sources, dashboards, variables, the observability trio
- `observability/loki/` — SingleBinary vs SimpleScalable, Promtail deprecation/Alloy, ArgoCD install manifest, LogQL

*Security*
- `security/ssh/` — key pairs, certificate auth (with diagrams), ssh config, hardening

*Frameworks/tools*
- `frameworks-tools/nginx/` — reverse proxy, SSL termination, load balancing, rate limiting
- `frameworks-tools/docker/` — Docker & OCI, Podman, Buildah, Skopeo, ORAS, Compose
- `frameworks-tools/k9s/` — K9s (TUI, preferred) + Lens merged; kubectx/kubens section included

*Languages*
- `languages/bash/`, `languages/golang/`, `languages/java/`, `languages/python/` — all published

**Draft stubs (content not yet written):**

*Cloud infrastructure*
- `ceph/`, `cm/`, `etcd/`, `istio/`, `k3d/`, `k3s/`, `kind/`, `kubevirt/`, `microk8s/`, `minikube/`, `rook/`
- `keda/`, `karpenter/`, `lvm/`, `odf/`, `velero/`

*CI/CD*
- `cicd/github/`, `cicd/tekton/`

*Observability*
- `observability/jaeger/`

*Security*
- `security/bastion/`, `security/cert-manager/`, `security/certbot/`, `security/clair/`
- `security/freeipa/`, `security/k8s-secrets/`, `security/kyverno/`
- `security/letsencrypt/`, `security/luks/`, `security/osquery/`, `security/snort/`, `security/sssd/`

*Frameworks/tools*
- `frameworks-tools/decktape/`, `frameworks-tools/elasticsearch/`, `frameworks-tools/hugo/`
- `frameworks-tools/idea/`, `frameworks-tools/kibana/`, `frameworks-tools/kvm/`
- `frameworks-tools/markdown/`, `frameworks-tools/molecule/`, `frameworks-tools/nexus/`
- `frameworks-tools/reloader/`, `frameworks-tools/reveal/`, `frameworks-tools/sonarqube/`
- `frameworks-tools/structure101/`

**Technical setup:**
- All pages use page bundles (folder + index.md) — Stack theme render hook requirement
- Images referenced with relative paths (no leading `/`)
- Local dev: `make serve` (uses local Hugo extended)
- `canonifyURLs = true` in config.toml
- No pilotfish/pfn org references in any published content — use example-org/example.io

**Style:**
- Problem→solution narrative preferred (user's sentiment): lead with the pain, then introduce the tool
- Honest, opinionated takes welcome (e.g. Forgejo over Gitea, K9s over Lens, Terraform over CDK)
- Related tools folded into one note rather than thin stubs (Terragrunt→Terraform, Lens→K9s, Buildah/Podman→Docker)

**How to apply:** Priority draft candidates: keda, karpenter, kyverno, jaeger, cert-manager, velero, reloader, k8s-secrets. Problem→solution narrative ready from user's notes for most of these.
