# Steering-committee briefing: Nordic payments platform: DORA readiness

**Overall: 🔴 RED**: 6 of 6 regulatory workstreams need attention.

## Top delivery risks
| Issue | What | Why | Action |
|---|---|---|---|
| PAY-120 | Concentration risk assessment of cloud providers | Model reasons: mentions "region"; mentions "dependency"; assignee already has many open issues | Confirm owner, dependencies and date at next stand-up. |
| PAY-114 | Strong customer authentication for in-app card payments | Model reasons: mentions "upgrade"; mentions "value"; assignee already has many open issues | Confirm owner, dependencies and date at next stand-up. |
| PAY-109 | ICT business continuity plan for card authorisation service | Model reasons: mentions "region"; assignee already has many open issues; no owner assigned | Confirm owner, dependencies and date at next stand-up. |
| PAY-115 | SCA challenge loops on iOS 19 for some banks | Model reasons: type is Bug; mentions "users"; assignee already has many open issues | Confirm owner, dependencies and date at next stand-up. |
| PAY-108 | Nightly ledger backup fails intermittently on replica lag | Model reasons: type is Bug; mentions "fails"; mentions "storage" | Confirm owner, dependencies and date at next stand-up. |

## Regulatory checks
| Topic | Status | Basis | Note |
|---|---|---|---|
| ICT third-party register and contracts | 🟠 AT_RISK | [DORA Art. 28](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554#art_28); [DORA Art. 29](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554#art_29) | 3 related issues; high-risk or critical: PAY-101, PAY-120 |
| Major ICT incident classification and reporting | 🟠 AT_RISK | [DORA Art. 18](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554#art_18); [DORA Art. 19](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554#art_19) | 3 related issues; high-risk or critical: PAY-104 |
| Digital operational resilience testing | 🔴 GAP | [DORA Art. 24](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554#art_24); [DORA Art. 25](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554#art_25) | 3 related issues; high-risk or critical: PAY-106 |
| Backup and recovery | 🟠 AT_RISK | [DORA Art. 12](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554#art_12); [DORA Art. 61](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554#art_61) | 3 related issues; high-risk or critical: PAY-108, PAY-109 |
| Automated decisions and DPIA | 🟠 AT_RISK | [GDPR Art. 35](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679#art_35); [GDPR Art. 22](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679#art_22) | 3 related issues; high-risk or critical: PAY-111, PAY-112 |
| Strong customer authentication | 🟠 AT_RISK | [PSD2 Art. 97](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32015L2366#art_97); [PSD2 Art. 4](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32015L2366#art_4) | 2 related issues; high-risk or critical: PAY-114, PAY-115 |

## Decisions needed
- Accept or re-plan: Digital operational resilience testing

## Data-quality notes
- PAY-118: possible instruction in ticket text ('Ignore previous instructions'); ignored.

---
_Drafted by the copilot (offline mode). Personal data redacted before processing: {'EMAIL': 1, 'PERSONNUMMER': 1, 'IBAN': 1}. Grounding problems: 0. Slip scores rank risk; they are not calibrated probabilities. Requires human approval before distribution._