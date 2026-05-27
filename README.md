# Transcript Intelligence Take-Home

This workspace contains a reproducible solution for the interview assignment in
`interview-assignment/`.

## What is included

- `solution/transcript_intelligence.py` - deterministic analysis pipeline.
- `outputs/meeting_analysis.csv` - meeting-level call type, themes, modules, sentiment, and risk.
- `outputs/theme_summary.csv` - topic/theme taxonomy with examples.
- `outputs/call_type_sentiment.csv` - sentiment trends across Support, External Customer, and Internal calls.
- `outputs/risk_register.csv` - highest-priority meetings to investigate.
- `outputs/leadership_report.md` - concise leadership-facing findings and recommendations.
- `outputs/*.svg` - chart assets for a slide deck.

## Run

```bash
python3 solution/transcript_intelligence.py --dataset interview-assignment/dataset --output outputs
```

The pipeline uses only the Python standard library.

## Approach

I used a transparent hybrid approach:

1. Infer call type from title patterns and participant domains.
2. Combine title, supplied summary, topics, and action items into an analysis text.
3. Apply an auditable keyword taxonomy for themes and product modules.
4. Use provided summary sentiment scores as the primary sentiment signal.
5. Use sentence-level transcript sentiment counts as a supporting validation signal.
6. Rank risks when negative sentiment overlaps with outage, churn, compliance, SLA, or competitive language.

This is intentionally easy to defend in an interview: the taxonomy can be edited,
the outputs are deterministic, and every classification can be traced back to the
source meeting.
