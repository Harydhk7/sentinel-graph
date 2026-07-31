"""Executive report generation for SentinelGraph AI."""

from __future__ import annotations


def build_executive_report(data: dict) -> str:
    """Build a markdown executive summary report."""
    dataset = data.get("dataset")
    findings = data.get("findings", [])
    impact = data.get("impact")
    risk = data.get("risk")
    recommendations = data.get("recommendations", [])
    lineage = data.get("lineage")
    ai_summary = data.get("ai_summary")
    analyst_answers = data.get("analyst_answers", {})

    lines = [
        "# SentinelGraph: An Autonomous Data Security Agent for DataHub",
        "",
        "## Executive Summary",
        ai_summary or f"SentinelGraph analyzed {dataset.name if dataset else 'the selected dataset'} and identified {len(findings)} finding(s).",
        "",
        "SentinelGraph runs autonomously on DataHub metadata: it reads metadata, reasons about lineage and risk, and writes actionable findings back to DataHub without human intervention.",
        "",
        "## Environment Summary",
        f"- Dataset URN: {dataset.urn if dataset else 'n/a'}",
        f"- Platform: {dataset.platform if dataset else 'n/a'}",
        f"- Owners: {', '.join(owner.name for owner in dataset.owners) if dataset and dataset.owners else 'n/a'}",
        f"- Domains: {', '.join(domain.name for domain in dataset.domains) if dataset and dataset.domains else 'n/a'}",
        f"- Downstream assets: {len(impact.affected_datasets) if impact else 0}",
        "",
        "## Critical Findings",
    ]
    if findings:
        for finding in findings:
            lines.append(f"- {finding.category}: {finding.description} [{finding.severity}]")
    else:
        lines.append("- No findings identified")

    lines.extend([
        "",
        "## Top Risks",
        f"- Overall risk score: {risk.overall_score if risk else 'n/a'}",
        f"- Threat level: {risk.threat_level if risk else 'n/a'}",
        f"- Blast radius: {impact.blast_radius if impact else 'n/a'}",
        "",
        "## Recommendations",
    ])
    if recommendations:
        for recommendation in recommendations:
            lines.append(f"- {recommendation.technical_summary}")
    else:
        lines.append("- No recommendations generated")

    lines.extend([
        "",
        "## AI Analyst Q&A",
    ])
    if analyst_answers:
        for question_key, answer in analyst_answers.items():
            lines.append(f"- {question_key.replace('_', ' ').title()}: {answer}")
    else:
        lines.append("- No AI Analyst answers generated")

    lines.extend([
        "",
        "## Trend Analysis",
        f"- Trend: {risk.risk_trend if risk else 'n/a'}",
        f"- Lineage edges: {len(lineage.edges) if lineage else 0}",
    ])
    return "\n".join(lines)
