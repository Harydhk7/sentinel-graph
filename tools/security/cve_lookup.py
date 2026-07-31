"""CVE and OSV lookup adapter for safe vulnerability context."""

from __future__ import annotations


class CVELookupAdapter:
    """Placeholder adapter for CVE and OSV lookups."""

    def lookup(self, package: str, version: str | None = None) -> dict:
        """Look up vulnerability data for an artifact."""
        raise NotImplementedError("CVE lookup adapter is not implemented yet")
