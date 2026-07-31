# SentinelGraph

SentinelGraph is an autonomous data-security agent for DataHub. It inspects metadata, lineage, ownership, tags, domains, assertions, and schema signals; turns them into explainable risk findings; and produces reports, dashboard output, and optional DataHub custom-property updates.

## What It Does

- Discovers DataHub dataset metadata, owners, schema, tags, domains, assertions, pipelines, ML assets, and lineage.
- Assesses security posture without destructive scanning.
- Computes downstream impact and blast radius from lineage.
- Correlates findings into explainable risk scores and threat levels.
- Generates prioritized remediation recommendations.
- Adds an `aiSummary` through the AI Analyst component, with a deterministic offline fallback for demos.
- Answers grounded questions such as "What's the riskiest dataset in the finance domain?" and "Show me all datasets with PII exposure."
- Produces executive reports and a lightweight local dashboard.

## Why It Is Agentic

SentinelGraph is built as a coordinated workflow rather than a one-off script:

- `PlannerAgent` orchestrates the full loop from DataHub observation to outputs.
- `MetadataDiscoveryAgent` reads DataHub context.
- `SecurityAssessmentAgent` reasons over metadata posture and platform risk signals.
- `ImpactAnalysisAgent` traverses lineage to estimate downstream impact.
- `RiskCorrelationEngine` combines findings, confidence, and lineage impact.
- `RecommendationAgent` converts findings into remediation actions.
- `AIAnalystAgent` generates summaries and answers grounded questions.
- `DataHubPublisherAgent` writes results back to DataHub when `--publish` is enabled.

Together these pieces create an observe, reason, decide, act, and report cycle for DataHub security operations.

## Quick Start

### Windows PowerShell

```powershell
cd "D:\Downloads\sentinel graph"
py -3 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install pytest pytest-asyncio
```

Run the offline demo:

```powershell
python sentinelgraph.py demo --output examples\demo-output
start examples\demo-output\dashboard\index.html
```

Run the local test suite:

```powershell
pytest tests\test_sentinelgraph_end_to_end.py tests\test_datahub_integration.py tests\test_security_reasoning.py
```

Analyze a real DataHub dataset:

```powershell
$env:DATAHUB_BASE_URL="http://localhost:9002"
$env:DATAHUB_GRAPHQL_URL="http://localhost:9002/api/graphql"
$env:DATAHUB_REST_URL="http://localhost:9002/api/v2/entities"
$env:SENTINELGRAPH_LLM_PROVIDER="local"

python sentinelgraph.py analyze --dataset "urn:li:dataset:(urn:li:dataPlatform:postgres,customers,PROD)" --output sentinelgraph-out
start sentinelgraph-out\dashboard\index.html
```

Publish results back to DataHub:

```powershell
python sentinelgraph.py analyze --dataset "urn:li:dataset:(urn:li:dataPlatform:postgres,customers,PROD)" --publish --output sentinelgraph-out
```

Ask the AI Analyst:

```powershell
python sentinelgraph.py ask --dataset "urn:li:dataset:(urn:li:dataPlatform:postgres,customers,PROD)" --question "Show me all datasets with PII exposure."
```

### Linux or macOS

```bash
cd /path/to/sentinel-graph
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install pytest pytest-asyncio
```

Run the offline demo:

```bash
python sentinelgraph.py demo --output examples/demo-output
```

Open the dashboard:

```bash
xdg-open examples/demo-output/dashboard/index.html
```

On macOS:

```bash
open examples/demo-output/dashboard/index.html
```

Run tests:

```bash
pytest tests/test_sentinelgraph_end_to_end.py tests/test_datahub_integration.py tests/test_security_reasoning.py
```

Analyze a real DataHub dataset:

```bash
export DATAHUB_BASE_URL=http://localhost:9002
export DATAHUB_GRAPHQL_URL=http://localhost:9002/api/graphql
export DATAHUB_REST_URL=http://localhost:9002/api/v2/entities
export SENTINELGRAPH_LLM_PROVIDER=local

python sentinelgraph.py analyze --dataset 'urn:li:dataset:(urn:li:dataPlatform:postgres,customers,PROD)' --output sentinelgraph-out
```

Publish results back to DataHub:

```bash
python sentinelgraph.py analyze --dataset 'urn:li:dataset:(urn:li:dataPlatform:postgres,customers,PROD)' --publish --output sentinelgraph-out
```

Ask the AI Analyst:

```bash
python sentinelgraph.py ask --dataset 'urn:li:dataset:(urn:li:dataPlatform:postgres,customers,PROD)' --question 'Show me all datasets with PII exposure.'
```

Replace the sample dataset URN with a dataset URN from your DataHub UI.

## Optional LLM Summary

SentinelGraph uses a deterministic local AI Analyst by default so demos work offline. To enable an OpenAI-compatible model for richer summaries:

```bash
export SENTINELGRAPH_LLM_PROVIDER=openai
export SENTINELGRAPH_LLM_MODEL=gpt-4o-mini
export OPENAI_API_KEY=<your key>
```

## Architecture

SentinelGraph centers on a planner that connects to DataHub, builds an in-memory knowledge graph, and runs the analysis workflow:

1. Metadata discovery
2. Security assessment
3. Impact analysis
4. Risk correlation
5. Recommendation generation
6. AI Analyst summarization and Q&A
7. Optional publishing back to DataHub
8. Report and dashboard generation
9. Execution history capture

## DataHub Integration

SentinelGraph uses two DataHub integration paths:

- GraphQL reads for metadata, schema, owners, tags, domains, assertions, pipelines, ML assets, and lineage.
- REST entity writes for persisting risk metadata into dataset `customProperties`.

Published custom properties include:

- `securityScore`
- `threatLevel`
- `riskTrend`
- `aiSummary`
- `assessmentTimestamp`
- `recommendations`
- `relatedFindings`
- `riskCategory`
- `remediationStatus`
- `lastScanVersion`

## Demo Assets

The `examples/` folder contains artifacts that work without a running DataHub instance:

- `sample-datahub-metadata.json`: representative DataHub metadata, ownership, tags, assertions, domain, pipeline, ML asset, and lineage payloads.
- `precomputed-sentinelgraph-report.json`: a precomputed output with `aiSummary`, findings, lineage impact, recommendations, and custom-property writes.

Running `python sentinelgraph.py demo --output examples/demo-output` generates `examples/demo-output/dashboard/index.html` with org-risk metrics, top findings, lineage blast radius, recommendations, and clickable AI Analyst prompts.

## Docker

Use `docker-compose.sentinelgraph.yml` or `Dockerfile.sentinelgraph` for SentinelGraph-specific container workflows. The primary workflow remains the standalone Python CLI using DataHub as the source of truth.

## Environment

Use `.env.example` for production configuration. Set DataHub URLs and optional runtime flags before running real analysis or publishing results.

## Command Reference

```bash
python sentinelgraph.py demo
python sentinelgraph.py analyze --dataset <dataset-urn> --output sentinelgraph-out
python sentinelgraph.py analyze --dataset <dataset-urn> --publish --output sentinelgraph-out
python sentinelgraph.py ask --dataset <dataset-urn> --question "What's the riskiest dataset in the finance domain?"
```

## Roadmap

- Add hosted demo deployment instructions and a short demo video link.
- Support multi-dataset domain scans.
- Add historical trend analysis and time-series risk scoring.
- Improve dashboard filtering and lineage graph interactivity.

## Disclaimer

Use SentinelGraph only with explicit authorization. This tool is intended for authorized security analysis in data environments and should not be run against systems without permission.
