# 03 · Risk and compliance assessment of the copilot itself

**Version:** 0.9 (draft for sign-off at M3, 2026-12-05) · **Owner:** TPM · **Reviewers:** DPO, CISO, Head of Compliance, Model risk

A tool that helps with compliance must itself be compliant. This document assesses the copilot under GDPR, DORA and the EU AI Act, plus model risk and information security. *It is a realistic program artefact for a fictional client, not legal advice.*

## 1. GDPR: data protection impact assessment (summary)
| Question | Assessment |
|---|---|
| **Is a DPIA required?** (Art. 35) | Precautionary yes: new technology (an LLM) processing workplace data, and ticket text can contain customer personal data |
| **Personal data involved** | Employee names (assignee, reporter) in Jira; customer data that occasionally appears in ticket text |
| **Purpose and lawful basis** (Art. 6) | Legitimate interest (Art. 6(1)(f)) in efficient, compliant delivery; balancing test documented below |
| **Data minimisation** (Art. 5(1)(c)) | Emails, personnummer, IBANs, card numbers and phone numbers are **redacted before any AI call**. Assignees are used only as anonymous workload counts |
| **Automated decisions** (Art. 22) | None. Risk scores rank *tickets*, not people, and every report needs human approval |
| **Processor** (Art. 28) | Anthropic as AI processor: a data processing agreement is required; check retention and training-use terms (CISO action V1) |
| **International transfers** (Ch. V) | Confirm the processing region and transfer mechanism (SCCs or adequacy) before pilot go-live |
| **Retention** | No ticket text stored by the copilot; the audit log is metadata only; feedback is redacted and kept for 12 months |
| **Residual risk** | **Low**, provided actions V1 and V2 close before go-live |

## 2. DORA: ICT third-party risk (Art. 28–30)
The copilot introduces new ICT third-party providers, so NordPay's DORA obligations apply.

| Requirement | Application | Status |
|---|---|---|
| **Register of information** (Art. 28(3)) | Add Anthropic (AI model API) and Render (demo hosting only, EU region; not used in the pilot) | ⏳ Action V3 |
| **Does it support a critical or important function?** | **No.** The copilot advises; it doesn't run payments or a critical function, and the free baseline works without the vendor | Assessed |
| **Contract provisions** (Art. 30) | Service description, data location, security, audit rights and exit terms in the vendor terms; gaps go to procurement | ⏳ Action V1 |
| **Exit strategy** (Art. 28(8)) | The offline baseline needs no vendor; the model is behind one client wrapper, so it can be switched to another provider | ✅ Designed |
| **Concentration risk** (Art. 29) | Low: a single non-critical use | Assessed |

## 3. EU AI Act: classification
| Question | Assessment |
|---|---|
| Prohibited practice? | No |
| **High-risk (Annex III)?** | **No.** It isn't used for creditworthiness, employment decisions or worker evaluation. ⚠️ **Guardrail:** risk scores must never be used to evaluate individual employees (that could fall under Annex III employment). This is recorded as an operating rule and in user training |
| Transparency obligations | Users are told they're using AI; outputs are labelled as AI drafts |
| Role | NordPay is a **deployer** of a general-purpose AI model provided by Anthropic |
| **Conclusion** | Minimal or limited risk, provided the employee-evaluation prohibition is followed |

## 4. Model risk
| Model | Risk | Control |
|---|---|---|
| Slip-risk model | Domain shift (trained on open-source projects); learns jargon | One signal among several; v2 behavioural features; retrain on NordPay data; monitor precision monthly |
| Answer writer (LLM) | Unsupported claims (faithfulness 20% by AI judge); judge is noisy | **Go-live gate:** human-graded faithfulness ≥ 80% on 30 sampled answers; interpretation labelled; compliance reviews pilot answers |
| Understanding step | Wrong restatement leads to the wrong answer | Restatement shown to the user, who can correct it; logged in feedback |
| Agent | Follows injected instructions | Tool output treated as data; code-guaranteed reporting; red-team test in CI |

## 5. Information security
| Threat | Control | Tested |
|---|---|---|
| Prompt injection via tickets | Fenced tool data; pattern flags; guaranteed reporting | ✅ red-team |
| Leaked API key | Never in code; secret scan in the build script; vault in production | ✅ scan |
| Data exfiltration through tools | All tools read-only; no write or send capability | ✅ by design |
| Malicious output in the UI (XSS) | All model output HTML-escaped | ✅ test |
| Cost abuse | Daily cap, per-visitor limit, vendor-side spend limit | ✅ |
| Tampered audit trail | Hash chain + `verify-audit` | ✅ test |

## 6. Actions before go-live
| ID | Action | Owner | Due |
|---|---|---|---|
| V1 | Review Anthropic commercial terms, DPA, retention and training-use settings; confirm EU data handling | CISO + Procurement | 2026-12-01 |
| V2 | DPO sign-off of the DPIA | DPO | 2026-12-05 |
| V3 | Add vendors to the DORA register of information | Vendor management | 2026-12-05 |
| V4 | Human-graded faithfulness sample (30 answers) ≥ 80% | Compliance + TPM | 2026-12-10 |
| V5 | User guidance: no employee evaluation from risk scores | Head of PMO | 2026-12-12 |
