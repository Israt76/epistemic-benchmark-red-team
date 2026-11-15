const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/root/.claude/skills/synced/4062f5d0-fc95-467b-b908-9496a6ab8f05_4b661739-505d-4529-875b-fe9639f60134/pptx/scripts/apply_theme.js");
const THEME = { name: "Benchmark Red Team", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "0F1B33", lt1: "FFFFFF", dk2: "2B3A55", lt2: "EEF1F6", accent1: "C8372D", accent2: "2A78D6",
            accent3: "6B7A90", accent4: "EDA100", accent5: "1BAF7A", accent6: "9AA5B8", hlink: "2A78D6", folHlink: "6B7A90" } };
const HEX = THEME.colors;
(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.title = "Epistemic Benchmark Red Team: When Better Scores Mean Worse Decisions";
  pres.author = "Israt Jahan Aunika";
  const C = pres.SchemeColor;
  const FIG = "/home/claude/ebrt/figures/";

  pres.defineSlideMaster({ title: "TITLE_DARK", background: { color: HEX.dk1 }, objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.7, y: 2.0, w: 7.4, h: 1.5, fontSize: 44, bold: true, color: C.background1, align: "left", valign: "top", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.7, y: 3.65, w: 7.4, h: 2.4, fontSize: 24, color: C.background2, align: "left", valign: "top", margin: 0 }, text: "" } },
  ] });
  pres.defineSlideMaster({ title: "CONTENT", background: { color: HEX.lt1 }, margin: [0.5, 0.6, 0.7, 0.6], objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.45, w: 12.1, h: 1.25, fontSize: 36, bold: true, color: C.text1, align: "left", valign: "top", margin: 0 }, text: "" } },
    { text: { text: "Epistemic Benchmark Red Team", options: { x: 0.6, y: 6.95, w: 6, h: 0.3, fontSize: 10, color: C.accent3, margin: 0 } } },
  ], slideNumber: { x: 12.2, y: 6.95, w: 0.6, h: 0.3, fontSize: 10, color: HEX.accent3, align: "right" } });
  pres.defineSlideMaster({ title: "CLOSE_DARK", background: { color: HEX.dk1 }, objects: [
    { placeholder: { options: { name: "title", type: "title", x: 1.0, y: 1.5, w: 11.3, h: 2.2, fontSize: 40, bold: true, color: C.background1, align: "left", valign: "top", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 1.0, y: 4.0, w: 11.3, h: 2.2, fontSize: 22, color: C.background2, align: "left", valign: "top", margin: 0 }, text: "" } },
  ] });

  const card = (s, x, y, w, h, fill, name) => s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.12, fill: { color: fill || C.background2 }, line: { color: fill || C.background2, width: 0 }, objectName: name });
  const txt = (s, t, o) => s.addText(t, Object.assign({ isTextBox: true, margin: 0, valign: "top", color: C.text1 }, o));
  const dot = (s, x, y, label, color) => { s.addShape(pres.ShapeType.ellipse, { x, y, w: 0.62, h: 0.62, fill: { color }, line: { color, width: 0 } });
    txt(s, label, { x, y, w: 0.62, h: 0.62, fontSize: 20, bold: true, color: C.background1, align: "center", valign: "middle" }); };

  // 1 title
  pres.addSection({ title: "Talk" });
  let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Talk" });
  s.addText("Epistemic Benchmark Red Team", { placeholder: "title" });
  s.addText([{ text: "When Better Scores Mean Worse Decisions", options: { breakLine: true } },
             { text: " ", options: { fontSize: 12, breakLine: true } },
             { text: "Israt Jahan Aunika", options: { fontSize: 18, breakLine: true } },
             { text: "Montclair State University", options: { fontSize: 18, breakLine: true } },
             { text: "Apart Research AI x Epistemics Sprint, November 2026", options: { fontSize: 14 } }], { placeholder: "body" });
  card(s, 8.7, 1.7, 3.9, 1.75, C.text2, "score card");
  txt(s, "Benchmark score", { x: 9.0, y: 1.9, w: 3.3, h: 0.4, fontSize: 16, color: C.background2 });
  txt(s, "↑ up", { x: 9.0, y: 2.3, w: 3.3, h: 0.9, fontSize: 44, bold: true, color: C.background1 });
  card(s, 8.7, 3.85, 3.9, 1.75, C.text2, "decision card");
  txt(s, "Decision quality", { x: 9.0, y: 4.05, w: 3.3, h: 0.4, fontSize: 16, color: C.background2 });
  txt(s, "↓ down", { x: 9.0, y: 4.45, w: 3.3, h: 0.9, fontSize: 44, bold: true, color: C.accent1 });
  s.addNotes("Can an AI evaluation get a better score while the AI actually becomes less useful? I'm Israt Jahan Aunika from Montclair State University, and this project red-teams the benchmarks themselves.");

  // 2 problem
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Talk" });
  s.addText("Can an evaluation improve without improving the AI?", { placeholder: "title" });
  const ex = [["1", "Constant confidence", "Say “80% sure” about every answer.", "Calibration score", "near perfect", "Help choosing which answers to trust", "none"],
              ["2", "Strategic abstention", "Refuse every question you might get wrong.", "Accuracy on answered questions", "superb", "Questions actually answered", "few"]];
  ex.forEach((e, i) => { const x = 0.6 + i * 6.2;
    card(s, x, 1.95, 5.9, 3.75, C.background2, "example " + e[0]);
    dot(s, x + 0.35, 2.25, e[0], C.text1);
    txt(s, e[1], { x: x + 1.15, y: 2.3, w: 4.5, h: 0.55, fontSize: 24, bold: true });
    txt(s, e[2], { x: x + 0.35, y: 3.1, w: 5.2, h: 0.5, fontSize: 18 });
    txt(s, e[3], { x: x + 0.35, y: 3.85, w: 3.4, h: 0.7, fontSize: 15, color: C.accent3 });
    txt(s, e[4], { x: x + 3.8, y: 3.8, w: 1.8, h: 0.6, fontSize: 22, bold: true, color: C.accent5, align: "right" });
    txt(s, e[5], { x: x + 0.35, y: 4.7, w: 3.4, h: 0.7, fontSize: 15, color: C.accent3 });
    txt(s, e[6], { x: x + 3.8, y: 4.65, w: 1.8, h: 0.6, fontSize: 22, bold: true, color: C.accent1, align: "right" }); });
  txt(s, "Neither trick changes a single answer.", { x: 0.6, y: 6.05, w: 12.1, h: 0.5, fontSize: 20, bold: true });
  s.addNotes("Benchmarks shape what developers optimise. Here are two tricks. First: report the same confidence for every answer. The standard calibration metric says you are nearly perfect, but the user learns nothing about which answers to trust. Second: refuse every question you might get wrong. Your accuracy on what you answer looks superb. Neither trick changes a single answer.");

  // 3 what I built
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Talk" });
  s.addText("The Epistemic Benchmark Integrity Test", { placeholder: "title" });
  const steps = [["System outputs", "answers, stated confidence"], ["Red-team attacker", "edits confidence or abstains; answers unchanged"],
                 ["Two measurements", "benchmark score and downstream decision quality"], ["Verdict", "Integrity Gap and harmful-win rate"]];
  steps.forEach((st, i) => { const x = 0.6 + i * 3.12;
    card(s, x, 2.2, 2.75, 2.5, i === 1 ? C.text1 : C.background2, "step " + (i + 1));
    txt(s, String(i + 1), { x: x + 0.25, y: 2.4, w: 0.6, h: 0.5, fontSize: 20, bold: true, color: i === 1 ? C.accent6 : C.accent3 });
    txt(s, st[0], { x: x + 0.25, y: 2.95, w: 2.3, h: 0.5, fontSize: 20, bold: true, color: i === 1 ? C.background1 : C.text1 });
    txt(s, st[1], { x: x + 0.25, y: 3.5, w: 2.3, h: 1.1, fontSize: 15, color: i === 1 ? C.background2 : C.text2 });
    if (i < 3) txt(s, "→", { x: x + 2.75, y: 3.1, w: 0.37, h: 0.6, fontSize: 24, color: C.accent3, align: "center" }); });
  txt(s, [{ text: "Held-out attacker: ", options: { bold: true } }, { text: "each exploit is tuned on one half of the data and judged on the other half." }],
      { x: 0.6, y: 5.15, w: 12.1, h: 0.45, fontSize: 18 });
  txt(s, [{ text: "Harmful win: ", options: { bold: true } }, { text: "the score goes up while users’ decisions get worse." }],
      { x: 0.6, y: 5.75, w: 12.1, h: 0.45, fontSize: 18 });
  s.addNotes("So I built a red-team test for the scoring rule itself. An attacker may only edit a system's stated confidence or decide which questions to decline. It never changes an answer. It tunes each exploit on half the data and is judged on the other half. Then I compare two things: what the benchmark sees, and what a user who acts on the answers actually gains. The difference is the Integrity Gap. When the score goes up and decisions get worse, I call that a harmful win.");

  // 4 scope
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Talk" });
  s.addText("What was tested", { placeholder: "title" });
  [["80", "real classifiers", "8 model families on real datasets"], ["9", "real forecast archives", "public sports and election forecasts"],
   ["150", "simulated systems", "controlled skill and miscalibration"], ["10", "scores in common use", "ECE, Brier, log loss, accuracy and more"]]
    .forEach((d, i) => { const x = 0.6 + i * 3.12;
      card(s, x, 2.0, 2.75, 2.9, C.background2, "stat " + d[1]);
      txt(s, d[0], { x: x + 0.25, y: 2.2, w: 2.3, h: 1.1, fontSize: 66, bold: true, color: i < 2 ? C.accent1 : C.text1 });
      txt(s, d[1], { x: x + 0.25, y: 3.45, w: 2.3, h: 0.45, fontSize: 18, bold: true });
      txt(s, d[2], { x: x + 0.25, y: 3.95, w: 2.3, h: 0.8, fontSize: 14, color: C.accent3 }); });
  txt(s, "Four exploit families: confidence gaming, strategic abstention, metric shopping, question-mix sensitivity.", { x: 0.6, y: 5.3, w: 12.1, h: 0.45, fontSize: 18 });
  txt(s, "No language model was evaluated. The results concern scoring rules, which apply to any system scored by them.", { x: 0.6, y: 5.9, w: 12.1, h: 0.45, fontSize: 16, color: C.accent3 });
  s.addNotes("I audited ten scores in common use, on eighty real classifiers, nine real forecast archives, and one hundred and fifty controlled simulated systems. One honest caveat up front: no language model was run. These are results about scoring rules, and they apply to any system scored by them.");

  // 5 confidence gaming (native chart)
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Talk" });
  s.addText("ECE improves dramatically while decisions get worse", { placeholder: "title" });
  s.addChart(pres.charts.BAR, [
    { name: "Calibration error removed", labels: ["Real classifiers", "Real forecasts", "Simulation"], values: [86, 53, 87] },
    { name: "Systems whose decisions got worse", labels: ["Real classifiers", "Real forecasts", "Simulation"], values: [56, 89, 71] }],
    { x: 0.6, y: 1.85, w: 7.6, h: 4.8, barDir: "col", barGrouping: "clustered", barGapWidthPct: 60,
      chartColors: [HEX.accent2, HEX.accent1], showLegend: true, legendPos: "b", legendFontSize: 13, legendFontFace: "+mn-lt", legendColor: HEX.dk2,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0\"%\"", dataLabelFontSize: 14, dataLabelFontFace: "+mn-lt", dataLabelColor: HEX.dk1,
      catAxisLabelFontSize: 14, catAxisLabelFontFace: "+mn-lt", catAxisLabelColor: HEX.dk2, valAxisHidden: true, valAxisMaxVal: 100, valAxisMinVal: 0,
      valGridLine: { style: "none" }, catGridLine: { style: "none" }, showTitle: false, objectName: "ECE chart" });
  card(s, 8.6, 1.95, 4.1, 2.35, C.background2, "exploit card");
  txt(s, "The exploit", { x: 8.9, y: 2.15, w: 3.5, h: 0.4, fontSize: 14, color: C.accent3 });
  txt(s, "One constant confidence for every answer", { x: 8.9, y: 2.55, w: 3.5, h: 1.0, fontSize: 22, bold: true });
  txt(s, "No answer changed.", { x: 8.9, y: 3.65, w: 3.5, h: 0.4, fontSize: 16, color: C.text2 });
  txt(s, "Brier score and log loss resisted this attack: their best “exploit” was a real improvement.", { x: 8.6, y: 4.7, w: 4.1, h: 1.5, fontSize: 16, color: C.text2 });
  s.addNotes("Result one: confidence gaming. Using one fixed confidence value, the attacker reduced calibration error by eighty-six percent on real classifiers, even though downstream decisions became worse for fifty-six percent of those systems. On real forecasts, the error fell by fifty-three percent, and decisions got worse for eighty-nine percent. Brier score and log loss resisted this attack.");

  // 6 abstention
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Talk" });
  s.addText("Proper scoring rules still fail when unanswered items disappear", { placeholder: "title" });
  s.addImage({ path: FIG + "fig2_harmful_win_rate.png", x: 0.6, y: 1.9, w: 7.4, h: 4.69, altText: "Heatmap of harmful-win rate for eleven scores under confidence and abstention attackers on three data sources" });
  [["Attack", "Abstain on most questions (median coverage after attack: 20–42%)."],
   ["Result", "Selective accuracy, hallucination rate, Brier and log loss: harmful wins for at least 89% of systems in every setting."],
   ["Why", "Brier is proper for the confidences it sees, not for the questions it never sees."]]
    .forEach((b, i) => { const y = 2.0 + i * 1.55;
      txt(s, b[0], { x: 8.4, y, w: 4.3, h: 0.35, fontSize: 14, bold: true, color: C.accent1 });
      txt(s, b[1], { x: 8.4, y: y + 0.38, w: 4.3, h: 1.05, fontSize: 16 }); });
  s.addNotes("Result two: strategic abstention. When the attacker may decline questions, it declines most of them. Selective accuracy, hallucination rate, Brier score and log loss all improve, while decisions get worse for at least eighty-nine percent of systems in every setting. Brier is a proper scoring rule, but only for the confidences it sees. Drop the refused questions from the average, and refusing is rewarded.");

  // 7 integrity profile table
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Talk" });
  s.addText("Integrity Profile: no standard score passes everything", { placeholder: "title" });
  const hdr = ["Score", "Harmful wins:\nconfidence attack", "Harmful wins:\nabstention attack", "Rank agreement\nwith decisions", "Responds to\nreal gains", "Ranking flips\nwith question mix"];
  const rowsT = [["ECE", "89%", "100%", "0.23", "+0.14", "35%"], ["Brier", "0%", "100%", "0.53", "+0.62", "29%"], ["Log loss", "6%", "100%", "0.39", "+0.40", "25%"],
                 ["Selective accuracy", "0%", "100%", "0.82", "+0.83", "0%"], ["Accuracy", "0%", "0%", "0.82", "+0.83", "0%"], ["Net benefit (hardened)", "0%", "0%", "0.99", "+1.00", "8%"]];
  const bad = (r, c) => (c === 1 || c === 2) && parseInt(r[c]) >= 50;
  const tbl = [hdr.map((h, c) => ({ text: h, options: { bold: true, fontSize: 13, color: HEX.lt1, fill: { color: HEX.dk1 }, align: c ? "center" : "left", valign: "middle" } }))]
    .concat(rowsT.map((r, i) => r.map((v, c) => ({ text: v, options: { fontSize: 16, bold: c === 0 || bad(r, c) || i === 5, color: bad(r, c) ? HEX.accent1 : HEX.dk1,
      fill: { color: i === 5 ? "DDE9F8" : (i % 2 ? HEX.lt2 : HEX.lt1) }, align: c ? "center" : "left", valign: "middle" } }))));
  s.addTable(tbl, { x: 0.6, y: 1.85, w: 12.1, colW: [3.1, 1.8, 1.8, 1.8, 1.8, 1.8], rowH: [0.7, 0.52, 0.52, 0.52, 0.52, 0.52, 0.52], border: { type: "solid", color: HEX.lt2, pt: 1 }, fontFace: "Calibri", objectName: "Integrity Profile table" });
  txt(s, "Harmful wins: worst case across the three data sources. Other columns: simulated systems. Accuracy is robust but cannot see confidence quality.", { x: 0.6, y: 5.95, w: 12.1, h: 0.7, fontSize: 14, color: C.accent3 });
  s.addNotes("Putting it together gives each score an Integrity Profile. Calibration error is vulnerable to confidence gaming and ranks systems poorly. Brier and log loss are vulnerable to abstention. Accuracy is hard to game but blind to confidence. The net-benefit score, which charges every refusal the value it withheld, is the strongest overall.");

  // 8 fix and contribution
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Talk" });
  s.addText("Red-team the benchmark before trusting it", { placeholder: "title" });
  card(s, 0.6, 1.95, 3.0, 3.3, C.background2, "primary stat");
  txt(s, "0%", { x: 0.85, y: 2.15, w: 2.5, h: 1.1, fontSize: 66, bold: true });
  txt(s, "harmful wins for the hardened score under the primary yardstick, all three data sources", { x: 0.85, y: 3.4, w: 2.5, h: 1.6, fontSize: 15, color: C.text2 });
  card(s, 3.9, 1.95, 3.0, 3.3, C.background2, "robustness stat");
  txt(s, "8%", { x: 4.15, y: 2.15, w: 2.5, h: 1.1, fontSize: 66, bold: true, color: C.accent1 });
  txt(s, "worst case under the low-stakes robustness profile", { x: 4.15, y: 3.4, w: 2.5, h: 1.6, fontSize: 15, color: C.text2 });
  txt(s, "The contribution", { x: 7.4, y: 1.95, w: 5.3, h: 0.45, fontSize: 22, bold: true });
  [["1", "A red-team procedure for scoring rules"], ["2", "Measurements on real classifiers and real forecasts"], ["3", "A closure test: the repair must survive the same attack"]]
    .forEach((c, i) => { dot(s, 7.4, 2.65 + i * 0.9, c[0], C.text1); txt(s, c[1], { x: 8.25, y: 2.65 + i * 0.9, w: 4.45, h: 0.62, fontSize: 17, valign: "middle" }); });
  txt(s, "Not a new calibration metric: the hardened score belongs to a known family of net-benefit scores.", { x: 0.6, y: 5.65, w: 12.1, h: 0.8, fontSize: 16, color: C.accent3 });
  s.addNotes("The hardened score had zero percent harmful wins under the primary yardstick across all three data sources. Under the low-stakes robustness profile, its worst case was eight percent. I do not claim that score as new; it belongs to a known family. The contribution is the red-team procedure, the measurements on real data, and the closure test: any repair has to survive the same attack.");

  // 9 takeaway
  s = pres.addSlide({ masterName: "CLOSE_DARK", sectionTitle: "Talk" });
  s.addText("Better benchmark scores do not necessarily mean better decisions", { placeholder: "title" });
  s.addText([{ text: "Epistemic evaluations should themselves be adversarially evaluated before they are trusted.", options: { breakLine: true } },
             { text: " ", options: { fontSize: 12, breakLine: true } },
             { text: "Israt Jahan Aunika, Montclair State University", options: { fontSize: 16 } }], { placeholder: "body" });
  s.addNotes("Better benchmark scores do not necessarily mean better decisions. The individual weaknesses were partly known; what is new here is one test that measures them and checks a fix. Epistemic evaluations should themselves be adversarially evaluated before they are trusted. Thank you.");

  await pres.writeFile({ fileName: "slides.pptx" });
  await applyTheme("slides.pptx", THEME);
  console.log("deck written");
})();
