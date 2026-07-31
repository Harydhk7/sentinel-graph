from __future__ import annotations

from agents.impact_analysis import create_impact_analysis_agent
from agents.recommendation_agent import create_recommendation_agent
from agents.risk_correlation import create_risk_correlation_agent
from agents.security_assessment import create_security_assessment_agent
from tools.datahub.models import DataHubDataset, DataHubLineage, DataHubLineageEdge, DataHubOwner, DataHubDomain


def test_end_to_end_security_reasoning_flow() -> None:
    dataset = DataHubDataset(
        urn="urn:li:dataset:(urn:li:dataPlatform:postgres,customers,PROD)",
        name="customers",
        platform="postgres",
        owners=[DataHubOwner(name="Alice")],
        domains=[DataHubDomain(name="Finance")],
    )
    lineage = DataHubLineage(edges=[DataHubLineageEdge(source=dataset.urn, target="urn:li:dashboard:(analytics,finance-dashboard)")])

    agent = create_security_assessment_agent()
    findings = agent.assess_dataset(dataset)
    assert findings

    impact_agent = create_impact_analysis_agent()
    impact = impact_agent.analyze(dataset, lineage, findings)
    assert impact.blast_radius >= 1
    assert impact.affected_datasets

    risk_agent = create_risk_correlation_agent()
    risk = risk_agent.correlate(dataset, findings, impact)
    assert risk.threat_level in {"low", "medium", "high", "critical"}

    recommendation_agent = create_recommendation_agent()
    recommendations = recommendation_agent.generate(dataset, findings, risk)
    assert recommendations
    assert recommendations[0].priority in {"high", "medium", "low"}
