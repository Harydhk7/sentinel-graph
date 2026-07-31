"""Risk scoring helpers for SentinelGraph AI.

This module will normalize findings into an enterprise risk score.
"""

from __future__ import annotations


class RiskScorer:
    """Placeholder risk scoring implementation."""

    def score(self, findings: list[dict]) -> dict:
        """Return a normalized risk score payload."""
        raise NotImplementedError("Risk scoring is not implemented yet")
