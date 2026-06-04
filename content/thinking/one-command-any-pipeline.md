---
title: "These Are Not the Pipelines You Are Looking For"
date: 2026-06-04
draft: false
showReadingTime: false
layout: single
tags: ["cicd", "make", "dagger", "pipelines", "build"]
---

There are a lot of [CI/CD platforms](/public-notes/cicd/platforms/). GitHub Actions, Tekton, Jenkins, Jenkins X, Harness, Bitbucket Pipelines, GitLab CI, CircleCI, Argo Workflows. The choice between them is a perennial argument — and mostly the wrong one.

The mistake is putting your build logic inside the pipeline. Once you do that, the pipeline owns your build. Reproducing a failure locally means setting up the CI environment. Switching platforms means rewriting all the steps. Testing the pipeline means pushing a commit and waiting. The platform becomes load-bearing.

The fix is straightforward: keep all logic in [Make](/public-notes/cicd/make/) or [Dagger](/public-notes/cicd/dagger/). The pipeline calls one command. `make build`. `make test`. `dagger call publish`. That's it.

---

The pipeline shrinks to thin orchestration: trigger on a git event, check out the code, call the command, report the result. It does not know what the build does. It does not care. You can swap GitHub Actions for Tekton or Tekton for Argo Workflows and the only thing that changes is the YAML wrapper around the same command.

More importantly: you can run the same command on your laptop. No CI environment to replicate, no "it works locally but fails in CI" gap to debug. The build is the build, wherever it runs.

---

This matters more the longer a project lives. Build tools consolidate and diverge. Platforms get acquired, deprecated, or repriced. Jenkins pipelines from five years ago are maintained by people who weren't there when they were written and can't run them outside of Jenkins. The projects that survive these transitions cleanly are the ones where the build logic was never in the pipeline to begin with — it was in a Makefile or a build tool that could run anywhere.

[Gradle](/public-notes/cicd/build-systems/), Maven, Make — these predate CI/CD platforms by decades and will outlast the current generation of them. Put your logic there. The pipeline is a trigger and a reporter. Keep it that way.

---

The pattern in practice:

```makefile
build:
    docker build -t myimage:$(VERSION) .

test:
    go test ./...

publish:
    docker push myimage:$(VERSION)
```

```yaml
# GitHub Actions — the entire pipeline
steps:
  - uses: actions/checkout@v4
  - run: make build
  - run: make test
  - run: make publish
```

```yaml
# Tekton — same command, different wrapper
steps:
  - name: build-test-publish
    image: golang:1.22
    script: |
      make build
      make test
      make publish
```

Same logic. One command. Any pipeline.
