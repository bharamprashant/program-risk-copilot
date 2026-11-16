# 02 · Solution design and data

**Version:** 1.0 · 2026-11-16 · **Owner:** Engineering lead / TPM

## 1. Architecture
```
 NordPay Jira (read-only) ─┐
 Apache Jira (training) ───┼─► Guardrails: redact PII, flag injection ─► Slip-risk model (logistic regression + reasons)
                           │                                                     │
 EU Publications Office ───┴─► Article-level chunks ─► Hybrid search (BM25 + LSA + rank fusion)
 (DORA, GDPR, PSD2)                                                    │         │
 User question ─► Understanding step (Claude Haiku 5.5) ───────────────┘         ▼
                                                     Agent / answer writer (Claude Opus 5.5, structured output)
                                                                                 │
                                    Grounding check (code) ─► Draft ─► Named approver ─► Hash-chained audit log
```
Design principle: **the AI proposes, code verifies, a human decides.** Safety checks never depend on the model behaving.

## 2. Components
| Component | Technology | Purpose |
|---|---|---|
| Understanding step | Claude Haiku 5.5, JSON schema | Fix typos, translate, restate, detect off-topic questions, generate legal search terms |
| Retrieval | BM25 + LSA (TF-IDF + SVD) + Reciprocal Rank Fusion, multi-query | Find the right articles; refuse on weak evidence |
| Answer writer | Claude Opus 5.5, JSON schema, refusal fallback | Answer only from retrieved text; full, partial or no coverage |
| Agent | Claude Opus 5.5, three read-only tools | Investigate the portfolio and draft the report |
| Slip-risk model | scikit-learn logistic regression | Rank tickets, with faithful per-feature reasons |
| Guardrails | Python (regex, Luhn check, grounding check) | PII, injection, citation verification |
| Audit log | SHA-256 hash chain (JSONL) | Tamper-evident record of drafts and approvals |
| Demo UI | Gradio 6, custom design | Public demo with spending guard |

## 3. Data sources and licensing
| Source | Owner | Access | Use | Terms |
|---|---|---|---|---|
| **DORA** Reg. (EU) 2022/2554, **GDPR** Reg. (EU) 2016/679, **PSD2** Dir. (EU) 2015/2366 | European Union | EU Publications Office content API (`publications.europa.eu/resource/celex/…`); EUR-Lex blocks automated download | Retrieval corpus (423 chunks from 280 articles) | EU legal texts may be reused under the Commission's reuse policy (Decision 2011/833/EU). Only the official EU texts are authentic |
| **Apache Software Foundation Jira** (Kafka, Spark, Flink, Hive, Cassandra, HBase) | The Apache Software Foundation | Public REST API at `issues.apache.org/jira`, no login, 1 request/second | Training data: 9,000 resolved issues with fix-version history, 2023–2026 | Publicly visible project-management data; used for research and demonstration. Raw data isn't redistributed in the repo |
| **NordPay Jira** (pilot) | NordPay AB | Jira Cloud REST API through a **read-only service account**; token held in a secrets vault | Portfolio to analyse | Internal data. Personal data redacted before any AI call (see doc 03) |
| **Demo portfolio** | Fictional | `data/demo/portfolio.json` | Public demo and tests | Contains planted personal data and an injection, for testing |

**Cold start:** a new Jira has too little history to train a model, so the pilot uses (1) transparent rules, plus (2) the model trained on public Apache data, and (3) retraining on NordPay data once ≥ 500 resolved tickets with fix versions exist (story A4). This is a known limitation, recorded in RAID as R3.

## 4. The slip-risk model
- **Label:** a concrete fix version removed from a ticket (missed release). Excludes placeholder versions (`5.x`) and bulk edits (≥ 30 tickets, same version, same day).
- **Features (v1):** project, type, priority, number of components and labels, text length, ownership, assignee load, and TF-IDF of the text.
- **Validation:** time-based split; tickets younger than 180 days excluded (censoring).
- **Result:** PR-AUC 0.21 vs a 0.12 base rate; reviewing the riskiest 20% catches 32% of slips (1.6× lift).
- **Known weakness:** the strongest learned signals are project jargon ("tez", "metastore"), not delivery behaviour, so it won't transfer well to NordPay. **v2 (story A3)** adds behavioural features: days in status, sprint carry-over, blocking links, reopen count, scope edits, time to target release.

## 5. Integration and security design
- **Jira:** read-only API token for a dedicated service account; scopes limited to `read:jira-work`; no write calls exist in the code.
- **Secrets:** `.env` locally (git-ignored); an encrypted environment variable on Render for the demo; a corporate vault in production.
- **Network:** outbound calls only to the Anthropic API and Jira; no inbound API exposed (Gradio endpoints private).
- **Logging:** the audit log holds metadata only (status, counts, cost), with no ticket text. Feedback is PII-redacted.

## 6. Environments
| Environment | Purpose | Data |
|---|---|---|
| Local | Development and evaluation | Public + demo |
| Public demo ([Render, Frankfurt](https://program-risk-copilot.onrender.com)) | Portfolio demonstration | Demo only; spending guard; key as an encrypted environment variable |
| Pilot (NordPay) | 1 program, 3 PMs | NordPay Jira, read-only |
