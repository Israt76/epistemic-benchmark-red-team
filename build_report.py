"""Build report/report.md from the result tables, so every number in the
paper is read from results/ and never typed by hand.   python build_report.py"""
import json
import os

import pandas as pd

P = pd.read_csv("results/integrity_profile.csv")
A = pd.read_csv("results/attack.csv")
S = json.load(open("results/summary.json"))
HARD = "Net benefit (hardened)"
SRC = ["synthetic", "classifiers", "forecasts"]
ORDER = ["ECE", "Adaptive ECE", "Selective accuracy", "Hallucination rate", "Penalty score", "E-AURC",
         "Log loss", "Brier", "AUROC", "Accuracy", HARD]


def v(src, att, metric, col):
    return P[(P.source == src) & (P.attacker == att) & (P.metric == metric)][col].iloc[0]


def pct(x):
    return f"{100 * x:.0f}%"


def table_attack(att):
    ab = {"synthetic": "Syn.", "classifiers": "Clf.", "forecasts": "Fcst."}
    head = "| Score | " + " | ".join(f"{ab[s]} gain | {ab[s]} harmful" for s in SRC) + " |"
    lines = [head, "|:--|" + "--:|" * 6]
    for m in ORDER:
        cells = []
        for s in SRC:
            cells += [f"{v(s, att, m, 'score_gain'):+.2f}", pct(v(s, att, m, "harmful_rate"))]
        name = "**Net benefit**" if m == HARD else m
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def table_rank():
    lines = ["| Score | Rank agr. (syn.) | Rank agr. (clf.) | Picks best (syn.) | "
             "Respons. | Real gains seen | Mix flips |", "|:--|" + "--:|" * 6]
    for m in ORDER:
        r = P[(P.source == "synthetic") & (P.attacker == "confidence") & (P.metric == m)].iloc[0]
        c = P[(P.source == "classifiers") & (P.attacker == "confidence") & (P.metric == m)].iloc[0]
        name = f"**{m}**" if m == HARD else m
        lines.append(f"| {name} | {r.rank_agreement_tau:.2f} | {c.rank_agreement_tau:.2f} | "
                     f"{pct(r.picks_best_decisions)} | {r.responsiveness_spearman:+.2f} | "
                     f"{pct(r.real_gain_detected)} | {pct(r.flip_rate_easy_vs_hard_mix)} |")
    return "\n".join(lines)


