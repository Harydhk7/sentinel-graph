import contextlib
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from tools.datahub.service import DataHubMetadataService


class DataHubStubHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length else b"{}"
        body = json.loads(raw_body.decode("utf-8"))

        if self.path == "/api/graphql":
            query = body.get("query", "")
            if "dataset(" in query:
                payload = {
                    "data": {
                        "dataset": {
                            "urn": "urn:li:dataset:(urn:li:dataPlatform:postgres,customer_orders,PROD)",
                            "name": "customer_orders",
                            "platform": "postgres",
                            "description": "Customer order facts",
                            "properties": {"customProperties": {"lastAnalysis": "2026-07-25T00:00:00Z"}},
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
def running_stub_server() -> Any:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DataHubStubHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_datahub_service_discovers_and_writes_metadata() -> None:
    with running_stub_server() as server:
        service = DataHubMetadataService(
            base_url=f"http://127.0.0.1:{server.server_address[1]}",
            graphql_url=f"http://127.0.0.1:{server.server_address[1]}/api/graphql",
            rest_url=f"http://127.0.0.1:{server.server_address[1]}/api/v2/entities",
        )

        dataset = service.get_dataset("urn:li:dataset:(urn:li:dataPlatform:postgres,customer_orders,PROD)")
        assert dataset.name == "customer_orders"
        assert dataset.owners[0].name == "Data Platform"
        assert dataset.domains[0].name == "Finance"

        lineage = service.get_lineage("urn:li:dataset:(urn:li:dataPlatform:postgres,customer_orders,PROD)")
        assert lineage.nodes[0].urn == dataset.urn
        assert lineage.edges[0].source == dataset.urn

        owner = service.find_owner(dataset.urn)
        assert owner is not None
        assert owner.name == "Data Platform"

        downstream = service.find_downstream(dataset.urn)
        assert downstream[0].urn.endswith("orders_topic,PROD)")

        updated = service.write_custom_property(
            dataset.urn,
            "lastAnalysis",
            "2026-07-25T01:00:00Z",
        )
        assert updated.properties["lastAnalysis"] == "2026-07-25T01:00:00Z"

        cached_dataset = service.get_dataset(dataset.urn)
        assert cached_dataset.properties["lastAnalysis"] == "2026-07-25T01:00:00Z"
