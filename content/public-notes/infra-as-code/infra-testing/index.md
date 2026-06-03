---
title: "Infrastructure Testing — Molecule, Test Kitchen, InSpec, Chainsaw"
date: 2026-06-03
draft: false
showReadingTime: false
layout: single
---

Infrastructure code needs testing like application code does. The tools here cover different layers: role testing, integration testing, compliance checking, and Kubernetes end-to-end testing.

---

## Molecule — Ansible role testing

Molecule is the standard testing framework for Ansible roles and playbooks. It manages the full test lifecycle: spin up instances, apply the role, verify the result, tear everything down.

**Stages:**

```
molecule create    # spin up test instances (Docker, Podman, EC2, etc.)
molecule converge  # apply the role/playbook
molecule verify    # run assertions
molecule destroy   # clean up
molecule test      # full cycle in sequence
```

**Drivers** control where instances run — Docker or Podman for local development, EC2 or other cloud providers for closer-to-production testing.

**Verifiers** run assertions after converge. The default is Ansible itself (run a playbook of assertions), but [Testinfra](https://testinfra.readthedocs.io/) (pytest-based) and [Goss](https://github.com/goss-org/goss) are popular alternatives.

A minimal `molecule/default/molecule.yml`:

```yaml
driver:
  name: docker

platforms:
  - name: instance
    image: ubuntu:22.04

provisioner:
  name: ansible

verifier:
  name: ansible
```

Wire into CI: `molecule test` runs the full cycle and exits non-zero on failure.

---

## Test Kitchen — integration testing for infrastructure

Test Kitchen (kitchen.ci) is an integration testing framework originally built for Chef but now multi-platform. It creates instances, applies configuration, runs a verifier, and destroys.

**Drivers**: Docker, Vagrant, and cloud providers (EC2, GCP, Azure). Plugins also exist for Ansible (`kitchen-ansible`) and Terraform (`kitchen-terraform`).

**Verifiers**: InSpec (most common), Busser.

A `kitchen.yml` for a Chef cookbook:

```yaml
driver:
  name: docker

provisioner:
  name: chef_zero

verifier:
  name: inspec

platforms:
  - name: ubuntu-22.04

suites:
  - name: default
    verifier:
      inspec_tests:
        - test/integration/default
```

```bash
kitchen list      # show instance state
kitchen converge  # apply provisioner
kitchen verify    # run verifier
kitchen test      # full cycle
```

Test Kitchen is less commonly adopted outside Chef shops, but the multi-platform support means it can be useful for testing across providers in one framework.

---

## InSpec — compliance testing as code

InSpec (now Progress Chef InSpec) is a compliance testing framework. You write assertions about the state of a system — packages installed, ports listening, file permissions, user accounts — in a Ruby DSL. InSpec executes them locally, over SSH, against Docker containers, or against cloud APIs.

```ruby
describe package('nginx') do
  it { should be_installed }
end

describe service('nginx') do
  it { should be_running }
  it { should be_enabled }
end

describe port(80) do
  it { should be_listening }
end

describe file('/etc/nginx/nginx.conf') do
  its('mode') { should cmp '0644' }
end
```

**Profiles** are the distributable unit — a collection of controls with metadata. The InSpec community maintains profiles for CIS benchmarks, DISA STIGs, and other compliance standards.

**Where it fits**: compliance auditing, security baselines, post-deploy verification. Wired into CI as a final gate or run on a schedule against production.

```bash
inspec exec path/to/profile --target ssh://user@host
inspec exec path/to/profile --target docker://container-id
```

---

## Chainsaw — Kubernetes e2e testing

Chainsaw is a declarative end-to-end testing framework for Kubernetes. Originally from the Kyverno project, now standalone. Write test scenarios in YAML — apply manifests, assert on resource state, clean up — without writing Go or any test framework code.

Particularly useful for testing Kubernetes operators, controllers, and admission webhooks: the things that are hard to unit test because they depend on the Kubernetes API.

```yaml
apiVersion: chainsaw.kyverno.io/v1alpha1
kind: Test
metadata:
  name: basic-deployment
spec:
  steps:
  - name: create deployment
    try:
    - apply:
        resource:
          apiVersion: apps/v1
          kind: Deployment
          metadata:
            name: test-app
          spec:
            replicas: 2
            # ...
    - assert:
        resource:
          apiVersion: apps/v1
          kind: Deployment
          metadata:
            name: test-app
          status:
            readyReplicas: 2
  - name: cleanup
    try:
    - delete:
        ref:
          apiVersion: apps/v1
          kind: Deployment
          name: test-app
```

```bash
chainsaw test ./tests/
```

**vs Terratest for Kubernetes**: Terratest requires Go code; Chainsaw is YAML. For testing Kubernetes resources and operators specifically, Chainsaw is simpler to write and maintain.

---

## Terratest — Go-based infrastructure testing

Covered in the [Terraform page](../terraform/#testing-and-validation). The short version: Go tests that deploy real infrastructure, run assertions via cloud SDKs, then tear it down. The most complete integration testing approach for Terraform modules — and the highest cost in setup and test execution time.

---

## Choosing

| Tool | Best for | Language |
|------|----------|----------|
| Molecule | Ansible role testing | YAML + Python/Ansible |
| Test Kitchen | Multi-platform integration testing | YAML + Ruby (InSpec) |
| InSpec | Compliance assertions, security baselines | Ruby DSL |
| Chainsaw | Kubernetes operators and controllers | YAML |
| Terratest | Terraform module integration testing | Go |
