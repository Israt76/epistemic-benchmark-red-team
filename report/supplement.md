---
title: "Supplementary Material. Epistemic Benchmark Red Team: When Better Scores Mean Worse Decisions"
author: "Israt Jahan Aunika, Montclair State University"
geometry: margin=0.9in
fontsize: 10pt
---

This supplement gives the complete definitions and the full result tables behind the report. Every table is generated from the released result files by `supplement.py`. No language model was evaluated; the results concern scoring rules.

# S1. Score definitions

Each item has correctness $y \in \{0,1\}$, stated confidence $c \in [0,1]$ and an answered flag. $N$ is the number of items and $A$ the set of answered items. All scores are expressed as losses (0 is perfect) so that "improved" always means "decreased".

| Score | Loss used | Computed on |
|:--|:--|:--|
| Accuracy | $1 - \frac{1}{N}\sum_{i \in A} y_i$ (abstention counts as wrong) | all items |
| Selective accuracy | $1 - \frac{1}{|A|}\sum_{i \in A} y_i$ | answered |
| Hallucination rate | $\frac{1}{N}\sum_{i \in A} (1 - y_i)$ | all items |
| ECE | 15 equal-width bins, $\sum_b \frac{n_b}{|A|}\,|\bar c_b - \bar y_b|$ | answered |
| Adaptive ECE | same with 15 equal-mass bins | answered |
| Brier | $\frac{1}{|A|}\sum_{i \in A}(c_i - y_i)^2$ | answered |
| Log loss | $-\frac{1}{|A|}\sum_{i \in A} [y_i \log c_i + (1-y_i)\log(1-c_i)]$, $c$ clipped to $[10^{-4}, 1-10^{-4}]$ | answered |
| AUROC | $1 - \mathrm{AUROC}(c, y)$ | answered |
| E-AURC | area under the risk-coverage curve minus that of the optimal ordering | answered |
| Penalty score | $1 - \frac{1}{N}\sum_{i \in A}[y_i - 3(1-y_i)]$ | all items |
| Net benefit (hardened) | $0.5 - \frac{1}{N}\sum_{i \in A}[y_i(c_i - c_i^2/2) - (1-y_i)c_i^2/2]$ | all items |

The hardened score is a threshold-averaged net-benefit score of a known family (Schervish, 1989; Vickers and Elkin, 2006; Wu et al., 2026). It is not proposed as a new metric.

# S2. Decision-quality yardsticks

A user with stake threshold $t$ gains $1-t$ from acting on a correct answer and loses $t$ from acting on a wrong one; not acting yields 0. *Threshold users* act iff $c \ge t$. *Naive users* act on every answer given. Stake profiles over $t$: uniform, low-stakes Beta(2,5), high-stakes Beta(5,2), and their equal mixture (the primary yardstick). Decision regret is measured against an oracle that acts exactly on the system's correct answers; for cross-system comparisons the reference is a perfect system.

Gains are the fraction of loss removed, clipped to $[-1, 1]$. A harmful win is a score gain above 0.01 with a decision gain below -0.01.

# S3. Exploit catalogue

| Family | Exploit | Parameters |
|:--|:--|:--|
| Confidence | Constant confidence | value = development-set accuracy |
| Confidence | Shrink toward accuracy | factor 0.5, 0.25 |
| Confidence | Temperature scaling (logit) | 0.5, 2, 4 |
| Confidence | Binarise | 0.99 if $c \ge 0.5$ else 0.01 |
| Confidence | Shuffle confidences across items | fixed seed |
| Abstention | Abstain on lowest-confidence items | 20%, 50%, 80% |
| Abstention | Abstain at random | 50% |
| Abstention | Abstain on 80% and report constant confidence | constant = accuracy of retained items |
| Optimised | Piecewise-constant remap, 8 quantile bins, 8 values (plus "abstain" when allowed), coordinate descent on the audited score | fitted on the development half |
| Control | Platt scaling; histogram binning (10 and 3 bins) | honest recalibration, not available to the attacker |

