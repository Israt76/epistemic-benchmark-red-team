"""Metrics, the decision-quality yardstick, and exploit transformations.

A "system" is three arrays over benchmark items:
  c  stated confidence that its answer is correct, in [0, 1]
  y  1 if the answer is correct, else 0
  a  True if the system answered (False = abstained)

Every metric is returned as a LOSS (distance from its perfect value, >= 0),
so "the score improved" always means the loss went down.
"""
import numpy as np

EPS = 1e-12


def _ans(c, y, a):
    return c[a], y[a]


def acc_loss(c, y, a):            # abstention counts as wrong
    return 1 - (y[a].sum() / len(y))


def selacc_loss(c, y, a):         # accuracy on answered items only
    return 1 - y[a].mean() if a.any() else 1.0


def halluc(c, y, a):              # wrong answers / all items
    return (1 - y[a]).sum() / len(y)


def ece(c, y, a, bins=15):
    c, y = _ans(c, y, a)
    if len(c) == 0:
        return 0.0
    idx = np.minimum((c * bins).astype(int), bins - 1)
    out = 0.0
    for b in np.unique(idx):
        m = idx == b
        out += m.mean() * abs(c[m].mean() - y[m].mean())
    return out


def aece(c, y, a, bins=15):       # equal-mass bins
    c, y = _ans(c, y, a)
    if len(c) == 0:
        return 0.0
    order = np.argsort(c, kind="stable")
    out = 0.0
    for chunk in np.array_split(order, min(bins, len(c))):
        out += len(chunk) / len(c) * abs(c[chunk].mean() - y[chunk].mean())
    return out


def brier(c, y, a):
    c, y = _ans(c, y, a)
    return float(np.mean((c - y) ** 2)) if len(c) else 0.0


def nll(c, y, a):
    c, y = _ans(c, y, a)
    if len(c) == 0:
        return 0.0
    c = np.clip(c, 1e-4, 1 - 1e-4)
    return float(-np.mean(y * np.log(c) + (1 - y) * np.log(1 - c)))


