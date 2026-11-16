# 01 · Requirements (business and product)

**Program:** Program Risk & Compliance Copilot · **Client:** NordPay AB (fictional) · **Owner:** Head of PMO · **Version:** 1.0 · 2026-11-16
Status key: ✅ delivered in the pilot build · 🔄 in progress · ⏳ planned. The Jira key is the tracking story.

## 1. Users
| Persona | Need |
|---|---|
| **Program manager** (primary) | Know where delivery risk is; answer regulatory questions fast; produce the weekly report with less effort |
| **Head of PMO** | A consistent, comparable status across programs |
| **Compliance officer** (2nd line) | Answers that cite the law exactly, and clearly separate interpretation from the text |
| **Steering committee** | A short, reliable status with the decisions it needs to take |
| **Internal audit** | Evidence of who approved what, and when |

## 2. Epics and user stories

### Epic A · Delivery-risk insight
| ID | Story | Acceptance criteria | Status |
|---|---|---|---|
| A1 | As a PM, I want open tickets ranked by slip risk so I know where to look first | Each ticket has a score and a rank; reviewing the riskiest 20% catches ≥ 30% of slips on held-out data | ✅ (32% at 20%) |
| A2 | As a PM, I want the top reasons behind each score so I can judge it | Up to 3 plain-language reasons per ticket; reasons never contradict the ticket's data (e.g. "no owner" when it has one) | ✅ |
| A3 | As a PM, I want risk based on how work behaves over time (stuck, carried over, blocked, reopened) | Behavioural features from the Jira change history; transparent rules alongside the model; must beat v1 PR-AUC on the same test set | ⏳ Sprint 2 |
| A4 | As the PMO, I want the model to learn from NordPay's own history once enough exists | Retraining pipeline; minimum 500 resolved tickets with a fix version; validation report signed off by model risk | ⏳ Phase 2 |

### Epic B · Regulatory Q&A
| ID | Story | Acceptance criteria | Status |
|---|---|---|---|
| B1 | As a PM, I want to ask in my own words and get an answer from DORA, GDPR or PSD2 with the article | Correct article cited for ≥ 85% of held-out questions | ✅ (100% on 25 test questions) |
| B2 | As a PM, I want to see how my question was understood before the answer, and correct it | Restatement, language and search terms shown first; an edited restatement can be re-asked | ✅ |
| B3 | As a PM, I want to ask with typos, in Swedish, or by describing a situation | ≥ 80% correct on the messy-question set; answers in the user's language | ✅ (88%) |
| B4 | As a compliance officer, I want no made-up answers | Off-topic questions refused 100%; every citation verified in code against the retrieved text | ✅ |
| B5 | As a compliance officer, I want the law separated from interpretation | Interpretation labelled; claims limited to the cited text; faithfulness ≥ 80% on **human-graded** samples | 🔄 (AI judge 20%; human grading in Sprint 2) |
| B6 | As the product owner, I want users to flag wrong answers for review | 👍/👎 plus comment, PII-redacted, into a review queue; never fed directly to the model | ✅ |

### Epic C · Steering-committee report
| ID | Story | Acceptance criteria | Status |
|---|---|---|---|
| C1 | As a PM, I want a draft report in a fixed structure | Overall status, top risks with actions, regulatory checks with citations, decisions needed, data-quality notes | ✅ |
| C2 | As the product owner, I want a free fallback that works without AI | Rule-based baseline with the same structure | ✅ |
| C3 | As a PM, I want to see what the copilot did to produce the draft | Every tool call listed in plain language | ✅ |
| C4 | As a PM, I want the report based on our live Jira project | Read-only Jira Cloud connector through a service account; no write scopes | ⏳ Sprint 2 |

### Epic D · Safety, governance and audit
| ID | Story | Acceptance criteria | Status |
|---|---|---|---|
| D1 | As the DPO, I want personal data never sent to the AI vendor | Email, personnummer, IBAN, card (Luhn-checked) and phone redacted before any model call; tested | ✅ |
| D2 | As the CISO, I want hidden instructions in tickets neutralised | Injection patterns flagged; the agent ignores them; code guarantees they are reported | ✅ |
| D3 | As internal audit, I want an approval trail | A report is a draft until a named approver releases it; hash-chained log; tampering detected | ✅ |
| D4 | As the CISO, I want the API key and spend controlled | Secrets in a vault or environment, never in code; daily spend cap; vendor-side limit | ✅ |
| D5 | As compliance, I want the tool itself assessed under GDPR, DORA and the AI Act | DPIA, DORA third-party assessment and AI Act classification signed off | 🔄 drafted (doc 03) · sign-off M3 |

## 3. Non-functional requirements
| Area | Requirement | Status |
|---|---|---|
| Accuracy | Release gate: retrieval recall@5 ≥ 64% on the test set; correct-citation rate ≥ 85% | ✅ automated test |
| Safety | 0 personal-data items in model requests; 0 reports released without an approver | ✅ tested |
| Performance | Answer in < 10 s (p50); report in < 90 s | ✅ ~6 s / ~38 s |
| Cost | < $0.05 per answer, < $0.50 per report; daily cap | ✅ $0.018 / $0.14 |
| Availability | Business hours; if the AI vendor is down, the free baseline still works | ✅ fallback built |
| Security | Read-only data access; private API endpoints; inputs length-limited; output HTML-escaped | ✅ |
| Explainability | Every risk score has reasons; every answer has sources | ✅ |
| Data residency | Prefer EU processing; document the vendor's data handling and retention | ⏳ CISO review |
| Accessibility | Usable on a phone; readable in light and dark mode | ✅ |

## 4. Constraints and assumptions
- The pilot uses public Apache Jira history to train the risk model until NordPay has enough history of its own (see [doc 02 §3](02-solution-design.md)).
- Answers explain the law; they are not legal advice. Compliance remains accountable.
- Only the three laws listed are loaded; national FI regulations are out of scope for the pilot.
