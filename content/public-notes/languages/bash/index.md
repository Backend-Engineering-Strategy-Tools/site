---
title: "Bash"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
---

Bash is unavoidable in DevOps work — CI/CD pipelines, container entrypoints, system init scripts, and quick automation all end up as shell scripts eventually. Knowing how to write it well saves a lot of pain.

## Tooling

**Linting:** [ShellCheck](https://www.shellcheck.net/) — catches common mistakes and anti-patterns. Run it in CI, or install the IDE plugin. Most of what it flags is genuinely wrong.

**IDE:** Any editor works. ShellCheck integrations exist for VS Code, IntelliJ, Vim, and most others.

## Good habits

Set these at the top of every non-trivial script:

```bash
#!/usr/bin/env bash
set -euo pipefail
```

- `-e` — exit on error
- `-u` — error on unset variables
- `-o pipefail` — catch errors in pipes, not just the last command

Use `shellcheck` before committing. Most Bash bugs it catches are subtle and only surface under specific conditions in production.

## When to reach for Python instead

When the script grows beyond ~50 lines, needs associative arrays, JSON parsing, or HTTP calls — switch to Python. Bash is great glue; it's a poor application language.

## Resources

- [ShellCheck](https://www.shellcheck.net/)
- [Bash Reference Manual](https://www.gnu.org/software/bash/manual/)
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
