"""Train and compare slip-risk models, then save the chosen one with its metrics.

Design choices worth defending in an interview:
- Time-based split: train on older issues, test on the newest 20%. A random split would let the
  model "see the future" (later conventions, later people) and overstate accuracy.
- Imbalanced label (~10-20% slip): judge by PR-AUC and recall at a fixed alert budget, not accuracy.
  A model that predicts "never slips" is ~85% accurate and useless.
- Explainable model preferred: if logistic regression is close to gradient boosting, we ship the
  model whose reasons a steering committee can read.
"""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from copilot.risk.features import build_table, load_issues

CAT = ["project", "type", "priority"]
NUM = ["n_components", "n_labels", "summary_words", "desc_words_log", "has_description",
       "self_assigned", "unassigned", "assignee_load"]
MODEL = Path("artifacts/risk_model.joblib")
METRICS = Path("artifacts/risk_metrics.json")
ALERT_BUDGET = 0.20  # the PMO can review the riskiest 20% of planned work
MATURITY_DAYS = 180  # only learn from issues old enough to have had the chance to slip (avoids censoring bias)


def preprocessor(text: bool) -> ColumnTransformer:
    parts = [("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=20), CAT),
             ("num", StandardScaler(), NUM)]
    if text:
        parts.append(("txt", TfidfVectorizer(max_features=300, min_df=10, stop_words="english"), "text"))
    return ColumnTransformer(parts)


def at_budget(y: np.ndarray, p: np.ndarray, budget: float = ALERT_BUDGET) -> dict:
    """If we flag the top `budget` share of issues, how many real slips do we catch?"""
    n = int(len(p) * budget)
    flagged = np.argsort(-p)[:n]
    caught = y[flagged].sum()
    return {"precision": round(caught / n, 3), "recall": round(caught / y.sum(), 3),
            "lift": round((caught / n) / y.mean(), 2)}


def evaluate(name: str, y: np.ndarray, p: np.ndarray) -> dict:
    return {"model": name, "roc_auc": round(roc_auc_score(y, p), 3),
            "pr_auc": round(average_precision_score(y, p), 3), "base_rate": round(y.mean(), 3),
            f"top_{int(ALERT_BUDGET * 100)}pct": at_budget(y, p)}


def main():
    t = build_table(load_issues()).sort_values("created").reset_index(drop=True)
    # Censoring: we only downloaded resolved issues, so recent ones are biased toward quick wins
    # (slow, slipping work from that period is still open). Keep issues with time to mature.
    cutoff = t["created"].max() - pd.Timedelta(days=MATURITY_DAYS)
    print(f"dropping {(t.created > cutoff).sum()} issues newer than {cutoff:%Y-%m-%d} (not mature)")
    t = t[t["created"] <= cutoff].reset_index(drop=True)
    cut = int(len(t) * 0.8)
    train, test = t.iloc[:cut], t.iloc[cut:]
    X_cols = CAT + NUM + ["text"]
    y_tr, y_te = train["slipped"].values, test["slipped"].values
    print(f"train {len(train)} ({train.created.min():%Y-%m} to {train.created.max():%Y-%m}), "
          f"test {len(test)} (to {test.created.max():%Y-%m}); slip rate train {y_tr.mean():.3f} test {y_te.mean():.3f}")

    candidates = {
        "logistic_regression": Pipeline([("prep", preprocessor(text=True)),
                                         ("clf", LogisticRegression(max_iter=2000, C=0.5, class_weight="balanced"))]),
        "gradient_boosting": Pipeline([("prep", preprocessor(text=True)),
                                       ("clf", HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05,
                                                                              class_weight="balanced", random_state=0))]),
        "logistic_no_text": Pipeline([("prep", preprocessor(text=False)),
                                      ("clf", LogisticRegression(max_iter=2000, class_weight="balanced"))]),
    }
    results = [{"model": "baseline_random", "roc_auc": 0.5, "pr_auc": round(y_te.mean(), 3),
                "base_rate": round(y_te.mean(), 3), f"top_{int(ALERT_BUDGET * 100)}pct": {"precision": round(y_te.mean(), 3), "recall": ALERT_BUDGET, "lift": 1.0}}]
    fitted = {}
    for name, pipe in candidates.items():
        if name == "gradient_boosting":
            pipe.set_params(prep__txt__max_features=100)
            Xtr = pipe.named_steps["prep"].fit_transform(train[X_cols]).toarray()
            pipe.named_steps["clf"].fit(Xtr, y_tr)
            p = pipe.named_steps["clf"].predict_proba(pipe.named_steps["prep"].transform(test[X_cols]).toarray())[:, 1]
        else:
            pipe.fit(train[X_cols], y_tr)
            p = pipe.predict_proba(test[X_cols])[:, 1]
        fitted[name] = pipe
        results.append(evaluate(name, y_te, p))

    for r in results:
        print(json.dumps(r))
    lr = next(r for r in results if r["model"] == "logistic_regression")
    gb = next(r for r in results if r["model"] == "gradient_boosting")
    chosen = "logistic_regression" if lr["pr_auc"] >= gb["pr_auc"] - 0.02 else "gradient_boosting"
    print(f"chosen: {chosen} (explainable model kept unless the challenger beats it by >0.02 PR-AUC)")
    joblib.dump({"pipeline": fitted[chosen], "name": chosen, "columns": X_cols}, MODEL)
    METRICS.write_text(json.dumps({"chosen": chosen, "n_train": len(train), "n_test": len(test),
                                   "split": "time-based, newest 20% held out", "results": results}, indent=2))


if __name__ == "__main__":
    main()
