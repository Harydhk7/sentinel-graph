"""DataHub GraphQL client adapter.

This module will provide GraphQL access to DataHub metadata.
"""

from __future__ import annotations


class DataHubGraphClient:
    """Minimal GraphQL client placeholder for DataHub access."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url

    def fetch_metadata(self, query: str | None = None) -> dict:
        """Fetch metadata from DataHub."""
        raise NotImplementedError("DataHub GraphQL client is not implemented yet")
