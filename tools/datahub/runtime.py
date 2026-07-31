from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tools.datahub.models import DataHubDataset, DataHubLineage


@dataclass(slots=True)
class Finding:
    id: str
    dataset_urn: str
    platform: str
    severity: str
    confidence: float
    category: str
    description: str
    evidence: dict[str, Any] = field(default_factory=dict)
    recommendation: str = ""
    timestamp: str = ""


@dataclass(slots=True)
class ImpactReport:
    dataset_urn: str
    affected_datasets: list[str] = field(default_factory=list)
    affected_dashboards: list[str] = field(default_factory=list)
    affected_pipelines: list[str] = field(default_factory=list)
    affected_ml_models: list[str] = field(default_factory=list)
    affected_downstream_assets: list[str] = field(default_factory=list)
    business_owner: str | None = None
    business_domain: str | None = None
    criticality: str = "medium"
    blast_radius: int = 0
    reasoning: str = ""


@dataclass(slots=True)
class RiskAssessment:
    dataset_urn: str
    overall_score: int
    threat_level: str
    risk_trend: str
    confidence: float
    reasoning: str
    historical_comparison: str = ""


@dataclass(slots=True)
class Recommendation:
    dataset_urn: str
    executive_summary: str
    technical_summary: str
    why_this_matters: str
    business_impact: str
    root_cause: str
    remediation_steps: list[str] = field(default_factory=list)
    estimated_effort: str = "medium"
    priority: str = "medium"
    owner: str | None = None
    expected_risk_reduction: str = ""


@dataclass(slots=True)
class ExecutionResult:
    dataset_urn: str
    findings: list[Finding] = field(default_factory=list)
    impact: ImpactReport | None = None
    risk: RiskAssessment | None = None
    recommendation: Recommendation | None = None
    published: bool = False
    history_entry: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AnalysisContext:
    datasets: list[DataHubDataset] = field(default_factory=list)
    lineage: dict[str, DataHubLineage] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    impacts: list[ImpactReport] = field(default_factory=list)
    risks: list[RiskAssessment] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)