For each score and scope the attacker keeps the exploit with the best development-half score and is evaluated on the held-out half.


# S4. Confidence-only attacker: full results

Median score gain with 95% bootstrap interval, median decision gain, harmful-win rate, and the exploit chosen most often.


**Real classifiers** (n = 80)

| Score | Score gain [95% CI] | Decision gain | Harmful wins | Most-chosen exploit |
|:--|:--|--:|--:|:--|
| ECE | +0.86 [+0.79, +0.90] | -0.11 | 56% | conf: constant = accuracy |
| Adaptive ECE | +0.43 [+0.29, +0.54] | +0.03 | 20% | optimised remap |
| Selective accuracy | +0.00 [+0.00, +0.00] | -0.11 | 0% | conf: constant = accuracy |
| Hallucination rate | +0.00 [+0.00, +0.00] | -0.11 | 0% | conf: constant = accuracy |
| Penalty score | +0.00 [+0.00, +0.00] | -0.11 | 0% | conf: constant = accuracy |
| E-AURC | +0.00 [+0.00, +0.00] | +0.00 | 4% | conf: shrink x0.5 |
| Log loss | +0.16 [+0.07, +0.38] | +0.05 | 6% | optimised remap |
| Brier | +0.07 [+0.05, +0.10] | +0.05 | 0% | optimised remap |
| AUROC | +0.00 [+0.00, +0.00] | +0.01 | 1% | conf: shrink x0.5 |
| Accuracy | +0.00 [+0.00, +0.00] | -0.11 | 0% | conf: constant = accuracy |
| Net benefit (hardened) | +0.03 [+0.02, +0.05] | +0.05 | 0% | optimised remap |

**Real forecasts** (n = 9)

| Score | Score gain [95% CI] | Decision gain | Harmful wins | Most-chosen exploit |
|:--|:--|--:|--:|:--|
| ECE | +0.53 [+0.16, +0.89] | -0.06 | 89% | conf: constant = accuracy |
| Adaptive ECE | -0.02 [-0.48, +0.31] | -0.02 | 11% | optimised remap |
| Selective accuracy | +0.00 [+0.00, +0.00] | -0.06 | 0% | conf: constant = accuracy |
| Hallucination rate | +0.00 [+0.00, +0.00] | -0.06 | 0% | conf: constant = accuracy |
| Penalty score | +0.00 [+0.00, +0.00] | -0.06 | 0% | conf: constant = accuracy |
| E-AURC | +0.00 [+0.00, +0.00] | -0.02 | 0% | conf: shrink x0.5 |
| Log loss | -0.00 [-0.01, -0.00] | -0.01 | 0% | optimised remap |
| Brier | -0.01 [-0.03, +0.00] | -0.01 | 0% | optimised remap |
| AUROC | +0.00 [-0.05, +0.00] | -0.05 | 0% | conf: shrink x0.5 |
| Accuracy | +0.00 [+0.00, +0.00] | -0.06 | 0% | conf: constant = accuracy |
| Net benefit (hardened) | -0.00 [-0.01, +0.00] | -0.01 | 0% | optimised remap |

**Simulated** (n = 150)

| Score | Score gain [95% CI] | Decision gain | Harmful wins | Most-chosen exploit |
|:--|:--|--:|--:|:--|
| ECE | +0.87 [+0.84, +0.89] | -0.12 | 71% | conf: constant = accuracy |
| Adaptive ECE | +0.77 [+0.73, +0.79] | +0.02 | 41% | conf: constant = accuracy |
| Selective accuracy | +0.00 [+0.00, +0.00] | -0.12 | 0% | conf: constant = accuracy |
| Hallucination rate | +0.00 [+0.00, +0.00] | -0.12 | 0% | conf: constant = accuracy |
| Penalty score | +0.00 [+0.00, +0.00] | -0.12 | 0% | conf: constant = accuracy |
| E-AURC | +0.00 [+0.00, +0.00] | -0.00 | 1% | conf: shrink x0.5 |
| Log loss | +0.15 [+0.12, +0.19] | +0.11 | 0% | optimised remap |
| Brier | +0.11 [+0.09, +0.13] | +0.11 | 0% | optimised remap |
| AUROC | +0.00 [+0.00, +0.00] | +0.04 | 0% | conf: shrink x0.5 |
| Accuracy | +0.00 [+0.00, +0.00] | -0.12 | 0% | conf: constant = accuracy |
| Net benefit (hardened) | +0.04 [+0.03, +0.05] | +0.11 | 0% | optimised remap |

