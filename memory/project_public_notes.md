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
- `cloud-infrastructure/terraform/` — Terragrunt folded in, multi-env patterns, testing/validation
- `cloud-infrastructure/cdk/` — AWS CDK (Java), CloudFormation drift, cross-stack export/import pain, SSM workaround

*CI/CD*
- `cicd/git/` — workflows, merge vs rebase, branch strategies
- `cicd/gitea/` — Gogs→Gitea→Forgejo lineage, Forgejo recommended, issue tracker screenshots
- `cicd/argo/` — GitOps, App of Apps, repo structure, bootstrap, self-management

*Observability*
- `observability/prometheus/` — kube-prometheus-stack + CRD workaround, ServiceMonitor, PromQL, alerting, Metrics Server
- `observability/grafana/` — data sources, dashboards, variables, the observability trio
- `observability/loki/` — SingleBinary vs SimpleScalable, Promtail deprecation/Alloy, ArgoCD install manifest, LogQL

*Security*
- `security/ssh/` — key pairs, certificate auth (with diagrams), ssh config, hardening

*Frameworks/tools*
- `frameworks-tools/nginx/` — reverse proxy, SSL termination, load balancing, rate limiting
- `frameworks-tools/docker/` — Docker & OCI, Podman, Buildah, Skopeo, ORAS, Compose
- `frameworks-tools/k9s/` — K9s (TUI) + Lens merged, kubectx/kubens included

*Languages*
- `languages/bash/`, `languages/golang/`, `languages/java/`, `languages/python/` — all published

**Draft stubs (content not yet written):**

*Cloud infrastructure — high priority (problem→solution material ready)*
- `keda/`, `karpenter/`, `velero/`, `lvm/`, `odf/`
- `rook/` (has rook.svg), `ceph/` (has ceph.png)
- `etcd/`, `istio/`, `k3s/`, `k3d/`, `kind/`, `microk8s/`, `minikube/`, `kubevirt/`, `cm/`

*CI/CD*
- `cicd/github/` (has githubpages.svg), `cicd/tekton/`

*Observability*
- `observability/jaeger/`

*Security — high priority*
- `security/k8s-secrets/` — comparison note: CSI driver vs ESO vs SOPS vs Sealed Secrets
- `security/kyverno/`, `security/cert-manager/`
- `security/certbot/` (has svg), `security/letsencrypt/` (has svg)
- `security/freeipa/` (has images), `security/clair/` (has png)
- `security/osquery/` (has png), `security/snort/` (has png)
- `security/bastion/`, `security/luks/`, `security/sssd/`
- `security/_index.md` — still draft: true, security section hidden from production

*Frameworks/tools*
- `frameworks-tools/reloader/` — high priority
- `frameworks-tools/hugo/` (has svg), `frameworks-tools/reveal/` (has images)
- `frameworks-tools/idea/`, `frameworks-tools/markdown/` (has svg)
- `frameworks-tools/molecule/`, `frameworks-tools/nexus/`, `frameworks-tools/sonarqube/`
- `frameworks-tools/elasticsearch/`, `frameworks-tools/kibana/`
- `frameworks-tools/kvm/`, `frameworks-tools/decktape/`, `frameworks-tools/structure101/`

**Technical setup:**
- All pages use page bundles (folder + index.md) — Stack theme render hook requirement
- Images referenced with relative paths (no leading `/`)
- Local dev: `make serve` (uses local Hugo extended)
- `canonifyURLs = true` in config.toml
- No pilotfish/pfn org references in any published content — use example-org/example.io
- Breadcrumbs implemented via `layouts/partials/breadcrumbs.html` + `assets/scss/custom.scss`

**Style:**
- Problem→solution narrative preferred: lead with the pain, then introduce the tool
- Honest, opinionated takes welcome (Forgejo over Gitea, K9s over Lens, Terraform over CDK)
- Related tools folded into one note rather than thin stubs (Terragrunt→Terraform, Lens→K9s, Buildah/Podman→Docker)
