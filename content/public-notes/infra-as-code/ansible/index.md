---
title: "Ansible"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["ansible", "configuration-management", "automation", "iac", "agentless"]
---

Ansible is an open-source automation tool for configuration management, application deployment, and orchestration. The key selling point: it's agentless — you push from a control machine over SSH, no daemon running on managed hosts.

## Why Ansible

- **Free and open source** — Red Hat maintains it, commercially supported via Ansible Automation Platform (formerly Tower)
- **Agentless** — no software to install on managed nodes; plain SSH is enough
- **Simple** — playbooks are YAML, readable without special knowledge
- **Flexible** — works on servers, cloud platforms, network devices, and bare-metal

## What it does

**Configuration management** — define what state a system should be in; Ansible gets it there and keeps it there.

**Application deployment** — deploy multi-tier applications with a playbook; let Ansible figure out the ordering and state transitions.

**Orchestration** — coordinate complex workflows across databases, networks, front-end and back-end services in the right order.

**Security and compliance** — enforce firewall rules, user policies, and security baselines across all hosts from a single playbook run.

**Cloud provisioning** — provision infrastructure on AWS, Azure, GCP, OpenStack, or bare-metal with the same tooling.

## Architecture

**Modules** — small programs pushed to nodes over SSH, executed, then removed. Ansible ships with 750+ modules for packages, services, files, cloud APIs, and more.

**Plugins** — extend Ansible's core: connection types, callbacks, caching, filtering. Write your own or use community plugins.

**Inventory** — a file (INI or YAML) listing all managed hosts, their IPs, groups, and variables. Can also pull dynamic inventory from AWS, GCP, Azure, etc.

**Playbooks** — YAML files describing tasks to run on which hosts. The core unit of work. Each play maps a group of hosts to a set of tasks; each task calls a module.

**APIs** — extend connection transports beyond SSH (WinRM for Windows, network device APIs, etc.).

## Ansible Automation Platform

Red Hat's commercial wrapper around Ansible. Adds a web UI, RBAC, job scheduling, audit logging, and a workflow editor. Worth it once you have multiple teams running automation.

## Where Ansible still excels

Network device configuration is the clearest remaining stronghold. Ansible has mature modules for switches, routers, and firewalls (Cisco IOS, Arista EOS, Juniper JunOS, and many others) and the agentless SSH model works well for network gear that can't run an agent. For network automation, Ansible is still state of the art.

For server configuration management — the original use case — most teams should consider moving to other models. Terraform manages provisioning, container images handle application configuration (immutable infrastructure), and Kubernetes operators handle runtime state. The gap Ansible used to fill is smaller.

## The configuration management landscape

Ansible is one of several tools in this space. The others worth knowing:

- **Salt** (SaltStack) — agent-based, event-driven, fast for large fleets. More complex than Ansible.
- **Puppet** — agent-based, declarative DSL, strong in enterprise. Puppet Forge has a large module library.
- **Chef** — agent-based, Ruby DSL, infrastructure as code before the term was common. Less common now.

See [Configuration Management — Puppet, Chef, Salt](../config-management/) for a full comparison.

All four predate the Kubernetes era. Ansible has survived best because it is agentless and YAML-based — lower barrier. The others are still found in large enterprise environments with long-lived infrastructure.

## Resources

- [docs.ansible.com](https://docs.ansible.com/)
- [ansible.com](https://www.ansible.com/)
