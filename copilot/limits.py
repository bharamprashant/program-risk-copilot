"""Spending guard for the public demo.

Before every live LLM call we *reserve* its estimated cost against two daily limits:
a global dollar cap for the whole app, and a per-visitor run cap. After the call we replace
the estimate with the real cost. When a limit is hit, the app falls back to free, offline paths.
Counters live in memory and reset at midnight UTC (and on restart, which only makes them stricter
on the first day of a restart, never looser than the Anthropic Console spend limit).
"""
import hashlib
import os
import threading
from datetime import datetime, timezone

DAILY_USD_CAP = float(os.environ.get("DEMO_DAILY_USD_CAP", "2.0"))
RUNS_PER_VISITOR = int(os.environ.get("DEMO_RUNS_PER_VISITOR", "6"))
ESTIMATE = {"ask": 0.04, "brief": 0.40}

_lock = threading.Lock()
_state = {"day": None, "spent": 0.0, "visitors": {}}


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _visitor_id(ip: str | None) -> str:
    # Store only a hash of the IP address, never the address itself.
    return hashlib.sha256((ip or "unknown").encode()).hexdigest()[:16]


def reserve(kind: str, ip: str | None) -> tuple[bool, str]:
    with _lock:
        if _state["day"] != _today():
            _state.update(day=_today(), spent=0.0, visitors={})
        v = _visitor_id(ip)
        if _state["visitors"].get(v, 0) >= RUNS_PER_VISITOR:
            return False, f"You've used today's {RUNS_PER_VISITOR} live AI runs. Showing the free version instead."
        if _state["spent"] + ESTIMATE[kind] > DAILY_USD_CAP:
            return False, "Today's demo budget is used up. Showing the free version instead."
        _state["spent"] += ESTIMATE[kind]
        _state["visitors"][v] = _state["visitors"].get(v, 0) + 1
        return True, ""


def settle(kind: str, actual_usd: float) -> None:
    with _lock:
        _state["spent"] += actual_usd - ESTIMATE[kind]


def status() -> dict:
    with _lock:
        return {"day": _state["day"], "spent_usd": round(_state["spent"], 3), "cap_usd": DAILY_USD_CAP}
