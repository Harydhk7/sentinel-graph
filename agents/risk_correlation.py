"""Risk correlation agent for SentinelGraph AI.

This agent merges metadata, lineage, ownership, and findings into a
single enterprise risk posture.
"""

from __future__ import annotations

from typing import Any

from tools.datahub.runtime import RiskAssessment


class RiskCorrelationEngine:
    """Correlate findings, lineage, and metadata into an explanatory risk score."""

    def correlate(self, dataset: Any, findings: list[Any], impact_report: Any) -> RiskAssessment:
        severity_weights = {"high": 3, "medium": 2, "low": 1}
        total_weight = sum(severity_weights.get(f.severity, 1) for f in findings)
        avg_confidence = sum(f.confidence for f in findings) / max(1, len(findings))
        score = min(100.0, round((total_weight * 10) + (avg_confidence * 20) + (impact_report.blast_radius * 5), 1))

        if score >= 80:
            level = "critical"
        elif score >= 60:
            level = "high"
        elif score >= 35:
            level = "medium"
        else:
            level = "low"

        return RiskAssessment(
            dataset_urn=dataset.urn,
            overall_score=int(score),
            threat_level=level,
            risk_trend="stable",
            confidence=round(avg_confidence, 2),
            reasoning=f"{dataset.name} presents {level} overall risk based on {len(findings)} finding(s) and downstream impact.",
            historical_comparison="No historical baseline available",
        )


def create_risk_correlation_agent() -> RiskCorrelationEngine:
    """Create the risk correlation agent instance."""
    return RiskCorrelationEngine()
