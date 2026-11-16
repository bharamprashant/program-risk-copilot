# 06 · RAID and decision log

**Updated:** 2026-11-16 · **Owner:** TPM · Reviewed at each steering committee.

## Risks
| ID | Risk | Impact | Likelihood | Rating | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|
| R1 | AI answers include claims not supported by the cited text (judge-rated faithfulness 20% in v4) | High: wrong compliance guidance | Medium | 🔴 | Law/interpretation separation; human-graded sample ≥ 80% as a go-live gate; compliance reviews pilot answers | TPM + Compliance | Open |
| R2 | The automated faithfulness judge is unreliable (different grades for identical answers) | Medium: quality unknown | High | 🟠 | Calibrate against 30 human-graded answers; use agreement rate before trusting the score | TPM | Open |
| R3 | Slip model learned project jargon from public data, so it won't transfer to NordPay (domain shift) | Medium: weak risk ranking | High | 🟠 | Behavioural features (v2); rules alongside; retrain on NordPay data after 500 tickets | Engineering | Open |
| R4 | Personal data reaches the AI vendor through a pattern not covered by redaction | High: GDPR breach | Low | 🟠 | Redaction tests; DPO review of patterns; vendor DPA; incident procedure | DPO | Open |
| R5 | Prompt injection in tickets manipulates the report | High | Low | 🟢 | Fenced tool data; code-guaranteed reporting; red-team test | CISO | Mitigated |
| R6 | Users treat answers as legal advice | High | Medium | 🟠 | Labelling, training, compliance remains accountable | Head of PMO | Open |
| R7 | Risk scores misused to evaluate employees (could make it high-risk under the AI Act) | High | Low | 🟠 | Operating rule, training, scores at ticket level only | Head of PMO | Open |
| R8 | AI vendor outage or price change | Low | Medium | 🟢 | Free baseline; provider behind one wrapper; spend caps | TPM | Mitigated |
| R9 | Cost overrun from abuse of the public demo | Low | Medium | 🟢 | Daily cap, per-visitor limit, vendor limit | TPM | Mitigated |

## Assumptions
| ID | Assumption | Validated by |
|---|---|---|
| A1 | PMs spend ~3 h/week on report preparation | Time study in week 1 of the pilot |
| A2 | Compliance will review 30 answers in UAT | Head of Compliance agreement |
| A3 | Read-only Jira API access is approved for a service account | CISO |
| A4 | The vendor offers terms compatible with NordPay's DPA and DORA requirements | Procurement / CISO (V1) |

## Issues
| ID | Issue | Action | Owner | Status |
|---|---|---|---|---|
| I1 | EUR-Lex blocks automated download of regulation texts | Use the EU Publications Office content API | Engineering | ✅ Closed |
| I2 | Neural embedding libraries don't support the Python version in use | Use LSA embeddings; measure against keyword search (hybrid wins) | Engineering | ✅ Closed |
| I3 | Confluence not active on the Atlassian site | Program documents kept in git (`docs/program/`), linked from Jira | TPM | ✅ Workaround |
| I4 | API credit ran out during evaluation | Credit added; vendor spend limit set to $20/month | TPM | ✅ Closed |
| I5 | Hugging Face requires a paid plan for interactive demos | Moved hosting to Render's free plan (DEC-10) | TPM | ✅ Closed |

## Dependencies
| ID | Dependency | Needed by | Status |
|---|---|---|---|
| D1 | Jira service account and API token | Sprint 2 (C4) | ⏳ |
| D2 | DPO availability for DPIA review | M3 | ⏳ |
| D3 | Pilot program and 3 PMs nominated | UAT | ⏳ |

## Decision log
| # | Date | Decision | Rationale | Alternatives considered |
|---|---|---|---|---|
| DEC-01 | 2026-11-16 | Read-only integration only; no write-back to Jira | Minimises risk; meets the need | Auto-updating ticket fields (rejected for the pilot) |
| DEC-02 | 2026-11-16 | Human approval required before any report is released | Accountability; AI output is a draft | Auto-send (rejected) |
| DEC-03 | 2026-11-16 | Explainable logistic regression over gradient boosting | Simpler model won (PR-AUC 0.21 vs 0.17) and is explainable | Gradient boosting |
| DEC-04 | 2026-11-16 | Refuse on weak keyword evidence, not on similarity score | Similarity let off-topic questions through | Similarity threshold |
| DEC-05 | 2026-11-16 | No automatic self-learning from user feedback | Data-poisoning and audit risk | Online learning from 👍/👎 |
| DEC-06 | 2026-11-16 | Show the copilot's understanding of a question before the answer, and allow correction | Messy real-world input; transparency | Silent rewriting |
| DEC-07 | 2026-11-16 | Allow partial answers with "what's missing", instead of refusing | Over-refusal blocked useful answers | All-or-nothing answering |
| DEC-08 | 2026-11-16 | Program documents in git, linked from Jira | Confluence unavailable; version control and review | Wait for Confluence |
| DEC-09 | 2026-11-16 | Fictional client (NordPay AB) for the public version | Realistic context without any real employer's data | Using a real company's data (rejected) |
| DEC-10 | 2026-11-16 | Host the public demo on Render's free plan in Frankfurt (EU), not Hugging Face | Hugging Face now charges for Gradio apps; Render is free, EU-hosted, and deploys from git (`render.yaml`). Trade-off accepted: about 50 s wake-up after idle | Hugging Face PRO at $9/month; static showcase without live AI |
