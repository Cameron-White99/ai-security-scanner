# AI Security Scanner

A security analysis tool for LLM-powered applications. Detects prompt injection attacks, scores risk, generates structured security reports, and maintains a full audit log of analysed inputs.

> **Status:** In active development. Core detection engine and API in progress.

---

## The Problem

LLM-based applications introduce a new class of vulnerabilities that traditional security tooling doesn't address. Prompt injection — where malicious input manipulates an AI model's behaviour — is now a real attack vector in production systems. Most development teams have no visibility into whether their AI applications are being probed or exploited.

This tool provides that visibility.

---

## Features

| Feature                        | Description                                                                     | Status         |
| ------------------------------ | ------------------------------------------------------------------------------- | -------------- |
| **Prompt Injection Detection** | Pattern and heuristic-based detection of direct and indirect injection attempts | 🔨 In progress |
| **Risk Scoring**               | Severity scoring per request with configurable thresholds                       | 🔨 In progress |
| **Security Report Generation** | Structured JSON and human-readable reports per scan session                     | 📋 Planned     |
| **Audit Logging**              | Immutable log of all analysed inputs, detections, and risk scores               | 📋 Planned     |
| **REST API**                   | FastAPI-based API for integration into existing pipelines                       | 🔨 In progress |
| **Dashboard**                  | React frontend for visualising scan results and trends                          | 📋 Planned     |

---

## Architecture

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   Client / API  │────▶│   FastAPI Application │────▶│   PostgreSQL    │
│   (REST calls)  │     │                       │     │  (Audit Logs &  │
└─────────────────┘     │  ┌─────────────────┐  │     │   Scan Results) │
                        │  │ Detection Engine │  │     └─────────────────┘
                        │  │                  │  │
                        │  │ · Pattern rules  │  │     ┌─────────────────┐
                        │  │ · Heuristics     │  │────▶│  GCP Cloud Run  │
                        │  │ · Risk scorer    │  │     │  (Deployment)   │
                        │  └─────────────────┘  │     └─────────────────┘
                        └──────────────────────┘
```

**Services:**

- **FastAPI** — REST API layer, request handling, report generation
- **Detection Engine** — modular rule-based and heuristic detection pipeline
- **PostgreSQL** — persistent storage for audit logs, scan history, risk scores
- **Docker** — containerised for consistent local dev and cloud deployment
- **Google Cloud Run** — serverless deployment target
- **React / Next.js** — frontend dashboard (in progress)

---

## Detection Approach

The scanner analyses input text across several detection layers:

1. **Pattern Matching** — known injection signatures (role overrides, instruction injection, system prompt leakage attempts)
2. **Heuristic Analysis** — structural anomalies, unusual instruction density, delimiter abuse
3. **Risk Scoring** — weighted severity score (0–100) based on detection confidence and attack type
4. **Classification** — categorises detections by attack type (direct injection, indirect injection, jailbreak attempt, data exfiltration probe)

Attack taxonomy follows [OWASP Top 10 for LLMs](https://owasp.org/www-project-top-10-for-large-language-model-applications/).

---

## Tech Stack

- **Language:** Python 3.11+
- **API Framework:** FastAPI
- **Database:** PostgreSQL
- **Containerisation:** Docker / Docker Compose
- **Cloud:** Google Cloud Run
- **Frontend:** React / Next.js _(planned)_

---

## Getting Started

> Full setup instructions will be added as the project stabilises. Architecture and detection design are being documented first.

```bash
# Clone the repository
git clone https://github.com/cameron-white99/ai-security-scanner.git
cd ai-security-scanner

# Start services
docker compose up --build

# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

---

## API (Planned)

```
POST /scan          — Submit text for analysis, returns risk score and detections
GET  /scans         — List historical scan results
GET  /scans/{id}    — Retrieve a specific scan result
GET  /report/{id}   — Generate a security report for a scan session
```

---

## Roadmap

- [x] Project architecture and design
- [ ] Detection engine — pattern matching layer
- [ ] Detection engine — heuristic analysis layer
- [ ] Risk scoring model
- [ ] FastAPI application with `/scan` endpoint
- [ ] PostgreSQL schema and audit logging
- [ ] Docker Compose local environment
- [ ] Security report generation
- [ ] GCP Cloud Run deployment
- [ ] React dashboard
- [ ] CI/CD pipeline

---

## Background & Motivation

This project is part of my transition into AI security. I'm a software developer with 5+ years of experience in real-time systems and fintech (including securing APIs and WebSocket connections in regulated environments), currently completing a Master of Cyber Security at QUT.

AI security is an emerging field with a real gap between what practitioners need and what tooling currently provides. This scanner is my attempt to build something practically useful while developing deep expertise in LLM threat modelling.

---

## References

- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [MITRE ATLAS — Adversarial Threat Landscape for AI Systems](https://atlas.mitre.org/)
- [Prompt Injection Attacks — Simon Willison](https://simonwillison.net/series/prompt-injection/)

---

## License

MIT
