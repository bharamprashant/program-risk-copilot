"""User feedback for the supervised improvement loop.

Feedback is a review queue for the owner, never an automatic training signal: letting anonymous users change
the system's behaviour directly would invite data poisoning and fail an audit. Confirmed problems are added to
the evaluation set, fixed, and released only if the evaluation improves.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from copilot.guardrails import redact

LOG = Path("artifacts/feedback.jsonl")
MAX_COMMENT = 500


def record(question: str, rating: str, comment: str, citations: list[str], understood_as: str | None) -> None:
    LOG.parent.mkdir(exist_ok=True)
    entry = {
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rating": rating,
        "question": redact(question or "")[0][:300],
        "understood_as": redact(understood_as or "")[0][:300],
        "citations": citations[:5],
        "comment": redact((comment or "")[:MAX_COMMENT])[0],
    }
    with LOG.open("a") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
