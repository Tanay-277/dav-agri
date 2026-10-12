import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.session import Base
from app.database.init_db import init_db
from app.models import User, ProductionRecord
from app.services.analytics_service import AnalyticsService

TEST_USER_ID = "usr_test_crop_income"


@pytest.fixture()
def db():
    """In-memory SQLite session seeded with the demo crops catalog plus
    production records for a single user (2 crops across 3 years)."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()

    # Seed the demo crops catalog (Cotton, Wheat, Ragi, Soybean, ...)
    init_db(session)

    # A user with 2 crops of production records across 3 years
    user = User(id=TEST_USER_ID, phone="9998887766")
    session.add(user)
    session.flush()
    session.add_all([
        ProductionRecord(user_id=TEST_USER_ID, crop_id="crop_cotton", year=2022, month=10,
                         quantity_quintals=10.0, revenue_inr=60000.0),
        ProductionRecord(user_id=TEST_USER_ID, crop_id="crop_cotton", year=2023, month=10,
                         quantity_quintals=12.0, revenue_inr=90000.0),
        ProductionRecord(user_id=TEST_USER_ID, crop_id="crop_cotton", year=2024, month=10,
                         quantity_quintals=14.0, revenue_inr=120000.0),
        ProductionRecord(user_id=TEST_USER_ID, crop_id="crop_wheat", year=2022, month=4,
                         quantity_quintals=20.0, revenue_inr=40000.0),
        ProductionRecord(user_id=TEST_USER_ID, crop_id="crop_wheat", year=2023, month=4,
                         quantity_quintals=22.0, revenue_inr=50000.0),
        ProductionRecord(user_id=TEST_USER_ID, crop_id="crop_wheat", year=2024, month=4,
                         quantity_quintals=25.0, revenue_inr=70000.0),
    ])
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_crop_income_line_uses_real_production_records(db):
    service = AnalyticsService(db)

    viz = service.generate_crop_income_line_visualization(TEST_USER_ID, language="en")

    assert viz.type == "line"
    assert viz.labels == ["2022", "2023", "2024"]
    assert viz.unit == "INR (Thousands)"
    assert len(viz.datasets) == 2

    by_name = {ds.name: ds.data for ds in viz.datasets}
    # Real revenue sums converted to thousands (revenue_inr / 1000)
    assert by_name["Cotton"] == [60.0, 90.0, 120.0]
    assert by_name["Wheat"] == [40.0, 50.0, 70.0]


def test_crop_income_line_localized_titles_and_names(db):
    service = AnalyticsService(db)

    en = service.generate_crop_income_line_visualization(TEST_USER_ID, language="en")
    hi = service.generate_crop_income_line_visualization(TEST_USER_ID, language="hi")
    mr = service.generate_crop_income_line_visualization(TEST_USER_ID, language="mr")

    assert en.title == "Income from Different Crops"
    assert hi.title == "विभिन्न फसलों से प्राप्त आय"
    assert mr.title == "वेगवेगळ्या पिकांमधून मिळालेले उत्पन्न"

    # Dataset names use localized crop labels from the Crop rows
    assert {ds.name for ds in en.datasets} == {"Cotton", "Wheat"}
    assert {ds.name for ds in hi.datasets} == {"कपास", "गेहूं"}
    assert {ds.name for ds in mr.datasets} == {"कापूस", "गहू"}
    assert mr.unit == "रुपये (हजार)"


def test_crop_income_line_fallback_skeleton_for_user_without_records(db):
    service = AnalyticsService(db)

    viz = service.generate_crop_income_line_visualization("usr_without_records", language="mr")

    assert viz.type == "line"
    assert viz.labels == ["2021", "2022", "2023", "2024", "2025"]
    assert len(viz.datasets) == 4
    assert [ds.name for ds in viz.datasets] == ["कापूस", "गहू", "नाचणी", "सोयाबीन"]
    for ds in viz.datasets:
        assert ds.data == [80, 90, 110, 120, 152]