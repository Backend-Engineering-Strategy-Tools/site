---
title: "K9s & Lens"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
---

You run everything with `kubectl`. Get pods, describe, logs, exec, delete, apply — fifty times a day across five namespaces. It works, but every command is a context switch: type, wait, read, type again. `-n namespace` on every single invocation.

So you use K9s. A terminal UI that shows your entire cluster in one view. Switch namespaces and clusters in a keystroke, tail logs in real time, exec into a pod without constructing the command — everything you reach for in `kubectl`, but without the friction.

## K9s

K9s is a TUI (terminal UI) for Kubernetes. It stays in your terminal, updates live, and is keyboard-driven throughout.

```bash
brew install derailed/k9s/k9s
k9s                          # connect to current context
k9s --context prod           # specific context
k9s -n monitoring            # start in a specific namespace
```

### Navigation

| Key | Action |
|-----|--------|
| `:pod` | Jump to pods view |
| `:deploy` | Deployments |
| `:svc` | Services |
| `:ns` | Switch namespace |
| `/` | Filter/search |
| `l` | Logs |
| `e` | Edit resource YAML |
| `d` | Describe |
| `s` | Shell into pod |
| `ctrl-d` | Delete |
| `?` | Help / full keybinding list |

Most resource types are reachable by typing `:` followed by the resource name — `:configmap`, `:secret`, `:ingress`, `:pvc`, and so on.

### Why TUI over GUI

K9s lives in the terminal alongside your other tools. No window switching, works over SSH, starts instantly, and the keyboard-driven workflow is faster once it is in muscle memory. For day-to-day cluster work it is the right default.

## Lens

Lens is a desktop GUI for Kubernetes — a full IDE-style interface with a visual cluster overview, resource browsing, metrics charts, log streaming, and terminal access built in.

It is the better choice when you need to onboard someone who is not yet comfortable with the terminal, or when you want a visual overview to share with a non-technical stakeholder. For engineers doing operational work all day, K9s is faster.

Worth noting: Lens has moved toward a commercial model (Lens Desktop Pro). **[OpenLens](https://github.com/MuhammedKalkan/OpenLens)** is the open-source build of the same codebase, without the account requirement.

## kubectx / kubens

If K9s is more than you need and you just want to stop typing `--context` and `-n` on every command, `kubectx` and `kubens` solve exactly that:

```bash
kubectx                  # list contexts
kubectx prod             # switch to prod context
kubectx -                # switch back to previous context

kubens                   # list namespaces
kubens monitoring        # switch default namespace
```

No TUI, no GUI — just fast context and namespace switching that persists for the rest of your terminal session. Install alongside K9s; they complement each other.

```bash
brew install kubectx
```

## Resources

- [K9s documentation](https://k9scli.io/)
- [K9s GitHub](https://github.com/derailed/k9s)
- [Lens](https://k8slens.dev/)
- [OpenLens](https://github.com/MuhammedKalkan/OpenLens) — open-source Lens build
- [kubectx/kubens](https://github.com/ahmetb/kubectx) — fast context and namespace switching
