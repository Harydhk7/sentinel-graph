from __future__ import annotations

import json
import os
from collections import OrderedDict
from typing import Any
from urllib import error, request
from urllib.parse import urlsplit, urlunsplit

from tools.datahub.models import (
    DataHubAssertion,
    DataHubDataset,
    DataHubDomain,
    DataHubGlossaryTerm,
    DataHubLineage,
    DataHubLineageEdge,
    DataHubLineageNode,
    DataHubMLAsset,
    DataHubOwner,
    DataHubPipeline,
    DataHubSchemaField,
    DataHubStorageLocation,
    DataHubTag,
)


class DataHubMetadataService:
    """Service for reading and writing DataHub metadata via GraphQL and REST."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        graphql_url: str | None = None,
        rest_url: str | None = None,
        gms_url: str | None = None,
    ) -> None:
        env_base_url = os.environ.get("DATAHUB_BASE_URL")
        env_graphql_url = os.environ.get("DATAHUB_GRAPHQL_URL")
        env_rest_url = os.environ.get("DATAHUB_REST_URL")
        env_gms_url = os.environ.get("DATAHUB_GMS_URL")

        resolved_base_url = (base_url or env_base_url or "http://localhost:8080").rstrip("/")
        self.base_url = resolved_base_url
        self.graphql_url = graphql_url or env_graphql_url or f"{self.base_url}/api/graphql"
        self.rest_url = rest_url or env_rest_url or f"{self.base_url}/api/v2/entities"
        self.gms_url = gms_url or env_gms_url or self.base_url
        self.entity_write_url = self.rest_url.rstrip("/")
        self._dataset_cache: OrderedDict[str, DataHubDataset] = OrderedDict()
        self._lineage_cache: OrderedDict[str, Any] = OrderedDict()

    @classmethod
    def from_env(cls) -> "DataHubMetadataService":
        return cls(
            base_url=os.environ.get("DATAHUB_BASE_URL"),
            graphql_url=os.environ.get("DATAHUB_GRAPHQL_URL"),
            rest_url=os.environ.get("DATAHUB_REST_URL"),
            gms_url=os.environ.get("DATAHUB_GMS_URL"),
        )

    def _post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        candidates = [url]
        parsed = urlsplit(url)
        if parsed.hostname == "host.docker.internal":
            fallback = parsed._replace(netloc=f"127.0.0.1:{parsed.port or 80}") if parsed.port else parsed._replace(netloc="127.0.0.1")
            candidates.append(urlunsplit(fallback))

        last_error: Exception | None = None
        for candidate in candidates:
            req = request.Request(candidate, data=body, headers={"Content-Type": "application/json"}, method="POST")
            try:
                with request.urlopen(req, timeout=10) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except error.URLError as exc:
                last_error = exc

        raise RuntimeError(f"Unable to reach DataHub endpoint at {url}: {last_error}") from last_error

    def _build_dataset(self, payload: dict[str, Any]) -> DataHubDataset:
        if not isinstance(payload, dict):
            payload = {}

        data_section = payload.get("data") if isinstance(payload.get("data"), dict) else {}
        dataset_payload = payload.get("dataset") or data_section.get("dataset") or payload
        if not isinstance(dataset_payload, dict):
            dataset_payload = {}

        properties = dataset_payload.get("properties") or {}
        if not isinstance(properties, dict):
            properties = {}
        custom_properties = properties.get("customProperties") or {}
        if not isinstance(custom_properties, dict):
            custom_properties = {}
        normalized_properties = {**custom_properties, "customProperties": custom_properties}

        schema_items = dataset_payload.get("schema") or []
        if not isinstance(schema_items, list):
            schema_items = []
        owners_items = dataset_payload.get("owners") or []
        if not isinstance(owners_items, list):
            owners_items = []
        tags_items = dataset_payload.get("tags") or []
        if not isinstance(tags_items, list):
            tags_items = []
        glossary_items = dataset_payload.get("glossaryTerms") or []
        if not isinstance(glossary_items, list):
            glossary_items = []
        assertion_items = dataset_payload.get("assertions") or []
        if not isinstance(assertion_items, list):
            assertion_items = []
        domain_items = dataset_payload.get("domains") or []
        if not isinstance(domain_items, list):
            domain_items = []
        storage_items = dataset_payload.get("storageLocations") or []
        if not isinstance(storage_items, list):
            storage_items = []
        pipeline_items = dataset_payload.get("pipelines") or []
        if not isinstance(pipeline_items, list):
            pipeline_items = []
        ml_items = dataset_payload.get("mlAssets") or []
        if not isinstance(ml_items, list):
            ml_items = []

        return DataHubDataset(
            urn=dataset_payload.get("urn", ""),
            name=dataset_payload.get("name", ""),
            platform=dataset_payload.get("platform", ""),
            description=dataset_payload.get("description"),
            properties=normalized_properties,
            schema=[
                DataHubSchemaField(
                    name=item.get("name", "") if isinstance(item, dict) else "",
                    type=item.get("type") if isinstance(item, dict) else None,
                    description=item.get("description") if isinstance(item, dict) else None,
                )
                for item in schema_items
                if isinstance(item, dict)
            ],
            owners=[
                DataHubOwner(name=item.get("name", ""), email=item.get("email"), urn=item.get("urn"))
                for item in owners_items
                if isinstance(item, dict)
            ],
            tags=[DataHubTag(name=item.get("name", ""), urn=item.get("urn")) for item in tags_items if isinstance(item, dict)],
            glossary_terms=[
                DataHubGlossaryTerm(name=item.get("name", ""), urn=item.get("urn"))
                for item in glossary_items
                if isinstance(item, dict)
            ],
            assertions=[DataHubAssertion(name=item.get("name", ""), urn=item.get("urn")) for item in assertion_items if isinstance(item, dict)],
            domains=[DataHubDomain(name=item.get("name", ""), urn=item.get("urn")) for item in domain_items if isinstance(item, dict)],
            storage_locations=[
                DataHubStorageLocation(location=item.get("location", ""), urn=item.get("urn"))
                for item in storage_items
                if isinstance(item, dict)
            ],
            pipelines=[DataHubPipeline(name=item.get("name", ""), urn=item.get("urn")) for item in pipeline_items if isinstance(item, dict)],
            ml_assets=[DataHubMLAsset(name=item.get("name", ""), urn=item.get("urn")) for item in ml_items if isinstance(item, dict)],
        )

    def get_dataset(self, urn: str) -> DataHubDataset:
        cached = self._dataset_cache.get(urn)
        if cached is not None:
            return cached

        payload = self._post_json(
            self.graphql_url,
            {
                "query": f"""
                query Dataset($urn: String!) {{
                  dataset(urn: $urn) {{
                    urn
                    name
                    platform
                    description
                    properties {{
                      customProperties
                    }}
                    schema {{
                      name
                      type
                      description
                    }}
                    owners {{
                      name
                      email
                      urn
                    }}
                    tags {{
                      name
                      urn
                    }}
                    glossaryTerms {{
                      name
                      urn
                    }}
                    assertions {{
                      name
                      urn
                    }}
                    domains {{
                      name
                      urn
                    }}
                    storageLocations {{
                      location
                      urn
                    }}
                    pipelines {{
                      name
                      urn
                    }}
                    mlAssets {{
                      name
                      urn
                    }}
                  }}
                }}
                """,
                "variables": {"urn": urn},
            },
        )
        dataset = self._build_dataset(payload.get("data", {}))
        self._dataset_cache[urn] = dataset
        self._dataset_cache.move_to_end(urn)
        return dataset

    def get_lineage(self, urn: str) -> DataHubLineage:
        cached = self._lineage_cache.get(urn)
        if cached is not None:
            return cached

        payload = self._post_json(
            self.graphql_url,
            {
                "query": f"""
                query Lineage($urn: String!) {{
                  lineage(urn: $urn) {{
                    nodes {{
                      urn
                      type
                      name
                    }}
                    edges {{
                      source
                      target
                    }}
                  }}
                }}
                """,
                "variables": {"urn": urn},
            },
        )
        lineage_payload = payload.get("data", {}).get("lineage", {}) if isinstance(payload.get("data"), dict) else {}
        if not isinstance(lineage_payload, dict):
            lineage_payload = {}
        nodes_payload = lineage_payload.get("nodes") or []
        if not isinstance(nodes_payload, list):
            nodes_payload = []
        edges_payload = lineage_payload.get("edges") or []
        if not isinstance(edges_payload, list):
            edges_payload = []
        nodes = [
            DataHubLineageNode(urn=item.get("urn", ""), type=item.get("type", "dataset"), name=item.get("name"))
            for item in nodes_payload
            if isinstance(item, dict)
        ]
        edges = [DataHubLineageEdge(source=item.get("source", ""), target=item.get("target", "")) for item in edges_payload if isinstance(item, dict)]
        result = DataHubLineage(nodes=nodes, edges=edges)
        self._lineage_cache[urn] = result
        self._lineage_cache.move_to_end(urn)
        return result

    def find_owner(self, urn: str) -> DataHubOwner | None:
        dataset = self.get_dataset(urn)
        return dataset.owners[0] if dataset.owners else None

    def find_downstream(self, urn: str) -> list[DataHubLineageNode]:
        lineage = self.get_lineage(urn)
        downstream: list[DataHubLineageNode] = []
        for edge in lineage.edges:
            if edge.source == urn:
                downstream.extend(node for node in lineage.nodes if node.urn == edge.target)
        return downstream

    def write_custom_properties(self, urn: str, custom_properties: dict[str, str]) -> DataHubDataset:
        dataset = self.get_dataset(urn)
        existing_properties = dict(dataset.properties.get("customProperties", {}))
        existing_properties.update(custom_properties)
        dataset.properties = {**existing_properties, "customProperties": existing_properties}
        self._dataset_cache[urn] = dataset

        write_url = self.entity_write_url
        if not write_url.endswith("/entities") and not write_url.endswith("/entities/"):
            write_url = write_url.rstrip("/") + "/entities"

        try:
            response = self._post_json(
                write_url.rstrip("/") + f"/{urn}",
                {
                    "entity": {
                        "urn": urn,
                        "properties": {"customProperties": existing_properties},
                    }
                },
            )
        except RuntimeError as exc:
            self._dataset_cache[urn] = dataset
            return dataset

        if response.get("status") != "ok":
            raise RuntimeError(f"DataHub write failed: {response}")
        return dataset

    def write_custom_property(self, urn: str, key: str, value: str) -> DataHubDataset:
        return self.write_custom_properties(urn, {key: value})

    def enumerate_datasets(self) -> list[DataHubDataset]:
        return [self.get_dataset(urn) for urn in self._dataset_cache if urn]
