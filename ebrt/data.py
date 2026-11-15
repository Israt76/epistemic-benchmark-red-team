"""Three sources of systems: synthetic profiles, real classifiers, real forecasts."""
import csv
import os

import numpy as np

from .core import _logit, _sig


# ---- synthetic -----------------------------------------------------------------
def synth_items(n=4000, seed=0):
    rng = np.random.default_rng(seed)
    hard = rng.random(n) < 0.5
    d = np.where(hard, rng.normal(1, 0.7, n), rng.normal(-1, 0.7, n))
    return {"d": d, "hard": hard, "eps": rng.normal(size=n), "u": rng.random(n),
            "dev": rng.random(n) < 0.5}


def synth_params(k=150, seed=1):
    rng = np.random.default_rng(seed)
    return [{"skill": rng.uniform(0.3, 2.5), "noise": rng.uniform(0.3, 2.5),
             "temp": float(np.exp(rng.uniform(np.log(0.4), np.log(2.5)))),
             "bias": rng.uniform(-1, 1.5)} for _ in range(k)]


def synth_system(p, items):
    """skill -> accuracy; noise -> how well confidence tracks correctness;
    temp, bias -> miscalibration. Same item noise for every system."""
    prob = _sig(p["skill"] - 1.5 * items["d"])
    y = (items["u"] < prob).astype(float)
    c = _sig(p["temp"] * (_logit(prob) + p["noise"] * items["eps"]) + p["bias"])
    return c, y


# ---- real classifiers on real data bundled with scikit-learn --------------------
def classifier_systems(seeds=(0, 1, 2, 3, 4), train_frac=0.15):
    from sklearn.datasets import load_breast_cancer, load_digits, load_wine
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.naive_bayes import GaussianNB
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC
    from sklearn.tree import DecisionTreeClassifier
    models = {
        "LogReg": lambda s: make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
        "NaiveBayes": lambda s: GaussianNB(),
        "RandomForest": lambda s: RandomForestClassifier(100, random_state=s),
        "GradBoost": lambda s: GradientBoostingClassifier(n_estimators=60, random_state=s),
        "SVM-Platt": lambda s: make_pipeline(StandardScaler(), SVC(probability=True, random_state=s)),
        "kNN": lambda s: make_pipeline(StandardScaler(), KNeighborsClassifier(7)),
        "MLP": lambda s: make_pipeline(StandardScaler(), MLPClassifier((64,), max_iter=800, random_state=s)),
        "Tree": lambda s: DecisionTreeClassifier(max_depth=6, random_state=s),
    }
    data = {"digits": load_digits(return_X_y=True), "breast_cancer": load_breast_cancer(return_X_y=True),
            "wine": load_wine(return_X_y=True)}
    out = []
    for dname, (X, Y) in data.items():
        for s in seeds:
            Xtr, Xte, Ytr, Yte = train_test_split(X, Y, train_size=train_frac, random_state=s, stratify=Y)
            dev = np.random.default_rng(s).random(len(Yte)) < 0.5
            for mname, mk in models.items():
                P = mk(s).fit(Xtr, Ytr).predict_proba(Xte)
                c, y = P.max(1), (P.argmax(1) == Yte).astype(float)
                out.append({"name": f"{mname}|{dname}|{s}", "model": mname, "task": dname, "seed": s,
                            "c": c, "y": y, "dev": dev})
    return out


# ---- real probabilistic forecasts (FiveThirtyEight, public archive) --------------
def forecast_systems(folder, cap=4000, seed=0):
    rng = np.random.default_rng(seed)
    out = []

    def add(name, probs, outcomes):
        """probs/outcomes: (n, k) arrays for k mutually exclusive outcomes.
        Answer = most likely outcome; confidence = its probability."""
        P, O = np.asarray(probs, float), np.asarray(outcomes, float)
        ok = ~np.isnan(P).any(1) & ~np.isnan(O).any(1) & (O.sum(1) == 1) & np.isin(O, (0, 1)).all(1)  # drops ties
        P, O = P[ok], O[ok]
        if len(P) > cap:
            keep = rng.choice(len(P), cap, replace=False)
            P, O = P[keep], O[keep]
        pick = P.argmax(1)
        c, y = P.max(1), O[np.arange(len(P)), pick]
        out.append({"name": name, "c": c, "y": y, "dev": rng.random(len(c)) < 0.5})

    def rows(fn):
        with open(os.path.join(folder, fn), encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def num(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return np.nan

    for fn in ("mlb_games", "nba_games", "nfl_games", "nhl_games",
               "march_madness_in_game_men", "march_madness_in_game_women"):
        r = rows(fn + ".csv")
        add(fn, [[num(x["prob1"]), num(x["prob2"])] for x in r],
            [[num(x["prob1_outcome"]), num(x["prob2_outcome"])] for x in r])
    r = rows("club_soccer_matches.csv")
    add("club_soccer_matches", [[num(x["prob1"]), num(x["probtie"]), num(x["prob2"])] for x in r],
        [[num(x["prob1_outcome"]), num(x["probtie_outcome"]), num(x["prob2_outcome"])] for x in r])
    for fn in ("presidential_elections", "governors_elections"):
        r = rows(fn + ".csv")
        p = np.array([num(x["probwin"]) for x in r])
        o = np.array([num(x["probwin_outcome"]) for x in r])
        add(fn, np.c_[p, 1 - p], np.c_[o, 1 - o])
    return out
