---
title: "Linux Identity Management — FreeIPA and SSSD"
date: 2024-01-01
draft: false
showReadingTime: false
layout: single
tags: ["freeipa", "sssd", "ldap", "kerberos", "identity", "linux", "security"]
---

Managing user accounts across many Linux machines by hand — creating the same user on every host, syncing passwords, maintaining sudo rules — breaks down fast. FreeIPA provides centralised identity management: one place to define users, groups, sudo rules, host policies, and SSH keys. SSSD is the daemon that runs on each Linux machine and connects it to FreeIPA (or any LDAP/Kerberos provider), making those central definitions available locally.

## FreeIPA

An integrated identity management solution from Red Hat, combining LDAP (389 Directory Server), Kerberos, DNS, a certificate authority, and a web UI into a single deployable stack. Users, groups, sudo rules, HBAC (host-based access control) rules, and SSH public keys are all managed centrally and enforced on enrolled hosts. FreeIPA is the open source upstream of Red Hat Identity Management (IdM).

Install on RHEL/Rocky/AlmaLinux:

```bash
dnf install freeipa-server
ipa-server-install --domain=example.com --realm=EXAMPLE.COM
```

Once the server is running, enroll a client host:

```bash
dnf install freeipa-client
ipa-client-install --server=ipa.example.com --domain=example.com
```

After enrollment, users defined in FreeIPA can log into the host with Kerberos SSO — no separate account needed on the machine.

## SSSD

The System Security Services Daemon. SSSD runs on each Linux host and mediates all identity lookups — NSS (name service switch) queries for users and groups, PAM authentication, sudo rule lookups. It caches responses locally so logins still work when the identity server is temporarily unreachable, and it handles the Kerberos ticket lifecycle transparently.

SSSD is not FreeIPA-specific. It supports:
- FreeIPA (the natural pairing)
- Active Directory (via the `ad` provider — direct AD integration without Samba)
- Generic LDAP and Kerberos

The `ipa-client-install` command configures SSSD automatically when enrolling a FreeIPA client. For AD integration, the configuration is similar but uses the `ad` provider:

```ini
[domain/example.com]
id_provider = ad
auth_provider = ad
access_provider = ad
ad_domain = example.com
krb5_realm = EXAMPLE.COM
```

## The pairing

FreeIPA and SSSD are complementary halves of the same solution. FreeIPA is the authoritative store — where you create and manage identities. SSSD is the enforcer on each host — it translates FreeIPA's policies into local authentication decisions, caches them for resilience, and keeps Kerberos tickets current. Neither replaces the other; together they give you centralised identity management with no single point of failure for login availability.

## Resources

- [FreeIPA documentation](https://www.freeipa.org/page/Documentation)
- [SSSD documentation](https://sssd.io/docs/)
- [Red Hat IdM documentation](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/managing_idm_users_groups_hosts_and_access_control_rules/)
