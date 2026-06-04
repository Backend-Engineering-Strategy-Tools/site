---
title: "Managing Secrets in Kubernetes"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["kubernetes", "secrets", "security", "vault", "external-secrets", "csi"]
---

Kubernetes has a built-in `Secret` resource, but it is not a secrets management solution — it is base64-encoded storage with no encryption at rest by default and no access audit trail. How you actually manage secrets in a Kubernetes cluster depends on how far you need to go beyond the default.

## Native Kubernetes Secrets

The baseline. A `Secret` is a key-value store mounted into pods as environment variables or files:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  username: YWRtaW4=   # base64("admin")
  password: cGFzc3dvcmQ=
```

The problems: base64 is encoding, not encryption. Secrets are stored in etcd — enabling etcd encryption at rest is a cluster configuration step that is easy to skip. Secrets are visible to anyone with `kubectl get secret` in that namespace. For anything beyond a local dev cluster or a low-sensitivity workload, you need something more.

## Sealed Secrets

A Kubernetes controller from Bitnami. `SealedSecret` resources contain secrets encrypted with the cluster's public key — only the controller running in that cluster can decrypt them. The encrypted form is safe to commit to Git, which makes GitOps workflows possible without a separate secrets store. Simple to operate, no external dependency. The tradeoff: secrets are tied to a specific cluster's key, cross-cluster sharing requires re-encryption, and there is no centralised audit trail.

## External Secrets Operator

ESO reads secrets from an external store (AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager, Azure Key Vault, 1Password) and syncs them into native Kubernetes Secrets. Your source of truth stays in the external system; the K8s Secret is a read-only projection of it, refreshed on a configurable interval:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: db-credentials
  data:
    - secretKey: password
      remoteRef:
        key: prod/db/password
```

ESO is the right choice when you already have a secrets store and want Kubernetes workloads to consume from it without changing how secrets are managed elsewhere.

## Secrets Store CSI Driver

An alternative to ESO for the same problem: mount secrets from an external store directly as files in a pod, without creating a Kubernetes Secret at all. The secret materialises only in the pod's filesystem, is not stored in etcd, and disappears when the pod terminates. Supported by AWS, Azure, GCP, and Vault providers. Used in combination with a `SecretProviderClass` to define what to fetch and where to mount it.

## HashiCorp Vault

A dedicated secrets management platform. Vault stores arbitrary secrets, issues dynamic credentials (database passwords that expire, AWS IAM credentials valid for an hour), manages PKI, and provides a full audit log of every read and write. Kubernetes workloads authenticate to Vault via the Kubernetes auth method (using the pod's service account token) and receive a Vault token scoped to the secrets their service account is allowed to read. More to operate than the other options, but the right answer for organisations that need dynamic credentials, fine-grained access control, and audit logs.

## Summary

| Approach | Good for |
|---|---|
| Native Secrets | Local dev, low-sensitivity workloads |
| Sealed Secrets | GitOps, single-cluster, no external dependency |
| External Secrets Operator | Syncing from existing external stores |
| Secrets Store CSI | Avoiding etcd entirely, file-based secret injection |
| HashiCorp Vault | Dynamic credentials, audit logs, enterprise requirements |

## Resources

- [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets)
- [External Secrets Operator](https://external-secrets.io/)
- [Secrets Store CSI Driver](https://secrets-store-csi-driver.sigs.k8s.io/)
- [HashiCorp Vault on Kubernetes](https://developer.hashicorp.com/vault/docs/platform/k8s)
