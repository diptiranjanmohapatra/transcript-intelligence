# Transcript Intelligence Findings

## Executive Summary

- Processed **100 meetings** from the supplied dataset using a deterministic hybrid pipeline.
- The largest theme is **Product Roadmap & Feature Gaps** with **77 meetings**.
- **39 meetings (39%)** carry negative or mixed-negative sentiment.
- **26 meetings (26%)** triggered elevated risk signals.
- Most risk is concentrated where reliability incidents overlap with renewal, compliance, or competitive pressure.

## Sentiment Across Call Types

| Call type | Meetings | Avg sentiment | Avg risk | Top themes |
|---|---:|---:|---:|---|
| External Customer | 40 | 3.85 | 3.47 | Compliance & Audit Readiness; Reliability & Incident Response; Identity & Access Management; Product Roadmap & Feature Gaps |
| Internal | 30 | 3.42 | 3.53 | Reliability & Incident Response; Compliance & Audit Readiness; Product Roadmap & Feature Gaps; Competitive Pressure |
| Support | 30 | 2.83 | 3.9 | Reliability & Incident Response; Product Roadmap & Feature Gaps; Compliance & Audit Readiness; Renewal, Churn & Commercial Risk |

Interpretation:

- Support calls are the clearest operational pain signal: they skew toward reliability, alerting, backup, and identity issues.
- External customer calls are where technical incidents become commercial decisions: renewal confidence, churn risk, and competitive comparisons show up together.
- Internal calls are more positive because many are planning, launch readiness, and retrospectives, but they still reveal root causes that explain customer-facing dissatisfaction.

## Topic / Theme Taxonomy

| Theme | Meetings | Avg sentiment | Avg risk | Examples |
|---|---:|---:|---:|---|
| Product Roadmap & Feature Gaps | 77 | 3.39 | 3.68 | Detect Outage - Escalation Bridge (01KQ46A9DE0AECB006D897A0) | Detect Outage - Customer Impact Assessment (01KQ2331EFD78BF3B1CAB747) | Aegis / Quantum Edge - Renewal Concerns (01KQ1DCC80852AE384C898C9) |
| Compliance & Audit Readiness | 56 | 3.79 | 3.45 | Aegis / Quantum Edge - Renewal Concerns (01KQ1DCC80852AE384C898C9) | Aegis / Northstar Pharma - Urgent: Detect Outage Impact (01KQ351E141926AB7CAB668D) | Aegis / Ironworks Corp - Vendor Comparison Discussion (01KQ6CAA850EAFDC48B52846) |
| Reliability & Incident Response | 54 | 2.87 | 4.97 | URGENT: Blackridge Investments - Complete Loss of Threat Visibility (01KQ2D93184912F0147315E7) | Detect Outage - Escalation Bridge (01KQ46A9DE0AECB006D897A0) | Detect Outage - Customer Impact Assessment (01KQ2331EFD78BF3B1CAB747) |
| Renewal, Churn & Commercial Risk | 24 | 3.3 | 4.39 | Detect Outage - Customer Impact Assessment (01KQ2331EFD78BF3B1CAB747) | Aegis / Quantum Edge - Renewal Concerns (01KQ1DCC80852AE384C898C9) | Aegis / Northstar Pharma - Urgent: Detect Outage Impact (01KQ351E141926AB7CAB668D) |
| Identity & Access Management | 23 | 3.62 | 2.86 | Aegis / Summit Trust - Platform Concerns Discussion (01KQ5A966832A146DA4B7D41) | Support Case #7615 - Crestline Wealth Group Policy Sync Delay (01KQC166F678CBA584AAFF8B) | Aegis / Axiom Labs - Multi-Year Renewal (01KQ410FB7E434BA3F99EE7D) |
| Competitive Pressure | 22 | 2.9 | 5.83 | URGENT: Blackridge Investments - Complete Loss of Threat Visibility (01KQ2D93184912F0147315E7) | Aegis / Quantum Edge - Renewal Concerns (01KQ1DCC80852AE384C898C9) | Aegis / Northstar Pharma - Urgent: Detect Outage Impact (01KQ351E141926AB7CAB668D) |
| Customer Onboarding & Adoption | 15 | 4.26 | 2.24 | Support Case #8179 - Clearwater Medical Overage Charges Dispute (01KQ56AA6B60801ABC01AB1C) | Support Case #6635 - Nova Retail Group SSO Login Failures (01KQADC32D89E2B76B698E84) | Aegis / Blackridge Investments - Renewal Discussion (01KQFFC0F889AE8CFEE7A00D) |
| Backup & Recovery | 11 | 3.77 | 2.53 | URGENT: Cobalt Software - Aegis Detect Dashboard Down (01KQEDB92E33CF9945A7F71B) | Support Case #6977 - Brightpath Commerce Slow Backup Performance (01KQ1A6B7E81B06F4A13B60D) | Aegis / Coastal Living Co - Onboarding Kickoff (01KQ9BB82FD97C9607D57E90) |

