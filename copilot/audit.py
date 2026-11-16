"""Tamper-evident audit log: each entry stores the hash of the previous one.

Changing or deleting any past entry breaks the chain, and verify() says where.
This is what lets you show an auditor exactly what the AI proposed and who approved it.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

LOG = Path("artifacts/audit_log.jsonl")


def _hash(entry: dict) -> str:
    return hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()


def append(event: str, **data) -> dict:
    LOG.parent.mkdir(exist_ok=True)
    prev = "0" * 64
    if LOG.exists() and LOG.stat().st_size:
        prev = json.loads(LOG.read_text().splitlines()[-1])["hash"]
    entry = {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "event": event, "data": data, "prev": prev}
    entry["hash"] = _hash(entry)
    with LOG.open("a") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry


def verify() -> tuple[bool, str]:
    if not LOG.exists():
        return True, "empty log"
    prev = "0" * 64
    for n, line in enumerate(LOG.read_text().splitlines(), 1):
        e = json.loads(line)
        claimed = e.pop("hash")
        if e["prev"] != prev or _hash(e) != claimed:
            return False, f"chain broken at entry {n}"
        prev = claimed
    return True, f"{n} entries, chain intact"
