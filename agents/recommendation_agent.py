from __future__ import annotations

from typing import Any

from tools.datahub.runtime import Recommendation


class RecommendationAgent:
    """Generate explainable remediation suggestions."""

    def generate(self, dataset: Any, findings: list[Any], risk_assessment: Any) -> list[Recommendation]:
        recommendations = []
        for finding in findings:
            recommendations.append(
                Recommendation(
                    dataset_urn=dataset.urn,
                    executive_summary=f"Address {finding.category} findings",
                    technical_summary=finding.recommendation,
                    why_this_matters=f"Risk score {risk_assessment.overall_score} and evidence suggest this control gap should be closed.",
                    business_impact="Improves operational and compliance posture for the dataset.",
                    root_cause=f"{finding.category} posture gap",
                    remediation_steps=[finding.recommendation],
                    estimated_effort="medium",
                    priority="high" if finding.severity == "high" else "medium",
                    owner=None,
                    expected_risk_reduction="Moderate reduction in exposure",
                )
            )
        return recommendations


def create_recommendation_agent() -> RecommendationAgent:
    return RecommendationAgent()
