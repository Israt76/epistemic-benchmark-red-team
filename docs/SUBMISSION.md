# Apart submission: what goes in each form field

## Required fields

- **Project title:** Epistemic Benchmark Red Team: When Better Scores Mean Worse Decisions
- **Track:** Track 1 (Model Epistemics and Decision-Making Evals)
- **PDF report:** your export of the official Google Doc template, filled from `report/report.docx`
- **Project summary:**

> Benchmarks that score an AI's calibration, honesty or caution are meant to tell us whether people can rely on it. We tested whether those scores can go up while nobody's decisions get better. We built a red-team test for the scoring rules themselves: an attacker changes only a system's stated confidence or which questions it declines, never an answer, and we compare what the benchmark sees with what a user acting on the answers would actually gain. Across 80 real classifiers, 9 real forecast archives and 150 controlled simulated systems, the most common calibration metric (ECE) could be improved by 53 to 87% with a single constant confidence while decisions got worse for most systems. Refusing most questions improved selective accuracy, hallucination rate, Brier score and log loss for at least 89% of systems while decisions got worse. A score that charges abstention its withheld value had 0% harmful wins under the primary yardstick across all three data sources. Existing calibration and misinformation evaluations measure models; this work measures whether the measurement can be trusted. We release the test as a reusable tool and recommend that epistemic benchmarks be adversarially evaluated before their scores are used as evidence. No language model was evaluated; the results concern scoring rules.

## Optional fields

| Form field | What to put there | File |
|:--|:--|:--|
| Presentation recording | Link to your unlisted YouTube video: either your own narrated recording (script in `docs/PRESENTATION.md`) or the ready-made narrated video (computer-generated voice) | `media/presentation_narrated.mp4` |
| Project code | Link to your public GitHub repository | this whole folder |
| Slides | Upload the PDF (or the PPTX if the form accepts it) | `slides/slides.pdf`, `slides/slides.pptx` |
| Project image | Upload the PNG (1920 x 1080) | `media/project_image.png` |
| Additional material | Upload the supplement | `report/supplement.pdf` |

## GitHub repository

- **Suggested name:** epistemic-benchmark-red-team
- **Description:** Red-team framework that tests whether epistemic evaluation scores (ECE, Brier, selective accuracy and more) can be improved without improving downstream decisions.
- **Topics:** ai-evaluation, benchmarks, calibration, uncertainty-quantification, selective-prediction, red-teaming, ai-safety, epistemics, decision-theory, proper-scoring-rules

To publish: create an empty public repository with that name, then in this folder run
`git remote add origin https://github.com/<your-username>/epistemic-benchmark-red-team.git` and `git push -u origin main`.

## 30-second pitch

An AI can look more trustworthy without becoming more useful. Report the same confidence for every answer and the standard calibration metric says you are nearly perfect. Refuse every hard question and your accuracy looks superb. I built a red-team test that attacks the benchmark instead of the model, and measured the damage on real classifiers and real forecasts: scores improved while users' decisions got worse. A score that charges every refusal its withheld value had no harmful wins under the primary yardstick. Before we trust an epistemic benchmark, we should try to break it.

## Final checklist

- [ ] Paste `report/report.docx` into your copy of the official Google Doc template; confirm the body (Introduction to Discussion) is at most 8 pages and the abstract is 150 to 250 words (it is 226).
- [ ] Read the report once and spot-check the references.
- [ ] Export the template to PDF (under 25 MB).
- [ ] Record the talk and upload it (3 to 5 minutes).
- [ ] Push the repository and make it public; add the link to the YouTube description.
- [ ] Fill the form: title, summary, PDF, track, then the five optional fields from the table above.
- [ ] Deadline: Sunday Nov 15, 11:59 PM AoE = Monday Nov 16, 6:59 AM New York time.
- [ ] Check for the confirmation email. Resubmitting under the same title replaces the earlier submission.

## Wording to keep consistent

- Say: "0% harmful wins under the primary yardstick across all three data sources" and "worst case 8% under the low-stakes robustness profile".
- Do not say "never gamed", "ungameable" or "first ever".
- No language model was evaluated; the findings concern scoring rules.
- The contribution is the red-team framework, the measurements and the closure test, not a new metric.
