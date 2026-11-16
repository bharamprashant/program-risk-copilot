# Program Risk & Compliance Copilot

An AI assistant for program managers in regulated EU fintech. It **predicts which work will slip**, **checks the program against DORA, GDPR and PSD2 with citations**, and **drafts the steering-committee briefing**. A named person approves every briefing before it goes out.

Every number below is measured, and the limits are stated. **[Results dashboard →](docs/index.html)**

```
 Jira issues ──► [ML] slip-risk model ─────────────┐
                 (explains each score)              │
 DORA/GDPR/PSD2 ─► [RAG] hybrid search ─────────────┼──► [Agent] Claude picks tools ──► briefing (fixed JSON schema)
                   (cites articles, or refuses)     │                                       │
 ticket text ──► [Guardrails] redact PII, flag injection                                   ▼
                                                     grounding check ──► human approval ──► audit log (hash chain)
```

## What's in it

| Part | AI concept | Where |
|---|---|---|
| Slip-risk predictor trained on 9,000 Apache Jira issues | Classic ML, label design, time-based split, explainability | `copilot/risk/` |
| Article-level search over the official EU texts | RAG: chunking, BM25 + LSA embeddings, rank fusion, abstention | `copilot/rag/index.py` |
| Answers with citations | LLM generation, query rewriting, structured output, grounding check | `copilot/rag/answer.py` |
| Briefing agent | Tool use, agent loop, model routing, refusal fallback | `copilot/agent.py` |
| Guardrails | PII redaction, prompt-injection flags, human approval, tamper-evident log | `copilot/guardrails.py`, `copilot/audit.py` |
| Evaluation | Golden set with dev/test split, LLM-as-judge, red team, cost and latency | `evals/` |

## Results (held-out test data)

| Measure | Result |
|---|---|
| Right regulation article in the top 5 search results | see dashboard (dev 84%, test 68% before LLM query rewriting) |
| Off-topic questions refused | 100% |
| Slip model: share of slips caught when reviewing the riskiest 20% of work | 32% (1.6× random) |
| PII reaching the model or tools in the demo | none (email, personnummer, IBAN redacted) |
| Planted prompt injection followed | see dashboard (red-team result) |

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt anthropic
.venv/bin/python -m copilot.data.fetch_regs        # official texts from the EU Publications Office
.venv/bin/python -m copilot.data.fetch_jira        # ~10 min, public Apache Jira
.venv/bin/python -m copilot.risk.train
.venv/bin/python -m copilot.cli brief              # offline baseline, no API key needed
.venv/bin/python -m copilot.cli brief --mode llm   # Claude agent (ANTHROPIC_API_KEY in .env)
.venv/bin/python -m copilot.cli approve --approver "Your Name"
.venv/bin/python -m copilot.cli ask "Do we need a register of our cloud vendors?"
.venv/bin/python -m pytest -q                      # 16 tests, including a retrieval-quality release gate
```

## Limitations

- The RAG test set is 30 questions written by the author. Some "misses" are arguably right (e.g. DORA Art. 23 for payment incidents that PSD2 Art. 96 used to cover).
- The slip model learned from open-source projects. On a fintech program it is one signal among several (**domain shift**); retraining on the organisation's own Jira history is the fix. Scores rank risk; they are not calibrated probabilities.
- The demo portfolio is fictional. Nothing here is legal advice.

See [DECISIONS.md](DECISIONS.md) for every design choice and the alternatives considered.
