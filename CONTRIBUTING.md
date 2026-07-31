# Contributing to SentinelGraph

Thank you for helping improve SentinelGraph. Contributions should stay focused on DataHub security analysis, metadata reasoning, reporting, and safe automation.

## Getting Started

### Prerequisites

- Python 3.13+
- `pytest` and `pytest-asyncio`
- DataHub access for integration testing when your change touches live DataHub behavior

### Development Setup

```bash
git clone <repository-url>
cd sentinel-graph
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install pytest pytest-asyncio
```

On Windows PowerShell:

```powershell
cd "D:\Downloads\sentinel graph"
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install pytest pytest-asyncio
```

## Running Tests

```bash
pytest tests/test_sentinelgraph_end_to_end.py tests/test_datahub_integration.py tests/test_security_reasoning.py
```

## Pull Requests

1. Keep each PR focused on one clear concern.
2. Describe the behavior or documentation change.
3. Include the tests or manual checks you ran.
4. Avoid unrelated formatting, generated files, or copied upstream metadata.
5. Keep security-sensitive behavior conservative and clearly documented.

## Code Conventions

- Prefer small, typed Python functions with clear names.
- Keep DataHub reads and writes explicit and easy to audit.
- Use deterministic fallbacks where demos or tests must work offline.
- Avoid destructive scanning or changes outside authorized DataHub targets.

## Security

Report security issues privately according to `SECURITY.md`. Do not open a public issue for a vulnerability.