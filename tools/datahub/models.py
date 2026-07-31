from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class DataHubOwner:
    name: str
    email: str | None = None
    urn: str | None = None


@dataclass(slots=True)
class DataHubTag:
    name: str
    urn: str | None = None


@dataclass(slots=True)
class DataHubGlossaryTerm:
    name: str
    urn: str | None = None


@dataclass(slots=True)
class DataHubAssertion:
    name: str
    urn: str | None = None


@dataclass(slots=True)
class DataHubDomain:
    name: str
    urn: str | None = None


@dataclass(slots=True)
class DataHubStorageLocation:
    location: str
    urn: str | None = None


@dataclass(slots=True)
class DataHubPipeline:
    name: str
    urn: str | None = None


@dataclass(slots=True)
class DataHubMLAsset:
    name: str
    urn: str | None = None


@dataclass(slots=True)
class DataHubSchemaField:
    name: str
    type: str | None = None
    description: str | None = None


@dataclass(slots=True)
class DataHubLineageNode:
    urn: str
    type: str
    name: str | None = None


@dataclass(slots=True)
class DataHubLineageEdge:
    source: str
    target: str


@dataclass(slots=True)
class DataHubLineage:
    nodes: list[DataHubLineageNode] = field(default_factory=list)
    edges: list[DataHubLineageEdge] = field(default_factory=list)


@dataclass(slots=True)
class DataHubDataset:
    urn: str
    name: str
    platform: str | None = None
    description: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)
    schema: list[DataHubSchemaField] = field(default_factory=list)
    owners: list[DataHubOwner] = field(default_factory=list)
    tags: list[DataHubTag] = field(default_factory=list)
    glossary_terms: list[DataHubGlossaryTerm] = field(default_factory=list)
    assertions: list[DataHubAssertion] = field(default_factory=list)
    domains: list[DataHubDomain] = field(default_factory=list)
    storage_locations: list[DataHubStorageLocation] = field(default_factory=list)
    pipelines: list[DataHubPipeline] = field(default_factory=list)
    ml_assets: list[DataHubMLAsset] = field(default_factory=list)
