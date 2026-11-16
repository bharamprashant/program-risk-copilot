"""Score issues for slip risk and explain each score in plain words.

For logistic regression, each feature's contribution to the score is exactly coefficient x value,
so the "top reasons" are faithful to the model, not a post-hoc approximation.
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

MODEL = Path("artifacts/risk_model.joblib")

READABLE = {
    "num__assignee_load": "assignee already has many open issues",
    "num__unassigned": "no owner assigned",
    "num__self_assigned": "reporter assigned it to themselves",
    "num__desc_words_log": "length of the description",
    "num__has_description": "has a description",
    "num__n_components": "touches several components",
    "num__n_labels": "number of labels",
    "num__summary_words": "length of the summary",
}


def readable(feature: str) -> str:
    if feature in READABLE:
        return READABLE[feature]
    kind, _, rest = feature.partition("__")
    if kind == "txt":
        return f'mentions "{rest}"'
    if kind == "cat":
        col, _, val = rest.partition("_")
        return f"{col} is {val}"
    return feature


class RiskModel:
    def __init__(self):
        bundle = joblib.load(MODEL)
        self.pipe, self.columns = bundle["pipeline"], bundle["columns"]
        self.prep, self.clf = self.pipe.named_steps["prep"], self.pipe.named_steps["clf"]
        self.names = self.prep.get_feature_names_out()

    def score(self, issues: pd.DataFrame, top_n: int = 3) -> list[dict]:
        X = self.prep.transform(issues[self.columns])
        probs = self.clf.predict_proba(X)[:, 1]
        contrib = X.multiply(self.clf.coef_[0]).toarray() if hasattr(X, "multiply") else X * self.clf.coef_[0]
        out = []
        for i, key in enumerate(issues["key"]):
            order = np.argsort(-contrib[i])
            # A numeric feature only counts as a reason when it is above average (z > 0): its label
            # ("many open issues", "no owner") describes the high side. Below-average values can still push
            # the score up through a negative weight, but "has an owner" is not a reason to worry.
            dense_row = X[i].toarray()[0] if hasattr(X, "toarray") else X[i]
            reasons = [readable(self.names[j]) for j in order
                       if contrib[i, j] > 0 and (not self.names[j].startswith("num__") or dense_row[j] > 0)][:top_n]
            out.append({"key": key, "slip_risk": round(float(probs[i]), 3), "reasons": reasons})
        return out


def features_for_open(issues: list[dict]) -> pd.DataFrame:
    """Build model features for open work (no resolution dates yet): load = other open issues per assignee."""
    df = pd.DataFrame(issues)
    open_per_assignee = df["assignee"].value_counts()
    return pd.DataFrame({
        "key": df["key"], "project": df["project"], "type": df["type"], "priority": df["priority"],
        "n_components": df["components"].str.len(), "n_labels": df["labels"].str.len(),
        "summary_words": df["summary"].str.split().str.len(),
        "desc_words_log": np.log1p(df["description"].str.split().str.len()),
        "has_description": (df["description"].str.len() > 0).astype(int),
        "self_assigned": (df["reporter"] == df["assignee"]).astype(int),
        "unassigned": df["assignee"].isna().astype(int),
        "assignee_load": df["assignee"].map(open_per_assignee).fillna(1).astype(int) - 1,
        "text": (df["summary"] + " " + df["description"]).str.lower(),
    })


if __name__ == "__main__":
    from copilot.risk.features import build_table, load_issues
    t = build_table(load_issues()).sort_values("created").tail(400)
    scored = sorted(RiskModel().score(t), key=lambda r: -r["slip_risk"])
    for r in scored[:5]:
        print(r)
