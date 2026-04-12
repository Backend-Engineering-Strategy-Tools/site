---
title: "NGINX"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
---

![NGINX](NGINX.svg)

NGINX is a high-performance web server and reverse proxy built around an event-driven, non-blocking architecture. Where Apache spawns a thread per connection, NGINX handles thousands of concurrent connections from a small, fixed number of worker processes — making it well-suited to acting as the entry point for modern distributed systems.

## Server blocks

NGINX configuration is structured around `server` blocks (analogous to Apache's VirtualHost). Each block defines how to handle requests for a given hostname or port:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        root /var/www/html;
        index index.html;
    }
}
```

Multiple server blocks in a single NGINX instance handle traffic for different domains — NGINX selects the block by matching the `Host` header against `server_name`.

## Reverse proxy

The primary use case in infrastructure work: NGINX sits in front of application servers and forwards requests to them. The application never needs to be exposed directly.

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

`X-Forwarded-For` and `X-Real-IP` headers pass the original client IP to the upstream — without these the application sees only the proxy address.

## SSL termination

NGINX handles TLS and speaks plain HTTP to backends. This centralises certificate management and offloads crypto from application processes:

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://127.0.0.1:8080;
    }
}

# Redirect HTTP → HTTPS
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}
```

Pair with [Let's Encrypt](../letsencrypt/) and Certbot for automated certificate issuance and renewal.

## Load balancing

NGINX distributes traffic across multiple upstream instances using an `upstream` block:

```nginx
upstream app {
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;
    server 10.0.0.3:8080;
}

server {
    listen 80;
    location / {
        proxy_pass http://app;
    }
}
```

Default is round-robin. Other strategies: `least_conn` (fewest active connections), `ip_hash` (sticky sessions by client IP), `hash` (consistent hashing by arbitrary key).

## Static files

NGINX serves static assets efficiently — far more so than most application frameworks. A common pattern: serve static files directly from NGINX, proxy only dynamic requests to the application.

```nginx
location /static/ {
    alias /var/www/static/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location / {
    proxy_pass http://app;
}
```

## Useful patterns

**Rate limiting** — protect endpoints from abuse:
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://app;
}
```

**Health check path** — expose a simple status endpoint:
```nginx
location /healthz {
    access_log off;
    return 200 "ok\n";
    add_header Content-Type text/plain;
}
```

Test config before reloading: `nginx -t`. Reload without dropping connections: `nginx -s reload`.

## Resources

- [NGINX documentation](https://nginx.org/en/docs/)
- [NGINX config generator](https://www.digitalocean.com/community/tools/nginx)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
