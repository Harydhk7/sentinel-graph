"""DataHub publisher agent for SentinelGraph AI."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from tools.datahub.models import DataHubDataset
from tools.datahub.runtime import Finding, ImpactReport, Recommendation, RiskAssessment
from tools.datahub.service import DataHubMetadataService


class DataHubPublisherAgent:
    """Publish analysis results back into DataHub as custom metadata."""

    def __init__(self, service: DataHubMetadataService | None = None) -> None:
        self.service = service or DataHubMetadataService()

    def publish(
        self,
        *,
        dataset: DataHubDataset,
        findings: list[Finding],
        impact: ImpactReport,
        risk: RiskAssessment,
        recommendations: list[Recommendation],
        knowledge_graph: dict[str, Any],
        ai_summary: str | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        custom_properties = {
            "securityScore": str(risk.overall_score),
            "threatLevel": risk.threat_level,
            "riskTrend": risk.risk_trend,
            "aiSummary": ai_summary or risk.reasoning,
            "assessmentTimestamp": now,
            "recommendations": " | ".join(r.remediation_steps[0] if r.remediation_steps else r.technical_summary for r in recommendations),
            "relatedFindings": " | ".join(f.title if hasattr(f, "title") else f.category for f in findings),
            "riskCategory": risk.threat_level,
            "remediationStatus": "open",
            "lastScanVersion": "sentinelgraph-v1",
        }
        self.service.write_custom_properties(dataset.urn, custom_properties)
        published_dataset = self.service.get_dataset(dataset.urn)
        return {"published": True, "dataset_urn": dataset.urn, "statistics": {"properties_written": len(custom_properties)}}


def create_datahub_publisher_agent(service: DataHubMetadataService | None = None) -> DataHubPublisherAgent:
    """Create the DataHub publisher agent instance."""
    return DataHubPublisherAgent(service=service)
