from __future__ import annotations

import contextlib
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from agents.planner import create_planner_agent
from tools.datahub.service import DataHubMetadataService


class SentinelGraphStubHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length else b"{}"
        body = json.loads(raw_body.decode("utf-8"))

        if self.path == "/api/graphql":
            query = body.get("query", "")
            if "dataset(" in query:
                custom_properties = self.server.state.get("custom_properties", {})
                payload = {
                    "data": {
                        "dataset": {
                            "urn": "urn:li:dataset:(urn:li:dataPlatform:postgres,customer_orders,PROD)",
                            "name": "customer_orders",
                            "platform": "postgres",
                            "description": "Customer order facts",
                            "properties": {"customProperties": custom_properties},
                            "schema": [{"name": "order_id", "type": "string"}],
                            "owners": [{"name": "Data Platform", "email": "platform@example.com"}],
                            "tags": [{"name": "pii"}],
                            "glossaryTerms": [{"name": "Customer Data"}],
                            "assertions": [{"name": "Not Null"}],
                            "domains": [{"name": "Finance"}],
                            "storageLocations": [{"location": "s3://warehouse/orders"}],
                            "pipelines": [{"name": "orders_etl"}],
                            "mlAssets": [{"name": "orders_score"}],
                        }
                    }
                }
            elif "lineage" in query:
                payload = {
                    "data": {
                        "lineage": {
                            "nodes": [
                                {"urn": "urn:li:dataset:(urn:li:dataPlatform:postgres,customer_orders,PROD)", "type": "dataset"},
                                {"urn": "urn:li:dataset:(urn:li:dataPlatform:kafka,orders_topic,PROD)", "type": "dataset"},
                            ],
                            "edges": [
                                {
                                    "source": "urn:li:dataset:(urn:li:dataPlatform:postgres,customer_orders,PROD)",
                                    "target": "urn:li:dataset:(urn:li:dataPlatform:kafka,orders_topic,PROD)",
                                }
                            ],
                        }
                    }
                }
            else:
                payload = {"data": {}}
        elif self.path.startswith("/api/v2/entities/"):
            entity_urn = self.path.rsplit("/", 1)[-1]
            self.server.state.setdefault("custom_properties", {})[entity_urn] = body.get("entity", {}).get("properties", {}).get("customProperties", {})
            payload = {"status": "ok"}
        else:
            payload = {"error": "not found"}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


@contextlib.contextmanager
def running_sentinelgraph_stub_server() -> Any:
    server = ThreadingHTTPServer(("127.0.0.1", 0), SentinelGraphStubHandler)
    server.state = {"custom_properties": {}}
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_sentinelgraph_analyze_pipeline_publishes_and_reports(tmp_path: Path) -> None:
    with running_sentinelgraph_stub_server() as server:
        service = DataHubMetadataService(
            base_url=f"http://127.0.0.1:{server.server_address[1]}",
            graphql_url=f"http://127.0.0.1:{server.server_address[1]}/api/graphql",
            rest_url=f"http://127.0.0.1:{server.server_address[1]}/api/v2/entities",
        )
        planner = create_planner_agent(service=service, publish=True, output_dir=str(tmp_path))
        result = planner.run(dataset_urn="urn:li:dataset:(urn:li:dataPlatform:postgres,customer_orders,PROD)")

        assert result["status"] == "completed"
        assert result["risk"].overall_score >= 0
        assert result["publishing"]["published"] is True

        dataset = service.get_dataset("urn:li:dataset:(urn:li:dataPlatform:postgres,customer_orders,PROD)")
        custom_properties = dataset.properties.get("customProperties", {})
        assert custom_properties["securityScore"]
        assert custom_properties["threatLevel"]
        assert custom_properties["lastScanVersion"]

        report_path = tmp_path / "reports" / "executive.md"
        dashboard_path = tmp_path / "dashboard" / "index.html"
        assert report_path.exists()
        assert dashboard_path.exists()
