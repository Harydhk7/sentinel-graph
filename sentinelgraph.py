from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from agents.planner import create_planner_agent
from tools.datahub.models import DataHubLineage, DataHubLineageEdge, DataHubLineageNode
from tools.datahub.service import DataHubMetadataService


class SampleDataHubMetadataService(DataHubMetadataService):
    """Offline DataHub service backed by examples/sample-datahub-metadata.json."""

    def __init__(self, sample_path: Path) -> None:
        super().__init__(base_url="offline://sample-datahub", graphql_url="offline://sample-datahub/graphql", rest_url="offline://sample-datahub/entities")
        self.sample = json.loads(sample_path.read_text(encoding="utf-8"))
        self.published_properties: dict[str, str] = {}

    def get_dataset(self, urn: str):  # type: ignore[override]
        dataset = self._build_dataset({"dataset": self.sample.get("dataset", {})})
        dataset.properties = {**self.published_properties, "customProperties": self.published_properties}
        return dataset

    def get_lineage(self, urn: str) -> DataHubLineage:  # type: ignore[override]
        lineage = self.sample.get("lineage", {})
        nodes = [DataHubLineageNode(urn=item.get("urn", ""), type=item.get("type", "dataset"), name=item.get("name")) for item in lineage.get("nodes", [])]
        edges = [DataHubLineageEdge(source=item.get("source", ""), target=item.get("target", "")) for item in lineage.get("edges", [])]
        return DataHubLineage(nodes=nodes, edges=edges)

    def write_custom_properties(self, urn: str, custom_properties: dict[str, str]):  # type: ignore[override]
        self.published_properties.update(custom_properties)
        return self.get_dataset(urn)


def main() -> int:
    parser = argparse.ArgumentParser(prog="sentinelgraph")
    parser.add_argument("command", choices=["analyze", "ask", "demo"], nargs="?")
    parser.add_argument("--dataset", dest="dataset_urn")
    parser.add_argument("--domain")
    parser.add_argument("--owner")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--question")
    args = parser.parse_args()

    if args.command == "demo":
        sample_path = Path(__file__).parent / "examples" / "sample-datahub-metadata.json"
        service = SampleDataHubMetadataService(sample_path)
        planner = create_planner_agent(service=service, publish=True, output_dir=args.output or "./sentinelgraph-out")
        result = planner.run(dataset_urn="urn:li:dataset:(urn:li:dataPlatform:postgres,customer_orders,PROD)")
        print(f"Demo completed with status {result['status']}")
        print(f"Dashboard: {result['reports']['dashboard']}")
        return 0

    if args.command == "ask":
        if not args.dataset_urn:
            parser.error("--dataset is required for ask")
        if not args.question:
            parser.error("--question is required for ask")
        output_dir = args.output or os.environ.get("SENTINELGRAPH_OUTPUT", "./sentinelgraph-out")
        service = DataHubMetadataService.from_env()
        planner = create_planner_agent(service=service, publish=False, output_dir=output_dir)
        result = planner.run(dataset_urn=args.dataset_urn)
        analyst = result["ai_analyst"]
        context = {key: value for key, value in result.items() if key != "ai_analyst"}
        print(analyst.answer(args.question, context))
        return 0

    if args.command != "analyze":
        parser.print_help()
        return 1

    if not args.dataset_urn:
        parser.error("--dataset is required for analyze")

    output_dir = args.output or os.environ.get("SENTINELGRAPH_OUTPUT", "./sentinelgraph-out")
    service = DataHubMetadataService.from_env()
    planner = create_planner_agent(service=service, publish=args.publish, output_dir=output_dir)
    print(f"Starting analysis against DataHub at {service.base_url}...")
    result = planner.run(dataset_urn=args.dataset_urn)
    print(f"Completed: {result['status']}")
    print(f"Risk score: {result['risk'].overall_score}")
    print(f"Report: {result['reports']['markdown']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