def table_robust():
    lines = ["| Score | Attacker | Mixed stakes | Low stakes | High stakes | Naive users |", "|:--|:--|" + "--:|" * 4]
    for m in ("ECE", "Selective accuracy", "Brier", HARD):
        for att in ("confidence", "abstention"):
            cells = [pct(max(v(s, att, m, c) for s in SRC)) for c in
                     ("harmful_rate", "harmful_rate_low_stakes", "harmful_rate_high_stakes", "harmful_rate_naive_users")]
            lines.append(f"| {m} | {att} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def table_profile():
    lines = ["| Score | Harmful: conf. | Harmful: abst. | Rank agr. | Respons. | Mix flips |",
             "|:--|" + "--:|" * 5]
    for m in ("ECE", "Brier", "Log loss", "Selective accuracy", "Accuracy", HARD):
        r = P[(P.source == "synthetic") & (P.attacker == "confidence") & (P.metric == m)].iloc[0]
        hc = max(v(s, "confidence", m, "harmful_rate") for s in SRC)
        ha = max(v(s, "abstention", m, "harmful_rate") for s in SRC)
        name = f"**{m}**" if m == HARD else m
        lines.append(f"| {name} | {pct(hc)} | {pct(ha)} | {r.rank_agreement_tau:.2f} | "
                     f"{r.responsiveness_spearman:+.2f} | {pct(r.flip_rate_easy_vs_hard_mix)} |")
    return "\n".join(lines)


cov = A.groupby(["source", "attacker"]).coverage.median()
n = S["n_systems"]
e = {s: (v(s, "confidence", "ECE", "score_gain"), v(s, "confidence", "ECE", "harmful_rate")) for s in SRC}
hard_max = max(v(s, a, HARD, "harmful_rate") for s in SRC for a in ("confidence", "abstention"))
hard_low = max(v(s, a, HARD, "harmful_rate_low_stakes") for s in SRC for a in ("confidence", "abstention"))
ans_only = ["Selective accuracy", "Hallucination rate", "Brier", "Log loss"]
ab_min = min(v(s, "abstention", m, "harmful_rate") for s in SRC for m in ans_only)
syn = lambda m, c: v("synthetic", "confidence", m, c)
clf = lambda m, c: v("classifiers", "confidence", m, c)
brier_conf = max(v(s, "confidence", "Brier", "harmful_rate") for s in SRC)

ABSTRACT = f"""Can an AI evaluation be improved without improving the AI? Epistemic benchmarks score how well a system knows what it knows, and those scores shape what developers optimise. We build the Epistemic Benchmark Integrity Test, a red-team procedure that attacks a scoring rule with answer-preserving manipulations: editing stated confidence, abstaining strategically, and directly optimising a confidence remap against the score. The attacker is tuned on one half of the data and judged on the other, against an explicit model of downstream decision quality. We audit ten scores in common use on {n['classifiers']} real classifiers and {n['forecasts']} real forecast archives, plus {n['synthetic']} controlled simulated systems. Expected calibration error is gameable by confidence edits alone: a single constant confidence removes a median {pct(e['classifiers'][0])} of the error for classifiers and {pct(e['forecasts'][0])} for forecasts ({pct(e['synthetic'][0])} in simulation), while decisions get worse for {pct(e['classifiers'][1])} and {pct(e['forecasts'][1])} of those systems ({pct(e['synthetic'][1])}). Strategic abstention games selective accuracy, hallucination rate, Brier score and log loss for at least {pct(ab_min)} of systems in every setting. Proper scoring rules resist confidence-only attacks. A threshold-averaged net-benefit score that charges abstention its withheld value was not gamed under the primary yardstick. We also quantify metric shopping and question-mix sensitivity, and release the test as a reusable tool. No language model is evaluated; the results concern scoring rules. Epistemic evaluations should themselves be adversarially evaluated before they are trusted."""
assert 150 <= len(ABSTRACT.split()) <= 250, len(ABSTRACT.split())

MD = f"""---
title: "Epistemic Benchmark Red Team: When Better Scores Mean Worse Decisions"
author: "Israt Jahan Aunika, Montclair State University"
date: "Apart Research AI x Epistemics Research Sprint, November 2026 (Track 1: Model Epistemics and Decision-Making Evals)"
geometry: margin=0.85in
fontsize: 10pt
colorlinks: true
---

**Abstract.** {ABSTRACT}

# 1. Introduction

Suppose a benchmark reports that an AI system has become better calibrated, or hallucinates less. A user who relies on that system wants to know one thing: will my decisions be better? This paper tests whether the answer can be "no" while the score still goes up.

Two examples make the problem concrete. A system that reports the same confidence for every answer, equal to its average accuracy, is perfectly calibrated by the most widely used calibration metric, and tells the user nothing about which answers to trust. A system that refuses every question it might get wrong shows an excellent accuracy on the questions it does answer, and is of little use. Neither system changed a single answer.

These individual weaknesses are known (Section 2). What is missing is a way to test a scoring rule for them systematically, measure how much they matter, and check whether a proposed fix closes them. Track 1 of this sprint asks which exploits make benchmarks gameable and whether one can be demonstrated and closed. We answer with a red-team procedure for the benchmark itself.

**Contributions.**

1. The **Epistemic Benchmark Integrity Test**: a procedure that attacks any scoring rule over (answer correctness, stated confidence, abstention) with answer-preserving exploits and reports an Integrity Profile.
2. The **Integrity Gap**: the score improvement an attacker obtains minus the change in downstream decision quality, and the **harmful-win rate**: how often the score rises while decisions get worse.
3. An **audit of ten scores in common use** on real classifiers, real probabilistic forecasts and controlled simulated systems, covering four exploit families: confidence gaming, strategic abstention, metric shopping and question-mix sensitivity.
4. A demonstration that **one exploit family can be closed**: scoring abstention at its lost value, with a threshold-averaged net-benefit score, removes the abstention exploit under the primary yardstick in every setting we tested.

*The contribution is not another calibration metric. It is a benchmark red-teaming methodology: optimise against the evaluation adversarially on held-out data, measure whether the apparent improvement transfers to decision value, and require any proposed repair to survive the same attack.*

No language model is evaluated in this work. The results are about scoring rules, and they apply to any system, LLM or otherwise, that is scored by them.

# 2. Related Work

**Calibration metrics and their weaknesses.** Expected calibration error (ECE) was introduced for probabilistic classifiers by Naeini et al. (2015) and popularised for neural networks by Guo et al. (2017). It is known that ECE can be minimised by a predictor that carries no instance-level information; a recent textbook states that one "can easily achieve ECE = 0" without reporting true uncertainties (Mucsányi et al., 2023), and Nixon et al. (2019) and Kumar et al. (2019) document binning sensitivity. Proper scoring rules such as the Brier score (Brier, 1950) and log loss were designed so that honest probabilities are optimal (Gneiting and Raftery, 2007).

**Abstention and selective prediction.** Selective classification studies the trade-off between coverage and risk (El-Yaniv and Wiener, 2010; Geifman and El-Yaniv, 2017), and E-AURC summarises the risk-coverage curve (Geifman et al., 2019). For language models, Kalai et al. (2025) argue that accuracy-based evaluation rewards guessing over abstaining, and Burns (2026) proposes scoring the full answer distribution for the same reason.

**Decision-theoretic evaluation.** Schervish (1989) showed that proper scoring rules are averages of threshold decision losses; decision curve analysis applies the same idea in medicine (Vickers and Elkin, 2006). Wu et al. (2026) introduce the Behavioral Alignment Score, which averages realised utility over risk thresholds with zero utility for abstention. Our hardened score belongs to this family and we do not claim it as new. Our contribution is the adversarial test that shows which scores are gameable, by how much, and that this family is not.

**Benchmark integrity.** Recent work treats evaluation integrity as measurable, but targets agents that tamper with evaluation code or leak test data (Atinafu and Cohen, 2026) and test-set memorisation on open leaderboards. We target a different layer: the scoring rule itself, with honest data and unchanged answers.

**What is new here.** To our knowledge, based on a targeted search and not an exhaustive review, no prior work provides a single adversarial procedure that (i) searches answer-preserving exploits against arbitrary epistemic scores, (ii) measures the result against an explicit decision-quality yardstick under more than one user model, and (iii) verifies a fix. The individual phenomena in Sections 4.1 and 4.2 are known in principle; the measurements, the common framework and the closure test are ours.

# 3. Methodology

## 3.1 Setting

A system is described on each benchmark item by whether its answer is correct, $y \\in \\{{0,1\\}}$, its stated confidence $c \\in [0,1]$ that the answer is correct, and whether it answered or abstained. A scoring rule maps these to a number. We express every score as a loss (distance from its perfect value), so "the score improved" means the loss fell.

## 3.2 Scores audited

Ten scores in common use: accuracy (abstention counted as wrong); selective accuracy (accuracy on answered items); hallucination rate (wrong answers over all items); ECE with 15 equal-width bins; adaptive ECE with 15 equal-mass bins; Brier score; log loss; AUROC of confidence against correctness; E-AURC; and a penalty score (+1 correct, -3 wrong, 0 abstain, i.e. a 0.75 confidence threshold). Following common practice, confidence-based scores are computed on answered items only. Hallucination rate is computed over all items, but it also falls whenever a wrong answer is withheld, so it rewards abstention in the same way.

One hardened score: **threshold-averaged net benefit**. A user with stake threshold $t$ acts on an answer if $c \\ge t$, gaining $1-t$ if it is right and losing $t$ if it is wrong; an abstention yields 0. Averaging over $t \\sim U(0,1)$ gives the per-item score $y(c - c^2/2) - (1-y)c^2/2$ for answered items and 0 for abstentions. For full coverage this equals half the negative Brier score plus a term in accuracy; the difference from Brier-on-answered-items is entirely in how abstention is charged.

## 3.3 Decision-quality yardstick

We need a definition of "decisions got better" that is independent of the scores under audit. We use two user models.

- **Threshold users** act on an answer only if its confidence clears their own stake threshold $t$, with the payoffs above. We average over a mixture of three stake distributions: uniform, low-stakes (Beta(2,5)) and high-stakes (Beta(5,2)). This mixture is our primary yardstick; we also report each profile separately.
- **Naive users** act on every answer the system gives and ignore confidence. Only abstention protects them.

Decision regret is the shortfall relative to an oracle that acts exactly on the system's correct answers. For comparing different systems we use the shortfall relative to a perfect system, which also charges for wrong answers.

The hardened score coincides with the threshold-user yardstick under uniform stakes. It is therefore not an independent check under that profile, and we report results under the low-stakes, high-stakes and naive-user yardsticks, where it is not identical, as the meaningful test.

## 3.4 Exploits

All exploits leave every answer unchanged.

- **Confidence gaming (8 hand-made):** constant confidence equal to accuracy; shrinking toward accuracy (two strengths); temperature scaling (three temperatures); binarising to 0.99/0.01; shuffling confidences across items.
- **Strategic abstention (5 hand-made):** abstaining on the lowest 20%, 50% or 80% of items by confidence; abstaining at random on 50%; abstaining on 80% and reporting a constant confidence on the rest.
- **Direct optimisation:** confidence is cut into 8 quantile bins and each bin is remapped to one of 8 confidence values, or to "abstain" when allowed, by coordinate descent on the audited score. This search space contains the constant, shrinking, binarising and threshold-abstention exploits.
- **Honest recalibration (control, 3 methods):** Platt scaling and histogram binning with 10 and 3 bins. These are expected to help decisions and check that the test does not flag legitimate improvement.

**Attacker protocol.** Each system's items are split in half. For each score and each scope (confidence-only, or abstention allowed), the attacker fits every exploit on the development half, keeps the one with the best development score, and is evaluated on the held-out half. We report the score gain and the decision gain, each as the fraction of loss removed, clipped to $[-1, 1]$ (+1: loss eliminated; -1: loss at least doubled). The **Integrity Gap** is score gain minus decision gain. A **harmful win** is a score gain above 0.01 with a decision gain below -0.01.

**Metric shopping.** In random pools of ten systems we count how many different systems are ranked first by at least one of the ten standard scores, and compute Kendall's tau between each score's ranking and the decision-value ranking.

**Question-mix sensitivity.** We re-score systems on a benchmark with 20% hard questions and on one with 80% hard questions and count how often the ranking of a pair of systems reverses.

**Responsiveness.** A score that never moves cannot be gamed, so the profile also checks that a score responds to real improvement. We apply three genuine improvements to each simulated system (more skill, better discrimination, corrected calibration) and correlate the score gain with the decision-value gain.

## 3.5 Systems

- **Synthetic ({n['synthetic']}).** Items have a difficulty; a system has a skill (accuracy), a noise level (how well confidence tracks correctness), and a temperature and bias (miscalibration). 4,000 items per system, half hard and half easy.
- **Real classifiers ({n['classifiers']}).** Eight scikit-learn model families (logistic regression, naive Bayes, random forest, gradient boosting, SVM with Platt scaling, k-nearest neighbours, a small neural network, a decision tree) trained on 15% of the digits and breast-cancer datasets, five random splits each; confidence is the top predicted probability (Pedregosa et al., 2011).
- **Real forecasts ({n['forecasts']}).** FiveThirtyEight's public archive of its own probabilistic forecasts with outcomes: MLB, NBA, NFL and NHL games, men's and women's in-game basketball, club soccer, and presidential and gubernatorial elections, up to 4,000 forecasts each. The answer is the most likely outcome and the confidence is its probability. Repeated forecasts of the same event are not independent.

Medians over systems are reported with percentile-bootstrap 95% intervals in the released tables. All code is deterministic and runs in about one minute on a laptop CPU.

# 4. Results

## 4.1 Confidence gaming: ECE fails, proper scoring rules hold

![Best answer-preserving exploit per score. Each point is one score (median over systems). The shaded quadrant is where the benchmark score improves and users' decisions get worse.](figures/fig1_score_vs_decisions.png){{width=90%}}

Table 1 gives the confidence-only attacker. Against ECE the attacker always chose the constant-confidence exploit, and it removed a median {pct(e['synthetic'][0])} of the calibration error on simulated systems, {pct(e['classifiers'][0])} on real classifiers and {pct(e['forecasts'][0])} on real forecasts. Threshold users' decisions got worse for {pct(e['synthetic'][1])}, {pct(e['classifiers'][1])} and {pct(e['forecasts'][1])} of those systems. Adaptive binning reduces the problem but does not remove it.

Brier score, log loss and the hardened score were not gameable this way: the best "exploit" the attacker could find was a remap that also improved decisions, and the harmful-win rate for Brier was {"0% in every setting tested" if brier_conf == 0 else "at most " + pct(brier_conf) + " in any setting"}. Accuracy-type scores cannot be moved by confidence edits at all, which also means they cannot see confidence quality (Section 4.4).

Table: Confidence-only attacker (Syn. = simulated, Clf. = classifiers, Fcst. = forecasts). "Gain" is the median fraction of the score's loss removed on held-out data; "harmful" is the share of systems whose score rose while threshold users' decisions got worse.

{table_attack('confidence')}

## 4.2 Strategic abstention games selective and answered-only metrics, even proper scoring rules

When abstention is allowed (Table 2), the attacker abstained on most items: median coverage after the attack was {pct(cov[('synthetic', 'abstention')])} for simulated systems, {pct(cov[('classifiers', 'abstention')])} for classifiers and {pct(cov[('forecasts', 'abstention')])} for forecasts. Selective accuracy, hallucination rate, Brier score and log loss all improved while decisions got worse for at least {pct(ab_min)} of systems in every setting. The Brier score's resistance in Section 4.1 does not survive: it is proper for the confidences it sees, but when abstained items are dropped from the average, refusing the uncertain ones is rewarded.

Accuracy with abstention counted as wrong and the hardened score had no harmful wins under the primary yardstick. They differ in what they can see: accuracy is blind to confidence, the hardened score is not.

Table: Abstention attacker (may also edit confidence). Columns as in Table 1.

{table_attack('abstention')}

![Harmful-win rate for every score, attacker and data source.](figures/fig2_harmful_win_rate.png){{width=58%}}

## 4.3 The fix holds under other user models

Table 3 reports the worst case across the three data sources under each yardstick. Abstention exploits against selective and answered-only scores remain harmful for high-stakes users and for naive users who ignore confidence: abstaining on 60 to 80% of items removes more value from correct answers than it saves on wrong ones. Confidence-only exploits never harm naive users, since those users ignore confidence, but the score still rises with no benefit to them.

The hardened score has a harmful-win rate of {pct(hard_max)} under the primary yardstick in every setting. Under the low-stakes profile, where it is not identical to the yardstick, the worst case is {pct(hard_low)}.

Table: Worst-case harmful-win rate across the three data sources, by yardstick.

{table_robust()}

## 4.4 Metric shopping, responsiveness and question mix

In random pools of ten simulated systems, the ten standard scores named on average {S['shopping_distinct_winners_mean']['synthetic']:.1f} different systems as "best", and {pct(S['shopping_share_pools_with_3plus_winners']['synthetic'])} of pools had three or more different winners. For the eight real classifiers the figures were {S['shopping_distinct_winners_mean']['classifiers']:.1f} and {pct(S['shopping_share_pools_with_3plus_winners']['classifiers'])}. A developer free to choose the reported score can usually find one that puts their system first.

Table 4 shows how well each score tracks delivered decision value. ECE ranks systems poorly (Kendall's tau {syn('ECE', 'rank_agreement_tau'):.2f} on simulated systems, {clf('ECE', 'rank_agreement_tau'):.2f} on classifiers) because it ignores accuracy and discrimination. AUROC responds negatively to genuine improvements on average ({syn('AUROC', 'responsiveness_spearman'):+.2f}), because more skill leaves fewer errors to discriminate. Accuracy-type scores rank well ({syn('Accuracy', 'rank_agreement_tau'):.2f}) but detect only {pct(syn('Accuracy', 'real_gain_detected'))} of real gains, since two of the three improvements change only confidence.

Changing the share of hard questions from 20% to 80% reverses the ECE ranking of {pct(syn('ECE', 'flip_rate_easy_vs_hard_mix'))} of system pairs, against {pct(S['decision_ranking_flip_rate_easy_vs_hard'])} for decision value itself. Some sensitivity to question mix is legitimate, because real value depends on the questions asked; the excess is a property of the score.

Table: Alignment with decision value. Rank agreement is Kendall's tau with the decision-value ranking in pools of ten (synthetic) or eight (classifiers) systems. Responsiveness is the Spearman correlation between score gain and decision-value gain under genuine improvements (synthetic only).

{table_rank()}

# 5. Discussion

**What the Integrity Profile shows.** Table 5 puts the five dimensions side by side. No standard score passes on every one. ECE is gameable by confidence edits and ranks systems poorly. Selective and answered-only scores are gameable by abstention. Accuracy-type scores are hard to game and blind to confidence. AUROC moves the wrong way under real improvement. A profile across manipulability, harmful-win rate, responsiveness, ranking agreement and question-mix sensitivity describes these trade-offs better than a single verdict.

Table: Integrity Profile for six representative scores. Harmful: worst-case harmful-win rate across the three data sources under the confidence-only and abstention attackers (lower is better). Rank agreement with decision value, responsiveness to real gains and ranking flips with question mix are from the simulated systems (Table 4).

{table_profile()}

**Why the fix works.** The abstention exploit works because dropped items cost nothing. A score that charges an abstention the value of the answer it withheld, zero gain, removes the incentive unless abstaining really is the better action for the user. This is a property of the whole net-benefit family (Schervish, 1989; Vickers and Elkin, 2006; Wu et al., 2026), and our test gives an empirical reason to prefer it.

**Recommendations for benchmark designers.** (1) Run an integrity test on the scoring rule before publishing a leaderboard. (2) Never compute confidence scores on answered items only; charge abstention explicitly. (3) Report a proper or decision-based score as primary and ECE only as a diagnostic. (4) Declare the primary score and the question-mix weights in advance. (5) Report coverage next to every selective metric.

**Implication for AI epistemics.** A benchmark that can be improved without improving decisions will, under optimisation pressure, select for systems that look calibrated or cautious. Epistemic evaluations should be adversarially evaluated before they are trusted as evidence about models.

# References

- Atinafu, Y., and Cohen, R. (2026). RewardHackingAgents: Benchmarking Evaluation Integrity for LLM ML-Engineering Agents. arXiv:2603.11337.
- Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review*, 78(1), 1-3.
- Burns, T. F. (2026). When Guessing is Rewarded: Rethinking Language Model Evaluation with Distributional Uncertainty Scoring. NeurIPS 2026. An apparent earlier version: Measuring Language Model Hallucinations Through Distributional Correctness, arXiv:2510.04302 (2025).
- El-Yaniv, R., and Wiener, Y. (2010). On the foundations of noise-free selective classification. *Journal of Machine Learning Research*, 11, 1605-1641.
- FiveThirtyEight. checking-our-work-data. https://github.com/fivethirtyeight/checking-our-work-data
- Geifman, Y., and El-Yaniv, R. (2017). Selective classification for deep neural networks. NeurIPS.
- Geifman, Y., Uziel, G., and El-Yaniv, R. (2019). Bias-reduced uncertainty estimation for deep neural classifiers. ICLR.
- Gneiting, T., and Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359-378.
- Guo, C., Pleiss, G., Sun, Y., and Weinberger, K. Q. (2017). On calibration of modern neural networks. ICML.
- Kalai, A. T., Nachum, O., Vempala, S. S., and Zhang, E. (2025). Why language models hallucinate. arXiv:2509.04664.
- Kumar, A., Liang, P., and Ma, T. (2019). Verified uncertainty calibration. NeurIPS.
- Mucsányi, B., Kirchhof, M., Nguyen, E., Rubinstein, A., and Oh, S. J. (2023). Trustworthy Machine Learning. arXiv:2310.08215.
- Naeini, M. P., Cooper, G. F., and Hauskrecht, M. (2015). Obtaining well calibrated probabilities using Bayesian binning. AAAI.
- Nixon, J., Dusenberry, M. W., Zhang, L., Jerfel, G., and Tran, D. (2019). Measuring calibration in deep learning. CVPR Workshops.
- Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825-2830.
- Schervish, M. J. (1989). A general method for comparing probability assessors. *Annals of Statistics*, 17(4), 1856-1879.
- Vickers, A. J., and Elkin, E. B. (2006). Decision curve analysis: a novel method for evaluating prediction models. *Medical Decision Making*, 26(6), 565-574.
- Wu, S., Gustafsson, F. K., Phillips, E., Gao, B., Thakur, A., and Clifton, D. A. (2026). BAS: A Decision-Theoretic Approach to Evaluating Large Language Model Confidence. arXiv:2604.03216.

# Appendix A. Limitations and Dual-Use / Ethical Considerations

**What the results establish.** They show that specific scoring rules reward specific answer-preserving manipulations, on the data we used, relative to the decision models we defined. They do not show that any existing leaderboard has been gamed, or that any particular model developer has done so.

**Limitations.**

- No language model was evaluated. The classifiers are small models on small tabular and image datasets, and the forecasts are sports and election forecasts. The scoring-rule mathematics is the same for LLM confidence, but the size of the effects on real LLM benchmarks is untested.
- The individual weaknesses of ECE and of selective metrics are known. The novelty claim is limited to the unified test, the measurements and the closure check, and rests on a targeted literature search, not a systematic review.
- The decision-quality yardstick is a model. Real users are neither pure threshold users nor fully naive, and payoffs are not symmetric in the way assumed.
- The hardened score equals the threshold-user yardstick under uniform stakes, so its strong showing under the primary yardstick is partly by construction. Under the low-stakes profile its worst-case harmful-win rate is {pct(hard_low)}, not zero.
- Only {n['forecasts']} forecast archives were available, and forecasts of the same event on different dates are correlated, so the forecast intervals are wide and optimistic.
- The optimiser is a greedy search over a coarse grid. A stronger attacker could find larger gains, so reported gameability is a lower bound; a score that passed is not thereby proven ungameable.
- Gains are clipped to [-1, 1], which understates large decision losses.
- Metric shopping and question-mix results for ranking use simulated systems and eight classifiers only.

**Dual-use.** The exploits could be used to inflate a system's reported epistemic quality. We judge the risk to be low relative to the benefit: the strongest exploits (constant confidence, mass abstention) are already documented, are trivial to implement, and are easy to detect when coverage and confidence histograms are reported. Publishing a test that benchmark maintainers can run is more useful to defenders than to attackers.

**Data and privacy.** No personal data was collected or used. The classifier datasets ship with scikit-learn. The forecast data is FiveThirtyEight's public archive of its own forecasts about public sports and election outcomes.

**Provenance and AI assistance.** All code and analysis were produced during the sprint; there is no pre-existing project code. An AI assistant (Claude) was used to write code and draft text. The author is responsible for the content. Every number in this report is generated from the released result files by `build_report.py`.

# Appendix B. Reproduction

```
pip install -r requirements.txt
git clone --depth 1 https://github.com/fivethirtyeight/checking-our-work-data data_raw/538
python run_audit.py      # all analyses -> results/
python figures.py        # figures -> figures/
python build_report.py   # this report -> report/
```

Result files: `integrity_profile.csv` (every score, attacker and source, with bootstrap intervals), `attack.csv` (the attacker's chosen exploit per system and score), `exploit_grid.csv` (every hand-made exploit on every system), `honest_recalibration.csv`, `shopping.csv`, `distribution.csv`, `responsiveness.csv`.
"""
os.makedirs("report", exist_ok=True)
open("report/report.md", "w", encoding="utf-8").write(MD)
open("report/abstract.txt", "w", encoding="utf-8").write(ABSTRACT + "\n")
print("abstract words:", len(ABSTRACT.split()))