# S5. Abstention attacker: full results

Median score gain with 95% bootstrap interval, median decision gain, harmful-win rate, and the exploit chosen most often.


**Real classifiers** (n = 80)

| Score | Score gain [95% CI] | Decision gain | Harmful wins | Most-chosen exploit |
|:--|:--|--:|--:|:--|
| ECE | +1.00 [+1.00, +1.00] | -1.00 | 100% | abstain 80% + constant conf |
| Adaptive ECE | +1.00 [+1.00, +1.00] | -1.00 | 100% | abstain 80% + constant conf |
| Selective accuracy | +0.92 [+0.82, +1.00] | -1.00 | 95% | abstain: lowest 50% |
| Hallucination rate | +1.00 [+1.00, +1.00] | -1.00 | 100% | abstain: lowest 50% |
| Penalty score | +0.19 [+0.09, +0.22] | -0.41 | 64% | optimised remap + abstain |
| E-AURC | +1.00 [+1.00, +1.00] | -1.00 | 95% | abstain: lowest 50% |
| Log loss | +1.00 [+1.00, +1.00] | -1.00 | 99% | abstain 80% + constant conf |
| Brier | +1.00 [+1.00, +1.00] | -1.00 | 100% | abstain 80% + constant conf |
| AUROC | +0.00 [-0.04, +0.01] | -1.00 | 39% | optimised remap + abstain |
| Accuracy | +0.00 [+0.00, +0.00] | -0.02 | 0% | optimised remap + abstain |
| Net benefit (hardened) | +0.03 [+0.02, +0.05] | +0.05 | 0% | optimised remap + abstain |

**Real forecasts** (n = 9)

| Score | Score gain [95% CI] | Decision gain | Harmful wins | Most-chosen exploit |
|:--|:--|--:|--:|:--|
| ECE | +0.62 [+0.16, +1.00] | -1.00 | 89% | abstain 80% + constant conf |
| Adaptive ECE | +0.12 [-0.62, +1.00] | -0.07 | 56% | conf: constant = accuracy |
| Selective accuracy | +0.49 [+0.33, +1.00] | -1.00 | 89% | optimised remap + abstain |
| Hallucination rate | +0.94 [+0.92, +1.00] | -1.00 | 100% | optimised remap + abstain |
| Penalty score | +0.26 [+0.15, +0.39] | -1.00 | 100% | optimised remap + abstain |
| E-AURC | +0.33 [+0.10, +1.00] | -1.00 | 89% | abstain: lowest 80% |
| Log loss | +0.24 [+0.11, +1.00] | -1.00 | 100% | optimised remap + abstain |
| Brier | +0.31 [+0.15, +1.00] | -1.00 | 100% | optimised remap + abstain |
| AUROC | +0.08 [-0.01, +0.45] | -0.94 | 78% | optimised remap + abstain |
| Accuracy | +0.00 [+0.00, +0.00] | -0.00 | 0% | optimised remap + abstain |
| Net benefit (hardened) | -0.00 [-0.01, +0.00] | -0.01 | 0% | optimised remap + abstain |

**Simulated** (n = 150)

