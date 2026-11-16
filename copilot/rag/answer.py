"""Answer a regulatory question with citations, or refuse.

Pipeline:
1. Query rewriting (small, cheap model): translate PM language into the regulation's own vocabulary.
   Retrieval uses both the original and the rewritten query.
2. Retrieval + abstention: if nothing matches well enough, refuse without calling the big model.
3. Generation (capable model, structured output): answer only from the retrieved chunks, citing chunk ids.
4. Grounding check in code: drop any cited id that was not retrieved; if none remain, refuse.

Offline mode (no API key) returns the top passages as an extractive answer.
"""
import json

from copilot.llm.client import FAST, LLM, available
from copilot.rag.index import Hit, Retriever

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answerable": {"type": "boolean"},
        "answer": {"type": "string"},
        "chunk_ids": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["answerable", "answer", "chunk_ids"],
    "additionalProperties": False,
}

ANSWER_SYSTEM = """You answer compliance questions for an EU fintech using ONLY the regulation excerpts provided \
inside <document> tags. Rules:
- If the excerpts do not answer the question, set answerable to false and say what is missing.
- Cite the chunk_id of every excerpt you rely on. Never cite anything else.
- Two to four sentences, plain English, for a program manager. This is not legal advice."""

_retriever = None


def retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever.load()
    return _retriever


def rewrite(llm: LLM, question: str) -> str:
    resp = llm.create("query_rewrite", model=FAST, max_tokens=200, messages=[{"role": "user", "content":
        "Rewrite this question using the vocabulary of EU financial regulation (DORA, GDPR, PSD2), as a short search "
        f"query of key legal terms. Output only the query.\n\nQuestion: {question}"}])
    return LLM.text(resp).strip()


def fuse(a: list[Hit], b: list[Hit], k: int = 5) -> list[Hit]:
    scores, by_id = {}, {}
    for hits in (a, b):
        for rank, h in enumerate(hits):
            scores[h.chunk["id"]] = scores.get(h.chunk["id"], 0) + 1 / (60 + rank + 1)
            by_id.setdefault(h.chunk["id"], h)
    return [by_id[i] for i in sorted(scores, key=lambda i: -scores[i])[:k]]


def answer(question: str, llm: LLM | None = None, use_rewrite: bool = True) -> dict:
    r = retriever()
    if llm is None and available():
        llm = LLM()
    hits = r.search(question, k=5)
    rewritten = None
    if llm and use_rewrite:
        rewritten = rewrite(llm, question)
        hits = fuse(hits, r.search(rewritten, k=5))
    if not r.answerable(hits):
        return {"question": question, "answerable": False, "answer": "No relevant provision found in DORA, GDPR or PSD2.",
                "citations": [], "rewritten_query": rewritten, "mode": "llm" if llm else "offline"}
    if not llm:
        top = hits[0].chunk
        return {"question": question, "answerable": True, "answer": top["text"][:500] + " ...",
                "citations": [h.chunk["citation"] for h in hits[:3]], "chunk_ids": [h.chunk["id"] for h in hits[:3]],
                "mode": "offline"}
    docs = "\n".join(f'<document chunk_id="{h.chunk["id"]}" citation="{h.chunk["citation"]}">{h.chunk["text"]}</document>'
                     for h in hits)
    resp = llm.create("rag_answer", system=ANSWER_SYSTEM, max_tokens=2000,
                      output_config={"format": {"type": "json_schema", "schema": ANSWER_SCHEMA}},
                      messages=[{"role": "user", "content": f"{docs}\n\nQuestion: {question}"}])
    out = json.loads(LLM.text(resp))
    retrieved = {h.chunk["id"]: h.chunk for h in hits}
    grounded = [i for i in out["chunk_ids"] if i in retrieved]
    ungrounded = [i for i in out["chunk_ids"] if i not in retrieved]
    answerable = out["answerable"] and bool(grounded)
    return {"question": question, "answerable": answerable,
            "answer": out["answer"] if answerable else "No supported answer in the retrieved provisions.",
            "citations": [retrieved[i]["citation"] for i in grounded], "chunk_ids": grounded,
            "ungrounded_citations_dropped": ungrounded, "rewritten_query": rewritten, "mode": "llm"}
