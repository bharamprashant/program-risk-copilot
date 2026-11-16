"""How well does the copilot handle questions as real users write them?

30 messy questions: typos and broken English, Swedish, situations instead of questions, and off-topic
chatter. Each in-scope question lists the acceptable article(s). Metrics per kind:
- correct  : answered AND cited an acceptable article
- refused  : declined to answer (good for off-topic, bad for real questions)
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

from copilot.llm.client import LLM
from copilot.rag.answer import answer

GOLD = Path("evals/golden_messy.jsonl")


def run(tag: str) -> dict:
    llm = LLM()
    rows = [json.loads(l) for l in GOLD.open()]
    per, by_kind = [], defaultdict(lambda: {"n": 0, "correct": 0, "refused": 0})
    for x in rows:
        a = answer(x["question"], llm=llm)
        cited = [c.split(" — ")[0] for c in a["citations"]]
        ok = a["answerable"] and any(g in cited for g in x["gold"]) if x["gold"] else not a["answerable"]
        k = by_kind[x["kind"]]
        k["n"] += 1; k["correct"] += ok; k["refused"] += not a["answerable"]
        per.append({"id": x["id"], "kind": x["kind"], "question": x["question"], "gold": x["gold"], "answered": a["answerable"],
                    "cited": cited, "correct": ok, "understood_as": a.get("understood_as"), "language": a.get("language")})
    in_scope = [p for p in per if p["gold"]]
    out = {"tag": tag,
           "in_scope_correct": round(sum(p["correct"] for p in in_scope) / len(in_scope), 3),
           "in_scope_refused": round(sum(not p["answered"] for p in in_scope) / len(in_scope), 3),
           "off_topic_refused": round(by_kind["off_topic"]["refused"] / by_kind["off_topic"]["n"], 3),
           "by_kind": {k: {"correct": f"{v['correct']}/{v['n']}", "refused": v["refused"]} for k, v in by_kind.items()},
           "cost_usd": llm.summary()["cost_usd"], "per_question": per}
    Path(f"artifacts/messy_eval_{tag}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    return out


if __name__ == "__main__":
    r = run(sys.argv[1] if len(sys.argv) > 1 else "current")
    print(json.dumps({k: v for k, v in r.items() if k != "per_question"}, ensure_ascii=False))
    for p in r["per_question"]:
        if not p["correct"]:
            print(f"  ✗ [{p['kind']}] {p['question'][:70]!r} want {p['gold']} got {p['cited'][:3]} answered={p['answered']}")
