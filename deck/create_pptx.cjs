const fs = require("fs");
const path = require("path");
const PptxGenJS = require("/Users/diptiranjanmohapatra/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "outputs", "transcript-intelligence-leadership-deck.pptx");

function parseCsv(file) {
  const text = fs.readFileSync(file, "utf8").trim();
  const rows = [];
  let row = [];
  let cell = "";
  let inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    const n = text[i + 1];
    if (c === '"' && inQuotes && n === '"') {
      cell += '"';
      i++;
    } else if (c === '"') {
      inQuotes = !inQuotes;
    } else if (c === "," && !inQuotes) {
      row.push(cell);
      cell = "";
    } else if ((c === "\n" || c === "\r") && !inQuotes) {
      if (c === "\r" && n === "\n") i++;
      row.push(cell);
      rows.push(row);
      row = [];
      cell = "";
    } else {
      cell += c;
    }
  }
  row.push(cell);
  rows.push(row);
  const headers = rows.shift();
  return rows.filter((r) => r.length === headers.length).map((r) => Object.fromEntries(headers.map((h, i) => [h, r[i]])));
}

const callTypes = parseCsv(path.join(ROOT, "outputs", "call_type_sentiment.csv"));
const themes = parseCsv(path.join(ROOT, "outputs", "theme_summary.csv"));
const risks = parseCsv(path.join(ROOT, "outputs", "risk_register.csv"));

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Dipti Ranjan Mohapatra";
pptx.subject = "Transcript Intelligence take-home analysis";
pptx.title = "Transcript Intelligence Findings";
pptx.company = "AegisCloud case study";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-US",
};
pptx.defineLayout({ name: "CUSTOM_WIDE", width: 13.333, height: 7.5 });
pptx.layout = "CUSTOM_WIDE";

const C = {
  ink: "1F2933",
  muted: "667085",
  line: "D9DEE5",
  bg: "FBFAF7",
  teal: "2F6F73",
  gold: "D08C2E",
  plum: "7B4F9D",
  red: "B94B5F",
  blue: "586F9F",
  green: "5D7A35",
  white: "FFFFFF",
};

function addBg(slide) {
  slide.background = { color: C.bg };
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.12, fill: { color: C.teal }, line: { color: C.teal } });
}

function title(slide, text, sub) {
  slide.addText(text, { x: 0.55, y: 0.35, w: 11.8, h: 0.45, fontFace: "Aptos Display", fontSize: 24, bold: true, color: C.ink, margin: 0 });
  if (sub) slide.addText(sub, { x: 0.57, y: 0.87, w: 11.7, h: 0.3, fontSize: 9.5, color: C.muted, margin: 0 });
}

function foot(slide, n) {
  slide.addText(`Transcript Intelligence | ${n}`, { x: 0.55, y: 7.13, w: 3.8, h: 0.18, fontSize: 7.5, color: C.muted, margin: 0 });
}

function pill(slide, text, x, y, w, color) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h: 0.34, rectRadius: 0.05, fill: { color }, line: { color } });
  slide.addText(text, { x: x + 0.12, y: y + 0.08, w: w - 0.24, h: 0.16, fontSize: 8, bold: true, color: C.white, align: "center", margin: 0 });
}

function metric(slide, label, value, x, y, w, color) {
  slide.addText(value, { x, y, w, h: 0.55, fontSize: 28, bold: true, color, margin: 0 });
  slide.addText(label, { x, y: y + 0.62, w, h: 0.35, fontSize: 9.2, color: C.muted, margin: 0, breakLine: false });
}

function bar(slide, label, value, max, x, y, w, color, suffix = "") {
  slide.addText(label, { x, y: y + 0.03, w: 2.45, h: 0.22, fontSize: 8.6, color: C.ink, margin: 0 });
  slide.addShape(pptx.ShapeType.rect, { x: x + 2.65, y, w, h: 0.24, fill: { color: "ECEFF2" }, line: { color: "ECEFF2" } });
  slide.addShape(pptx.ShapeType.rect, { x: x + 2.65, y, w: Math.max(0.05, w * value / max), h: 0.24, fill: { color }, line: { color } });
  slide.addText(`${value}${suffix}`, { x: x + 2.75 + w, y: y + 0.03, w: 0.8, h: 0.18, fontSize: 8, color: C.ink, margin: 0 });
}

