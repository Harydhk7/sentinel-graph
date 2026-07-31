"""Security assessment agent for SentinelGraph AI.

This agent performs safe security checks such as metadata assurance,
storage posture, database posture, dependency checks, and policy alignment.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from tools.datahub.models import DataHubDataset
from tools.datahub.runtime import Finding


class SecurityAssessmentAgent:
    """Evaluate datasets using safe security checks only."""

    def __init__(self) -> None:
        self.platform_rules = {
            "postgres": self._assess_postgres,
            "mysql": self._assess_mysql,
            "snowflake": self._assess_snowflake,
            "bigquery": self._assess_bigquery,
            "redshift": self._assess_redshift,
            "s3": self._assess_s3,
            "iceberg": self._assess_iceberg,
            "delta lake": self._assess_delta_lake,
            "kafka": self._assess_kafka,
            "hive": self._assess_hive,
        }

    def assess_dataset(self, dataset: DataHubDataset) -> list[Finding]:
        platform = (dataset.platform or "").lower()
        assessor = self.platform_rules.get(platform, self._assess_generic)
        findings = assessor(dataset)
        for finding in findings:
            finding.timestamp = datetime.now(timezone.utc).isoformat()
        return findings

    def assess_all(self, datasets: list[DataHubDataset]) -> list[Finding]:
        findings: list[Finding] = []
        for dataset in datasets:
            findings.extend(self.assess_dataset(dataset))
        return findings

    def _assess_generic(self, dataset: DataHubDataset) -> list[Finding]:
        findings: list[Finding] = []
        if not dataset.owners:
            findings.append(self._make_finding(dataset, "metadata", "high", 0.95, "Missing owner", "Dataset has no declared owner.", {"owners": []}, "Assign an accountable owner to the dataset."))
        if not dataset.tags:
            findings.append(self._make_finding(dataset, "metadata", "medium", 0.82, "Missing tags", "Dataset is missing business or classification tags.", {"tags": []}, "Apply relevant tags and classifications."))
        if not dataset.glossary_terms:
            findings.append(self._make_finding(dataset, "metadata", "medium", 0.78, "Missing glossary terms", "Dataset is not linked to glossary context.", {"glossary_terms": []}, "Link the dataset to glossary terms for context."))
        return findings

    def _assess_postgres(self, dataset: DataHubDataset) -> list[Finding]:
        findings = self._assess_generic(dataset)
        findings.append(self._make_finding(dataset, "database", "medium", 0.8, "TLS not verified", "No evidence of TLS enforcement was detected from metadata.", {"platform": dataset.platform}, "Ensure database connections enforce TLS."))
        return findings

    def _assess_mysql(self, dataset: DataHubDataset) -> list[Finding]:
        findings = self._assess_generic(dataset)
        findings.append(self._make_finding(dataset, "database", "medium", 0.77, "Version posture unknown", "No version metadata was captured.", {"platform": dataset.platform}, "Record the database version and monitor supportability."))
        return findings

    def _assess_snowflake(self, dataset: DataHubDataset) -> list[Finding]:
        findings = self._assess_generic(dataset)
        findings.append(self._make_finding(dataset, "infrastructure", "medium", 0.74, "Storage policy not validated", "No storage policy metadata was found.", {"platform": dataset.platform}, "Validate storage policies and access controls."))
        return findings

    def _assess_bigquery(self, dataset: DataHubDataset) -> list[Finding]:
        findings = self._assess_generic(dataset)
        findings.append(self._make_finding(dataset, "infrastructure", "medium", 0.73, "IAM review required", "No explicit IAM posture metadata was found.", {"platform": dataset.platform}, "Review IAM bindings for the hosted dataset."))
        return findings

    def _assess_redshift(self, dataset: DataHubDataset) -> list[Finding]:
        findings = self._assess_generic(dataset)
        findings.append(self._make_finding(dataset, "database", "medium", 0.75, "Access review required", "No access review evidence was collected from metadata.", {"platform": dataset.platform}, "Review access grants for the dataset."))
        return findings

    def _assess_s3(self, dataset: DataHubDataset) -> list[Finding]:
        findings = self._assess_generic(dataset)
        findings.append(self._make_finding(dataset, "storage", "high", 0.9, "Public exposure risk", "Storage metadata should be checked for public bucket exposure.", {"storage_locations": [item.location for item in dataset.storage_locations]}, "Validate public exposure and bucket policies."))
        return findings

    def _assess_iceberg(self, dataset: DataHubDataset) -> list[Finding]:
        findings = self._assess_generic(dataset)
        findings.append(self._make_finding(dataset, "storage", "medium", 0.72, "Table format governance", "Iceberg table format metadata should be validated for retention and policy coverage.", {"platform": dataset.platform}, "Ensure table format governance policies are applied."))
        return findings

    def _assess_delta_lake(self, dataset: DataHubDataset) -> list[Finding]:
        findings = self._assess_generic(dataset)
        findings.append(self._make_finding(dataset, "storage", "medium", 0.71, "Delta Lake retention check", "Delta Lake metadata should be checked for retention and access policy alignment.", {"platform": dataset.platform}, "Review retention and access policy coverage."))
        return findings

    def _assess_kafka(self, dataset: DataHubDataset) -> list[Finding]:
        findings = self._assess_generic(dataset)
        findings.append(self._make_finding(dataset, "dependencies", "medium", 0.69, "Streaming contract review", "Streaming datasets should have documented ownership and schema contracts.", {"platform": dataset.platform}, "Document schema contracts and streaming ownership."))
        return findings

    def _assess_hive(self, dataset: DataHubDataset) -> list[Finding]:
        findings = self._assess_generic(dataset)
        findings.append(self._make_finding(dataset, "metadata", "medium", 0.68, "Hive table classification", "Hive assets should have classification and ownership metadata.", {"platform": dataset.platform}, "Classify and document the Hive asset."))
        return findings

    def _make_finding(
        self,
        dataset: DataHubDataset,
        category: str,
        severity: str,
        confidence: float,
        title: str,
        description: str,
        evidence: dict[str, Any],
        recommendation: str,
    ) -> Finding:
        return Finding(
            id=f"{dataset.urn.split(':')[-1]}-{category}-{len(dataset.urn)}",
            dataset_urn=dataset.urn,
            platform=dataset.platform or "unknown",
            severity=severity,
            confidence=confidence,
            category=category,
            description=description,
            evidence=evidence,
            recommendation=recommendation,
        )


def create_security_assessment_agent() -> SecurityAssessmentAgent:
    """Create the security assessment agent instance."""
    return SecurityAssessmentAgent()
