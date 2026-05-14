---
title: "LLM Inference on Bare Metal"
date: 2026-05-14
draft: true
showReadingTime: false
layout: single
tags: ["llm", "talos", "kubernetes", "vllm", "ollama", "bare-metal", "gpu", "inference"]
---

Serving LLM inference from the lab — an OpenAI-compatible API endpoint running on owned hardware. [ODEN](/homelab/inventory/systems/) is the candidate node: it has a PCIe x16 riser and will take the [GTX 770](/homelab/inventory/gpu/).

---

## Goal

A persistent inference endpoint on the lab network. Point a client at it and get completions back, same interface as the hosted APIs. Good for experimentation without burning API credits, and for testing things that require a local model.

---

## Stack

| Layer | Technology | Role |
|---|---|---|
| Provisioning | PXE + iPXE | Boot ODEN from bare metal |
| OS / Orchestration | [Talos](/public-notes/cloud-infrastructure/talos/) + Kubernetes | Immutable OS, container runtime |
| Inference serving | [vLLM](/public-notes/frameworks-tools/vllm/) or [Ollama](/public-notes/frameworks-tools/ollama/) | Model serving, OpenAI-compatible API |
| GPU | NVIDIA GTX 770 (2GB VRAM) | Currently unplaced — target: ODEN |

---

## Hardware Reality

The GTX 770 has 2GB of GDDR5 VRAM and 1536 CUDA cores. That is not much.

What's feasible:
- Quantized models (Q4_K_M or smaller): 3B parameter models may fit with 2GB VRAM at q4
- Speed: roughly 1–5 tokens/second at this scale
- Practical use: local tool calling, small reasoning tasks, experimentation

What's not feasible without better hardware:
- 7B+ models at reasonable quality
- Multi-user serving
- Anything approaching production throughput

The GTX 770 is a starting point. The value is in getting the infrastructure right so swapping in a better GPU later is a configuration change, not a rebuild.

---

## Tool Choice: vLLM vs Ollama

|  | [vLLM](/public-notes/frameworks-tools/vllm/) | [Ollama](/public-notes/frameworks-tools/ollama/) |
|---|---|---|
| Throughput | High (PagedAttention, continuous batching) | Lower |
| Setup complexity | Moderate — Kubernetes deployment, GPU operator | Minimal — single binary |
| OpenAI API compat | Yes | Yes |
| Quantisation support | GPTQ, AWQ, bitsandbytes (int8/int4 runtime) | GGUF (llama.cpp backend) |
| Homelab fit | Better when GPU + multi-user matters | Better for single-user, low overhead |

**Starting with Ollama** — lower overhead, easier to get running on a constrained GPU. Switch to vLLM if throughput becomes a bottleneck.

---

## Open Decisions

- GPU driver handling under Talos (NVIDIA GPU Operator — required, no host package manager)
- Model selection: TinyLlama, Phi-3 mini, or Qwen2-0.5B as realistic 2GB-VRAM targets
- Persistent model storage: Kubernetes PVC backed by the lab storage
- Exposing the endpoint: internal only, or through VyOS/OPNsense with auth

---

## Next Steps

1. Place GTX 770 in ODEN (SYS-005, PCIe x16 riser slot)
2. Install NVIDIA GPU Operator on the existing Talos cluster
3. Deploy Ollama via Helm, verify GPU is picked up
4. Pull a small quantized model, test completions
5. Evaluate whether vLLM is worth the extra complexity at this GPU scale

---

*Planning phase. None of this is running yet.*
