---
title: "Elasticsearch & Kibana"
date: 2024-01-01
draft: false
showReadingTime: false
layout: single
tags: ["elasticsearch", "kibana", "elk", "search", "observability", "logging"]
---

Elasticsearch is a distributed search and analytics engine built on Apache Lucene. Kibana is its web UI for querying, visualising, and exploring the data stored in Elasticsearch. Together they form the search and analysis layer of the ELK stack — typically with Logstash or Beats collecting and shipping data into Elasticsearch, and Kibana on top for humans to interact with it.

## Elasticsearch

A document store where every document is JSON and every field is indexed by default. Queries are also JSON, using a rich query DSL that supports full-text search, structured filters, aggregations, and geospatial queries. Elasticsearch is horizontally scalable — an index is split into shards, shards are distributed across nodes, and replicas provide redundancy. Adding nodes increases both capacity and query throughput.

```json
# Index a document
POST /logs/_doc
{
  "timestamp": "2026-06-04T12:00:00Z",
  "level": "error",
  "service": "api",
  "message": "connection refused"
}

# Search with filter
GET /logs/_search
{
  "query": {
    "bool": {
      "filter": [
        { "term": { "level": "error" } },
        { "term": { "service": "api" } }
      ]
    }
  }
}
```

At scale, index lifecycle management (ILM) policies handle the hot-warm-cold tiering automatically — recent indices stay on fast nodes, older indices roll to cheaper storage, and expired indices are deleted.

## Kibana

The interface to Elasticsearch. Kibana's core is **Discover** — a time-series log explorer with free-text search and field filtering — and **Dashboards** — composable visualisations (time series, bar charts, pie charts, data tables, maps) that query Elasticsearch directly. For log aggregation and observability use cases, a typical workflow is: ship logs into Elasticsearch via Filebeat or Logstash, explore them in Discover, build dashboards for the signals that matter, set up alerting rules on those patterns.

Kibana also hosts the Elastic APM UI (application performance monitoring), the SIEM app (security event correlation), and the Lens visual editor for building dashboards without writing aggregation queries by hand.

## ELK vs the Grafana stack

The Grafana stack ([Loki](/public-notes/observability/loki/) + [Prometheus](/public-notes/observability/prometheus/) + [Grafana](/public-notes/observability/grafana/)) has become the common alternative for cloud-native environments. The key difference: Loki indexes only log metadata (labels), not the full log content — it is cheaper to run and query at scale, but full-text search across log bodies is slower. Elasticsearch indexes everything and full-text search is fast, but the storage and memory cost is significantly higher. For log volumes in the hundreds of GB/day and above, the operational cost of Elasticsearch becomes the dominant factor. For environments that need fast full-text search across structured and unstructured data — logs, documents, events — Elasticsearch earns its cost.

## Resources

- [Elasticsearch documentation](https://www.elastic.co/docs/solutions/search)
- [Kibana documentation](https://www.elastic.co/docs/solutions/observability)
- [Elastic common schema (ECS)](https://www.elastic.co/guide/en/ecs/current/)
