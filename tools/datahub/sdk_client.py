"""DataHub Python SDK adapter.

This module will wrap DataHub SDK operations for metadata retrieval and
enrichment.
"""

from __future__ import annotations


class DataHubSDKClient:
    """Minimal Python SDK client placeholder for DataHub."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}

    def get_entity(self, urn: str) -> dict:
        """Retrieve a single DataHub entity."""
        raise NotImplementedError("DataHub SDK client is not implemented yet")
