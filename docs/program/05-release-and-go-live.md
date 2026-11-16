# 05 · Release and go-live plan

**Version:** 1.0 · 2026-11-16 · **Go-live (pilot):** 2026-12-15 · **Decision forum:** go/no-go meeting, 2026-12-12

## 1. Releases
| Release | Content | Date | Status |
|---|---|---|---|
| **v0.1 Pilot build** | ML risk v1, RAG Q&A, agent, guardrails, evaluation, demo UI | 2026-11-16 | ✅ Released |
| **v0.2 Hardening** | Delivery-risk v2 (behavioural), Jira connector, faithfulness calibration, understanding step | 2026-11-28 | 🔄 Sprint 2 |
| **v1.0 Pilot go-live** | UAT fixes, governance sign-offs, production configuration | 2026-12-15 | ⏳ |
| v1.1 Hypercare fixes | Severity 3 defects, feedback-driven improvements | 2027-01-09 | ⏳ |

## 2. Go/no-go checklist
| # | Criterion | Evidence | Owner |
|---|---|---|---|
| 1 | All automated tests and the retrieval quality gate pass | CI run | Engineering |
| 2 | UAT exit criteria met (doc 04 §3) | UAT log | Head of PMO |
| 3 | Human-graded faithfulness ≥ 80% | Grading sheet | Compliance |
| 4 | DPIA signed off | DPO approval | DPO |
| 5 | Vendor terms reviewed; vendors in the DORA register | CISO note; register entry | CISO / Vendor mgmt |
| 6 | Read-only service account; secrets in the vault | Access review | CISO |
| 7 | Spend limits set (vendor and app) | Console screenshot | TPM |
| 8 | Runbook and rollback tested | Dry run | Engineering |
| 9 | Users trained, including "no employee evaluation" rule | Attendance | Head of PMO |
| 10 | Support model agreed for hypercare | RACI | TPM |

## 3. Runbook
**Deploy:** build the allowlisted package (`scripts/build_space.sh`, which aborts on anything secret-like) → deploy to the pilot environment → set secrets in the vault → smoke test (one question, one offline report, `verify-audit`) → announce to pilot users.

**Weekly operation:** the PM generates the draft on Thursday → reviews and edits → approves (`approve --approver NAME`) → distributes to the steering committee. The audit log records the approval.

**Monitoring (daily in hypercare, then weekly):** AI cost per day; error rate; refusal rate; 👎 feedback count; `verify-audit` result.

## 4. Rollback
| Trigger | Action |
|---|---|
| Severity 1 defect (e.g. personal data in a vendor request) | Disable live AI (remove the key); the free baseline continues; incident to the DPO within 24 h |
| AI vendor outage | Automatic fallback to the baseline; no action needed |
| Wrong answers trend (> 3 confirmed 👎 per week) | Pause Q&A; review; re-run evaluation; redeploy only if it improves |

## 5. Hypercare (2026-12-15 → 2027-01-09)
- Daily 15-minute check-in with pilot PMs for the first week, then twice a week.
- Feedback triaged within 2 business days: confirmed issues become new evaluation questions (supervised improvement loop, not self-learning).
- Exit criteria: no open Severity 1–2 defects; feedback triaged; benefits baseline captured.

## 6. Benefits tracking
Measured at the benefits review (2027-02-15) against the charter's success metrics: PM hours on reporting, time to a regulatory answer, slips flagged early, PII incidents (target 0), unapproved releases (target 0).
