# 07 · Status report: week 47, 2026

**Program:** Program Risk & Compliance Copilot · **Client:** NordPay AB (fictional) · **Reporting date:** 2026-11-16 · **Author:** TPM

## Overall: 🟠 AMBER
**Pilot build is complete and ahead of plan; quality of AI answers (faithfulness) is the open risk before go-live.**

| Dimension | Status | Comment |
|---|---|---|
| Scope | 🟢 | Pilot scope delivered; Sprint 2 scope agreed |
| Schedule | 🟢 | M0 and M1 done; go-live 2026-12-15 on track |
| Cost | 🟢 | ~$7 AI spend to date, including all evaluation runs |
| Quality | 🟠 | Citation accuracy 100%; judge-rated faithfulness 20% (R1, R2) |
| Risk | 🟠 | 2 amber risks need action before go-live (R1, R3) |

## Achieved this period
- Pilot build delivered: slip-risk model, regulation Q&A with citations, report agent, guardrails, audit log, public demo.
- Evaluation framework in place: 60-question golden set, 30-question messy set, red team, automated quality gate.
- Question understanding added: messy questions, Swedish, situations. Wrong refusals cut from 8% to 0%.
- Program documentation baselined (docs 00–06).

## Key metrics
| Metric | Value |
|---|---|
| Correct article cited (held-out questions) | 100% |
| Messy questions with the correct article | 88% |
| Off-topic questions refused | 100% |
| Planted injection followed / reported | No / Yes |
| Slips caught reviewing the riskiest 20% | 32% (1.6× random) |
| Cost per answer / per report | $0.018 / $0.14 |

## Next period (Sprint 2, to 2026-11-28)
1. Delivery-risk v2 with behavioural signals (A3).
2. Read-only Jira Cloud connector (C4).
3. Human-graded faithfulness sample and judge calibration (B5, V4).
4. Vendor terms review started with the CISO (V1).

## Decisions needed from the steering committee
1. **Approve the go-live gate:** human-graded faithfulness ≥ 80% on 30 answers.
2. **Nominate the pilot program and 3 PMs** for UAT (D3).
3. **Approve the read-only Jira service account** (D1).

## Top risks
| ID | Risk | Rating | Next action |
|---|---|---|---|
| R1 | Unsupported claims in AI answers | 🔴 | Human grading in Sprint 2 |
| R3 | Slip model domain shift | 🟠 | Behavioural features in Sprint 2 |
| R2 | Unreliable automated judge | 🟠 | Calibration against human grades |