| Score | Score gain [95% CI] | Decision gain | Harmful wins | Most-chosen exploit |
|:--|:--|--:|--:|:--|
| ECE | +0.92 [+0.89, +0.94] | -1.00 | 89% | abstain 80% + constant conf |
| Adaptive ECE | +0.79 [+0.77, +0.80] | -0.10 | 57% | conf: constant = accuracy |
| Selective accuracy | +0.90 [+0.88, +0.91] | -1.00 | 100% | optimised remap + abstain |
| Hallucination rate | +0.99 [+0.99, +0.99] | -1.00 | 100% | optimised remap + abstain |
| Penalty score | +0.40 [+0.38, +0.42] | -0.58 | 100% | optimised remap + abstain |
| E-AURC | +0.54 [+0.50, +0.63] | -1.00 | 99% | abstain: lowest 80% |
| Log loss | +0.73 [+0.70, +0.77] | -1.00 | 100% | abstain 80% + constant conf |
| Brier | +0.85 [+0.81, +0.87] | -1.00 | 100% | optimised remap + abstain |
| AUROC | +0.31 [+0.28, +0.38] | -1.00 | 100% | optimised remap + abstain |
| Accuracy | +0.00 [+0.00, +0.00] | -0.00 | 0% | optimised remap + abstain |
| Net benefit (hardened) | +0.04 [+0.03, +0.05] | +0.11 | 0% | optimised remap + abstain |

# S6. Harmful-win rate under each yardstick

Share of systems whose score rose while decisions got worse, for each user model.


**Real classifiers, confidence attacker**

| Score | Mixed stakes (primary) | Low stakes | High stakes | Naive users |
|:--|--:|--:|--:|--:|
| ECE | 56% | 44% | 57% | 0% |
| Adaptive ECE | 20% | 29% | 22% | 0% |
| Selective accuracy | 0% | 0% | 0% | 0% |
| Hallucination rate | 0% | 0% | 0% | 0% |
| Penalty score | 0% | 0% | 0% | 0% |
| E-AURC | 4% | 2% | 4% | 0% |
| Log loss | 6% | 11% | 8% | 0% |
| Brier | 0% | 8% | 1% | 0% |
| AUROC | 1% | 0% | 1% | 0% |
| Accuracy | 0% | 0% | 0% | 0% |
| Net benefit (hardened) | 0% | 8% | 0% | 0% |

**Real forecasts, confidence attacker**

| Score | Mixed stakes (primary) | Low stakes | High stakes | Naive users |
|:--|--:|--:|--:|--:|
| ECE | 89% | 67% | 89% | 0% |
| Adaptive ECE | 11% | 11% | 11% | 0% |
| Selective accuracy | 0% | 0% | 0% | 0% |
| Hallucination rate | 0% | 0% | 0% | 0% |
| Penalty score | 0% | 0% | 0% | 0% |
| E-AURC | 0% | 0% | 0% | 0% |
| Log loss | 0% | 0% | 0% | 0% |
| Brier | 0% | 0% | 0% | 0% |
| AUROC | 0% | 0% | 0% | 0% |
| Accuracy | 0% | 0% | 0% | 0% |
| Net benefit (hardened) | 0% | 0% | 0% | 0% |

**Simulated, confidence attacker**

| Score | Mixed stakes (primary) | Low stakes | High stakes | Naive users |
|:--|--:|--:|--:|--:|
| ECE | 71% | 57% | 89% | 0% |
| Adaptive ECE | 41% | 31% | 59% | 0% |
| Selective accuracy | 0% | 0% | 0% | 0% |
| Hallucination rate | 0% | 0% | 0% | 0% |
| Penalty score | 0% | 0% | 0% | 0% |
| E-AURC | 1% | 1% | 1% | 0% |
| Log loss | 0% | 2% | 1% | 0% |
| Brier | 0% | 2% | 1% | 0% |
| AUROC | 0% | 0% | 0% | 0% |
| Accuracy | 0% | 0% | 0% | 0% |
| Net benefit (hardened) | 0% | 2% | 0% | 0% |

**Real classifiers, abstention attacker**

| Score | Mixed stakes (primary) | Low stakes | High stakes | Naive users |
|:--|--:|--:|--:|--:|
| ECE | 100% | 100% | 100% | 98% |
| Adaptive ECE | 100% | 100% | 100% | 100% |
| Selective accuracy | 95% | 96% | 88% | 94% |
| Hallucination rate | 100% | 100% | 100% | 100% |
| Penalty score | 64% | 65% | 41% | 59% |
| E-AURC | 95% | 95% | 95% | 95% |
| Log loss | 99% | 99% | 99% | 99% |
| Brier | 100% | 100% | 100% | 100% |
| AUROC | 39% | 39% | 39% | 39% |
| Accuracy | 0% | 0% | 0% | 0% |
| Net benefit (hardened) | 0% | 8% | 0% | 0% |

