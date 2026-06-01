# 🛡️ PromptShield

> **One command. Zero config. Full AI security.**

An ultra-lightweight developer security proxy that sits between your application and LLM providers (OpenAI, Google Gemini, Anthropic). Block PII leaks, prevent bill shock, and enforce custom guardrails — all locally, in under 5 seconds.

```bash
docker compose up
```

No Postgres. No Redis. No YAML configuration hell.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
![Status: In Development](https://img.shields.io/badge/status-in%20development-orange)

---

## Why PromptShield?

| | LiteLLM / Portkey | **PromptShield** |
|---|---|---|
| Setup time | Minutes to hours | **5 seconds** |
| Dependencies | Postgres, Redis, YAML | **None** |
| For | Enterprise teams | **Solo devs & hackers** |
| Custom plugins | Complex | **Drop one `.py` file** |
| Runs locally | Partial | **100% local** |

---

## The Problems It Solves

### 1. PII & Credential Leaks
Developers accidentally paste API keys, customer emails, or proprietary code into LLM prompts every day — silently leaking sensitive data to third-party providers. PromptShield detects and redacts this before the prompt ever leaves your machine.

### 2. "Infinite Loop" Bill Shock
A single recursive bug or a malfunctioning agent can fire thousands of LLM calls in minutes, generating a surprise $5,000 cloud bill overnight. PromptShield's local rate limiter kills runaway loops before your wallet notices.

### 3. Infrastructure Complexity
Existing guardrail solutions are powerful but require heavy infrastructure just to run locally. PromptShield is stateless, single-binary, and designed to work in 5 seconds flat.

---

## How It Works

Change just **one line** in your application to route through PromptShield:

```python
# Before
client = OpenAI(api_key="sk-...")

# After — that's it
client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="your-provider-key-here"
)
```

Every prompt is intercepted, scanned by your plugin stack, then either blocked or forwarded:

```
[ Your App ] ──(prompt)──▶ [ PromptShield :8080 ]
                                     │
                           loops through /plugins/
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
           [ Threat Detected ]               [ Safe Prompt ]
                    │                                 │
                    ▼                                 ▼
           Block + Log to              Forward to LLM Provider
           Local Dashboard              Return response to app
```

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/promptshield.git
cd promptshield
docker compose up
```

> ⚠️ **Active development** — Full setup instructions coming with Day 2 release. Star the repo to follow along!

---

## Built-In Plugins (MVP)

| Plugin | What it does |
|---|---|
| `regex_pii_masker` | Redacts emails, phone numbers, credit card numbers |
| `credential_leak_detector` | Blocks prompts containing `sk-...`, `AIzaSy...` API keys |
| `rate_limiter` | Caps requests at 20/min per session to prevent bill shock |

---

## 🔌 Add Your Own Guardrail (It's This Simple)

PromptShield's entire security stack is built on a drop-in plugin architecture. **You don't need to understand proxies, async Python, or streaming pipelines to contribute.**

Create a single `.py` file in `/plugins/`:

```python
# /plugins/my_guardrail.py

class SecurityPlugin:
    def __init__(self):
        self.name = "Prompt Injection Detector"

    def inspect(self, prompt_text: str) -> dict:
        if "ignore previous instructions" in prompt_text.lower():
            return {
                "safe": False,
                "reason": "Prompt injection attempt blocked."
            }
        return {"safe": True, "prompt": prompt_text}
```

Drop it in. It loads automatically. That's the entire contribution.

→ See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide and open issues tagged `good first issue`.

---

## Roadmap (Hackathon MVP v1.0)

- [x] **Day 1** — Architecture design & repository initialization
- [ ] **Day 2** — Core FastAPI routing proxy (`POST /v1/chat/completions`)
- [ ] **Day 3** — Plugin engine + 3 core plugins + `pytest` test suite
- [ ] **Day 4** — SQLite analytics logging
- [ ] **Day 5** — Lightweight React request log dashboard
- [ ] **Day 6** — `Dockerfile` + `docker-compose.yml`
- [ ] **Day 7** — Documentation, demo video & submission

> SSE streaming support is scoped for **v0.2** to ensure a bulletproof v1.0 core.

---

## Contributing

Contributions are what make open source thrive. The easiest way to contribute is to **write a plugin** — if you can write a Python `if` statement, you can contribute to PromptShield.

See [CONTRIBUTING.md](CONTRIBUTING.md) to get started. Open issues are tagged:
- `good first issue` — write a new security plugin
- `enhancement` — improve the dashboard UI
- `documentation` — benchmark plugin latency

