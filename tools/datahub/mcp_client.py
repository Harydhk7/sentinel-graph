"""DataHub MCP client adapter.

This module connects to a DataHub MCP server and exposes safe metadata
retrieval operations.
"""

from __future__ import annotations

import json
from urllib import request


class DataHubMCPClient:
    """Minimal MCP client for DataHub access."""

    def __init__(self, endpoint: str | None = None):
        self.endpoint = endpoint

    def list_tools(self) -> list[str]:
        """List tools exposed by the MCP server."""
        if not self.endpoint:
            return []
        payload = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}
        response = self._post_json(payload)
        tools = response.get("result", {}).get("tools", [])
        return [tool.get("name", "") for tool in tools if isinstance(tool, dict)]

    def query(self, method: str, params: dict | None = None) -> dict:
        """Send a JSON-RPC request to the MCP server."""
        if not self.endpoint:
            return {}
        payload = {"jsonrpc": "2.0", "method": method, "params": params or {}, "id": 1}
        return self._post_json(payload)

    def _post_json(self, payload: dict) -> dict:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(self.endpoint, data=body, headers={"Content-Type": "application/json"}, method="POST")
        with request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
