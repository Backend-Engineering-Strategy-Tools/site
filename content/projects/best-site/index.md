---
title: "This Site"
date: 2026-06-18
draft: false
showReadingTime: false
layout: single
tags: ["hugo", "github-pages", "cicd", "static-site"]
---

This started as an effort to clean up and publish existing notes — things accumulated over years of work that were sitting in various raw forms and never properly written up. The act of publishing forces a level of clarity that private notes rarely get: you have to explain the context, fill the gaps, and decide what actually matters.

It doubles as deliberate practice in documentation. Getting into the habit of writing things up properly — not just as a record of what was done, but as something useful to come back to — is a skill that compounds. The site is both the output and the exercise.

Practically it also serves as a personal reference: a place to look things up that I have actually done and know the details of, rather than re-deriving them from scratch.

**Stack:** Hugo static site using the [Stack theme](https://github.com/CaiJimmy/hugo-theme-stack) v4 via Go modules. Deployed to [GitHub Pages](https://pages.github.com/) via GitHub Actions.

**Repo:** [Backend-Engineering-Strategy-Tools/site](https://github.com/Backend-Engineering-Strategy-Tools/site)

---

## Why Hugo

Static is the right default for content that does not need dynamic rendering. Hugo is fast — full site builds in milliseconds — and its template model maps well to a Go-centric mindset. The theme ecosystem is good and the Stack theme in particular supports the layout and content model needed here without significant customisation.

---

## Build Pipeline

The GHA workflow runs on push to `main`:

1. **Fetch private assets** — CV and cover letter PDFs are stored in a private release on a separate repo. The workflow fetches them via GitHub API using a scoped `BEST_SITE_PAT` secret and writes them into `static/cv/` before the build.
2. **Hugo build** — `hugo --minify` via the official `ghcr.io/gohugoio/hugo` Docker image, producing `public/`.
3. **Deploy** — `actions/deploy-pages` pushes `public/` to GitHub Pages.

This keeps CV content separate from site code — the PDF repo can be updated independently without touching the site repo, and a site redeploy picks up the latest version.

---

## Theme Customisation

Stack theme v4 is imported via `go.mod`. Hugo's lookup order means local files in `layouts/` or `assets/` override the theme without forking it.

The main override is `layouts/_default/single.html` — the site uses `layout: single` on all content pages to get full-width rendering (no sidebar). All pages also set `showReadingTime: false` in front matter.

---

## Domain

Currently served at `backend-engineering-strategy-tools.github.io/site/`. A redirect from `best.mjnet.info` is set up via an S3 static website bucket — no files in the bucket, just a redirect rule. DNS managed in Route53.

**S3 bucket setup** (bucket name must match domain):

```bash
aws s3api create-bucket \
  --bucket best.mjnet.info \
  --region eu-central-1 \
  --create-bucket-configuration LocationConstraint=eu-central-1

aws s3api put-public-access-block \
  --bucket best.mjnet.info \
  --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

aws s3api put-bucket-website \
  --bucket best.mjnet.info \
  --website-configuration '{"IndexDocument":{"Suffix":"index.html"},"RoutingRules":[{"Redirect":{"Protocol":"https","HostName":"backend-engineering-strategy-tools.github.io","ReplaceKeyPrefixWith":"site/"}}]}'
```

**Route53 ALIAS record** pointing `best.mjnet.info` at the S3 website endpoint:

```bash
aws route53 change-resource-record-sets \
  --hosted-zone-id <ZONE_ID> \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "best.mjnet.info",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z21DNDUVLTQW6Q",
          "DNSName": "s3-website.eu-central-1.amazonaws.com",
          "EvaluateTargetHealth": false
        }
      }
    }]
  }'
```

`Z21DNDUVLTQW6Q` is the fixed AWS hosted zone ID for S3 website endpoints in `eu-central-1`.

---

## Content Model

Two sections with distinct purposes:

| Section | Tone | What goes here |
|---------|------|----------------|
| `homelab/` | Narrative, first-person | What actually happened — the sequence, dead ends, workarounds |
| `public-notes/` | Reference, factual | How things work — distilled, structured, without the personal journey |

The separation keeps the narrative and reference writing from muddying each other. A reader looking for a quick reference does not want to read about what went wrong first; a reader following the homelab story wants the context.

`projects/` and `thinking/` round out the structure — projects are documented outcomes, thinking is longer-form analysis.

---

## What's Next

The current setup — Hugo on GitHub Pages — is the right foundation for a content-heavy site. A few things are planned or in progress:

- **Custom domain** — `best.mjnet.info` redirect via S3 + Route53 (see Domain section above). Proper custom domain with HTTPS as a follow-up.
- **Better build pipeline** — replacing the Makefile with a [Dagger](/public-notes/cicd/dagger/) Go module for local/CI parity and pinned Hugo versions.
- **More content** — the backlog of notes and projects is long. The site grows as things get cleaned up and published.

Longer term, the intent is to grow this into a more multi-faceted site — login-protected sections, dynamic content, interactive tooling. Hugo handles the static part well; the approach is to add separate paths alongside it for authentication and dynamic content rather than replacing the static foundation. The static site stays fast and low-cost, dynamic parts layer in where they are actually needed.
