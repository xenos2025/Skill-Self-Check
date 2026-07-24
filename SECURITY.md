# Security Policy

Skill Self-Check is an Agent Skill package: markdown workflows plus a local
Python hard-gate script. This document covers vulnerability reporting and
trust boundaries.

## Reporting a Vulnerability

**Do not open a public GitHub issue for security findings.**

1. Prefer a GitHub Security Advisory on this repository, or contact the
   repository owner privately (see [SUPPORT.md](SUPPORT.md)).
2. Include a minimal reproducer, affected path, and suggested severity.
3. Allow at least 14 days for a coordinated fix before public disclosure
   (faster for actively exploitable issues).

You should receive an acknowledgement within 7 days.

## Supported Versions

Only the latest commit on `main` (and tagged releases when published) receives
security fixes.

## In Scope

- Python under `skills/*/scripts/` and any future root `scripts/`
- Installers: `install.ps1`, `install.sh`
- Skill markdown that can be loaded as LLM instructions (`SKILL.md`, checklists)
- Path handling that could write outside an intended skill directory
- Accidental secret exposure in examples or `exp/` samples

## Out of Scope

- Vulnerabilities in Cursor, Claude Code, Codex, or host LLM platforms
- Skills the user points the checker *at* (third-party content)
- Social-engineering the user into pasting secrets into chat

## Trust boundaries

- The checker **reads** a target skill directory; it should not require network
  access for hard gates.
- Installers **copy** files into `~/.cursor/skills` or `.cursor/skills` — review
  the destination before `-Force` / `--force`.
- `exp/` may hold workflow drafts for factories / trade / ecommerce; never put
  live customer PII, tokens, or production CSVs there in a public fork.
