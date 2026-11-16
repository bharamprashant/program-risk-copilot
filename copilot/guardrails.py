"""Guardrails that run in code, before and after the model.

1. PII redaction  — personal data never leaves the machine (GDPR data minimisation, Art. 5(1)(c)).
2. Injection flags — ticket text is untrusted: someone can write "ignore your instructions" in a ticket.
   We flag it, and the prompt wraps all tool output as data, never as instructions.
3. Grounding check — every citation in the model's output must be a chunk we actually retrieved,
   and every issue key it mentions must exist in the portfolio. Anything else is rejected.
"""
import re

PII_PATTERNS = {
    "EMAIL": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "PERSONNUMMER": re.compile(r"\b(?:19|20)?\d{6}[-+]?\d{4}\b"),   # Swedish personal identity number
    "IBAN": re.compile(r"\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]{4}){3,7}\b"),
    "CARD": re.compile(r"\b(?:\d[ -]?){13,19}\b"),
    "PHONE": re.compile(r"(?<!\w)\+\d{1,3}[\s-]?\d{2,4}(?:[\s-]?\d{2,4}){2,3}\b"),
}

INJECTION = re.compile(
    r"ignore (?:all |any |the )?(?:previous|prior|above|your) (?:instructions|rules)|disregard (?:the|your|all)"
    r"|you are now|system prompt|reveal (?:your|the) (?:instructions|prompt)|mark (?:everything|all) (?:as )?green",
    re.IGNORECASE,
)


def luhn_ok(digits: str) -> bool:
    d = [int(c) for c in digits if c.isdigit()][::-1]
    return len(d) >= 13 and sum(x if i % 2 == 0 else (x * 2 - 9 if x * 2 > 9 else x * 2) for i, x in enumerate(d)) % 10 == 0


def redact(text: str) -> tuple[str, dict]:
    counts = {}
    for label, pat in PII_PATTERNS.items():
        def sub(m, label=label):
            if label == "CARD" and not luhn_ok(m.group()):
                return m.group()
            counts[label] = counts.get(label, 0) + 1
            return f"[{label}]"
        text = pat.sub(sub, text)
    return text, counts


def injection_flags(text: str) -> list[str]:
    return [m.group() for m in INJECTION.finditer(text)]


def check_grounding(brief: dict, retrieved_ids: set[str], issue_keys: set[str]) -> list[str]:
    problems = []
    for c in brief.get("compliance_checks", []):
        for cid in c.get("chunk_ids", []):
            if cid not in retrieved_ids:
                problems.append(f"citation {cid} was never retrieved")
    for r in brief.get("top_risks", []):
        if r.get("issue_key") not in issue_keys:
            problems.append(f"issue {r.get('issue_key')} is not in the portfolio")
    return problems