## Highest Priority Risks

| Rank | Meeting | Call type | Risk | Theme | Why it matters |
|---:|---|---|---:|---|---|
| 1 | URGENT: Blackridge Investments - Complete Loss of Threat Visibility | Support | 10.0 | Reliability & Incident Response | Julia reveals Blackridge has had zero threat visibility for over three hours, with a team of analysts staring at a dead screen — a critical situation for a financial services firm that is a constant target. |
| 2 | Detect Outage - Escalation Bridge | Internal | 9.23 | Reliability & Incident Response | Diana confirms all Detect customers have zero event processing and zero alert visibility during the outage |
| 3 | Detect Outage - Customer Impact Assessment | Internal | 8.88 | Reliability & Incident Response | Aisha reveals that a customer — not the internal team — flagged the outage at 2 AM, triggering the internal escalation |
| 4 | Aegis / Quantum Edge - Renewal Concerns | External Customer | 8.74 | Competitive Pressure | Brianna describes the six-hour Aegis Detect outage on March 10-11, citing lost visibility, compliance obligations, and the failure to be proactively notified by Aegis. |
| 5 | Aegis / Northstar Pharma - Urgent: Detect Outage Impact | External Customer | 8.26 | Reliability & Incident Response | Grace describes 36 hours of zero threat monitoring visibility for her security team in a healthcare environment, expressing deep frustration. |
| 6 | URGENT: Cobalt Software - Aegis Detect Dashboard Down | Support | 8.13 | Reliability & Incident Response | Lauren reports Aegis Detect dashboard is completely down with zero threat visibility, emphasizing the critical nature of the outage. |
| 7 | Aegis / Ironworks Corp - Vendor Comparison Discussion | External Customer | 8.11 | Product Roadmap & Feature Gaps | Catherine reveals they are actively considering leaving Aegis, framing it as a serious internal discussion about fit |
| 8 | ESCALATION: Northstar Pharma - Detect Outage Impact on Compliance | Support | 7.36 | Compliance & Audit Readiness | Grace reveals Northstar is subject to HIPAA and has had zero threat visibility for hours, escalating the severity of the outage |

## Additional Insight Ideas

1. **Renewal risk early warning:** combine sentiment, churn mentions, SLA/compliance language, and competitor mentions to flag accounts before a commercial review.
2. **Product-module pain map:** attribute themes to Detect, Comply, Protect, and Identity so product leaders can see which modules create the most support load and commercial friction.
3. **Action accountability:** mine action items by owner and function to reveal where follow-through clusters, especially after escalations or post-incident calls.
4. **Incident communication quality:** compare negative support calls with post-incident internal reviews to test whether communication gaps, not just technical failures, drive customer frustration.

## Recommended Leadership Actions

- Treat Detect reliability and alerting as both product quality and revenue protection work.
- Pair Comply roadmap updates with proactive customer messaging; compliance-positive calls are strong expansion opportunities.
- Create a recurring competitive-readiness review for accounts mentioning SentinelShield, VaultEdge, CyberNova, or direct competitive evaluation.
- Make support escalation patterns visible to product and engineering each week, not only after a major incident.

## Assets

- `meeting_analysis.csv`: meeting-level classifications and signals.
- `theme_summary.csv`: taxonomy counts, examples, sentiment, and risk.
- `call_type_sentiment.csv`: sentiment and risk by Support, External Customer, and Internal.
- `risk_register.csv`: ranked meetings to investigate first.
- `sentiment_by_call_type.svg` and `theme_counts.svg`: simple charts for slides.

## Presenter Note

A crisp leadership framing: support sentiment averages 2.83, external customer sentiment averages 3.85, and internal sentiment averages 3.42. The gap suggests customers feel the operational pain before internal teams fully price it into roadmap decisions.
