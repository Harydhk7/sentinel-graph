"""Misconfiguration detection adapter for SentinelGraph AI."""

from __future__ import annotations


class MisconfigurationAdapter:
    """Placeholder adapter for cloud or infrastructure misconfiguration checks."""

    def evaluate(self, metadata: dict) -> list[dict]:
        """Evaluate safe misconfiguration signals from metadata."""
        raise NotImplementedError("Misconfiguration adapter is not implemented yet")
