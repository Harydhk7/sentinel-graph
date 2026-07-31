"""Planner agent for SentinelGraph AI.

This module orchestrates the end-to-end workflow for DataHub-driven
security intelligence analysis.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agents.ai_analyst import create_ai_analyst_agent
from agents.datahub_publisher import create_datahub_publisher_agent
from agents.impact_analysis import create_impact_analysis_agent
from agents.metadata_discovery import create_metadata_discovery_agent
from agents.recommendation_agent import create_recommendation_agent
from agents.risk_correlation import create_risk_correlation_agent
from agents.security_assessment import create_security_assessment_agent
from dashboard import build_dashboard
from reports.executive import build_executive_report
from tools.datahub.models import DataHubDataset, DataHubLineage
from tools.datahub.service import DataHubMetadataService


class PlannerAgent:
    """Coordinate discovery, assessment, impact, scoring, publishing, and reporting."""

    def __init__(self, service: DataHubMetadataService | None = None, publish: bool = False, output_dir: str | None = None) -> None:
        self.service = service or DataHubMetadataService()
        self.publish = publish
        self.output_dir = Path(output_dir or "./sentinelgraph-out")
        self.logger = logging.getLogger("sentinelgraph.planner")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
            self.logger.addHandler(handler)

        self.discovery_agent = create_metadata_discovery_agent()
        self.assessment_agent = create_security_assessment_agent()
        self.impact_agent = create_impact_analysis_agent()
        self.risk_agent = create_risk_correlation_agent()
        self.recommendation_agent = create_recommendation_agent()
        self.ai_analyst = create_ai_analyst_agent()
        self.publisher = create_datahub_publisher_agent(service=self.service)

    def run(self, dataset_urn: str | None = None) -> dict[str, Any]:
        start = datetime.now(timezone.utc)
        self.logger.info("Starting SentinelGraph analysis")
        if not dataset_urn:
            raise ValueError("Dataset URN is required for analysis. Specify --dataset <urn>.")

        dataset = self.service.get_dataset(dataset_urn)
        lineage = self.service.get_lineage(dataset.urn)
        self.logger.info("Discovered dataset %s", dataset.urn)
        findings = self.assessment_agent.assess_dataset(dataset)
        impact = self.impact_agent.analyze(dataset, lineage, findings)
        risk = self.risk_agent.correlate(dataset, findings, impact)
        recommendations = self.recommendation_agent.generate(dataset, findings, risk)

        knowledge_graph = {
            "datasets": [dataset],
            "owners": dataset.owners,
            "schemas": dataset.schema,
            "lineage": lineage,
            "pipelines": dataset.pipelines,
            "domains": dataset.domains,
            "tags": dataset.tags,
            "assertions": dataset.assertions,
            "ml_assets": dataset.ml_assets,
            "findings": findings,
            "risk_scores": [risk],
            "recommendations": recommendations,
        }
        analysis_context = {"dataset": dataset, "lineage": lineage, "findings": findings, "impact": impact, "risk": risk, "recommendations": recommendations, "knowledge_graph": knowledge_graph}
        ai_summary = self.ai_analyst.summarize(analysis_context)
        analyst_answers = {
            "riskiest_dataset": self.ai_analyst.answer("What's the riskiest dataset in the finance domain?", analysis_context),
            "pii_exposure": self.ai_analyst.answer("Show me all datasets with PII exposure.", analysis_context),
            "lineage_blast_radius": self.ai_analyst.answer("What is the lineage blast radius?", analysis_context),
        }

        publishing_result = {"published": False, "statistics": {}}
        if self.publish:
            self.logger.info("Publishing results back to DataHub")
            publishing_result = self.publisher.publish(dataset=dataset, findings=findings, impact=impact, risk=risk, recommendations=recommendations, knowledge_graph=knowledge_graph, ai_summary=ai_summary)

        report_dir = self.output_dir / "reports"
        dashboard_dir = self.output_dir / "dashboard"
        report_dir.mkdir(parents=True, exist_ok=True)
        dashboard_dir.mkdir(parents=True, exist_ok=True)

        report_path = report_dir / "executive.md"
        report_path.write_text(build_executive_report({**analysis_context, "ai_summary": ai_summary, "analyst_answers": analyst_answers}), encoding="utf-8")
        dashboard_path = dashboard_dir / "index.html"
        dashboard_path.write_text(build_dashboard({**analysis_context, "ai_summary": ai_summary, "analyst_answers": analyst_answers}), encoding="utf-8")

        history_entry = {
            "dataset_urn": dataset.urn,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": int((datetime.now(timezone.utc) - start).total_seconds() * 1000),
            "findings": len(findings),
            "risk_score": risk.overall_score,
            "published": publishing_result["published"],
        }
        self.output_dir.joinpath("history.json").write_text(json.dumps(history_entry, indent=2), encoding="utf-8")

        return {
            "status": "completed",
            "dataset": dataset,
            "lineage": lineage,
            "findings": findings,
            "impact": impact,
            "risk": risk,
            "recommendations": recommendations,
            "ai_summary": ai_summary,
            "ai_analyst": self.ai_analyst,
            "analyst_answers": analyst_answers,
            "publishing": publishing_result,
            "reports": {"markdown": str(report_path), "dashboard": str(dashboard_path)},
            "history": history_entry,
        }


def create_planner_agent(service: DataHubMetadataService | None = None, publish: bool = False, output_dir: str | None = None) -> PlannerAgent:
    """Create the planner agent instance."""
    return PlannerAgent(service=service, publish=publish, output_dir=output_dir)
