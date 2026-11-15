"""Figures from results/integrity_profile.csv.   python figures.py"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

P = pd.read_csv("results/integrity_profile.csv")
SRC = [("synthetic", "Synthetic systems (n=150)"), ("classifiers", "Real classifiers (n=80)"),
       ("forecasts", "Real forecasts (n=9)")]
ATT = [("confidence", "Confidence-only attacker", "#2a78d6", "o"), ("abstention", "Abstention attacker", "#eb6834", "s")]
INK, MUTED, GRID = "#1f1f1d", "#6b6a63", "#ecebe6"
HARD = "Net benefit (hardened)"
LABEL = {"ECE", "Brier", "Selective accuracy", "Hallucination rate", HARD, "Accuracy"}
SHORT = {HARD: "Net benefit (hardened)", "Selective accuracy": "Selective acc.", "Hallucination rate": "Halluc. rate"}

# ---- Figure 1: score gain vs decision gain ----
fig, axes = plt.subplots(1, 3, figsize=(10.5, 4.3), sharey=True)
for ax, (src, title) in zip(axes, SRC):
    ax.axhspan(-1.08, 0, xmin=0.5, color="#fbe9e2", zorder=0)          # score up, decisions worse
    ax.axhline(0, color="#b9b8b0", lw=1)
    ax.axvline(0, color="#b9b8b0", lw=1)
    ax.text(0.55, -0.30, "score up, decisions worse", ha="center", va="center", fontsize=8, color="#a8431c")
    for att, lab, col, mk in ATT:
        g = P[(P.source == src) & (P.attacker == att)]
        hard = g.metric == HARD
        ax.scatter(g.score_gain[~hard], g.decision_gain[~hard], s=70, color=col, marker=mk,
                   edgecolor="white", linewidth=1.2, zorder=3, label=lab)
        ax.scatter(g.score_gain[hard], g.decision_gain[hard], s=150, color=col, marker="*",
                   edgecolor=INK, linewidth=0.8, zorder=4)
        for _, r in g.iterrows():
            show = {"confidence": ("ECE", HARD), "abstention": (HARD,)}[att]
            if r.metric in show:
                dy = 10 if att == "confidence" else -15
                ax.annotate(("Hardened" if r.metric == HARD else r.metric) + (" (abstention)" if att == "abstention" else ""),
                            (r.score_gain, r.decision_gain), xytext=(0, dy), textcoords="offset points",
                            ha="center", fontsize=7.5, color=INK)
    ax.text(0.55, -0.90, "answered-only metrics\nunder abstention", ha="center", va="bottom",
            fontsize=7.5, color=INK)
    ax.set_xlim(-1.08, 1.08)
    ax.set_ylim(-1.08, 1.08)
    ax.set_title(title, fontsize=10.5, loc="left", color=INK)
    ax.set_xlabel("Benchmark score gain (1 = loss eliminated)", fontsize=9, color=INK)
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#b9b8b0")
    ax.tick_params(colors=MUTED, labelsize=8)
axes[0].set_ylabel("Decision-quality gain (-1 = regret at least doubled)", fontsize=9, color=INK)
h, l = axes[0].get_legend_handles_labels()
h.append(plt.Line2D([], [], marker="*", ls="", ms=12, mfc="#b9b8b0", mec=INK))
l.append("Hardened score (either attacker)")
fig.legend(h, l, loc="lower center", ncol=3, frameon=False, fontsize=9, bbox_to_anchor=(0.5, -0.01))
fig.suptitle("Best answer-preserving exploit per metric: what the benchmark sees vs. what users get\n"
             "Each point is one metric (median over systems). No answer is ever changed.",
             fontsize=10.5, x=0.01, ha="left", color=INK)
fig.tight_layout(rect=(0, 0.05, 1, 0.91))
fig.savefig("figures/fig1_score_vs_decisions.png", dpi=300)

# ---- Figure 2: harmful-win rate heatmap ----
order = ["ECE", "Adaptive ECE", "Selective accuracy", "Hallucination rate", "Penalty score", "E-AURC",
         "Log loss", "Brier", "AUROC", "Accuracy", HARD]
cols = [(s, a) for s, _ in SRC for a, *_ in ATT]
M = np.array([[P[(P.source == s) & (P.attacker == a) & (P.metric == m)].harmful_rate.iloc[0] for s, a in cols]
              for m in order])
cmap = LinearSegmentedColormap.from_list("seq", ["#f6f9fd", "#cde2fb", "#86b6ef", "#2a78d6", "#0d366b"])
fig, ax = plt.subplots(figsize=(8.2, 5.2))
ax.imshow(M, cmap=cmap, vmin=0, vmax=1, aspect="auto")
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        ax.text(j, i, f"{M[i, j]:.0%}", ha="center", va="center", fontsize=9,
                color="white" if M[i, j] > 0.55 else INK)
ax.set_xticks(range(len(cols)), [f"{dict(SRC)[s].split(' (')[0]}\n{a}" for s, a in cols], fontsize=8, color=INK)
ax.set_yticks(range(len(order)), order, fontsize=9, color=INK)
for x in (1.5, 3.5):
    ax.axvline(x, color="white", lw=4)
ax.set_xticks(np.arange(-.5, len(cols)), minor=True)
ax.set_yticks(np.arange(-.5, len(order)), minor=True)
ax.grid(which="minor", color="white", lw=2)
ax.tick_params(which="both", length=0)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_title("Harmful-win rate: share of systems whose score rises while users' decisions get worse",
             fontsize=10, loc="left", color=INK, pad=10)
fig.tight_layout()
fig.savefig("figures/fig2_harmful_win_rate.png", dpi=300)
print("figures written")
