"""Download resolved Apache Jira issues (with change history) for training the slip model.

Apache's Jira is public, so no account is needed. We page politely (1 request/second)
and save one JSON line per issue, keeping only the fields the model is allowed to use.
"""
import json
import sys
import time
from pathlib import Path

import requests

BASE = "https://issues.apache.org/jira/rest/api/2/search"
PROJECTS = ["KAFKA", "SPARK", "FLINK", "HIVE", "CASSANDRA", "HBASE"]
PER_PROJECT = 1500
PAGE = 100
OUT = Path("data/raw/jira")
FIELDS = "issuetype,priority,components,created,resolutiondate,summary,description,fixVersions,labels,issuelinks,reporter,assignee"


def slim(issue: dict) -> dict:
    f = issue["fields"]
    fix_history = [
        {"at": h["created"], "from": it.get("fromString"), "to": it.get("toString")}
        for h in issue.get("changelog", {}).get("histories", [])
        for it in h["items"]
        if it["field"] == "Fix Version"
    ]
    return {
        "key": issue["key"],
        "project": issue["key"].split("-")[0],
        "type": f["issuetype"]["name"],
        "priority": (f.get("priority") or {}).get("name"),
        "components": [c["name"] for c in f.get("components") or []],
        "labels": f.get("labels") or [],
        "created": f["created"],
        "resolved": f.get("resolutiondate"),
        "summary": f.get("summary") or "",
        "description": (f.get("description") or "")[:4000],
        "fix_versions": [v["name"] for v in f.get("fixVersions") or []],
        "n_links": len(f.get("issuelinks") or []),
        "reporter": (f.get("reporter") or {}).get("name"),
        "assignee": (f.get("assignee") or {}).get("name"),
        "fix_version_history": fix_history,
    }


def fetch(project: str) -> int:
    out = OUT / f"{project}.jsonl"
    jql = f"project={project} AND resolution=Fixed AND fixVersion is not EMPTY AND created >= 2016-01-01 ORDER BY created DESC"
    n = 0
    with out.open("w") as fh:
        for start in range(0, PER_PROJECT, PAGE):
            for attempt in range(3):
                r = requests.get(BASE, params={"jql": jql, "startAt": start, "maxResults": PAGE,
                                               "expand": "changelog", "fields": FIELDS}, timeout=60)
                if r.ok:
                    break
                time.sleep(5 * (attempt + 1))
            r.raise_for_status()
            issues = r.json()["issues"]
            for i in issues:
                fh.write(json.dumps(slim(i)) + "\n")
            n += len(issues)
            print(f"{project}: {n}", flush=True)
            if len(issues) < PAGE:
                break
            time.sleep(1)
    return n


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    total = sum(fetch(p) for p in (sys.argv[1:] or PROJECTS))
    print(f"done: {total} issues")
