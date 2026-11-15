"""Epistemic Benchmark Red Team: run every analysis.   python run_audit.py

Writes results/*.csv and results/summary.json. Deterministic (fixed seeds).
"""
import itertools
import json
import warnings

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr

from ebrt.core import METRICS, STAKES, decision_regret, gain, make_exploits, optimise_remap, value_loss
from ebrt.data import classifier_systems, forecast_systems, synth_items, synth_params, synth_system

warnings.filterwarnings("ignore")
HARD = "Net benefit (hardened)"
ones = lambda n: np.ones(n, bool)

# ---------------------------------------------------------------- systems
items = synth_items()
params = synth_params()
systems = []
for i, p in enumerate(params):
    c, y = synth_system(p, items)
    systems.append({"source": "synthetic", "name": f"syn{i:03d}", "c": c, "y": y, "dev": items["dev"]})
clf = classifier_systems()
for s in clf:
    if s["task"] != "wine":                       # wine test sets are too small to split again
        systems.append({"source": "classifiers", **s})
for s in forecast_systems("data_raw/538"):
    systems.append({"source": "forecasts", **s})
print({src: sum(s["source"] == src for s in systems) for src in ("synthetic", "classifiers", "forecasts")})

# ---------------------------------------------------------------- exploits A + B
YARD = {"decision_gain": ("mixed", "threshold"), "decision_gain_uniform": ("uniform", "threshold"),
        "decision_gain_low": ("low", "threshold"), "decision_gain_high": ("high", "threshold"),
        "decision_gain_naive": ("mixed", "naive")}
grid, attack = [], []
for s in systems:
    d = s["dev"]
    cd, yd, ct, yt = s["c"][d], s["y"][d], s["c"][~d], s["y"][~d]
    ex = make_exploits(cd, yd)
    base = {"dev": {m: f(cd, yd, ones(len(cd))) for m, f in METRICS.items()},
            "test": {m: f(ct, yt, ones(len(ct))) for m, f in METRICS.items()}}
    reg0 = {k: decision_regret(ct, yt, ones(len(ct)), stakes=st, user=u) for k, (st, u) in YARD.items()}
    rows = {}
    for name, (family, kind, fn) in ex.items():
        c2d, a2d = fn(cd)
        c2t, a2t = fn(ct)
        gD = {k: gain(reg0[k], decision_regret(c2t, yt, a2t, y_base=yt, stakes=st, user=u))
              for k, (st, u) in YARD.items()}
        for m, f in METRICS.items():
            rows[(name, m)] = {"source": s["source"], "system": s["name"], "metric": m, "exploit": name,
                               "family": family, "kind": kind,
                               "score_gain_dev": gain(base["dev"][m], f(c2d, yd, a2d)),
                               "score_gain": gain(base["test"][m], f(c2t, yt, a2t)),
                               **gD, "coverage": float(a2t.mean())}
    grid += list(rows.values())
    # The red-team attacker. For each metric it considers every cosmetic hand-made exploit
    # plus a remap optimised directly against that metric, keeps whichever scores best on
    # DEV, and is then evaluated on TEST. Two scopes: confidence-only, or abstention allowed.
    for m in METRICS:
        opt = {}
        for scope, allow in (("confidence", False), ("abstention", True)):
            fn = optimise_remap(cd, yd, METRICS[m], allow)
            c2d, a2d = fn(cd)
            c2t, a2t = fn(ct)
            opt[scope] = {"source": s["source"], "system": s["name"], "metric": m,
                          "exploit": "optimised remap" + (" + abstain" if allow else ""),
                          "family": scope, "kind": "cosmetic",
                          "score_gain_dev": gain(base["dev"][m], METRICS[m](c2d, yd, a2d)),
                          "score_gain": gain(base["test"][m], METRICS[m](c2t, yt, a2t)),
                          **{k: gain(reg0[k], decision_regret(c2t, yt, a2t, y_base=yt, stakes=st, user=u))
                             for k, (st, u) in YARD.items()},
                          "coverage": float(a2t.mean())}
        for scope in ("confidence", "abstention"):
            cand = [rows[(n, m)] for n, (fam_, kind, _) in ex.items() if kind == "cosmetic" and fam_ == scope]
            cand.append(opt[scope])
            if scope == "abstention":                      # an abstention attacker may also only edit confidence
                cand.append(opt["confidence"])
                cand += [rows[(n, m)] for n, (fam_, kind, _) in ex.items() if kind == "cosmetic" and fam_ == "confidence"]
            best = max(cand, key=lambda r: r["score_gain_dev"])
            attack.append({**best, "attacker": scope})
grid, attack = pd.DataFrame(grid), pd.DataFrame(attack)
grid.to_csv("results/exploit_grid.csv", index=False)
attack.to_csv("results/attack.csv", index=False)


def med_ci(x, B=2000, seed=0):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    bs = np.median(rng.choice(x, (B, len(x))), axis=1)
    return float(np.median(x)), float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))


def rate(mask):
    return float(np.mean(mask))