def auroc_loss(c, y, a):          # 1 - AUROC of confidence vs correctness
    c, y = _ans(c, y, a)
    n1, n0 = y.sum(), (1 - y).sum()
    if n1 == 0 or n0 == 0:
        return 0.5
    from scipy.stats import rankdata
    r = rankdata(c)
    return 1 - (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def eaurc(c, y, a):               # excess area under the risk-coverage curve
    c, y = _ans(c, y, a)
    n = len(c)
    if n == 0:
        return 0.0
    rng = np.random.default_rng(0)
    order = np.lexsort((rng.random(n), -c))          # ties broken at random
    risk = np.cumsum(1 - y[order]) / np.arange(1, n + 1)
    best = np.cumsum(np.sort(1 - y)) / np.arange(1, n + 1)
    return float(risk.mean() - best.mean())


def penalty_loss(c, y, a, t=0.75):  # +1 right, -t/(1-t) wrong, 0 abstain
    return 1 - float((y[a] - (1 - y[a]) * t / (1 - t)).sum() / len(y))


def netbenefit_loss(c, y, a):
    """Hardened score. A user with stake threshold t acts on an answer iff
    c >= t, gaining (1-t) if it is right and losing t if it is wrong; an
    abstention gives 0. Averaged over t ~ Uniform(0,1) this has the closed
    form below. Needs no counterfactual for abstained items. Perfect = 0.5."""
    g = np.where(a, y * (c - c ** 2 / 2) - (1 - y) * c ** 2 / 2, 0.0)
    return 0.5 - float(g.mean())


METRICS = {
    "Accuracy": acc_loss, "Selective accuracy": selacc_loss, "Hallucination rate": halluc,
    "ECE": ece, "Adaptive ECE": aece, "Brier": brier, "Log loss": nll,
    "AUROC": auroc_loss, "E-AURC": eaurc, "Penalty score": penalty_loss,
    "Net benefit (hardened)": netbenefit_loss,
}

# ---- decision-quality yardstick ------------------------------------------------
T = np.linspace(0.005, 0.995, 199)
from scipy.stats import beta as _beta
STAKES = {"uniform": np.ones_like(T), "low": _beta.pdf(T, 2, 5), "high": _beta.pdf(T, 5, 2)}
STAKES = {k: v / v.sum() for k, v in STAKES.items()}
STAKES["mixed"] = (STAKES["uniform"] + STAKES["low"] + STAKES["high"]) / 3   # primary


def decision_regret(c, y, a, y_base=None, stakes="mixed", user="threshold"):
    """Expected regret relative to an oracle that acts exactly on the base
    system's correct answers. Lower is better; 0 is perfect.
      user="threshold": acts on an answer iff its confidence clears the
                        user's own stake threshold t (uses confidence).
      user="naive":     acts on every answer the system gives (ignores
                        confidence; only abstention protects this user)."""
    w = STAKES[stakes]
    yb = y if y_base is None else y_base
    if user == "naive":
        right, wrong = (y * a).sum() / len(y), ((1 - y) * a).sum() / len(y)
        return float((w * ((1 - T) * yb.mean() - ((1 - T) * right - T * wrong))).sum())
    order = np.argsort(np.where(a, c, -1.0))
    cs, ys, as_ = np.where(a, c, -1.0)[order], y[order], a[order]
    right = np.concatenate([[0], np.cumsum((ys * as_)[::-1])])[::-1]      # counts with c >= cut
    wrong = np.concatenate([[0], np.cumsum(((1 - ys) * as_)[::-1])])[::-1]
    k = np.searchsorted(cs, T, side="left")
    util = ((1 - T) * right[k] - T * wrong[k]) / len(y)
    oracle = (1 - T) * yb.mean()
    return float((w * (oracle - util)).sum())


def value_loss(c, y, a, stakes="mixed", user="threshold"):
    """Shortfall in delivered decision value relative to a PERFECT system
    (always right, always certain). Unlike decision_regret this also charges
    for wrong answers, so it is the yardstick for comparing different systems."""
    perfect = float((STAKES[stakes] * (1 - T)).sum())
    own_oracle = float((STAKES[stakes] * (1 - T)).sum() * y.mean())
    return perfect - (own_oracle - decision_regret(c, y, a, stakes=stakes, user=user))


# ---- exploits ------------------------------------------------------------------
def _logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def _sig(x):
    return 1 / (1 + np.exp(-x))


def make_exploits(cd, yd, seed=0):
    """Build transformations from a DEV split only. Each maps test-time
    confidences to (new confidence, answered mask). Answers never change."""
    acc = yd.mean()
    full = lambda c: np.ones(len(c), bool)
    ex = {}
    ex["conf: constant = accuracy"] = ("confidence", "cosmetic", lambda c: (np.full(len(c), acc), full(c)))
    for s in (0.5, 0.25):
        ex[f"conf: shrink x{s}"] = ("confidence", "cosmetic",
                                    lambda c, s=s: (acc + s * (c - acc), full(c)))
    for t in (0.5, 2.0, 4.0):
        ex[f"conf: temperature {t}"] = ("confidence", "cosmetic",
                                        lambda c, t=t: (_sig(_logit(c) / t), full(c)))
    ex["conf: binarize 0.99/0.01"] = ("confidence", "cosmetic",
                                      lambda c: (np.where(c >= 0.5, 0.99, 0.01), full(c)))

    def shuffle(c):
        return np.random.default_rng(seed).permutation(c), full(c)
    ex["conf: shuffle"] = ("confidence", "cosmetic", shuffle)

    # honest recalibration (expected to help decisions): Platt scaling, histogram binning
    from sklearn.linear_model import LogisticRegression
    if 0 < yd.sum() < len(yd):
        lr = LogisticRegression(C=1e6).fit(_logit(cd).reshape(-1, 1), yd.astype(int))
        ex["recal: Platt"] = ("confidence", "honest",
                              lambda c: (lr.predict_proba(_logit(c).reshape(-1, 1))[:, 1], full(c)))
    for kbin in (10, 3):
        edges = np.quantile(cd, np.linspace(0, 1, kbin + 1)[1:-1])
        means = np.array([yd[np.searchsorted(edges, cd) == b].mean() if (np.searchsorted(edges, cd) == b).any()
                          else acc for b in range(kbin)])
        ex[f"recal: histogram {kbin} bins"] = ("confidence", "honest",
                                               lambda c, e=edges, m=means: (m[np.searchsorted(e, c)], full(c)))
    for q in (0.2, 0.5, 0.8):
        cut = np.quantile(cd, q)
        ex[f"abstain: lowest {int(q * 100)}%"] = ("abstention", "cosmetic",
                                                  lambda c, cut=cut: (c, c > cut))
    ex["abstain: random 50%"] = ("abstention", "cosmetic",
                                 lambda c: (c, np.random.default_rng(seed).random(len(c)) < 0.5))
    cut8 = np.quantile(cd, 0.8)
    top = yd[cd > cut8].mean() if (cd > cut8).any() else acc
    ex["abstain 80% + constant conf"] = ("abstention", "cosmetic",
                                         lambda c: (np.full(len(c), top), c > cut8))
    return ex


def optimise_remap(cd, yd, loss_fn, allow_abstain, k=8,
                   values=(0.02, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 0.98)):
    """Direct optimisation against a metric. Confidence is cut into k bins
    (dev quantiles); each bin is remapped to one value from a grid, or to
    'abstain' if allowed. Coordinate descent on the DEV loss. This searches a
    space that contains constant confidence, shrinking, binarising and
    threshold abstention, so it is at least as strong as those hand-made
    exploits. Answers are never changed."""
    edges = np.quantile(cd, np.linspace(0, 1, k + 1)[1:-1])
    idx = np.searchsorted(edges, cd)
    v = np.array([cd[idx == b].mean() if (idx == b).any() else 0.5 for b in range(k)])   # start = identity

    def apply(c, v=None, edges=edges):
        vv = v_best if v is None else v
        j = np.searchsorted(edges, c)
        return np.where(vv[j] < 0, 0.0, vv[j]), vv[j] >= 0

    best = loss_fn(*apply(cd, v)[:1], yd, apply(cd, v)[1])
    for b in range(k):
        for cand in list(values) + ([-1.0] if allow_abstain else []):
            trial = v.copy()
            trial[b] = cand
            if (trial < 0).all():
                continue                                   # must answer something
            c2, a2 = apply(cd, trial)
            L = loss_fn(c2, yd, a2)
            if L < best - 1e-12:
                best, v = L, trial
    v_best = v
    return lambda c: apply(c, v_best)


def gain(before, after):
    """Fraction of the loss removed, clipped to [-1, 1]:
    +1 = loss eliminated, 0 = unchanged, -1 = loss at least doubled."""
    return float(np.clip((before - after) / max(before, 1e-9), -1, 1))
