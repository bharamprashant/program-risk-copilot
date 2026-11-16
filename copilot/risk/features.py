"""Turn raw Jira issues into a training table.

Label  — "slipped": a concrete Fix Version was removed from the issue, i.e. it missed a release it
         was planned for. Excluded, because they are process conventions rather than slips:
         - placeholder versions ("5.x", "4.1.x") that are swapped for the exact version on merge
         - bulk edits (>= 30 issues losing the same version on the same day: release renames/cleanups)
         Adding a version (a backport) is not a slip either.
Features — ONLY things a PM knows when the work is planned. Anything recorded later
         (final link count, resolution date, final fix versions) would leak the answer.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("data/raw/jira")


def load_issues() -> pd.DataFrame:
    rows = [json.loads(l) for f in sorted(RAW.glob("*.jsonl")) for l in f.open()]
    df = pd.DataFrame(rows)
    df["created"] = pd.to_datetime(df["created"], utc=True)
    df["resolved"] = pd.to_datetime(df["resolved"], utc=True)
    return df.drop_duplicates("key").reset_index(drop=True)


BULK_MIN = 30


def is_placeholder(version: str) -> bool:
    return version.lower().endswith("x")


def bulk_edits(df: pd.DataFrame) -> set[tuple[str, str, str]]:
    """(project, version, day) combinations where many issues lost the same version at once."""
    counts = {}
    for proj, hist in zip(df["project"], df["fix_version_history"]):
        for h in hist:
            if h.get("from"):
                k = (proj, h["from"], h["at"][:10])
                counts[k] = counts.get(k, 0) + 1
    return {k for k, n in counts.items() if n >= BULK_MIN}


def slipped(project: str, history: list[dict], bulk: set) -> int:
    return int(any(h.get("from") and not is_placeholder(h["from"]) and (project, h["from"], h["at"][:10]) not in bulk
                   for h in history))


def assignee_load(df: pd.DataFrame) -> pd.Series:
    """How many other issues the same assignee already had open when this one was created."""
    load = pd.Series(0, index=df.index)
    for _, g in df[df["assignee"].notna()].groupby("assignee"):
        created, resolved = g["created"].values, g["resolved"].values
        for i, c in zip(g.index, created):
            load[i] = int(((created < c) & (resolved > c)).sum())
    return load


def build_table(df: pd.DataFrame) -> pd.DataFrame:
    bulk = bulk_edits(df)
    t = pd.DataFrame({
        "key": df["key"],
        "project": df["project"],
        "type": df["type"].fillna("Unknown"),
        "priority": df["priority"].fillna("Unknown"),
        "n_components": df["components"].str.len(),
        "n_labels": df["labels"].str.len(),
        "summary_words": df["summary"].str.split().str.len(),
        "desc_words_log": np.log1p(df["description"].str.split().str.len()),
        "has_description": (df["description"].str.len() > 0).astype(int),
        "self_assigned": (df["reporter"] == df["assignee"]).astype(int),
        "unassigned": df["assignee"].isna().astype(int),
        "assignee_load": assignee_load(df),
        "text": (df["summary"] + " " + df["description"].str[:1000]).str.lower(),
        "created": df["created"],
        "slipped": [slipped(p, h, bulk) for p, h in zip(df["project"], df["fix_version_history"])],
    })
    return t


if __name__ == "__main__":
    t = build_table(load_issues())
    print(t.shape, "slip rate", round(t["slipped"].mean(), 3))
    print(t.groupby("project")["slipped"].agg(["mean", "count"]).round(3))
    print(t.groupby("priority")["slipped"].agg(["mean", "count"]).round(3))