**Real forecasts, abstention attacker**

| Score | Mixed stakes (primary) | Low stakes | High stakes | Naive users |
|:--|--:|--:|--:|--:|
| ECE | 89% | 89% | 89% | 56% |
| Adaptive ECE | 56% | 56% | 56% | 44% |
| Selective accuracy | 89% | 89% | 89% | 78% |
| Hallucination rate | 100% | 100% | 100% | 89% |
| Penalty score | 100% | 100% | 100% | 89% |
| E-AURC | 89% | 89% | 89% | 78% |
| Log loss | 100% | 100% | 100% | 89% |
| Brier | 100% | 100% | 100% | 89% |
| AUROC | 78% | 78% | 78% | 67% |
| Accuracy | 0% | 0% | 0% | 0% |
| Net benefit (hardened) | 0% | 0% | 0% | 0% |

**Simulated, abstention attacker**

| Score | Mixed stakes (primary) | Low stakes | High stakes | Naive users |
|:--|--:|--:|--:|--:|
| ECE | 89% | 85% | 89% | 57% |
| Adaptive ECE | 57% | 53% | 71% | 41% |
| Selective accuracy | 100% | 100% | 97% | 93% |
| Hallucination rate | 100% | 100% | 97% | 93% |
| Penalty score | 100% | 100% | 73% | 53% |
| E-AURC | 99% | 99% | 91% | 85% |
| Log loss | 100% | 100% | 91% | 85% |
| Brier | 100% | 100% | 91% | 85% |
| AUROC | 100% | 100% | 88% | 100% |
| Accuracy | 0% | 0% | 0% | 0% |
| Net benefit (hardened) | 0% | 2% | 0% | 0% |

# S7. Control: honest recalibration

Median gains from Platt scaling and histogram binning (pooled). A sound test should show these helping decisions or leaving them unchanged, not flag them as harmful.

| Score | Real classifiers: score gain | Real classifiers: decision gain | Real forecasts: score gain | Real forecasts: decision gain | Simulated: score gain | Simulated: decision gain |
|:--|--:|--:|--:|--:|--:|--:|
| ECE | +0.65 | +0.04 | +0.04 | -0.01 | +0.79 | +0.11 |
| Adaptive ECE | +0.38 | +0.04 | -0.14 | -0.01 | +0.75 | +0.11 |
| Selective accuracy | +0.00 | +0.04 | +0.00 | -0.01 | +0.00 | +0.11 |
| Hallucination rate | +0.00 | +0.04 | +0.00 | -0.01 | +0.00 | +0.11 |
| Penalty score | +0.00 | +0.04 | +0.00 | -0.01 | +0.00 | +0.11 |
| E-AURC | -0.07 | +0.04 | -0.03 | -0.01 | -0.02 | +0.11 |
| Log loss | +0.14 | +0.04 | -0.00 | -0.01 | +0.14 | +0.11 |
| Brier | +0.05 | +0.04 | -0.01 | -0.01 | +0.12 | +0.11 |
| AUROC | -0.12 | +0.04 | -0.02 | -0.01 | -0.02 | +0.11 |
| Accuracy | +0.00 | +0.04 | +0.00 | -0.01 | +0.00 | +0.11 |
| Net benefit (hardened) | +0.03 | +0.04 | -0.00 | -0.01 | +0.04 | +0.11 |

# S8. Metric shopping

In random pools of ten simulated systems, the ten standard scores named a mean of 3.11 different systems as best; 78% of pools had three or more winners. For the eight real classifiers (15 task-and-split pools) the figures were 2.93 and 60%. Between a 20%-hard and an 80%-hard question mix, the decision-value ranking itself reversed for 8% of simulated system pairs.

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
