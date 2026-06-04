---
title: "Configuration Management — Puppet, Chef, Salt"
date: 2026-06-03
draft: false
showReadingTime: false
layout: single
tags: ["configuration-management", "puppet", "chef", "salt", "iac"]
---

Before Terraform, before Kubernetes, before immutable infrastructure — configuration management tools were how you kept servers in a known state. Puppet, Chef, and Salt are the main players. All three solve the same core problem: a fleet of servers that should all look a certain way, continuously enforced.

They predate the cloud-native era and show their age in places, but they are still running in a lot of enterprise environments and still the right tool in some specific contexts.

---

## The shared model

All three follow a similar pattern:

- You describe the desired state of a system (packages installed, files present, services running, users configured)
- An agent runs on each managed node and enforces that state continuously
- Changes are made by updating the desired-state declaration, not by SSHing in and running commands

This is fundamentally different from Ansible's push model — Puppet, Chef, and Salt agents pull or receive configuration rather than waiting for a push. The continuous enforcement is the key property: a manual change to a managed server gets corrected on the next agent run.

---

## Puppet

**Model**: declarative DSL, agent pulls catalog from Puppet Server on a schedule (default 30 min).

**Language**: Puppet DSL — a declarative, domain-specific language for describing resources. Not a general programming language.

```puppet
package { 'nginx':
  ensure => installed,
}

service { 'nginx':
  ensure  => running,
  enable  => true,
  require => Package['nginx'],
}

file { '/etc/nginx/nginx.conf':
  source  => 'puppet:///modules/nginx/nginx.conf',
  notify  => Service['nginx'],
}
```

**Puppet Forge**: a large community module library — the main reason Puppet still has traction. Many vendors publish official Puppet modules for their software.

**Where it lives**: large enterprise environments that adopted it early and built significant module libraries around it. The inertia is real — migrating away is a significant project.

---

## Chef

**Model**: agent-based, Ruby DSL. Configuration is written as cookbooks containing recipes.

**Language**: Ruby — specifically a DSL built on Ruby. More expressive than Puppet's DSL, but requires Ruby knowledge and brings the associated complexity.

```ruby
package 'nginx'

service 'nginx' do
  action [:enable, :start]
end

template '/etc/nginx/nginx.conf' do
  source 'nginx.conf.erb'
  notifies :restart, 'service[nginx]'
end
```

**Chef Solo vs Chef Server**: Chef Solo runs without a server — cookbooks live locally or in version control. Chef Server is the full model with a central catalog and reporting. Knife is the CLI for managing Chef infrastructure.

**Where it lives**: similar story to Puppet — enterprises that adopted it early. Chef introduced the "infrastructure as code" framing before it was a widely used term. Less common in new projects, but still found running in organisations that built their automation around it.

---

## Salt

**Model**: agent-based (minions), master/minion architecture, ZeroMQ message bus for fast communication. Can also run agentless (SSH mode) like Ansible.

**Language**: YAML state files (SLS), with Jinja templating. More approachable than Puppet DSL or Chef Ruby.

```yaml
nginx:
  pkg.installed: []
  service.running:
    - enable: True
    - require:
      - pkg: nginx

/etc/nginx/nginx.conf:
  file.managed:
    - source: salt://nginx/files/nginx.conf
    - watch_in:
      - service: nginx
```

**Speed**: the ZeroMQ bus makes Salt significantly faster than Puppet or Chef for large fleets — sending a command to thousands of nodes and getting results back is near-instant.

**Event-driven**: Salt has a reactor system — events on nodes can trigger automatic responses. More dynamic than Puppet or Chef's scheduled pull model.

**Where it lives**: still used in organisations that needed to manage very large fleets efficiently. SaltStack was acquired by VMware, then Broadcom — commercial trajectory uncertain. The open-source Salt project continues.

---

## Comparison

| | Puppet | Chef | Salt |
|--|--|--|--|
| Language | Puppet DSL | Ruby | YAML + Jinja |
| Model | Agent, pull | Agent, pull/push | Agent, push (ZeroMQ) |
| Learning curve | Medium | High (Ruby) | Medium |
| Scale | Good | Good | Excellent |
| Community | Large (Forge) | Medium | Medium |
| Status | Declining (new projects) | Declining | Uncertain (VMware/Broadcom) |

---

## Where they still make sense

**Long-lived fleets of traditional VMs or bare metal** — if you have thousands of servers that are not containers and are not going away, a continuous enforcement model still makes sense. Terraform provisions them; Puppet/Chef/Salt keeps them configured.

**Network devices** — see [Ansible](../ansible/) for this use case; Ansible is the clearer choice, but Salt also has network automation modules.

**Legacy enterprise** — if the organisation has already built a Puppet or Chef codebase, migrating everything to a new tool is a significant project with real risk. Maintaining the existing automation often makes more sense than rewriting it.

---

## The general direction

New projects in the cloud-native era rarely reach for these tools. Immutable infrastructure (build a new image, replace the server) removes the need for continuous configuration enforcement. Kubernetes handles application configuration. Terraform handles provisioning. The gap these tools filled is smaller now.

That said, not all infrastructure is cloud-native, and "replace everything" is rarely a realistic option in a large organisation. These tools will be running in enterprise environments for years.

---

## See also

- [Ansible](../ansible/) — the agentless alternative that won the mindshare battle
- [Terraform](../terraform/) — handles the provisioning side; often used alongside config management
- [Crossplane](../crossplane/) — the Kubernetes-native model that may be the long-term successor for cloud-native environments
