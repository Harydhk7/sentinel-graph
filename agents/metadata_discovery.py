"""Metadata discovery agent for SentinelGraph AI.

This agent reads DataHub metadata for datasets, lineage, owners,
schemas, pipelines, storage locations, and ML assets.
"""

from __future__ import annotations

from tools.datahub.service import DataHubMetadataService


class MetadataDiscoveryAgent:
    """Discover normalized DataHub metadata and expose service methods."""

    def __init__(self, service: DataHubMetadataService | None = None) -> None:
        self.service = service or DataHubMetadataService()

    def create_metadata_discovery_agent(self) -> "MetadataDiscoveryAgent":
        """Compatibility helper for callers that expect a factory function."""
        return self

    def discover_dataset(self, urn: str):
        return self.service.get_dataset(urn)

    def discover_lineage(self, urn: str):
        return self.service.get_lineage(urn)

    def discover_owner(self, urn: str):
        return self.service.find_owner(urn)

    def discover_downstream(self, urn: str):
        return self.service.find_downstream(urn)

    def discover_overview(self, urn: str):
        dataset = self.service.get_dataset(urn)
        lineage = self.service.get_lineage(urn)
        return {
            "dataset": dataset,
            "lineage_nodes": lineage.nodes,
            "lineage_edges": lineage.edges,
            "owner": self.service.find_owner(urn),
            "downstream": self.service.find_downstream(urn),
        }


def create_metadata_discovery_agent() -> MetadataDiscoveryAgent:
    """Create the metadata discovery agent instance."""
    return MetadataDiscoveryAgent()
