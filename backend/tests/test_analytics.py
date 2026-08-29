from __future__ import annotations

import pandas as pd

from analytics.engine import (
    analyze_current_conditions,
    analyze_rainfall_trends,
    analyze_temperature_trends,
    check_thresholds,
    compare_time_periods,
    compute_kpis,
    detect_anomalies,
    generate_insights,
)


def _df(data: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(data)


class TestComputeKpis:
    def test_empty_dataframe(self):
        kpis = compute_kpis(pd.DataFrame())
        assert len(kpis) == 6
        assert all(k.value == "—" for k in kpis)

    def test_basic_kpis(self):
        df = _df(
            [
                {
                    "date": "2022-01-01",
                    "rainfall": 100.0,
                    "temperature": 25.0,
                    "yield": 300.0,
                    "production": 500.0,
                    "soil_moisture": 40.0,
                },
                {
                    "date": "2022-01-02",
                    "rainfall": 200.0,
                    "temperature": 30.0,
                    "yield": 400.0,
                    "production": 600.0,
                    "soil_moisture": 50.0,
                },
            ]
        )
        kpis = compute_kpis(df)
        labels = {k.label: k for k in kpis}
        assert labels["Average Rainfall"].value == 150.0
        assert labels["Average Temperature"].value == 27.5
        assert labels["Highest Yield"].value == 400.0
        assert labels["Lowest Yield"].value == 300.0
        assert labels["Total Production"].value == 1100.0
        assert labels["Average Soil Moisture"].value == 45.0


class TestAnalyzeCurrentConditions:
    def test_latest_values(self):
        df = _df(
            [
                {"date": "2022-01-01", "rainfall": 100.0, "temperature": 25.0},
                {"date": "2022-01-02", "rainfall": 200.0, "temperature": 30.0},
            ]
        )
        insights = analyze_current_conditions(df, location_id="test_loc")
        assert len(insights) == 2
        rain_ins = next(i for i in insights if i.metric == "rainfall")
        assert rain_ins.result["value"] == 200.0
        assert rain_ins.result["unit"] == "mm"
        assert rain_ins.confidence == 1.0
        assert rain_ins.type == "current_conditions"

    def test_empty_dataframe(self):
        insights = analyze_current_conditions(pd.DataFrame())
        assert len(insights) == 1
        assert insights[0].severity == "info"


class TestAnalyzeTemperatureTrends:
    def test_increasing_trend(self):
        df = _df(
            [
                {"date": "2022-01-01", "temperature": 20.0},
                {"date": "2022-01-02", "temperature": 22.0},
                {"date": "2022-01-03", "temperature": 24.0},
            ]
        )
        insights = analyze_temperature_trends(df)
        assert len(insights) == 1
        ins = insights[0]
        assert ins.type == "trend"
        assert ins.metric == "temperature"
        assert "increasing" in ins.message
        assert ins.result["trend_direction"] == "increasing"
        assert ins.calculation_method == "linear_regression (numpy polyfit degree=1)"

    def test_decreasing_trend(self):
        df = _df(
            [
                {"date": "2022-01-01", "temperature": 30.0},
                {"date": "2022-01-02", "temperature": 25.0},
                {"date": "2022-01-03", "temperature": 20.0},
            ]
        )
        insights = analyze_temperature_trends(df)
        assert len(insights) == 1
        assert "decreasing" in insights[0].message

    def test_insufficient_data(self):
        df = _df(
            [
                {"date": "2022-01-01", "temperature": 25.0},
            ]
        )
        insights = analyze_temperature_trends(df)
        assert len(insights) == 1
        assert "Insufficient data" in insights[0].message


class TestAnalyzeRainfallTrends:
    def test_increasing_trend(self):
        df = _df(
            [
                {"date": "2022-01-01", "rainfall": 10.0},
                {"date": "2022-01-02", "rainfall": 20.0},
                {"date": "2022-01-03", "rainfall": 30.0},
            ]
        )
        insights = analyze_rainfall_trends(df)
        assert len(insights) == 1
        assert "increasing" in insights[0].message
        assert insights[0].result["monthly_change_mm"] > 0


class TestDetectAnomalies:
    def test_detects_outliers(self):
        df = _df(
            [
                {"rainfall": 10.0},
                {"rainfall": 12.0},
                {"rainfall": 11.0},
                {"rainfall": 11.5},
                {"rainfall": 500.0},
            ]
        )
        insights = detect_anomalies(df, z_threshold=1.5)
        assert len(insights) >= 1
        assert insights[0].type == "anomaly"
        assert insights[0].severity in ("warning", "critical")

    def test_no_anomalies_in_normal_data(self):
        df = _df(
            [
                {"temperature": 25.0},
                {"temperature": 26.0},
                {"temperature": 24.5},
                {"temperature": 25.5},
            ]
        )
        insights = detect_anomalies(df)
        assert len(insights) == 0


class TestCheckThresholds:
    def test_low_rainfall_warning(self):
        df = _df(
            [
                {"rainfall": 30.0},
            ]
        )
        insights = check_thresholds(df)
        assert len(insights) == 1
        assert insights[0].type == "threshold"
        assert "Low" in insights[0].message
        assert insights[0].severity == "warning"

    def test_high_temperature_warning(self):
        df = _df(
            [
                {"temperature": 45.0},
            ]
        )
        insights = check_thresholds(df)
        assert len(insights) == 1
        assert "High" in insights[0].message

    def test_normal_values_no_warnings(self):
        df = _df(
            [
                {
                    "rainfall": 100.0,
                    "temperature": 25.0,
                    "humidity": 60.0,
                    "soil_moisture": 50.0,
                },
            ]
        )
        insights = check_thresholds(df)
        assert len(insights) == 0


class TestCompareTimePeriods:
    def test_period_comparison(self):
        df = _df(
            [
                {"date": "2022-01-01", "rainfall": 100.0},
                {"date": "2022-01-02", "rainfall": 110.0},
                {"date": "2022-02-01", "rainfall": 200.0},
                {"date": "2022-02-02", "rainfall": 220.0},
            ]
        )
        insights = compare_time_periods(
            df, "2022-01-01", "2022-01-31", "2022-02-01", "2022-02-28"
        )
        assert len(insights) >= 1
        rain_ins = next((i for i in insights if i.metric == "rainfall"), None)
        assert rain_ins is not None
        assert rain_ins.type == "comparison"
        assert "increased" in rain_ins.message
        assert rain_ins.result["period1_avg"] == 105.0
        assert rain_ins.result["period2_avg"] == 210.0


class TestGenerateInsights:
    def test_empty_dataframe(self):
        insights = generate_insights(pd.DataFrame())
        assert len(insights) == 1
        assert insights[0].type == "info"

    def test_produces_multiple_insight_types(self):
        df = _df(
            [
                {
                    "date": "2022-01-01",
                    "rainfall": 10.0,
                    "temperature": 45.0,
                    "humidity": 20.0,
                },
                {
                    "date": "2022-01-02",
                    "rainfall": 12.0,
                    "temperature": 46.0,
                    "humidity": 22.0,
                },
                {
                    "date": "2022-01-03",
                    "rainfall": 11.0,
                    "temperature": 47.0,
                    "humidity": 21.0,
                },
            ]
        )
        insights = generate_insights(df)
        types = {i.type for i in insights}
        assert "current_conditions" in types
        assert "trend" in types
        assert "threshold" in types
