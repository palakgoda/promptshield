# 🛡️ PromptShield — Open Source Hackathon Submission

### 👥 Team Details
- **Project Name:** PromptShield
- **Team Name:** VeritasCore
- **GitHub Username:** palakgoda
- **Repository Link:** https://github.com/palakgoda/promptshield

---

### 💡 Project Overview
PromptShield is a lightweight, cloud-native **AI Reverse Proxy Firewall** designed to secure LLM integration pipelines in real time. Instead of relying on heavy, complex enterprise security suites, PromptShield acts as a fast, local network middleman that mimics standard OpenAI/Gemini API endpoints. It automatically inspects, intercepts, and sanitizes outgoing prompts before they leave the local machine, preventing data privacy leaks and unexpected API budget spikes.

### 🛠️ Tech Stack & Architecture
- **Language:** Python 3.14+
- **Core Framework:** FastAPI (Asynchronous high-performance routing gateway)
- **Networking Client:** HTTPX (Async connection pooling for low-latency streaming)
- **Data Validation:** Pydantic v2 & Pydantic-Settings (Secure `.env` boundary parsing)
- **Testing Engine:** Pytest 9.0+ (Automated assertion pipelines)

---

### 🛡️ Active Security Shield Components
1. **Modular Plugin Manager:** A dynamic, sequential pipeline architecture that lets developers drop custom validation scripts directly into a `/plugins` directory.
2. **Regex PII Masker:** Automatically scans incoming prompt payloads for sensitive patterns (such as email addresses and credit cards) and redacts them dynamically (`[REDACTED_EMAIL]`, `[REDACTED_CARD]`) to maintain strict data compliance.
3. **Credential Leak Detector:** Catches high-risk developer oversights by identifying hardcoded API tokens or secret key strings (`sk-proj-...`, `AIzaSy...`) inside raw prompt strings, instantly dropping the request with a `403 Forbidden` status code.
4. **Local Rate Limiter:** An in-memory timestamp sliding-window guardrail that detects client-side infinite loop anomalies, blocking traffic spikes before they hit upstream LLM accounts to avoid bill shocks.

---

### 🧪 Quality Assurance & Robustness
PromptShield features a fully automated test coverage suite running on `pytest`. 
- **PII Integrity Tests:** Confirms flawless pattern identification and payload text mutation.
- **Leak Prevention Tests:** Assures that malicious key exposures are consistently blocked at the line-of-defense.
- **Budget Protection Tests:** Verifies sliding-window limit execution thresholds under pressure.
