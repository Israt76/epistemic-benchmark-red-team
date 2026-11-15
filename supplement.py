"""Build the supplementary PDF source from results/.   python supplement.py"""
import json
import pandas as pd

P = pd.read_csv("results/integrity_profile.csv")
H = pd.read_csv("results/honest_recalibration.csv")
S = json.load(open("results/summary.json"))
SRC = [("classifiers", "Real classifiers"), ("forecasts", "Real forecasts"), ("synthetic", "Simulated")]
ORDER = ["ECE", "Adaptive ECE", "Selective accuracy", "Hallucination rate", "Penalty score", "E-AURC",
         "Log loss", "Brier", "AUROC", "Accuracy", "Net benefit (hardened)"]
pct = lambda x: f"{100 * x:.0f}%"


def row(src, att, m):
    return P[(P.source == src) & (P.attacker == att) & (P.metric == m)].iloc[0]


out = ["""---
title: "Supplementary Material. Epistemic Benchmark Red Team: When Better Scores Mean Worse Decisions"
author: "Israt Jahan Aunika, Montclair State University"
geometry: margin=0.9in
fontsize: 10pt
---

This supplement gives the complete definitions and the full result tables behind the report. Every table is generated from the released result files by `supplement.py`. No language model was evaluated; the results concern scoring rules.

# S1. Score definitions

Each item has correctness $y \\in \\{0,1\\}$, stated confidence $c \\in [0,1]$ and an answered flag. $N$ is the number of items and $A$ the set of answered items. All scores are expressed as losses (0 is perfect) so that "improved" always means "decreased".

| Score | Loss used | Computed on |
|:--|:--|:--|
| Accuracy | $1 - \\frac{1}{N}\\sum_{i \\in A} y_i$ (abstention counts as wrong) | all items |
| Selective accuracy | $1 - \\frac{1}{|A|}\\sum_{i \\in A} y_i$ | answered |
| Hallucination rate | $\\frac{1}{N}\\sum_{i \\in A} (1 - y_i)$ | all items |
| ECE | 15 equal-width bins, $\\sum_b \\frac{n_b}{|A|}\\,|\\bar c_b - \\bar y_b|$ | answered |
| Adaptive ECE | same with 15 equal-mass bins | answered |
| Brier | $\\frac{1}{|A|}\\sum_{i \\in A}(c_i - y_i)^2$ | answered |
| Log loss | $-\\frac{1}{|A|}\\sum_{i \\in A} [y_i \\log c_i + (1-y_i)\\log(1-c_i)]$, $c$ clipped to $[10^{-4}, 1-10^{-4}]$ | answered |
| AUROC | $1 - \\mathrm{AUROC}(c, y)$ | answered |
| E-AURC | area under the risk-coverage curve minus that of the optimal ordering | answered |
| Penalty score | $1 - \\frac{1}{N}\\sum_{i \\in A}[y_i - 3(1-y_i)]$ | all items |
| Net benefit (hardened) | $0.5 - \\frac{1}{N}\\sum_{i \\in A}[y_i(c_i - c_i^2/2) - (1-y_i)c_i^2/2]$ | all items |

The hardened score is a threshold-averaged net-benefit score of a known family (Schervish, 1989; Vickers and Elkin, 2006; Wu et al., 2026). It is not proposed as a new metric.

# S2. Decision-quality yardsticks

A user with stake threshold $t$ gains $1-t$ from acting on a correct answer and loses $t$ from acting on a wrong one; not acting yields 0. *Threshold users* act iff $c \\ge t$. *Naive users* act on every answer given. Stake profiles over $t$: uniform, low-stakes Beta(2,5), high-stakes Beta(5,2), and their equal mixture (the primary yardstick). Decision regret is measured against an oracle that acts exactly on the system's correct answers; for cross-system comparisons the reference is a perfect system.

Gains are the fraction of loss removed, clipped to $[-1, 1]$. A harmful win is a score gain above 0.01 with a decision gain below -0.01.

# S3. Exploit catalogue

| Family | Exploit | Parameters |
|:--|:--|:--|
| Confidence | Constant confidence | value = development-set accuracy |
| Confidence | Shrink toward accuracy | factor 0.5, 0.25 |
| Confidence | Temperature scaling (logit) | 0.5, 2, 4 |
| Confidence | Binarise | 0.99 if $c \\ge 0.5$ else 0.01 |
| Confidence | Shuffle confidences across items | fixed seed |
| Abstention | Abstain on lowest-confidence items | 20%, 50%, 80% |
| Abstention | Abstain at random | 50% |
| Abstention | Abstain on 80% and report constant confidence | constant = accuracy of retained items |
| Optimised | Piecewise-constant remap, 8 quantile bins, 8 values (plus "abstain" when allowed), coordinate descent on the audited score | fitted on the development half |
| Control | Platt scaling; histogram binning (10 and 3 bins) | honest recalibration, not available to the attacker |

For each score and scope the attacker keeps the exploit with the best development-half score and is evaluated on the held-out half.
"""]