function bullet(slide, text, x, y, w, color = C.ink) {
  slide.addShape(pptx.ShapeType.ellipse, { x, y: y + 0.07, w: 0.08, h: 0.08, fill: { color: C.teal }, line: { color: C.teal } });
  slide.addText(text, { x: x + 0.18, y, w, h: 0.38, fontSize: 10.3, color, fit: "shrink", margin: 0 });
}

// 1. Title
{
  const s = pptx.addSlide();
  addBg(s);
  s.addText("Transcript Intelligence", { x: 0.62, y: 0.82, w: 9.8, h: 0.6, fontFace: "Aptos Display", fontSize: 34, bold: true, color: C.ink, margin: 0 });
  s.addText("Topic taxonomy, sentiment trends, and risk signals from 100 meeting transcripts", { x: 0.65, y: 1.55, w: 8.4, h: 0.35, fontSize: 15, color: C.muted, margin: 0 });
  pill(s, "Take-home assessment", 0.66, 2.12, 1.75, C.teal);
  pill(s, "Leadership readout", 2.55, 2.12, 1.65, C.gold);
  s.addShape(pptx.ShapeType.rect, { x: 0.65, y: 3.0, w: 11.7, h: 0.02, fill: { color: C.line }, line: { color: C.line } });
  metric(s, "meetings processed", "100", 0.75, 3.5, 2.4, C.teal);
  metric(s, "call types", "3", 3.55, 3.5, 2.4, C.gold);
  metric(s, "theme categories", "8", 6.1, 3.5, 2.4, C.plum);
  metric(s, "elevated risk", "26%", 8.75, 3.5, 2.4, C.red);
  s.addText("Core thesis: Detect reliability is not only an engineering issue. It directly affects renewal confidence, compliance trust, and competitive risk.", { x: 0.75, y: 5.55, w: 10.7, h: 0.62, fontSize: 18, bold: true, color: C.ink, margin: 0 });
  foot(s, 1);
}

// 2. Method
{
  const s = pptx.addSlide();
  addBg(s); title(s, "Method: transparent, reproducible, interview-ready", "The pipeline is deterministic and traceable back to source meetings.");
  const steps = [
    ["Load", "meeting metadata, summaries, action items, key moments, and sentence-level transcripts"],
    ["Infer", "call type from title patterns and participant domains"],
    ["Classify", "themes using an auditable keyword taxonomy"],
    ["Score", "sentiment from supplied meeting-level sentiment and transcript signals"],
    ["Rank", "risk when negative sentiment overlaps with outage, churn, compliance, SLA, or competitor language"],
  ];
  steps.forEach((d, i) => {
    const x = 0.7 + (i % 3) * 4.1;
    const y = 1.55 + Math.floor(i / 3) * 2.15;
    s.addShape(pptx.ShapeType.roundRect, { x, y, w: 3.55, h: 1.45, rectRadius: 0.08, fill: { color: C.white }, line: { color: C.line } });
    s.addText(d[0], { x: x + 0.22, y: y + 0.18, w: 1.4, h: 0.25, fontSize: 15, bold: true, color: C.teal, margin: 0 });
    s.addText(d[1], { x: x + 0.22, y: y + 0.55, w: 3.0, h: 0.55, fontSize: 9.2, color: C.ink, fit: "shrink", margin: 0 });
  });
  s.addText("Why this approach works for the assessment: it is explainable, fast to rerun, and easy for interviewers to inspect or challenge.", { x: 0.75, y: 6.28, w: 10.8, h: 0.35, fontSize: 13.5, bold: true, color: C.ink, margin: 0 });
  foot(s, 2);
}

