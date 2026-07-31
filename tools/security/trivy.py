"""Trivy adapter for safe metadata-driven security validation."""

from __future__ import annotations


class TrivyAdapter:
    """Placeholder adapter for Trivy-based inspection."""

    def scan(self, target: str) -> dict:
        """Run a Trivy scan against a supplied target."""
        raise NotImplementedError("Trivy adapter is not implemented yet")
