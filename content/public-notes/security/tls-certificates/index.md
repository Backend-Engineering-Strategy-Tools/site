---
title: "TLS Certificates — Let's Encrypt, Certbot, cert-manager"
date: 2024-01-01
draft: false
showReadingTime: false
layout: single
tags: ["tls", "certificates", "letsencrypt", "certbot", "cert-manager", "security"]
---

TLS certificates prove that a server is who it claims to be and encrypt traffic in transit. Getting and renewing them used to mean manual requests to a CA, waiting days, and calendar reminders to renew before expiry. Let's Encrypt automated the entire process in 2015 and made it free. Today there is no reason to run a public service without TLS.

## Let's Encrypt

A free, automated, open certificate authority run by the Internet Security Research Group. Let's Encrypt issues Domain Validation (DV) certificates valid for 90 days, automatically, via the ACME protocol. The short lifetime is intentional — it forces automation and limits the window if a certificate is compromised. Let's Encrypt is now the largest CA in the world by certificates issued. You never interact with Let's Encrypt directly; you use an ACME client that speaks the protocol on your behalf.

## Certbot

The EFF's ACME client — the most widely used way to obtain and renew Let's Encrypt certificates on a Linux server. Certbot handles the ACME challenge (proving you control the domain), fetches the certificate, installs it into your web server config (nginx, Apache), and sets up a cron job or systemd timer for automatic renewal. For a straightforward public-facing server, Certbot is the default choice:

```bash
certbot --nginx -d example.com -d www.example.com
```

Certbot supports HTTP-01 challenges (serve a file over port 80) and DNS-01 challenges (add a TXT record — required for wildcard certificates and useful when port 80 isn't accessible).

```bash
# Wildcard cert via DNS challenge
certbot certonly --manual --preferred-challenges dns -d "*.example.com"
```

Renewals run automatically. Check the timer is active:

```bash
systemctl status certbot.timer
```

## cert-manager

The Kubernetes-native way to manage certificates. cert-manager runs as a controller in the cluster and automates the full certificate lifecycle — requesting, renewing, and storing certificates as Kubernetes `Secret` resources. It supports Let's Encrypt via ACME (HTTP-01 and DNS-01 challenges) as well as other issuers (Vault, Venafi, self-signed).

A `ClusterIssuer` configures the CA once for the whole cluster:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: alb
```

A `Certificate` resource then requests a cert for a specific domain — or an Ingress annotation triggers cert-manager automatically. The certificate is stored as a Secret and mounted into pods or referenced by the Ingress. Renewal happens automatically before expiry.

## Resources

- [Let's Encrypt documentation](https://letsencrypt.org/docs/)
- [Certbot documentation](https://certbot.eff.org/docs/)
- [cert-manager documentation](https://cert-manager.io/docs/)
