from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from core.logging import get_logger
from data_ingestion.preprocessor import DataPreprocessor
from data_ingestion.quality_report import QualityReport

logger = get_logger(__name__)


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent.parent
    dataset_path = project_root / "dataset" / "agriculture.csv"
    output_dir = project_root / "dataset" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not dataset_path.exists():
        logger.error("Dataset not found at %s", dataset_path)
        return 1

    logger.info("Loading dataset from %s", dataset_path)
    raw_df = pd.read_csv(dataset_path)
    logger.info("Loaded %d rows", len(raw_df))

    proc = DataPreprocessor(source_name=dataset_path.name)
    clean_df = proc.run(raw_df)

    csv_path = output_dir / "agriculture_normalized.csv"
    clean_df.to_csv(csv_path, index=False)
    logger.info("Saved normalized CSV to %s", csv_path)

    records = proc.to_normalized_records(clean_df)
    report = QualityReport(
        source_file=dataset_path.name,
        total_rows=len(clean_df),
        valid_rows=int((~clean_df["is_invalid"]).sum()),
        invalid_rows=int(clean_df["is_invalid"].sum()),
        duplicate_rows=int(clean_df["is_duplicate"].sum()),
        outlier_rows=int(clean_df["is_outlier"].sum()),
        missing_value_counts=clean_df.isna().sum().to_dict(),
        invalid_value_counts=_count_flags(clean_df, "is_invalid"),
        outlier_counts=_count_flags(clean_df, "is_outlier"),
        processing_log=proc.quality_log,
        normalized_sample=[r.model_dump() for r in records[:3]],
    )

    report_path = output_dir / "quality_report.md"
    report_path.write_text(report.to_markdown())
    logger.info("Saved quality report to %s", report_path)

    json_path = output_dir / "quality_report.json"
    json_path.write_text(report.to_json())
    logger.info("Saved quality report JSON to %s", json_path)

    print(f"Preprocessing complete. Output: {csv_path}")
    print(f"Quality report: {report_path}")
    return 0


def _count_flags(df: pd.DataFrame, flag_col: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for idx, row in df.iterrows():
        if row.get(flag_col):
            for flag in row.get("validation_flags", []):
                field = flag.split(":")[0]
                counts[field] = counts.get(field, 0) + 1
    return counts


if __name__ == "__main__":
    sys.exit(main())
