"""Thin wrapper around the Anthropic SDK: model routing, refusal fallback, and per-call cost tracking.

Routing: the capable model does the reasoning (agent, briefing); the small model does cheap,
high-volume work (query rewriting, LLM-as-judge). Every call is logged with tokens, cost and latency
so the dashboard can show cost per briefing and cost per answered question.
"""
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

MAIN = "claude-opus-5-5"
FAST = "claude-haiku-5-5"
PRICES = {MAIN: (4.00, 20.00), FAST: (0.10, 0.50)}  # USD per million input / output tokens


def load_env(path: Path = Path(".env")) -> None:
    if path.exists():
        for line in path.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))


def available() -> bool:
    load_env()
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


@dataclass
class Call:
    purpose: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_s: float


@dataclass
class LLM:
    calls: list[Call] = field(default_factory=list)

    def __post_init__(self):
        import anthropic
        load_env()
        self.client = anthropic.Anthropic()

    def create(self, purpose: str, model: str = MAIN, **kwargs):
        kwargs.setdefault("max_tokens", 16000)
        # Thinking tokens count toward max_tokens; a tight cap can leave no room for the answer itself.
        kwargs["max_tokens"] = max(kwargs["max_tokens"], 4000)
        if model == MAIN:
            # Opus 5.5: thinking is always on; effort is the depth control (default is medium, so set it).
            kwargs.setdefault("output_config", {}).setdefault("effort", "medium")
            # If the main model declines a request, the API re-runs it on a fallback model in the same call.
            kwargs.update(betas=["server-side-fallback-2026-07-01"], fallbacks="default")
        else:
            kwargs.setdefault("output_config", {}).setdefault("effort", "low")
        t0 = time.time()
        resp = self.client.beta.messages.create(model=model, **kwargs)
        self.record(purpose, model, resp.usage, time.time() - t0)
        if resp.stop_reason == "refusal":
            raise RuntimeError(f"{purpose}: model declined the request")
        if resp.stop_reason == "max_tokens":
            raise RuntimeError(f"{purpose}: hit max_tokens before finishing; raise the limit")
        return resp

    def record(self, purpose, model, usage, latency):
        pin, pout = PRICES[model]
        cost = (usage.input_tokens * pin + usage.output_tokens * pout) / 1e6
        self.calls.append(Call(purpose, model, usage.input_tokens, usage.output_tokens, round(cost, 6), round(latency, 2)))

    @staticmethod
    def text(resp) -> str:
        return next(b.text for b in resp.content if b.type == "text")

    def summary(self) -> dict:
        return {"calls": len(self.calls),
                "cost_usd": round(sum(c.cost_usd for c in self.calls), 4),
                "latency_s": round(sum(c.latency_s for c in self.calls), 1),
                "by_purpose": [asdict(c) for c in self.calls]}
