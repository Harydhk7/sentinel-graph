"""Secret scanning adapter for safe metadata and repository inspection."""

from __future__ import annotations


class SecretScannerAdapter:
    """Placeholder adapter for secret scanning."""

    def scan(self, content: str | None = None) -> list[dict]:
        """Scan content or metadata for secret-like patterns."""
        raise NotImplementedError("Secret scanner adapter is not implemented yet")
