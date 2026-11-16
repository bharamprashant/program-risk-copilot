"""Command line: draft a briefing, and release it only with a named approver.

    python -m copilot.cli brief                  # offline baseline (no API key needed)
    python -m copilot.cli brief --mode llm       # Claude agent
    python -m copilot.cli approve --approver "Prashant Bharam"
    python -m copilot.cli ask "Do we need a register of our cloud vendors?"
    python -m copilot.cli verify-audit
"""
import argparse
import json
import shutil
from pathlib import Path

from copilot import audit
from copilot.agent import Copilot, to_markdown
from copilot.llm.client import available

DRAFT = Path("artifacts/outbox/draft_briefing.md")
APPROVED = Path("artifacts/outbox/approved_briefing.md")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("brief")
    b.add_argument("--mode", choices=["offline", "llm"], default="offline")
    a = sub.add_parser("approve")
    a.add_argument("--approver", required=True)
    q = sub.add_parser("ask")
    q.add_argument("question")
    sub.add_parser("verify-audit")
    args = ap.parse_args()

    if args.cmd == "brief":
        if args.mode == "llm" and not available():
            raise SystemExit("No ANTHROPIC_API_KEY found (.env). Run with --mode offline, or add a key.")
        r = Copilot().brief(args.mode)
        DRAFT.parent.mkdir(parents=True, exist_ok=True)
        DRAFT.write_text(to_markdown(r))
        Path(f"artifacts/brief_{args.mode}.json").write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(DRAFT.read_text())
        print(f"\nTools called: {len(r['trace'])}. Grounding problems: {r['grounding_problems'] or 'none'}.")
        if r["llm"]:
            print(f"LLM cost: ${r['llm']['cost_usd']} over {r['llm']['calls']} calls, {r['llm']['latency_s']}s")
        print(f"Draft saved to {DRAFT}. Not sent: run `approve --approver NAME` after review.")
    elif args.cmd == "approve":
        if not DRAFT.exists():
            raise SystemExit("No draft to approve.")
        shutil.copy(DRAFT, APPROVED)
        audit.append("brief_approved", approver=args.approver, file=str(APPROVED))
        print(f"Approved by {args.approver}: {APPROVED}")
    elif args.cmd == "ask":
        from copilot.rag.answer import answer
        print(json.dumps(answer(args.question), indent=2, ensure_ascii=False))
    elif args.cmd == "verify-audit":
        ok, msg = audit.verify()
        print(("OK: " if ok else "TAMPERED: ") + msg)


if __name__ == "__main__":
    main()