// 3. Sentiment
{
  const s = pptx.addSlide();
  addBg(s); title(s, "Support calls are the clearest pain signal", "Average sentiment is lowest in support calls; customer calls show where pain becomes commercial pressure.");
  const maxSent = 5;
  callTypes.forEach((r, i) => bar(s, r.segment, Number(r.avg_sentiment), maxSent, 0.75, 1.55 + i * 0.55, 5.2, [C.gold, C.blue, C.red][i], ""));
  s.addText("Average sentiment score, 1 = very negative, 5 = very positive", { x: 3.4, y: 3.28, w: 4.5, h: 0.2, fontSize: 8, color: C.muted, margin: 0 });
  s.addShape(pptx.ShapeType.rect, { x: 7.55, y: 1.32, w: 4.75, h: 2.65, fill: { color: C.white }, line: { color: C.line } });
  bullet(s, "Support: reliability, alerting, backup, and identity failures are felt most directly.", 7.85, 1.65, 3.85);
  bullet(s, "External customer calls connect incidents to renewals, churn risk, and competitor evaluation.", 7.85, 2.35, 3.85);
  bullet(s, "Internal calls are more constructive, but still explain the root causes behind customer frustration.", 7.85, 3.08, 3.85);
  foot(s, 3);
}

// 4. Themes
{
  const s = pptx.addSlide();
  addBg(s); title(s, "Theme landscape: roadmap is broad, reliability is sharp", "Theme coverage shows what appears often; risk score shows what leadership should treat urgently.");
  const topThemes = themes.slice(0, 8);
  const maxCount = Math.max(...topThemes.map((r) => Number(r.meeting_count)));
  topThemes.forEach((r, i) => bar(s, r.theme, Number(r.meeting_count), maxCount, 0.68, 1.35 + i * 0.45, 4.9, [C.teal, C.gold, C.red, C.plum, C.blue, C.green, "8A5A44", "6D7280"][i], ""));
  s.addShape(pptx.ShapeType.rect, { x: 7.2, y: 1.24, w: 5.15, h: 4.35, fill: { color: C.white }, line: { color: C.line } });
  s.addText("Interpretation", { x: 7.55, y: 1.55, w: 2.5, h: 0.3, fontSize: 16, bold: true, color: C.ink, margin: 0 });
  bullet(s, "Product roadmap and compliance appear widely because most calls touch roadmap, audit, or reporting language.", 7.55, 2.05, 4.1);
  bullet(s, "Reliability has lower sentiment and higher risk, especially when Detect visibility is lost.", 7.55, 2.85, 4.1);
  bullet(s, "Competitive pressure is less frequent but has the highest average risk signal.", 7.55, 3.65, 4.1);
  foot(s, 4);
}

// 5. Risk register
{
  const s = pptx.addSlide();
  addBg(s); title(s, "Highest-priority risk conversations", "The top risks combine low sentiment with outage, compliance, churn, or competitor language.");
  const header = [["Rank", "Meeting", "Type", "Risk", "Theme"]];
  const body = risks.slice(0, 7).map((r) => [r.risk_rank, r.title, r.call_type, r.risk_score, r.primary_theme]);
  s.addTable(header.concat(body), {
    x: 0.55, y: 1.3, w: 12.2, h: 4.55,
    border: { type: "solid", color: C.line, pt: 0.6 },
    fill: "FFFFFF",
    fontFace: "Aptos",
    fontSize: 8.2,
    color: C.ink,
    margin: 0.06,
    autoFit: false,
    colW: [0.45, 4.85, 1.35, 0.75, 3.0],
    rowH: 0.43,
    bold: false,
  });
  s.addShape(pptx.ShapeType.rect, { x: 0.55, y: 1.3, w: 12.2, h: 0.43, fill: { color: C.teal }, line: { color: C.teal } });
  s.addText("Leadership action: review these accounts first. They are where technical reliability, customer trust, and revenue risk intersect.", { x: 0.72, y: 6.22, w: 10.7, h: 0.3, fontSize: 13.2, bold: true, color: C.ink, margin: 0 });
  foot(s, 5);
}

