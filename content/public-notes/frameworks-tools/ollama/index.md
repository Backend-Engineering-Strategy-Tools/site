---
title: "Ollama"
date: 2026-05-14
draft: false
tags: ["ollama", "llm", "inference", "local", "serving"]
---

Ollama is a local LLM runner. Single binary, model library, REST API. The fastest path from zero to a running model on your own hardware.

https://ollama.com/

---

## What it does

Ollama wraps llama.cpp (and other backends) with a clean CLI and REST API. You pull a model by name, it downloads and quantizes if needed, and you're serving completions from localhost. OpenAI-compatible API included.

```bash
ollama pull llama3.2:3b
ollama run llama3.2:3b
```

Or via API:

```bash
curl http://localhost:11434/api/generate \
  -d '{"model": "llama3.2:3b", "prompt": "Hello"}'
```

---

## Key Concepts

**Modelfile** — a Dockerfile-like definition for customising a model: system prompt, parameters, template.

```
FROM llama3.2:3b
SYSTEM "You are a helpful assistant for infrastructure tasks."
PARAMETER temperature 0.7
```

**Model library** — https://ollama.com/library — pre-quantized models ready to pull. Includes Llama, Mistral, Phi, Qwen, Gemma, and many others.

**GGUF format** — Ollama uses GGUF (llama.cpp's model format). Q4_K_M quantization is the common balance of quality vs size.

---

## GPU Support

Ollama detects and uses available GPUs automatically (NVIDIA CUDA, Apple Metal, AMD ROCm). Falls back to CPU if no GPU is available — slower but functional.

For NVIDIA on Linux, the CUDA toolkit must be installed on the host (or available to the container). Under Talos, this means using the NVIDIA GPU Operator.

---

## When to Use Ollama

- Single-user or development use
- You want minimal setup overhead
- Constrained GPU or CPU-only inference
- Quick model experimentation before committing to a production stack

For concurrent multi-user serving or production throughput, [vLLM](/public-notes/frameworks-tools/vllm/) is the better choice.

---

## Related

- [Ollama model library](https://ollama.com/library)
- [vLLM](/public-notes/frameworks-tools/vllm/) — production serving alternative for concurrent workloads
- [LLM inference in the homelab](/homelab/llm-inference/)