prof = []
for (src, m, att), g in attack.groupby(["source", "metric", "attacker"]):
    row = {"source": src, "metric": m, "attacker": att, "n_systems": len(g)}
    for col, vals in (("score_gain", g.score_gain), ("decision_gain", g.decision_gain),
                      ("integrity_gap", g.score_gain - g.decision_gain)):
        row[col], row[col + "_lo"], row[col + "_hi"] = med_ci(vals)
    up = g.score_gain > 0.01
    row["unearned_rate"] = rate(up & (g.decision_gain <= 0.01))        # score up, decisions not better
    row["harmful_rate"] = rate(up & (g.decision_gain < -0.01))         # score up, decisions worse
    row["harmful_rate_low_stakes"] = rate(up & (g.decision_gain_low < -0.01))
    row["harmful_rate_high_stakes"] = rate(up & (g.decision_gain_high < -0.01))
    row["harmful_rate_naive_users"] = rate(up & (g.decision_gain_naive < -0.01))
    row["unearned_rate_naive_users"] = rate(up & (g.decision_gain_naive <= 0.01))
    row["top_exploit"] = g.exploit.value_counts().idxmax()
    prof.append(row)
prof = pd.DataFrame(prof)

# ---------------------------------------------------------------- responsiveness (synthetic)
resp = []
te = ~items["dev"]
for i, p in enumerate(params):
    c0, y0 = synth_system(p, items)
    L0 = {m: f(c0[te], y0[te], ones(te.sum())) for m, f in METRICS.items()}
    R0 = value_loss(c0[te], y0[te], ones(te.sum()))
    for label, q in (("more skill", {**p, "skill": p["skill"] + 0.5}),
                     ("better discrimination", {**p, "noise": p["noise"] * 0.5}),
                     ("calibration fix", {**p, "temp": 1.0, "bias": 0.0})):
        c1, y1 = synth_system(q, items)
        gD = gain(R0, value_loss(c1[te], y1[te], ones(te.sum())))
        for m, f in METRICS.items():
            resp.append({"system": i, "improvement": label, "metric": m,
                         "score_gain": gain(L0[m], f(c1[te], y1[te], ones(te.sum()))), "decision_gain": gD})
resp = pd.DataFrame(resp)
resp.to_csv("results/responsiveness.csv", index=False)
r_tab = resp.groupby("metric").apply(lambda g: pd.Series({
    "responsiveness_spearman": spearmanr(g.score_gain, g.decision_gain)[0],
    "real_gain_detected": float((g.score_gain[g.decision_gain > 0.01] > 0).mean())})).reset_index()

# ---------------------------------------------------------------- C: metric shopping
STD = [m for m in METRICS if m != HARD]
rng = np.random.default_rng(3)


def shop(pool_losses, pool_regret, alt=None):
    """pool_losses: metric -> array over systems. Returns winners + agreement
    with the decision-value ranking (and with low/high-stakes rankings)."""
    best_dec = int(np.argmin(pool_regret))
    winners = {m: int(np.argmin(v)) for m, v in pool_losses.items()}
    out = {"distinct_winners": len({winners[m] for m in STD}),
           "pool_size": len(pool_regret)}
    for m, v in pool_losses.items():
        out[f"tau|{m}"] = kendalltau(v, pool_regret)[0]
        out[f"top1|{m}"] = float(winners[m] == best_dec)
        for k, v2 in (alt or {}).items():
            out[f"tau_{k}|{m}"] = kendalltau(v, v2)[0]
    return out


syn = [s for s in systems if s["source"] == "synthetic"]
full = {s["name"]: ({m: f(s["c"][te], s["y"][te], ones(te.sum())) for m, f in METRICS.items()},
                    value_loss(s["c"][te], s["y"][te], ones(te.sum())),
                    {k: value_loss(s["c"][te], s["y"][te], ones(te.sum()), stakes=k) for k in ("low", "high")})
        for s in syn}
shop_rows = []
for k in range(500):
    pick = rng.choice(len(syn), 10, replace=False)
    L = {m: np.array([full[syn[j]["name"]][0][m] for j in pick]) for m in METRICS}
    R = np.array([full[syn[j]["name"]][1] for j in pick])
    alt = {k: np.array([full[syn[j]["name"]][2][k] for j in pick]) for k in ("low", "high")}
    shop_rows.append({"source": "synthetic", **shop(L, R, alt)})
for (task, seed), grp in itertools.groupby(sorted(clf, key=lambda s: (s["task"], s["seed"])),
                                           key=lambda s: (s["task"], s["seed"])):
    grp = list(grp)
    L = {m: np.array([f(s["c"], s["y"], ones(len(s["c"]))) for s in grp]) for m, f in METRICS.items()}
    R = np.array([value_loss(s["c"], s["y"], ones(len(s["c"]))) for s in grp])
    alt = {k: np.array([value_loss(s["c"], s["y"], ones(len(s["c"])), stakes=k) for s in grp]) for k in ("low", "high")}
    shop_rows.append({"source": "classifiers", **shop(L, R, alt)})
