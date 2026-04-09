---
name: public-notes section creation
description: Created a learning-in-public notes section from DevOpsStack slide repo — in progress, user will review before publishing
type: project
---

Converted the DevOpsStack reveal-hugo presentation repo (https://github.com/senare/DevOpsStack) into a `content/public-notes/` section in the mjnet Hugo Stack site.

**Why:** User wants a "learning in public" notes section. The source material was 51 reveal.js slide decks covering DevOps/cloud-native topics. All pages are set to `draft: true` pending review.

**What was done:**
- Cloned DevOpsStack into `TmpDevOpsStack/` (inside the site repo — can be deleted after review)
- Wrote and ran `convert_notes.py` (also deletable) which:
  - Converted TOML front matter → YAML
  - Stripped reveal-hugo shortcodes (`{{% section %}}`, `{{< slide >}}`, etc.)
  - Converted slide image backgrounds → markdown images
  - Converted YouTube shortcodes → links
  - Converted highlight shortcodes → fenced code blocks
  - Removed internal navigation links
  - Stripped `/senare/` prefix from all image paths → `/images/`
- Copied `TmpDevOpsStack/static/images/` → `static/images/`

**Structure created:**
```
content/public-notes/
├── _index.md
├── container-orchestration/   kubernetes, microk8s, minikube, kind, k3d, k3s, kubevirt, istio
├── cicd-gitops/               git, github, gogs, tekton, argo
├── infrastructure-as-code/    ansible, terraform, terragrunt, cm
├── storage-and-data/          ceph, rook, etcd, elasticsearch, kibana
├── security/                  clair, freeipa, sssd, certbot, letsencrypt, luks, snort, bastion, ssh, osquery
├── monitoring/                prometheus, grafana
├── containers/                docker, nexus
├── development/               golang, python, java, junit, bash, markdown, idea
└── tools/                     hugo, reveal, decktape, structure101, molecule, sonarqube, kvm, nginx
```

**How to apply:** Next session: user will have reviewed the drafts. Go through categories together, enrich content, flip `draft: false` to publish. Many stub pages (15-line originals) have just a title + logo — these need real content added before publishing.
