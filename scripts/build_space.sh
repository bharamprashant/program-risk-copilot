#!/usr/bin/env bash
# Assemble build/space/ for Hugging Face: an allowlist of files, nothing else.
# Secrets (.env), raw data and git history are never copied.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=build/space
rm -rf "$OUT" && mkdir -p "$OUT"/{data/processed,data/demo,artifacts}
cp app.py "$OUT"/
rsync -a --exclude '__pycache__' --exclude 'data/' copilot "$OUT"/
cp data/processed/chunks.jsonl "$OUT"/data/processed/
cp data/demo/portfolio.json "$OUT"/data/demo/
for f in risk_model.joblib rag_eval_test.json risk_metrics.json llm_eval.json; do
  [ -f "artifacts/$f" ] && cp "artifacts/$f" "$OUT"/artifacts/
done
cat > "$OUT"/requirements.txt <<'REQ'
anthropic==2.8.0
gradio==6.32.0
joblib==1.6.0
numpy==2.5.5
pandas==3.1.1
scikit-learn==1.9.1
REQ
cat > "$OUT"/README.md <<'MD'
---
title: Program Risk Copilot
emoji: 📋
colorFrom: green
colorTo: gray
sdk: gradio
sdk_version: 6.32.0
python_version: "3.12"
app_file: app.py
pinned: false
license: mit
short_description: ML slip risk + RAG over DORA/GDPR/PSD2 + AI agent
---
Program Risk & Compliance Copilot. Source and full documentation:
https://github.com/bharamprashant/program-risk-copilot
MD
# Safety check: refuse to continue if anything secret-looking slipped in.
if grep -rIl "sk-ant-" "$OUT" >/dev/null 2>&1 || find "$OUT" -name ".env*" | grep -q .; then
  echo "ABORT: secret-looking content found in $OUT" >&2; exit 1
fi
echo "built $OUT:"; find "$OUT" -type f | sort
