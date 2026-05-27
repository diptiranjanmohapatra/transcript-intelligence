#!/usr/bin/env python3
"""Transcript Intelligence take-home pipeline.

The assignment allows LLMs, clustering, rules, or hybrids. This implementation
uses a deterministic hybrid that is easy to audit in an interview:

1. Load meeting metadata, summaries, key moments, and sentence-level transcripts.
2. Infer call type from meeting title and participant domains.
3. Assign business themes with a keyword taxonomy over title, summary, topics,
   and action items.
4. Use provided summary sentiment as the primary signal and transcript sentence
   sentiment as a validation signal.
5. Export reviewer-friendly CSV, JSON, SVG, and Markdown outputs.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Iterable


THEMES = {
    "Reliability & Incident Response": [
        "outage",
        "incident",
        "latency",
        "pipeline failure",
        "dashboard down",
        "root cause",
        "post-mortem",
        "alert delays",
        "alerts not firing",
        "sla",
        "reliability",
        "timeout",
    ],
    "Compliance & Audit Readiness": [
        "compliance",
        "soc 2",
        "hipaa",
        "pci",
        "audit",
        "evidence",
        "framework",
        "regulatory",
        "reporting",
    ],
    "Identity & Access Management": [
        "identity",
        "mfa",
        "sso",
        "ldap",
        "rbac",
        "provisioning",
        "access",
        "session",
        "active directory",
    ],
    "Backup & Recovery": [
        "backup",
        "restore",
        "disaster recovery",
        "rto",
        "retention",
        "replication",
        "s3",
        "cloudprime",
    ],
    "Renewal, Churn & Commercial Risk": [
        "renewal",
        "churn",
        "pricing",
        "contract",
        "billing",
        "invoice",
        "qbr",
        "business review",
        "seat overage",
    ],
    "Product Roadmap & Feature Gaps": [
        "roadmap",
        "feature",
        "gap",
        "request",
        "custom",
        "launch",
        "ga",
        "early access",
        "design review",
        "planning",
    ],
    "Competitive Pressure": [
        "competitor",
        "competitive",
        "sentinelshield",
        "vaultedge",
        "cybernova",
        "evaluation",
        "displacement",
    ],
    "Customer Onboarding & Adoption": [
        "onboarding",
        "deployment",
        "setup",
        "migration",
        "adoption",
        "workshop",
        "configuration",
    ],
}

THEME_PRIORITY = {
    "Reliability & Incident Response": 0,
    "Renewal, Churn & Commercial Risk": 1,
    "Competitive Pressure": 2,
    "Compliance & Audit Readiness": 3,
    "Identity & Access Management": 4,
    "Backup & Recovery": 5,
    "Customer Onboarding & Adoption": 6,
    "Product Roadmap & Feature Gaps": 7,
}

MODULES = {
    "Detect": ["detect", "alert", "threat", "siem", "logvault"],
    "Comply": ["comply", "compliance", "audit", "soc 2", "hipaa", "pci"],
    "Protect": ["protect", "backup", "restore", "disaster recovery"],
    "Identity": ["identity", "mfa", "sso", "ldap", "rbac", "access"],
}

RISK_WORDS = [
    "churn",
    "renewal risk",
    "sla",
    "outage",
    "escalation",
    "urgent",
    "competitive",
    "competitor",
    "breach",
    "compliance",
    "down",
    "failure",
]

INTERNAL_DOMAIN = "aegiscloud.com"


@dataclass
class Meeting:
    meeting_id: str
    title: str
    call_type: str
    start_time: str
    duration: float
    summary: str
    topics: list[str]
    action_items: list[str]
    key_moments: list[dict]
    sentiment_label: str
    sentiment_score: float
    transcript_sentiments: Counter
    themes: list[str]
    primary_theme: str
    modules: list[str]
    risk_score: float
    notable_quote: str


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def infer_call_type(title: str, emails: Iterable[str]) -> str:
    title_l = title.lower()
    external_emails = [
        email for email in emails if "@" in email and not email.lower().endswith("@" + INTERNAL_DOMAIN)
    ]
    if title_l.startswith("support case") or title_l.startswith("urgent") or title_l.startswith("escalation"):
        return "Support"
    if external_emails or title_l.startswith("aegis /"):
        return "External Customer"
    return "Internal"


def match_terms(text: str, terms: Iterable[str]) -> int:
    text_l = normalize(text)
    return sum(1 for term in terms if term in text_l)


def assign_themes(text: str) -> list[str]:
    scored = [(theme, match_terms(text, terms)) for theme, terms in THEMES.items()]
    max_score = max(score for _, score in scored)
    threshold = 2 if max_score >= 2 else 1
    themes = [
        theme
        for theme, score in sorted(
            scored,
            key=lambda item: (-item[1], THEME_PRIORITY.get(item[0], 99), item[0]),
        )
        if score >= threshold
    ]
    return themes or ["General Account Discussion"]


def assign_modules(text: str) -> list[str]:
    modules = [module for module, terms in MODULES.items() if match_terms(text, terms) > 0]
    return modules or ["Cross-product"]


def choose_quote(summary: dict, transcript: dict) -> str:
    key_moments = summary.get("keyMoments") or []
    if key_moments:
        return key_moments[0].get("text", "")[:220]
    for row in transcript.get("data", []):
        sent = row.get("sentence", "")
        if len(sent) > 60:
            return sent[:220]
    return ""


def calculate_risk_score(
    title: str,
    summary: str,
    topics: list[str],
    key_moments: list[dict],
    sentiment_score: float,
) -> float:
    text = " ".join([title, summary, " ".join(topics), json.dumps(key_moments)]).lower()
    risk_hits = match_terms(text, RISK_WORDS)
    negative_sentiment = max(0.0, 3.0 - sentiment_score)
    moment_risk = sum(1 for moment in key_moments if moment.get("type") in {"concern", "feature_gap", "action_item"})
    return round(min(10.0, risk_hits * 0.9 + negative_sentiment * 1.4 + moment_risk * 0.35), 2)


def load_meetings(dataset_dir: Path) -> list[Meeting]:
    meetings: list[Meeting] = []
    for meeting_dir in sorted(path for path in dataset_dir.iterdir() if path.is_dir()):
        info = load_json(meeting_dir / "meeting-info.json")
        summary = load_json(meeting_dir / "summary.json")
        transcript = load_json(meeting_dir / "transcript.json")

        title = info["title"]
        summary_text = summary.get("summary", "")
        topics = summary.get("topics", [])
        action_items = summary.get("actionItems", [])
        key_moments = summary.get("keyMoments", [])
        combined_text = " ".join([title, summary_text, " ".join(topics), " ".join(action_items)])
        themes = assign_themes(combined_text)
        score = float(summary.get("sentimentScore", 0.0))

        meetings.append(
            Meeting(
                meeting_id=info["meetingId"],
                title=title,
                call_type=infer_call_type(title, info.get("allEmails", [])),
                start_time=info.get("startTime", ""),
                duration=float(info.get("duration", 0.0)),
                summary=summary_text,
                topics=topics,
                action_items=action_items,
                key_moments=key_moments,
                sentiment_label=summary.get("overallSentiment", "unknown"),
                sentiment_score=score,
                transcript_sentiments=Counter(row.get("sentimentType", "unknown") for row in transcript.get("data", [])),
                themes=themes,
                primary_theme=themes[0],
                modules=assign_modules(combined_text),
                risk_score=calculate_risk_score(title, summary_text, topics, key_moments, score),
                notable_quote=choose_quote(summary, transcript),
            )
        )
    return meetings


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize_by(items: Iterable[Meeting], key_fn) -> list[dict]:
    groups: dict[str, list[Meeting]] = defaultdict(list)
    for item in items:
        groups[key_fn(item)].append(item)
    rows = []
    for key, group in sorted(groups.items()):
        rows.append(
            {
                "segment": key,
                "meeting_count": len(group),
                "avg_sentiment": round(mean(m.sentiment_score for m in group), 2),
                "avg_risk": round(mean(m.risk_score for m in group), 2),
                "negative_or_mixed_negative": sum(
                    1 for m in group if "negative" in m.sentiment_label
                ),
                "top_themes": "; ".join(
                    theme for theme, _ in Counter(m.primary_theme for m in group).most_common(4)
                ),
            }
        )
    return rows


def theme_rows(meetings: list[Meeting]) -> list[dict]:
    rows = []
    for theme in sorted({theme for meeting in meetings for theme in meeting.themes}):
        group = [meeting for meeting in meetings if theme in meeting.themes]
        call_type_counts = Counter(meeting.call_type for meeting in group)
        examples = sorted(group, key=lambda meeting: (-meeting.risk_score, meeting.title))[:3]
        rows.append(
            {
                "theme": theme,
                "meeting_count": len(group),
                "avg_sentiment": round(mean(meeting.sentiment_score for meeting in group), 2),
                "avg_risk": round(mean(meeting.risk_score for meeting in group), 2),
                "call_type_mix": "; ".join(f"{k}: {v}" for k, v in call_type_counts.most_common()),
                "examples": " | ".join(f"{m.title} ({m.meeting_id})" for m in examples),
            }
        )
    return sorted(rows, key=lambda row: (-row["meeting_count"], -row["avg_risk"], row["theme"]))


def risk_register(meetings: list[Meeting], limit: int = 15) -> list[dict]:
    rows = []
    for meeting in sorted(meetings, key=lambda m: (-m.risk_score, m.sentiment_score, m.title))[:limit]:
        rows.append(
            {
                "risk_rank": len(rows) + 1,
                "meeting_id": meeting.meeting_id,
                "title": meeting.title,
                "call_type": meeting.call_type,
                "sentiment_score": meeting.sentiment_score,
                "risk_score": meeting.risk_score,
                "primary_theme": meeting.primary_theme,
                "modules": "; ".join(meeting.modules),
                "why_it_matters": meeting.notable_quote,
            }
        )
    return rows


def bar_svg(title: str, labels: list[str], values: list[float], path: Path, x_label: str = "") -> None:
    width = 920
    row_h = 42
    top = 72
    left = 260
    right = 48
    height = top + row_h * len(labels) + 54
    max_value = max(values) if values else 1
    scale = (width - left - right) / max_value if max_value else 1
    colors = ["#2f6f73", "#d08c2e", "#7b4f9d", "#b94b5f", "#586f9f", "#5d7a35"]

    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfaf7"/>',
        f'<text x="32" y="38" font-family="Arial" font-size="24" font-weight="700" fill="#1f2933">{html.escape(title)}</text>',
    ]
    for index, (label, value) in enumerate(zip(labels, values)):
        y = top + index * row_h
        bar_w = max(2, value * scale)
        color = colors[index % len(colors)]
        pieces.append(
            f'<text x="32" y="{y + 22}" font-family="Arial" font-size="14" fill="#263238">{html.escape(label)}</text>'
        )
        pieces.append(
            f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="24" rx="3" fill="{color}"/>'
        )
        pieces.append(
            f'<text x="{left + bar_w + 8:.1f}" y="{y + 18}" font-family="Arial" font-size="13" fill="#263238">{value:.2f}</text>'
        )
    if x_label:
        pieces.append(
            f'<text x="{left}" y="{height - 18}" font-family="Arial" font-size="12" fill="#5f6b73">{html.escape(x_label)}</text>'
        )
    pieces.append("</svg>")
    path.write_text("\n".join(pieces), encoding="utf-8")


def count_svg(title: str, rows: list[dict], label_key: str, value_key: str, path: Path) -> None:
    labels = [row[label_key] for row in rows]
    values = [float(row[value_key]) for row in rows]
    bar_svg(title, labels, values, path, "Meeting count")


def pct(part: int, total: int) -> str:
    return f"{(part / total * 100):.0f}%" if total else "0%"


def write_report(output_dir: Path, meetings: list[Meeting], themes: list[dict], call_types: list[dict], risks: list[dict]) -> None:
    total = len(meetings)
    high_risk = [meeting for meeting in meetings if meeting.risk_score >= 5.0]
    negative = [meeting for meeting in meetings if "negative" in meeting.sentiment_label]
    top_theme = themes[0]
    support = next((row for row in call_types if row["segment"] == "Support"), None)
    external = next((row for row in call_types if row["segment"] == "External Customer"), None)
    internal = next((row for row in call_types if row["segment"] == "Internal"), None)

    lines = [
        "# Transcript Intelligence Findings",
        "",
        "## Executive Summary",
        "",
        f"- Processed **{total} meetings** from the supplied dataset using a deterministic hybrid pipeline.",
        f"- The largest theme is **{top_theme['theme']}** with **{top_theme['meeting_count']} meetings**.",
        f"- **{len(negative)} meetings ({pct(len(negative), total)})** carry negative or mixed-negative sentiment.",
        f"- **{len(high_risk)} meetings ({pct(len(high_risk), total)})** triggered elevated risk signals.",
        "- Most risk is concentrated where reliability incidents overlap with renewal, compliance, or competitive pressure.",
        "",
        "## Sentiment Across Call Types",
        "",
        "| Call type | Meetings | Avg sentiment | Avg risk | Top themes |",
        "|---|---:|---:|---:|---|",
    ]
    for row in call_types:
        lines.append(
            f"| {row['segment']} | {row['meeting_count']} | {row['avg_sentiment']} | {row['avg_risk']} | {row['top_themes']} |"
        )

    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- Support calls are the clearest operational pain signal: they skew toward reliability, alerting, backup, and identity issues.",
            "- External customer calls are where technical incidents become commercial decisions: renewal confidence, churn risk, and competitive comparisons show up together.",
            "- Internal calls are more positive because many are planning, launch readiness, and retrospectives, but they still reveal root causes that explain customer-facing dissatisfaction.",
            "",
            "## Topic / Theme Taxonomy",
            "",
            "| Theme | Meetings | Avg sentiment | Avg risk | Examples |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for row in themes:
        lines.append(
            f"| {row['theme']} | {row['meeting_count']} | {row['avg_sentiment']} | {row['avg_risk']} | {row['examples']} |"
        )

    lines.extend(
        [
            "",
            "## Highest Priority Risks",
            "",
            "| Rank | Meeting | Call type | Risk | Theme | Why it matters |",
            "|---:|---|---|---:|---|---|",
        ]
    )
    for row in risks[:8]:
        lines.append(
            f"| {row['risk_rank']} | {row['title']} | {row['call_type']} | {row['risk_score']} | {row['primary_theme']} | {row['why_it_matters']} |"
        )

    lines.extend(
        [
            "",
            "## Additional Insight Ideas",
            "",
            "1. **Renewal risk early warning:** combine sentiment, churn mentions, SLA/compliance language, and competitor mentions to flag accounts before a commercial review.",
            "2. **Product-module pain map:** attribute themes to Detect, Comply, Protect, and Identity so product leaders can see which modules create the most support load and commercial friction.",
            "3. **Action accountability:** mine action items by owner and function to reveal where follow-through clusters, especially after escalations or post-incident calls.",
            "4. **Incident communication quality:** compare negative support calls with post-incident internal reviews to test whether communication gaps, not just technical failures, drive customer frustration.",
            "",
            "## Recommended Leadership Actions",
            "",
            "- Treat Detect reliability and alerting as both product quality and revenue protection work.",
            "- Pair Comply roadmap updates with proactive customer messaging; compliance-positive calls are strong expansion opportunities.",
            "- Create a recurring competitive-readiness review for accounts mentioning SentinelShield, VaultEdge, CyberNova, or direct competitive evaluation.",
            "- Make support escalation patterns visible to product and engineering each week, not only after a major incident.",
            "",
            "## Assets",
            "",
            "- `meeting_analysis.csv`: meeting-level classifications and signals.",
            "- `theme_summary.csv`: taxonomy counts, examples, sentiment, and risk.",
            "- `call_type_sentiment.csv`: sentiment and risk by Support, External Customer, and Internal.",
            "- `risk_register.csv`: ranked meetings to investigate first.",
            "- `sentiment_by_call_type.svg` and `theme_counts.svg`: simple charts for slides.",
        ]
    )

    if support and external and internal:
        lines.extend(
            [
                "",
                "## Presenter Note",
                "",
                f"A crisp leadership framing: support sentiment averages {support['avg_sentiment']}, external customer sentiment averages {external['avg_sentiment']}, and internal sentiment averages {internal['avg_sentiment']}. The gap suggests customers feel the operational pain before internal teams fully price it into roadmap decisions.",
            ]
        )

    (output_dir / "leadership_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(dataset_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    meetings = load_meetings(dataset_dir)

    meeting_rows = [
        {
            "meeting_id": m.meeting_id,
            "title": m.title,
            "call_type": m.call_type,
            "start_time": m.start_time,
            "duration_minutes": m.duration,
            "sentiment_label": m.sentiment_label,
            "sentiment_score": m.sentiment_score,
            "primary_theme": m.primary_theme,
            "themes": "; ".join(m.themes),
            "modules": "; ".join(m.modules),
            "risk_score": m.risk_score,
            "topics": "; ".join(m.topics),
            "action_item_count": len(m.action_items),
            "negative_sentence_count": m.transcript_sentiments.get("negative", 0),
            "positive_sentence_count": m.transcript_sentiments.get("positive", 0),
            "notable_quote": m.notable_quote,
        }
        for m in meetings
    ]
    write_csv(
        output_dir / "meeting_analysis.csv",
        meeting_rows,
        list(meeting_rows[0].keys()),
    )

    call_types = summarize_by(meetings, lambda m: m.call_type)
    write_csv(output_dir / "call_type_sentiment.csv", call_types, list(call_types[0].keys()))

    themes = theme_rows(meetings)
    write_csv(output_dir / "theme_summary.csv", themes, list(themes[0].keys()))

    risks = risk_register(meetings)
    write_csv(output_dir / "risk_register.csv", risks, list(risks[0].keys()))

    with (output_dir / "meeting_analysis.json").open("w", encoding="utf-8") as f:
        json.dump(meeting_rows, f, indent=2)

    bar_svg(
        "Average Sentiment by Call Type",
        [row["segment"] for row in call_types],
        [float(row["avg_sentiment"]) for row in call_types],
        output_dir / "sentiment_by_call_type.svg",
        "1 = very negative, 5 = very positive",
    )
    count_svg(
        "Theme Coverage",
        themes[:8],
        "theme",
        "meeting_count",
        output_dir / "theme_counts.svg",
    )
    write_report(output_dir, meetings, themes, call_types, risks)

    print(f"Processed {len(meetings)} meetings")
    print(f"Wrote outputs to {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Transcript Intelligence analysis")
    parser.add_argument("--dataset", type=Path, default=Path("interview-assignment/dataset"))
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    run(args.dataset, args.output)


if __name__ == "__main__":
    main()
