---
title: "vLLM"
description: "vLLM reference — high-throughput LLM inference engine using PagedAttention for maximum GPU utilisation under concurrent load."
date: 2026-05-14
draft: false
tags: ["vllm", "llm", "inference", "gpu", "serving"]
---

vLLM is a high-throughput inference engine for large language models. It implements PagedAttention — a memory management technique that dramatically improves GPU utilisation during inference — and provides an OpenAI-compatible API out of the box.

https://docs.vllm.ai/

---

## Why It Exists

Standard transformer inference wastes GPU memory because the KV cache for each request is pre-allocated contiguously. PagedAttention manages KV cache in non-contiguous pages (like OS virtual memory), enabling continuous batching across requests and much higher throughput under concurrent load.

The practical result: vLLM can serve significantly more requests per second per GPU than a naive implementation.

---

## Key Features

- **OpenAI-compatible REST API** — drop-in replacement for the OpenAI completions and chat endpoints
- **Continuous batching** — new requests join mid-flight rather than waiting for a full batch to finish
- **Quantisation** — GPTQ, AWQ, bitsandbytes (int8/int4)
- **Tensor parallelism** — split a model across multiple GPUs
- **Model support** — Llama, Mistral, Qwen, Phi, Gemma, and most HuggingFace-compatible architectures

---

## Quick Start

```bash
pip install vllm

python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.2-3B-Instruct \
  --quantization awq \
  --port 8000
```

Then use it like the OpenAI API:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "meta-llama/Llama-3.2-3B-Instruct", "messages": [{"role": "user", "content": "Hello"}]}'
```

---

## When to Use vLLM

- Multi-user or concurrent inference load
- Production-grade throughput matters
- You need tensor parallelism across multiple GPUs
- You want quantised model support with a clean API

For single-user or low-concurrency use with a constrained GPU, [Ollama](/public-notes/ai/ollama/) may be simpler to operate. vLLM's advantage shows under concurrent load.

---

## Related

- [vLLM documentation](https://docs.vllm.ai/)
- [Ollama](/public-notes/ai/ollama/) — simpler alternative for single-user or low-concurrency use
- [LLM inference in the homelab](/homelab/llm-inference/)
