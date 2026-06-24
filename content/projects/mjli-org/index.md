---
title: "mjli.org — DNS & DNSSEC Lab"
date: 2026-06-22
draft: false
showReadingTime: false
layout: single
tags: ["dns", "dnssec", "aws", "route53", "s3", "cloudfront"]
---

Hands-on with DNS and DNSSEC in practice — registering a domain, configuring Route 53, getting a static site resolving, and walking the full chain of trust through DNSSEC signing. `mjli.org` is the lab domain; it carries forward into real use once the foundations are in place.

→ [DNS & DNSSEC concepts](/public-notes/networking/dns-dnssec/)

---

## Why

DNS and DNSSEC are the kind of thing that's easy to read about but only clicks when you've actually done it — watched a record propagate, confused the S3 website endpoint with the object URL, seen the DS record appear at the TLD. This is that hands-on pass.

The downstream motivation: [ExternalDNS](https://kubernetes-sigs.github.io/external-dns/) for the Kubernetes stack and a proper custom domain with HTTPS for the main site. Both require understanding how Route 53 hosted zones, alias records, and DNSSEC signing actually work before wiring them up.

---

## Architecture

Three phases, each adding a layer.

### Phase 1 — S3 static site

```text
User
 |
Route 53 (alias record)
 |
S3 website endpoint
```

Two S3 buckets:

- `mjli.org` — static website hosting enabled, contains `index.html`, public `s3:GetObject` policy
- `www.mjli.org` — static website hosting in redirect mode, target `mjli.org`

Route 53 A alias records point each name at its bucket's specific website endpoint.

**Route 53 alias records** are a proprietary extension — they behave like A records but can target AWS resources. Unlike CNAME, they work at the zone apex (`mjli.org` itself). No charge per query for alias records targeting AWS resources.

When creating alias records targeting S3 website endpoints, Route 53 requires a fixed hosted zone ID per region:

| Region | S3 website hosted zone ID |
|--------|--------------------------|
| `us-east-1` | `Z3AQBSTGFYJSTF` |
| `us-west-2` | `Z3BJ6K6RIION7M` |
| `eu-central-1` | `Z21DNDUVLTQW6Q` |
| `eu-west-1` | `Z1BKCTXD74EZPE` |

**The key confusion with S3:** AWS gives S3 three different URL forms, and only one is right for Route 53 alias targets.

| Form | Example | Use |
|------|---------|-----|
| Object URL | `https://s3.us-east-1.amazonaws.com/mjli.org/index.html` | Direct file access — proves the file exists, not a website target |
| REST endpoint | `https://mjli.org.s3.us-east-1.amazonaws.com` | API/SDK access — not for website hosting |
| Website endpoint | `http://mjli.org.s3-website-us-east-1.amazonaws.com` | Static website behavior — the alias target for Route 53 |

Pointing a Route 53 alias at the generic S3 hostname instead of the bucket-specific website endpoint routes traffic to S3 infrastructure with no bucket context — redirect config is never applied.

The website endpoint is HTTP only. HTTPS requires CloudFront.

### Phase 2 — CloudFront + HTTPS

```text
User
 |
Route 53 (alias record)
 |
CloudFront (ACM certificate, CF Function for www → apex redirect)
 |
S3 (private, Origin Access Control)
```

- ACM certificate in `us-east-1` (required for CloudFront) covering `mjli.org` and `www.mjli.org`
- CloudFront distribution with Origin Access Control — S3 bucket stays private, no public bucket policy needed
- CloudFront Function on viewer request: redirects `www.mjli.org` → `mjli.org` (replaces the redirect bucket)
- S3 origin uses the REST endpoint (not website endpoint) — CloudFront + OAC uses the S3 API, not the website hosting layer
- Route 53 alias records updated to CloudFront distribution

### Phase 3 — DNSSEC

DNSSEC signing enabled on the Route 53 hosted zone. AWS generates the Key Signing Key (KSK) backed by a KMS key (must be in `us-east-1`) and manages the Zone Signing Key (ZSK). DS record linked at the registrar — also Route 53 in this case, so it's self-contained. Chain of trust: root → `.org` TLD → `mjli.org` zone.

→ [DNSSEC concepts](/public-notes/networking/dns-dnssec/#dnssec)

---

## Build plan

### Phase 1 — S3 + Route 53

```bash
# Main bucket — static website hosting
aws s3api create-bucket --bucket mjli.org --region us-east-1

aws s3api put-public-access-block --bucket mjli.org \
  --public-access-block-configuration \
  BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

aws s3api put-bucket-website --bucket mjli.org \
  --website-configuration '{"IndexDocument":{"Suffix":"index.html"}}'

aws s3api put-bucket-policy --bucket mjli.org --policy '{
  "Version":"2012-10-17",
  "Statement":[{"Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::mjli.org/*"}]
}'

aws s3 cp index.html s3://mjli.org/

# Redirect bucket
aws s3api create-bucket --bucket www.mjli.org --region us-east-1

aws s3api put-bucket-website --bucket www.mjli.org \
  --website-configuration '{"RedirectAllRequestsTo":{"HostName":"mjli.org","Protocol":"http"}}'
```

Route 53 alias records: create A records for `mjli.org` and `www.mjli.org` with `AliasTarget` pointing at each bucket's website endpoint and hosted zone ID `Z3AQBSTGFYJSTF`.

Verify:
```
$ curl -I http://mjli.org
HTTP/1.1 200 OK
x-amz-id-2: S2XsD9TuC45HWGc1nN79g2HVrjk3wRcM44V9tU05g6jd40d4gDP6qs35mxlyziBxFdE0Hcv3b9o=
x-amz-request-id: 21PF1Q736ZNNCGMW
Date: Mon, 22 Jun 2026 14:42:46 GMT
Last-Modified: Mon, 22 Jun 2026 10:49:52 GMT
ETag: "d15286d4bd455e1abdd406bbc05b6cdf"
Content-Type: text/html
Content-Length: 419
Server: AmazonS3

$ curl -I http://www.mjli.org
HTTP/1.1 301 Moved Permanently
x-amz-request-id: 0QM3QMADJ7AE2ZQX
Date: Mon, 22 Jun 2026 14:43:00 GMT
Location: http://mjli.org/
Content-Length: 0
Server: AmazonS3

$ dig mjli.org A
;; ANSWER SECTION:
mjli.org.               5       IN      A       16.15.236.158
mjli.org.               5       IN      A       16.182.69.93
mjli.org.               5       IN      A       16.182.102.205
mjli.org.               5       IN      A       52.217.141.53
mjli.org.               5       IN      A       54.231.231.85
mjli.org.               5       IN      A       16.15.199.202
mjli.org.               5       IN      A       16.15.207.61
mjli.org.               5       IN      A       16.15.230.121
```

`Server: AmazonS3` and TTL 5s confirm traffic is hitting the S3 website endpoint directly. After Phase 2 this becomes `Server: CloudFront` over HTTPS with a longer TTL.

### Phase 2 — CloudFront + HTTPS

1. Request ACM certificate in `us-east-1` — domains `mjli.org` and `www.mjli.org`, DNS validation (Route 53 adds CNAME records automatically)
2. Create CloudFront distribution:
   - Origin: `mjli.org.s3.amazonaws.com` (REST endpoint, not website endpoint) with OAC
   - Alternate domain names: `mjli.org`, `www.mjli.org`
   - SSL certificate: the ACM cert
   - Default root object: `index.html`
3. Add CloudFront Function (viewer request) for www redirect:
   ```javascript
   function handler(event) {
     var request = event.request;
     if (request.headers.host.value === 'www.mjli.org') {
       return { statusCode: 301, statusDescription: 'Moved Permanently',
         headers: { location: { value: 'https://mjli.org' + request.uri } } };
     }
     return request;
   }
   ```
4. Re-enable Block Public Access on the S3 bucket; replace public bucket policy with OAC policy
5. Update Route 53 alias records to target the CloudFront distribution

Verify:
```bash
curl -I https://mjli.org        # 200, certificate valid
curl -I https://www.mjli.org    # 301 → https://mjli.org
```

### Phase 3 — DNSSEC

1. Route 53 → Hosted zones → `mjli.org` → DNSSEC signing → Enable
2. Create KMS key when prompted (or use existing; must be in `us-east-1`)
3. Copy the DS record values from Route 53
4. Route 53 → Registered domains → `mjli.org` → DNSSEC → add the DS key
5. Wait for propagation

Verify:
```bash
dig mjli.org DNSKEY
dig mjli.org DS
dig +dnssec mjli.org A           # look for AD flag
```

---

## Status

| | Status |
|-|--------|
| Domain registered in Route 53 | done |
| S3 static site — apex (`mjli.org`) | done |
| S3 static site — www redirect | done |
| Phase 2 — CloudFront + HTTPS | planned |
| Phase 3 — DNSSEC signing | planned |

---

## What's next

Once this is working end-to-end, the same architecture applies directly to:

- Migrating the main site to a proper custom domain with HTTPS (same CloudFront + ACM + Route 53 pattern)
- [ExternalDNS](https://kubernetes-sigs.github.io/external-dns/) writing Route 53 records for Kubernetes cluster services
