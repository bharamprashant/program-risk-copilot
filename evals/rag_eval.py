"""Retrieval evaluation: does the search find the right article, and does it refuse off-topic questions?

Metrics (article level, because that is what a citation points to):
- hit@1     : the top result is the correct article
- recall@5  : the correct article is somewhere in the top 5 (what the LLM gets to read)
- MRR       : mean reciprocal rank; rewards putting the right answer higher
- refusal   : off-topic questions refused (true negatives) vs real questions wrongly refused

Tune on the dev split only; report the test split. Tuning on the test set would overstate quality.
"""
import argparse
import json
from pathlib import Path

from copilot.rag.index import Retriever

GOLD = Path("evals/golden_rag.jsonl")


def evaluate(r: Retriever, split: str) -> dict:
    rows = [json.loads(l) for l in GOLD.open() if json.loads(l)["split"] == split]
    in_scope = [x for x in rows if x["article"]]
    oos = [x for x in rows if not x["article"]]
    hit1 = rec5 = mrr = wrongly_refused = 0
    misses = []
    for x in in_scope:
        hits = r.search(x["question"], k=5)
        arts = [(h.chunk["reg"], h.chunk["article"]) for h in hits]
        target = (x["reg"], x["article"])
        if arts and arts[0] == target:
            hit1 += 1
        if target in arts:
            rec5 += 1
            mrr += 1 / (arts.index(target) + 1)
        else:
            misses.append({"q": x["question"], "want": f"{target[0]} {target[1]}", "got": [f"{a} {b}" for a, b in arts[:3]]})
        if not r.answerable(hits):
            wrongly_refused += 1
    correctly_refused = sum(not r.answerable(r.search(x["question"], k=5)) for x in oos)
    n = len(in_scope)
    return {
        "split": split, "n_in_scope": n, "n_out_of_scope": len(oos),
        "hit@1": round(hit1 / n, 3), "recall@5": round(rec5 / n, 3), "mrr": round(mrr / n, 3),
        "off_topic_refused": round(correctly_refused / len(oos), 3),
        "real_questions_wrongly_refused": round(wrongly_refused / n, 3),
        "misses": misses,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev")
    ap.add_argument("--save", action="store_true")
    a = ap.parse_args()
    res = evaluate(Retriever.load(), a.split)
    print(json.dumps({k: v for k, v in res.items() if k != "misses"}, indent=2))
    for m in res["misses"]:
        print(f"MISS  want {m['want']:8}  got {m['got']}  | {m['q']}")
    if a.save:
        Path("artifacts").mkdir(exist_ok=True)
        Path(f"artifacts/rag_eval_{a.split}.json").write_text(json.dumps(res, indent=2))
