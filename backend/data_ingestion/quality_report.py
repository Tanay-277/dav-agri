from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class QualityReport(BaseModel):
    """Data quality report for a preprocessing run."""

    source_file: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    total_rows: int = 0
    valid_rows: int = 0
    invalid_rows: int = 0
    duplicate_rows: int = 0
    outlier_rows: int = 0
    missing_value_counts: dict[str, int] = Field(default_factory=dict)
    invalid_value_counts: dict[str, int] = Field(default_factory=dict)
    outlier_counts: dict[str, int] = Field(default_factory=dict)
    schema_validation_errors: list[str] = Field(default_factory=list)
    processing_log: list[str] = Field(default_factory=list)
    normalized_sample: list[dict[str, Any]] = Field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [
            f"# Data Quality Report: {self.source_file}",
            f"Generated: {self.generated_at.isoformat()}",
            "",
            "## Summary",
            f"- **Total rows:** {self.total_rows}",
            f"- **Valid rows:** {self.valid_rows}",
            f"- **Invalid rows:** {self.invalid_rows}",
            f"- **Duplicate rows:** {self.duplicate_rows}",
            f"- **Outlier rows:** {self.outlier_rows}",
            "",
            "## Missing Values",
        ]
        for col, count in self.missing_value_counts.items():
            lines.append(f"- {col}: {count}")
        lines.extend(
            [
                "",
                "## Invalid Values",
            ]
        )
        for col, count in self.invalid_value_counts.items():
            lines.append(f"- {col}: {count}")
        lines.extend(
            [
                "",
                "## Outliers",
            ]
        )
        for col, count in self.outlier_counts.items():
            lines.append(f"- {col}: {count}")
        lines.extend(
            [
                "",
                "## Processing Log",
            ]
        )
        for entry in self.processing_log:
            lines.append(f"- {entry}")
        lines.extend(
            [
                "",
                "## Normalized Sample",
                "```json",
                json.dumps(self.normalized_sample[:3], indent=2, default=str),
                "```",
            ]
        )
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps(self.model_dump(), indent=2, default=str)
