---
title: "AI Coding Assistants"
description: "Comparison of CLI AI coding assistants — Claude Code, Aider, Pi, and Google AI Studio, with honest assessments of each."
date: 2026-05-14
draft: false
tags: ["ai", "llm", "claude-code", "aider", "pi", "coding"]
showReadingTime: false
layout: single
---

CLI tools and agents that integrate into your development workflow rather than just answering questions in a browser tab. The difference from chat tools is that these read your files, run commands, and make edits directly — they operate on the codebase, not alongside it.

This is the move when we want the agents to start doing the work for us, talk is cheap action speaks for itself :)

---

## Claude Code

[docs.anthropic.com/claude-code](https://docs.anthropic.com/en/claude-code/getting-started)

Anthropic's CLI agent. Works in the terminal, reads the project, edits files, runs commands, and iterates. The setup cost is real — there are things to configure (permissions, `CLAUDE.md`, hooks), it has opinions about how things should work, and you are working within its harness rather than directing it freely. That said, once it is set up and calibrated to the project, the net effect is positive: it does the work, catches things you'd miss, and the compound value per session adds up quickly.

**Notable**: Claude Code is meaningfully more out-of-the-box than the alternatives. The harness, workflow, and defaults are all provided — you adapt to them, but you don't have to build them.

**Cost**: Requires a paid Anthropic subscription (Claude Pro / Max, ~$20–$100/mo depending on tier). There is no meaningful free tier for coding use.

**Honest assessment**:
The harness is opinionated; it is worth it here — someone else is developing the tooling, you have to adapt and learn to use their tooling and their workflows. However *they* are doing the work of building the tooling and designing some kind of workflow for using it. Not worth it if you only touch code occasionally — the subscription cost, and more importantly the need to learn and adapt to the tooling outpaces the benefit at low usage.

### Configuration files

| File                          | Scope              | Purpose                                                 |
|-------------------------------|--------------------|---------------------------------------------------------|
| `~/.claude/CLAUDE.md`         | Global             | Instructions applied to every project                   |
| `CLAUDE.md`                   | Project            | Project-specific instructions, conventions, preferences |
| `~/.claude/settings.json`     | Global             | Permissions, tools, hooks                               |
| `.claude/settings.json`       | Project            | Project-level permissions and hooks                     |
| `.claude/settings.local.json` | Local (gitignored) | Personal overrides, not shared                          |
| `~/.claude/commands/`         | Global             | Custom slash commands (skills)                          |
| `.claude/commands/`           | Project            | Project-specific slash commands                         |
| `~/.claude/memory/`           | Global             | Persistent memory across sessions                       |

---

## Aider

[aider.chat](https://aider.chat)

Open-source CLI coding assistant. Works with any model via API — OpenAI, Anthropic, Google AI Studio, OpenRouter, or local models. You run it from the terminal, it reads selected files, you chat with it and it commits changes. No project-level config files to maintain — you select files per session.

**Verdict**: Tried it — the interaction model didn't land. Aider's file selection flow and how it structures its edits felt like more overhead than it was worth. Good tool in concept, and the model flexibility is genuinely useful, but it didn't stick.

---

## Pi

[github.com/earendil-works/pi](https://github.com/earendil-works/pi)

Open-source CLI coding agent by Mario Zechner. Reads files, runs commands, makes edits — flexible on auth: works with pay-per-token API keys (Anthropic, OpenAI, Google) or existing subscriptions (Claude Pro/Max, ChatGPT Plus, GitHub Copilot).

**Install**:
```bash
npm install -g @earendil-works/pi-coding-agent
# then: export ANTHROPIC_API_KEY=... (or /login inside Pi)
pi
```

**Key commands**:

| Command     | Purpose                                                            |
|-------------|--------------------------------------------------------------------|
| `/verbose`  | Show internal reasoning and tool calls — **recommended, use this** |
| `/model`    | Switch models mid-session                                          |
| `/settings` | Adjust thinking level, theme, delivery mode                        |
| `/session`  | Show token usage for current session                               |
| `/compact`  | Manually compact context                                           |
| `/tree`     | Navigate session history, continue from any point                  |
| `/fork`     | Branch a new session from a previous message                       |
| `/resume`   | Pick up a previous session                                         |

### Configuration files

| File                           | Scope             | Purpose                                                       |
|--------------------------------|-------------------|---------------------------------------------------------------|
| `~/.pi/agent/AGENTS.md`        | Global            | Instructions applied to all projects (also reads `CLAUDE.md`) |
| `AGENTS.md` / `CLAUDE.md`      | Project + parents | Project instructions, loaded from current dir and up          |
| `~/.pi/agent/settings.json`    | Global            | Default model, theme, thinking level, compaction              |
| `.pi/settings.json`            | Project           | Project overrides (merged with global)                        |
| `~/.pi/agent/SYSTEM.md`        | Global            | Replace the default system prompt entirely                    |
| `.pi/SYSTEM.md`                | Project           | Project-level system prompt replacement                       |
| `.pi/APPEND_SYSTEM.md`         | Project           | Append to the system prompt without replacing it              |
| `~/.pi/agent/models.json`      | Global            | Add custom providers and models                               |
| `~/.pi/agent/keybindings.json` | Global            | Keyboard shortcut overrides                                   |

**Backends and context windows**:

A real upside of Pi's model flexibility: use your existing Claude Pro/Max subscription as a backend via `/login` (no extra API cost), then toggle to [Gemini 2.5 Flash](https://ai.google.dev/gemini-api/docs/models) when you need a bigger context window. Switch mid-session with `/model`.

| Backend | Context window | Notes |
|---------|---------------|-------|
| Claude Sonnet/Opus (Pro) | 200K | 1M available via `/extra-usage` opt-in |
| Claude Sonnet/Opus (Max/Enterprise) | 1M | Automatic since March 2026 |
| Gemini 2.5 Flash | ~1M (1,048,576) | Fast and cheap — good default for large context tasks |

**Honest assessment**:
Genuinely interesting tool and the minimal harness is appealing in principle — but that minimalism is also the cost. There is no opinionated workflow handed to you. You end up building your own: install, auth, Docker isolation if you want it, project context files, model configuration. You are essentially assembling the harness yourself from first principles. It works, and the result is tailored, but the setup investment is real — noticeably more than Claude Code.

Worth it for a focused project with a longer time horizon — somewhere you would live in it long enough to amortise the setup. Less obviously worth it for short or varied work.

---

## Google AI Studio

[aistudio.google.com](https://aistudio.google.com)

Not a coding assistant itself — it's the API/playground interface for Google's Gemini model family. Useful as a backend for Aider, Pi, or any OpenAI-compatible client, or for direct experimentation with models.

Prepaid access (credit-based) makes it accessible without a monthly commitment. Flash 2.5 is the practical model for coding use: fast, cheap, capable enough for most tasks. Pro 2.5 is noticeably better but costs more per token.

Free tier (Google AI Studio quota) and OpenRouter free tier exist but are not reliable enough for actual use — rate limits, model quality variation, and timeouts make the free path frustrating.

---

## Comparison

| Tool | Model | Cost model | Setup effort | Verdict |
|------|-------|------------|--------------|---------|
| [Claude Code](https://docs.anthropic.com/en/claude-code/getting-started) | Claude Sonnet/Opus | Subscription | Medium — harness provided | Positive net effect |
| [Aider](https://aider.chat) | Any via API | Pay per use | Low — no project config | Didn't stick |
| [Pi](https://github.com/earendil-works/pi) | Any via API or sub | Flexible | High — DIY harness | Good, setup cost real |
