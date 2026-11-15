# Presentation package (3 to 5 minutes)

Deck: `slides/slides.pptx` (the narration below is also in each slide's speaker notes).

## Narration script with timing

| # | Time | On screen | Narration |
|--:|:--|:--|:--|
| 1 | 0:00-0:15 | Title slide: "Benchmark score up / Decision quality down" | Can an AI evaluation get a better score while the AI actually becomes less useful? I'm Israt Jahan Aunika from Montclair State University, and this project red-teams the benchmarks themselves. |
| 2 | 0:15-0:45 | Two example cards: constant confidence, strategic abstention | Benchmarks shape what developers optimise. Here are two tricks. First: report the same confidence for every answer. The standard calibration metric says you are nearly perfect, but the user learns nothing about which answers to trust. Second: refuse every question you might get wrong. Your accuracy on what you answer looks superb. Neither trick changes a single answer. |
| 3 | 0:45-1:25 | Four-step workflow: outputs, attacker, two measurements, verdict | So I built a red-team test for the scoring rule itself. An attacker may only edit a system's stated confidence or decide which questions to decline. It never changes an answer. It tunes each exploit on half the data and is judged on the other half. Then I compare two things: what the benchmark sees, and what a user who acts on the answers actually gains. The difference is the Integrity Gap. When the score goes up and decisions get worse, I call that a harmful win. |
| 4 | 1:25-1:50 | Four numbers: 80, 9, 150, 10 | I audited ten scores in common use, on eighty real classifiers, nine real forecast archives, and one hundred and fifty controlled simulated systems. One honest caveat up front: no language model was run. These are results about scoring rules, and they apply to any system scored by them. |
| 5 | 1:50-2:20 | Bar chart: calibration error removed vs systems with worse decisions | Result one: confidence gaming. Using one fixed confidence value, the attacker reduced calibration error by eighty-six percent on real classifiers, even though downstream decisions became worse for fifty-six percent of those systems. On real forecasts, the error fell by fifty-three percent, and decisions got worse for eighty-nine percent. Brier score and log loss resisted this attack. |
| 6 | 2:20-2:55 | Harmful-win heatmap (paper Figure 2) | Result two: strategic abstention. When the attacker may decline questions, it declines most of them. Selective accuracy, hallucination rate, Brier score and log loss all improve, while decisions get worse for at least eighty-nine percent of systems in every setting. Brier is a proper scoring rule, but only for the confidences it sees. Drop the refused questions from the average, and refusing is rewarded. |
| 7 | 2:55-3:20 | Integrity Profile table (paper Table 5) | Putting it together gives each score an Integrity Profile. Calibration error is vulnerable to confidence gaming and ranks systems poorly. Brier and log loss are vulnerable to abstention. Accuracy is hard to game but blind to confidence. The net-benefit score, which charges every refusal the value it withheld, is the strongest overall. |
| 8 | 3:20-3:55 | "0%" and "8%" callouts; three-part contribution | The hardened score had zero percent harmful wins under the primary yardstick across all three data sources. Under the low-stakes robustness profile, its worst case was eight percent. I do not claim that score as new; it belongs to a known family. The contribution is the red-team procedure, the measurements on real data, and the closure test: any repair has to survive the same attack. |
| 9 | 3:55-4:15 | Takeaway slide | Better benchmark scores do not necessarily mean better decisions. The individual weaknesses were partly known; what is new here is one test that measures them and checks a fix. Epistemic evaluations should themselves be adversarially evaluated before they are trusted. Thank you. |

About 560 words, which is roughly four minutes at a normal speaking pace.

## Speaker notes

- Slide 2: pause after "Neither trick changes a single answer." It is the idea the rest depends on.
- Slide 3: point at the dark "Red-team attacker" box when you say "it never changes an answer".
- Slide 5: this is the strongest finding. Slow down on "eighty-six percent" and "fifty-six percent"; the simulation numbers are on the chart and need not be read out.
- Slide 1: pause for a full second after the opening question.
- Slide 6: point to the dark columns of the heatmap (abstention) and then the light bottom row (hardened score).
- Slide 8: say "under the primary yardstick" and the eight percent. Do not say "never gamed".
- If you run long, cut the last sentence of slide 5 and the middle sentence of slide 9.

## Ready-made narrated video

`media/presentation_narrated.mp4` is a 3:46 video of the slides at 1080p with a spoken narration, a plain-language heading for each slide, and matching on-screen captions; `media/presentation_captions.srt` is the same text as a subtitle file. It can be uploaded as it is.

The voice is computer-generated (Piper text-to-speech, LibriTTS voice, dataset licence CC BY 4.0). Say so in the video description. A recording in your own voice is still the better option if you have ten minutes: follow the steps below.

## How to record

1. Open `slides/slides.pptx` in PowerPoint (or upload it to Google Slides) and start the slideshow.
2. Record the screen with voice:
   - PowerPoint: Slide Show > Record > From Beginning, then File > Export > Create a Video (1080p).
   - Or Zoom: start a meeting alone, share the slideshow window, press Record, and use the saved MP4.
   - Or macOS: Shift-Cmd-5 > Record Selected Portion, with the microphone enabled under Options.
3. Read the narration from the speaker notes (Presenter View shows them). One take is fine.
4. Keep the result between 3 and 5 minutes. Check that the audio is clear and the text is readable at 1080p.
5. Upload to YouTube as **Unlisted** (or Public) and paste the link into the form.

## YouTube title

Epistemic Benchmark Red Team: When Better Scores Mean Worse Decisions

## YouTube description

Can an AI evaluation get a better score while the AI becomes less useful?

This 4-minute talk presents the Epistemic Benchmark Integrity Test, a red-team procedure for the scoring rules used to evaluate AI calibration, honesty and caution. An attacker edits only a system's stated confidence, or which questions it declines, and never changes an answer. The benchmark's score gain is then compared with the change in downstream decision quality.

Audited: 10 scores in common use, on 80 real classifiers, 9 real forecast archives and 150 simulated systems.

Main results:
- One constant confidence removed 86% of calibration error (ECE) for real classifiers and 53% for real forecasts, while decisions got worse for 56% and 89% of those systems.
- Strategic abstention improved selective accuracy, hallucination rate, Brier score and log loss while decisions got worse for at least 89% of systems in every setting tested.
- A hardened net-benefit score had 0% harmful wins under the primary yardstick across all three data sources; its worst case under the low-stakes robustness profile was 8%.

No language model was evaluated; the results concern scoring rules. The individual metric weaknesses are partly known; the contribution is the unified red-team framework, the measurements and the closure test.

Author: Israt Jahan Aunika, Montclair State University
Narration: computer-generated voice (Piper text-to-speech, LibriTTS voice, CC BY 4.0).
Submitted to the Apart Research AI x Epistemics Research Sprint, November 2026.
Code and paper: [add your GitHub link]

## Thumbnail

Use `media/project_image.png` as it is. If you want text-only alternatives: "Better score. Worse decisions." or "Red-teaming AI benchmarks".
