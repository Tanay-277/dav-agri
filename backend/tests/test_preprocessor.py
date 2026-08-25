from __future__ import annotations

import pandas as pd
import pytest

from data_ingestion.preprocessor import DataPreprocessor
from data_ingestion.quality_report import QualityReport


class TestDataPreprocessor:
    @pytest.fixture
    def raw_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "date": ["2022-09-08", "2022-09-08", "2023-01-15", "not-a-date"],
                "state": ["Maharashtra", "Maharashtra", "Punjab", "Karnataka"],
                "district": ["Pune", "Pune", "Ludhiana", "Bangalore"],
                "crop": ["Maize", "Maize", "Wheat", "Rice"],
                "rainfall": [117.9, 117.9, 70.4, -5.0],
                "temperature": [27.4, 27.4, 33.9, 28.0],
                "humidity": [77.1, 77.1, 43.8, 60.0],
                "soil_moisture": [50.0, 50.0, 23.0, 40.0],
                "yield": [320.0, 320.0, 401.0, 350.0],
                "production": [305.0, 305.0, 337.0, 400.0],
                "area": [63.4, 63.4, 80.3, 100.0],
                "fertilizer": [117.2, 117.2, 85.3, 90.0],
                "irrigation": [60.3, 60.3, 49.8, 55.0],
            }
        )

    def test_pipeline_produces_expected_columns(self, raw_df: pd.DataFrame) -> None:
        proc = DataPreprocessor()
        out = proc.run(raw_df)
        expected = {
            "record_date",
            "timestamp",
            "state",
            "district",
            "crop",
            "rainfall_mm",
            "temperature_c",
            "humidity_pct",
            "soil_moisture_pct",
            "yield_kg_per_ha",
            "production_tonnes",
            "area_ha",
            "fertilizer_kg",
            "irrigation_pct",
            "location_id",
            "latitude",
            "longitude",
            "data_classification",
            "source",
            "source_row_id",
            "is_duplicate",
            "is_outlier",
            "is_invalid",
            "validation_flags",
        }
        assert expected.issubset(set(out.columns))

    def test_deduplication_flags_duplicates(self, raw_df: pd.DataFrame) -> None:
        proc = DataPreprocessor()
        out = proc.run(raw_df)
        assert out["is_duplicate"].sum() == 1

    def test_invalid_values_flagged(self, raw_df: pd.DataFrame) -> None:
        proc = DataPreprocessor()
        out = proc.run(raw_df)
        assert out["is_invalid"].sum() >= 1

    def test_location_normalization(self, raw_df: pd.DataFrame) -> None:
        proc = DataPreprocessor()
        out = proc.run(raw_df)
        assert "maharashtra_pune" in out["location_id"].values
        assert "punjab_ludhiana" in out["location_id"].values

    def test_timestamp_normalization(self, raw_df: pd.DataFrame) -> None:
        proc = DataPreprocessor()
        out = proc.run(raw_df)
        assert isinstance(out["timestamp"].iloc[0], pd.Timestamp)

    def test_source_tracking(self, raw_df: pd.DataFrame) -> None:
        proc = DataPreprocessor(source_name="test.csv")
        out = proc.run(raw_df)
        assert (out["source"] == "test.csv").all()

    def test_data_classification(self, raw_df: pd.DataFrame) -> None:
        proc = DataPreprocessor()
        out = proc.run(raw_df)
        assert "historical" in out["data_classification"].values

    def test_quality_report_generation(self, raw_df: pd.DataFrame) -> None:
        proc = DataPreprocessor()
        out = proc.run(raw_df)
        records = proc.to_normalized_records(out)
        report = QualityReport(
            source_file="test.csv",
            total_rows=len(out),
            valid_rows=int((~out["is_invalid"]).sum()),
            invalid_rows=int(out["is_invalid"].sum()),
            duplicate_rows=int(out["is_duplicate"].sum()),
            outlier_rows=int(out["is_outlier"].sum()),
            missing_value_counts=out.isna().sum().to_dict(),
            processing_log=proc.quality_log,
            normalized_sample=[r.model_dump() for r in records[:2]],
        )
        md = report.to_markdown()
        assert "# Data Quality Report" in md
        json_str = report.to_json()
        assert '"source_file": "test.csv"' in json_str

    def test_empty_dataframe(self) -> None:
        proc = DataPreprocessor()
        out = proc.run(pd.DataFrame())
        assert out.empty

    def test_missing_values_preserved(self) -> None:
        df = pd.DataFrame(
            {
                "date": ["2022-01-01", "2022-01-02"],
                "state": ["Punjab", "Punjab"],
                "district": ["Ludhiana", "Ludhiana"],
                "crop": ["Wheat", "Wheat"],
                "rainfall": [10.0, None],
                "temperature": [20.0, 22.0],
            }
        )
        proc = DataPreprocessor()
        out = proc.run(df)
        assert pd.isna(out["rainfall_mm"].iloc[1])
