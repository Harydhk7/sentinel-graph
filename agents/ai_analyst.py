"""AI analyst agent for SentinelGraph.

The analyst turns structured DataHub security findings into natural language
and answers grounded questions from the same analysis context. It can call an
OpenAI-compatible chat API when configured, but always has deterministic local
behavior for demos, tests, and offline use.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, is_dataclass
from typing import Any
from urllib import error, request


class AIAnalystAgent:
    """Generate summaries and answer questions from SentinelGraph context."""

    def __init__(self, *, provider: str | None = None, api_key: str | None = None, model: str | None = None, endpoint: str | None = None) -> None:
        self.provider = (provider or os.environ.get("SENTINELGRAPH_LLM_PROVIDER") or "local").lower()
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("SENTINELGRAPH_LLM_API_KEY")
        self.model = model or os.environ.get("SENTINELGRAPH_LLM_MODEL") or "gpt-4o-mini"
        self.endpoint = endpoint or os.environ.get("SENTINELGRAPH_LLM_ENDPOINT") or "https://api.openai.com/v1/chat/completions"

    def summarize(self, context: dict[str, Any]) -> str:
        """Create an aiSummary for DataHub customProperties and reports."""
        local_summary = self._local_summary(context)
        if self.provider in {"openai", "openai-compatible"} and self.api_key:
            return self._chat_completion(
                system="You are SentinelGraph's AI Analyst. Write concise, evidence-grounded DataHub security summaries.",
                user=f"Summarize this SentinelGraph analysis in 3 sentences:\n{self._safe_json(context)}",
                fallback=local_summary,
            )
        return local_summary

    def answer(self, question: str, context: dict[str, Any]) -> str:
        """Answer a user question using only the current analysis context."""
        local_answer = self._local_answer(question, context)
        if self.provider in {"openai", "openai-compatible"} and self.api_key:
            return self._chat_completion(
                system="Answer as SentinelGraph's AI Analyst. Use only the supplied DataHub analysis context.",
                user=f"Question: {question}\n\nContext:\n{self._safe_json(context)}",
                fallback=local_answer,
            )
        return local_answer

    def _chat_completion(self, *, system: str, user: str, fallback: str) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0.2,
            "max_tokens": 260,
        }
        req = request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (error.URLError, TimeoutError, ValueError, KeyError):
            return fallback
        return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip() or fallback

    def _local_summary(self, context: dict[str, Any]) -> str:
        dataset = context.get("dataset")
        findings = context.get("findings", [])
        risk = context.get("risk")
        impact = context.get("impact")
        recommendations = context.get("recommendations", [])
        dataset_name = getattr(dataset, "name", "the selected dataset")
        domain = ", ".join(getattr(item, "name", "") for item in getattr(dataset, "domains", []) if getattr(item, "name", "")) or "unassigned domain"
        top_finding = findings[0].description if findings else "no active security finding"
        next_step = recommendations[0].technical_summary if recommendations else "continue monitoring DataHub metadata and lineage."
        return (
            f"SentinelGraph is an AI agent that autonomously monitors DataHub for security risks. "
            f"For {dataset_name} in {domain}, it assigned a {getattr(risk, 'threat_level', 'unknown')} threat level "
            f"with score {getattr(risk, 'overall_score', 'n/a')} after reasoning over {len(findings)} finding(s), "
            f"including {top_finding}. Its lineage analysis found blast radius {getattr(impact, 'blast_radius', 0)}; "
            f"recommended action: {next_step}"
        )

    def _local_answer(self, question: str, context: dict[str, Any]) -> str:
        q = question.lower()
        dataset = context.get("dataset")
        findings = context.get("findings", [])
        risk = context.get("risk")
        impact = context.get("impact")
        recommendations = context.get("recommendations", [])
        if "riskiest" in q:
            return f"{getattr(dataset, 'name', 'The selected dataset')} is the riskiest dataset in this run with score {getattr(risk, 'overall_score', 'n/a')} and threat level {getattr(risk, 'threat_level', 'unknown')}."
        if "pii" in q:
            pii_findings = [finding for finding in findings if "pii" in f"{finding.category} {finding.description} {finding.evidence}".lower()]
            if pii_findings:
                return f"{getattr(dataset, 'name', 'The selected dataset')} has PII exposure signals: " + "; ".join(f.description for f in pii_findings)
            return "No PII exposure findings were identified in this analysis context."
        if "lineage" in q or "blast" in q:
            return f"Blast radius is {getattr(impact, 'blast_radius', 0)} with downstream assets: {', '.join(getattr(impact, 'affected_downstream_assets', []) or getattr(impact, 'affected_datasets', [])) or 'none'}."
        if "recommend" in q or "fix" in q:
            return "Recommended actions: " + "; ".join(rec.technical_summary for rec in recommendations) if recommendations else "No remediation recommendations were generated."
        return self._local_summary(context)

    def _safe_json(self, context: dict[str, Any]) -> str:
        def convert(value: Any) -> Any:
            if is_dataclass(value):
                return asdict(value)
            if isinstance(value, list):
                return [convert(item) for item in value]
            if isinstance(value, dict):
                return {key: convert(item) for key, item in value.items()}
            return value

        return json.dumps(convert(context), indent=2)[:12000]


def create_ai_analyst_agent() -> AIAnalystAgent:
    """Create the AI analyst agent."""
    return AIAnalystAgent()
