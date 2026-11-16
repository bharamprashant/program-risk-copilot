# 00 · Program charter: Program Risk & Compliance Copilot

| | |
|---|---|
| **Client** | NordPay AB, a Swedish payment institution authorised and supervised by Finansinspektionen (FI). *Fictional client, used to run this as a realistic program.* |
| **Program manager / TPM** | Prashant Bharam |
| **Sponsor** | Chief Operating Officer (COO) |
| **Product owner** | Head of PMO |
| **Status** | Pilot build complete · in Sprint 2 (hardening) · go-live pilot planned **2026-12-15** |
| **Tracker** | Jira project `PRC` · code: `github.com/bharamprashant/program-risk-copilot` |
| **Version** | 1.0 · 2026-11-16 |

## 1. Problem statement
NordPay runs about 12 change programs a year under DORA, GDPR and PSD2. Its six program managers spend an estimated **5 hours each per week** on three manual tasks:

1. **Spotting delivery risk late.** Slippage becomes visible only when a release date is missed. In 2026, 4 of 11 releases slipped by more than two weeks.
2. **Answering compliance questions.** Questions such as *"our cloud provider was down for 6 hours, do we report it?"* wait 2–5 days in the compliance team's queue, or are answered from memory.
3. **Writing the weekly steering-committee pack**, assembled by hand from Jira, spreadsheets and email.

Since DORA applied from 17 January 2025, every delivery risk on an ICT system is also a potential regulatory risk. The PMO cannot see that link today.

## 2. Objective
Give program managers an assistant that **(a)** ranks open work by slip risk with reasons, **(b)** answers regulatory questions from the official text with article citations, and **(c)** drafts the weekly steering-committee report. It must stay **safe for a regulated firm**: no personal data sent to the AI, no unreviewed output reaching executives, and a full audit trail.

## 3. Scope
| In scope (pilot) | Out of scope (pilot) |
|---|---|
| DORA, GDPR and PSD2 (official EU texts) | Other laws (MiFID II, AML, the EU AI Act text itself), FI's national regulations |
| Read-only access to Jira | Writing back to Jira, sending email or Slack |
| Weekly report draft with human approval | Automatic distribution |
| English and Swedish questions | Legal advice. Answers support, never replace, the compliance function |
| 1 pilot program, 3 PMs, 1 compliance reviewer | Rollout to all programs (phase 2, after the benefits review) |

## 4. Success metrics (measured at the pilot benefits review, 2027-02-15)
| Metric | Baseline | Target |
|---|---|---|
| PM time on report preparation | ~3 h/week | **≤ 1 h/week** |
| Time to a first answer on a regulatory question | 2–5 days | **< 1 minute**, with a citation the compliance reviewer agrees with in ≥ 90% of sampled cases |
| Slips flagged ≥ 2 weeks before the release date | not measured | ≥ 30% of slips |
| Personal data sent to the AI vendor | n/a | **0 incidents** |
| Steering-committee reports released without a named approver | n/a | **0** |

## 5. Business case (assumptions to be validated in the pilot)
| Item | Estimate |
|---|---|
| Time saved | 6 PMs × ~2.5 h/week × 44 weeks ≈ **660 h/year** |
| Value | 660 h × SEK 900/h (fully loaded) ≈ **SEK 594,000/year** |
| AI usage cost | ~$0.14 per report + ~$0.02 per question ≈ **under $500/year** at pilot volumes |
| Build and run cost | 3 sprints (1 TPM, 1 engineer part-time) + hosting ≈ SEK 250,000 one-off, SEK 30,000/year |
| **Payback** | **about 5–6 months** after go-live |

The larger, unquantified benefit is **fewer regulatory surprises**: incidents and supplier changes linked to the right DORA article before an inspection asks.

## 6. Stakeholders and RACI
| Role | Responsibility | R | A | C | I |
|---|---|---|---|---|---|
| COO (sponsor) | Funding, go/no-go | | ✔ | | |
| Head of PMO (product owner) | Requirements, acceptance, benefits | ✔ | | | |
| Program manager / TPM | Delivery, risks, governance, reporting | ✔ | | | |
| Engineering lead | Build, integration, operations | ✔ | | | |
| Head of Compliance (2nd line) | Validates regulatory answers in UAT | | | ✔ | |
| Data Protection Officer | DPIA sign-off | | | ✔ | |
| CISO | Security review, vendor assessment | | | ✔ | |
| Model risk (CRO office) | Model validation, monitoring | | | ✔ | |
| Program managers (end users) | UAT, feedback | | | ✔ | ✔ |
| Internal audit | Audit trail requirements | | | | ✔ |

## 7. Milestones
| # | Milestone | Date | Status |
|---|---|---|---|
| M0 | Charter and requirements baselined | 2026-11-16 | ✅ Done |
| M1 | Pilot build complete: ML, RAG, agent, guardrails, evaluation | 2026-11-16 | ✅ Done |
| M2 | Hardening: delivery-risk v2, Jira connector, faithfulness calibration | 2026-11-28 | 🔄 Sprint 2 |
| M3 | Governance sign-offs: DPIA, DORA third-party assessment, security review | 2026-12-05 | ⏳ Planned |
| M4 | UAT complete and go/no-go decision | 2026-12-12 | ⏳ Planned |
| M5 | Pilot go-live (1 program, read-only) | 2026-12-15 | ⏳ Planned |
| M6 | Hypercare ends | 2027-01-09 | ⏳ Planned |
| M7 | Benefits review and phase 2 decision | 2027-02-15 | ⏳ Planned |

## 8. Governance
- **Weekly status** to the product owner; **fortnightly steering committee** (sponsor, product owner, compliance, CISO).
- Tolerances: schedule ±1 week, budget ±10%. Exceptions escalate to the sponsor.
- Changes to scope, data sources or AI vendor go through the change board.
- Documents: this folder (`docs/program/`) is the controlled record; Jira is the delivery tracker.

## Related documents
[01 Requirements](01-requirements.md) · [02 Solution design](02-solution-design.md) · [03 Risk & compliance assessment](03-risk-and-compliance-assessment.md) · [04 Test strategy & UAT](04-test-strategy-and-uat.md) · [05 Release & go-live plan](05-release-and-go-live.md) · [06 RAID & decision log](06-raid-and-decision-log.md) · [07 Status report](07-status-report.md)