for att, title in (("confidence", "S4. Confidence-only attacker: full results"),
                   ("abstention", "S5. Abstention attacker: full results")):
    out.append(f"\n# {title}\n\nMedian score gain with 95% bootstrap interval, median decision gain, harmful-win rate, and the exploit chosen most often.\n")
    for src, name in SRC:
        out.append(f"\n**{name}** (n = {S['n_systems'][src]})\n")
        out.append("| Score | Score gain [95% CI] | Decision gain | Harmful wins | Most-chosen exploit |\n|:--|:--|--:|--:|:--|")
        for m in ORDER:
            r = row(src, att, m)
            out.append(f"| {m} | {r.score_gain:+.2f} [{r.score_gain_lo:+.2f}, {r.score_gain_hi:+.2f}] | "
                       f"{r.decision_gain:+.2f} | {pct(r.harmful_rate)} | {r.top_exploit} |")

out.append("\n# S6. Harmful-win rate under each yardstick\n\nShare of systems whose score rose while decisions got worse, for each user model.\n")
for att in ("confidence", "abstention"):
    for src, name in SRC:
        out.append(f"\n**{name}, {att} attacker**\n")
        out.append("| Score | Mixed stakes (primary) | Low stakes | High stakes | Naive users |\n|:--|--:|--:|--:|--:|")
        for m in ORDER:
            r = row(src, att, m)
            out.append(f"| {m} | {pct(r.harmful_rate)} | {pct(r.harmful_rate_low_stakes)} | "
                       f"{pct(r.harmful_rate_high_stakes)} | {pct(r.harmful_rate_naive_users)} |")

out.append("\n# S7. Control: honest recalibration\n\nMedian gains from Platt scaling and histogram binning (pooled). A sound test should show these helping decisions or leaving them unchanged, not flag them as harmful.\n")
out.append("| Score | " + " | ".join(f"{n}: score gain | {n}: decision gain" for _, n in SRC) + " |\n|:--|" + "--:|" * 6)
for m in ORDER:
    cells = []
    for src, _ in SRC:
        h = H[(H.source == src) & (H.metric == m)].iloc[0]
        cells += [f"{h.score_gain:+.2f}", f"{h.decision_gain:+.2f}"]
    out.append(f"| {m} | " + " | ".join(cells) + " |")

out.append(f"""
# S8. Metric shopping

In random pools of ten simulated systems, the ten standard scores named a mean of {S['shopping_distinct_winners_mean']['synthetic']:.2f} different systems as best; {pct(S['shopping_share_pools_with_3plus_winners']['synthetic'])} of pools had three or more winners. For the eight real classifiers (15 task-and-split pools) the figures were {S['shopping_distinct_winners_mean']['classifiers']:.2f} and {pct(S['shopping_share_pools_with_3plus_winners']['classifiers'])}. Between a 20%-hard and an 80%-hard question mix, the decision-value ranking itself reversed for {pct(S['decision_ranking_flip_rate_easy_vs_hard'])} of simulated system pairs.

# S9. Reproducibility

- Deterministic: fixed seeds throughout; re-running `run_audit.py` reproduces the released result files exactly.
- Runtime: about one minute for the full audit on a two-core CPU; no GPU.
- Dependencies: numpy, scipy, pandas, scikit-learn, matplotlib.
- Data: scikit-learn's bundled digits, breast-cancer and wine datasets; FiveThirtyEight's public `checking-our-work-data` repository (downloaded by the user, not redistributed here).
- Every number in the report and in this supplement is generated from `results/` by `build_report.py` and `supplement.py`.

```
pip install -r requirements.txt
git clone --depth 1 https://github.com/fivethirtyeight/checking-our-work-data data_raw/538
python run_audit.py && python figures.py && python build_report.py && python supplement.py
```
""")
open("report/supplement.md", "w", encoding="utf-8").write("\n".join(out))
print("supplement.md written")