shopdf = pd.DataFrame(shop_rows)
shopdf.to_csv("results/shopping.csv", index=False)
s_tab = pd.DataFrame([{"source": src, "metric": m, "rank_agreement_tau": g[f"tau|{m}"].mean(),
                       "rank_agreement_tau_low_stakes": g[f"tau_low|{m}"].mean(),
                       "rank_agreement_tau_high_stakes": g[f"tau_high|{m}"].mean(),
                       "picks_best_decisions": g[f"top1|{m}"].mean()}
                      for src, g in shopdf.groupby("source") for m in METRICS])

# ---------------------------------------------------------------- D: distribution gaming (synthetic)
hard_idx, easy_idx = np.where(items["hard"] & te)[0], np.where(~items["hard"] & te)[0]
N = 800


def mix(w):
    return np.r_[hard_idx[:int(w * N)], easy_idx[:N - int(w * N)]]


mixL = {}
for w in (0.2, 0.8):
    ix = mix(w)
    mixL[w] = ({m: np.array([f(s["c"][ix], s["y"][ix], ones(N)) for s in syn]) for m, f in METRICS.items()},
               np.array([value_loss(s["c"][ix], s["y"][ix], ones(N)) for s in syn]))
pairs = [tuple(rng.choice(len(syn), 2, replace=False)) for _ in range(3000)]
d_rows = []
for m in METRICS:
    flips = dis = 0
    for i, j in pairs:
        s2, s8 = np.sign(mixL[0.2][0][m][i] - mixL[0.2][0][m][j]), np.sign(mixL[0.8][0][m][i] - mixL[0.8][0][m][j])
        flips += s2 != s8
        dis += (s2 != np.sign(mixL[0.2][1][i] - mixL[0.2][1][j])) + (s8 != np.sign(mixL[0.8][1][i] - mixL[0.8][1][j]))
    d_rows.append({"metric": m, "flip_rate_easy_vs_hard_mix": flips / len(pairs),
                   "disagrees_with_decisions": dis / (2 * len(pairs))})
dflip = sum(np.sign(mixL[0.2][1][i] - mixL[0.2][1][j]) != np.sign(mixL[0.8][1][i] - mixL[0.8][1][j])
            for i, j in pairs) / len(pairs)
d_tab = pd.DataFrame(d_rows)
d_tab.to_csv("results/distribution.csv", index=False)

# ---------------------------------------------------------------- integrity profile
profile = prof.merge(s_tab, on=["source", "metric"], how="left")
syn_only = r_tab.merge(d_tab, on="metric")
syn_only["source"] = "synthetic"                      # these two analyses need a generative model
profile = profile.merge(syn_only, on=["source", "metric"], how="left")
profile.to_csv("results/integrity_profile.csv", index=False)

byex = grid.groupby(["source", "metric", "exploit", "family", "kind"]).apply(
    lambda g: pd.Series({"score_gain": g.score_gain.median(), "decision_gain": g.decision_gain.median(),
                         "decision_gain_naive": g.decision_gain_naive.median()})).reset_index()
byex.to_csv("results/by_exploit.csv", index=False)
honest = grid[grid.kind == "honest"].groupby(["source", "metric"]).apply(
    lambda g: pd.Series({"score_gain": g.score_gain.median(), "decision_gain": g.decision_gain.median()})).reset_index()
honest.to_csv("results/honest_recalibration.csv", index=False)

summary = {
    "n_systems": {src: int(sum(s["source"] == src for s in systems)) for src in ("synthetic", "classifiers", "forecasts")},
    "shopping_distinct_winners_mean": shopdf.groupby("source").distinct_winners.mean().round(2).to_dict(),
    "shopping_share_pools_with_3plus_winners": shopdf.groupby("source").apply(lambda g: float((g.distinct_winners >= 3).mean())).round(3).to_dict(),
    "decision_ranking_flip_rate_easy_vs_hard": round(float(dflip), 3),
}
json.dump(summary, open("results/summary.json", "w"), indent=1)
pd.set_option("display.width", 250, "display.max_columns", 30, "display.float_format", lambda v: f"{v:.2f}")
for src in ("synthetic", "classifiers", "forecasts"):
    for att in ("confidence", "abstention"):
        print("\n==", src, "| attacker:", att)
        print(profile[(profile.source == src) & (profile.attacker == att)][
            ["metric", "score_gain", "decision_gain", "integrity_gap", "unearned_rate", "harmful_rate",
             "harmful_rate_high_stakes", "harmful_rate_naive_users", "top_exploit"]].to_string(index=False))
print("\n== synthetic-only columns")
print(profile[(profile.source == "synthetic") & (profile.attacker == "confidence")][
    ["metric", "rank_agreement_tau", "rank_agreement_tau_low_stakes", "rank_agreement_tau_high_stakes", "picks_best_decisions", "responsiveness_spearman", "real_gain_detected",
     "flip_rate_easy_vs_hard_mix", "disagrees_with_decisions"]].to_string(index=False))
print(profile[(profile.source == "classifiers") & (profile.attacker == "confidence")][
    ["metric", "rank_agreement_tau", "rank_agreement_tau_low_stakes", "rank_agreement_tau_high_stakes",
     "picks_best_decisions"]].to_string(index=False))
print(json.dumps(summary, indent=1))
