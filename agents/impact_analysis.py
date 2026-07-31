"""Impact analysis agent for SentinelGraph AI.

This agent traverses lineage to compute downstream business impact
when a dataset or system is found to be at risk.
"""

from __future__ import annotations

from tools.datahub.models import DataHubDataset
from tools.datahub.runtime import ImpactReport


class ImpactAnalysisAgent:
    """Compute lineage-aware impact for datasets."""

    def analyze(self, dataset: DataHubDataset, lineage, findings) -> ImpactReport:
        affected_datasets = []
        affected_dashboards = []
        affected_pipelines = []
        affected_ml_models = []
        affected_downstream_assets = []

        for edge in lineage.edges:
            if edge.source == dataset.urn:
                affected_datasets.append(edge.target)
                affected_downstream_assets.append(edge.target)

        owner = dataset.owners[0].name if dataset.owners else None
        domain = dataset.domains[0].name if dataset.domains else None
        criticality = "high" if any(f.severity == "high" for f in findings) else "medium"
        blast_radius = max(1, len(affected_datasets) + len(dataset.storage_locations))

        return ImpactReport(
            dataset_urn=dataset.urn,
            affected_datasets=affected_datasets,
            affected_dashboards=affected_dashboards,
            affected_pipelines=affected_pipelines,
            affected_ml_models=affected_ml_models,
            affected_downstream_assets=affected_downstream_assets,
            business_owner=owner,
            business_domain=domain,
            criticality=criticality,
            blast_radius=blast_radius,
            reasoning=f"Lineage traversal identified {len(affected_datasets)} downstream asset(s) for {dataset.name}.",
        )


def create_impact_analysis_agent() -> ImpactAnalysisAgent:
    """Create the impact analysis agent instance."""
    return ImpactAnalysisAgent()
