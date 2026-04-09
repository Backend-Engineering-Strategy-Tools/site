---
title: "Python"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
---

Python is my scripting and automation language of choice. I reach for it when Bash starts getting unwieldy — data processing, API interactions, infrastructure automation scripts, and one-off tooling.

> **2024 note:** For anything beyond quick scripts I'm increasingly reaching for Go instead. Better performance, a single compiled binary, and stronger typing make Go a more honest choice for tools that end up running in production. Python still wins for data work and anything where the ecosystem matters (ML, pandas, etc.).

## Tooling

**IDE:** [PyCharm](https://www.jetbrains.com/pycharm/) — JetBrains' Python IDE. Good for larger projects. For scripts and smaller work, IntelliJ IDEA with the Python plugin does the job.

**Formatting:** [Black](https://black.readthedocs.io/) — opinionated formatter, no configuration needed.

**Linting:** [Ruff](https://docs.astral.sh/ruff/) — extremely fast linter and formatter, replacing Flake8 + isort in most setups.

**Dependency management:** [uv](https://docs.astral.sh/uv/) — modern, fast package manager replacing pip/virtualenv for most workflows.

## Where I use it

- Infrastructure automation and scripting alongside Ansible
- Data processing and log analysis
- CLI tooling for internal workflows
- Quick API clients and integration scripts

## Resources

- [docs.python.org](https://docs.python.org/3/)
- [Real Python](https://realpython.com/)
