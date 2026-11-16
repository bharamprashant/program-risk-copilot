"""Grid-search the fusion weights and refusal threshold on the DEV split only."""
import json
from copilot.rag.index import Retriever
from evals.rag_eval import evaluate

r = Retriever.load()
results = []
for w_dense in (0.0, 0.25, 0.5, 0.75, 1.0):
    for thr in (6.0, 8.0, 10.0, 12.0):
        r.weights, r.bm25_threshold = (1.0, w_dense), thr
        m = evaluate(r, "dev")
        # One number to optimise: what the LLM gets to read, minus a penalty for refusing real questions.
        objective = m["recall@5"] + 0.5 * m["mrr"] - m["real_questions_wrongly_refused"] + 0.5 * m["off_topic_refused"]
        results.append((round(objective, 3), w_dense, thr, m["hit@1"], m["recall@5"], m["mrr"], m["off_topic_refused"], m["real_questions_wrongly_refused"]))
results.sort(reverse=True)
print("objective w_dense thr  hit@1 rec@5  mrr  offtopic_refused wrongly_refused")
for row in results[:8]:
    print(row)
best = results[0]
json.dump({"w_dense": best[1], "bm25_threshold": best[2]}, open("artifacts/rag_params.json", "w"))