// 6. What it means
{
  const s = pptx.addSlide();
  addBg(s); title(s, "What the trends mean", "The signal is not just sentiment; it is where sentiment overlaps with business impact.");
  const cards = [
    ["Reliability is revenue protection", "Detect outages create direct risk in renewal and competitive conversations.", C.red],
    ["Compliance customers need proactive comms", "HIPAA, SOC 2, and PCI language increases the cost of unclear incident communication.", C.teal],
    ["Competitor mentions are warning lights", "SentinelShield and other alternatives appear when customers lose confidence after incidents.", C.gold],
    ["Support should feed roadmap weekly", "Escalation themes are strong product prioritization inputs, not just case-level problems.", C.plum],
  ];
  cards.forEach((c, i) => {
    const x = 0.72 + (i % 2) * 6.05;
    const y = 1.45 + Math.floor(i / 2) * 2.15;
    s.addShape(pptx.ShapeType.roundRect, { x, y, w: 5.45, h: 1.55, rectRadius: 0.08, fill: { color: C.white }, line: { color: C.line } });
    s.addShape(pptx.ShapeType.rect, { x, y, w: 0.12, h: 1.55, fill: { color: c[2] }, line: { color: c[2] } });
    s.addText(c[0], { x: x + 0.32, y: y + 0.24, w: 4.8, h: 0.28, fontSize: 15.5, bold: true, color: C.ink, margin: 0 });
    s.addText(c[1], { x: x + 0.32, y: y + 0.72, w: 4.65, h: 0.44, fontSize: 9.5, color: C.muted, margin: 0 });
  });
  foot(s, 6);
}

// 7. Additional insights
{
  const s = pptx.addSlide();
  addBg(s); title(s, "Additional insight ideas", "Where Transcript Intelligence could go next for product, engineering, support, and sales leaders.");
  const ideas = [
    ["Renewal risk early warning", "Combine sentiment, churn mentions, SLA/compliance language, and competitor mentions."],
    ["Product-module pain map", "Attribute themes to Detect, Comply, Protect, and Identity to expose module-level friction."],
    ["Action accountability", "Mine action items by owner and function after escalations and post-incident calls."],
    ["Incident communication quality", "Compare customer frustration against communication timing and status-page gaps."],
  ];
  ideas.forEach((d, i) => {
    const y = 1.45 + i * 1.12;
    s.addText(`0${i + 1}`, { x: 0.75, y, w: 0.6, h: 0.32, fontSize: 15, bold: true, color: C.teal, margin: 0 });
    s.addText(d[0], { x: 1.5, y, w: 3.25, h: 0.28, fontSize: 14, bold: true, color: C.ink, margin: 0 });
    s.addText(d[1], { x: 4.9, y: y + 0.02, w: 6.7, h: 0.32, fontSize: 10.3, color: C.muted, margin: 0 });
    s.addShape(pptx.ShapeType.rect, { x: 1.5, y: y + 0.58, w: 10.6, h: 0.01, fill: { color: C.line }, line: { color: C.line } });
  });
  foot(s, 7);
}

// 8. Recommendations
{
  const s = pptx.addSlide();
  addBg(s); title(s, "Recommended leadership actions", "Use the transcript signal as a recurring operating input, not a one-time analysis.");
  bullet(s, "Prioritize Detect reliability and alerting as both product quality and revenue protection work.", 0.8, 1.55, 9.7);
  bullet(s, "Proactively message compliance-heavy customers after incidents, with specific remediation and owner commitments.", 0.8, 2.35, 9.7);
  bullet(s, "Create a recurring competitive-readiness review for accounts mentioning direct alternatives.", 0.8, 3.15, 9.7);
  bullet(s, "Send weekly support escalation patterns to product and engineering leadership.", 0.8, 3.95, 9.7);
  s.addShape(pptx.ShapeType.roundRect, { x: 0.8, y: 5.3, w: 11.2, h: 0.75, rectRadius: 0.08, fill: { color: "E9F2F2" }, line: { color: "CFE3E3" } });
  s.addText("Decision to make: should Detect reliability and incident communication become a top leadership metric for the next planning cycle?", { x: 1.08, y: 5.55, w: 10.5, h: 0.25, fontSize: 14.5, bold: true, color: C.ink, margin: 0 });
  foot(s, 8);
}

pptx.writeFile({ fileName: OUT });
console.log(OUT);
