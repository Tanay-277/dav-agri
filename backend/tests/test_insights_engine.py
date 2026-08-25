from __future__ import annotations

import pandas as pd

from analytics.engine import generate_insights
from insights.engine import generate_story
from models.schemas import Insight


def _df(data: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(data)


class TestGenerateStory:
    def test_rule_based_story(self):
        df = _df(
            [
                {
                    "date": "2022-01-01",
                    "rainfall": 100.0,
                    "temperature": 25.0,
                    "yield": 300.0,
                },
                {
                    "date": "2022-01-02",
                    "rainfall": 150.0,
                    "temperature": 27.0,
                    "yield": 350.0,
                },
            ]
        )
        insights = generate_insights(df)
        recs = [{"message": "Test recommendation"}]
        story = generate_story(df, insights, recs)
        assert isinstance(story, dict)
        assert "story" in story
        assert "summary" in story
        assert "reasons" in story
        assert "recommendations" in story
        assert "source" in story
        assert story["source"] == "rule"
        assert "average rainfall" in story["summary"].lower()
        assert "Test recommendation" in story["recommendations"]

    def test_story_with_no_data(self):
        df = pd.DataFrame()
        insights = generate_insights(df)
        recs = []
        story = generate_story(df, insights, recs)
        assert "No data is available" in story["summary"]

    def test_story_includes_reasons(self):
        df = _df(
            [
                {"date": "2022-01-01", "rainfall": 100.0, "temperature": 25.0},
                {"date": "2022-01-02", "rainfall": 200.0, "temperature": 30.0},
            ]
        )
        insights = generate_insights(df)
        recs = []
        story = generate_story(df, insights, recs)
        assert len(story["reasons"]) > 0


class TestInsightStructure:
    def test_insight_has_required_fields(self):
        df = _df(
            [
                {"date": "2022-01-01", "temperature": 45.0},
                {"date": "2022-01-02", "temperature": 46.0},
                {"date": "2022-01-03", "temperature": 47.0},
            ]
        )
        insights = generate_insights(df)
        for ins in insights:
            assert isinstance(ins, Insight)
            assert ins.type
            assert ins.message
            assert ins.severity in ("info", "warning", "critical")
            assert ins.source == "rule"
            assert isinstance(ins.input_variables, dict)
            assert isinstance(ins.time_range, dict)
            assert isinstance(ins.calculation_method, str)
            assert isinstance(ins.result, dict)
            assert isinstance(ins.data_quality_flags, list)

    def test_insight_confidence_in_valid_range(self):
        df = _df(
            [
                {"date": "2022-01-01", "rainfall": 10.0},
                {"date": "2022-01-02", "rainfall": 12.0},
                {"date": "2022-01-03", "rainfall": 11.0},
                {"date": "2022-01-04", "rainfall": 1000.0},
            ]
        )
        insights = generate_insights(df)
        for ins in insights:
            if ins.confidence is not None:
                assert 0.0 <= ins.confidence <= 1.0
