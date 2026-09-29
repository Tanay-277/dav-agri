import logging
from sqlalchemy.orm import Session
from app.database.session import Base, engine, SessionLocal
from app.models import User, Profile, OnboardingPreference, Crop, ProductionRecord, ExpenseRecord, QueryHistory

logger = logging.getLogger(__name__)

DEFAULT_CROPS = [
    {"id": "crop_cotton", "name_en": "Cotton", "name_hi": "कपास", "name_mr": "कापूस", "season": "Kharif", "is_default": True},
    {"id": "crop_wheat", "name_en": "Wheat", "name_hi": "गेहूं", "name_mr": "गहू", "season": "Rabi", "is_default": True},
    {"id": "crop_ragi", "name_en": "Ragi", "name_hi": "रागी", "name_mr": "नाचणी", "season": "Kharif", "is_default": True},
    {"id": "crop_soybean", "name_en": "Soybean", "name_hi": "सोयाबीन", "name_mr": "सोयाबीन", "season": "Kharif", "is_default": False},
    {"id": "crop_sugarcane", "name_en": "Sugarcane", "name_hi": "गन्ना", "name_mr": "ऊस", "season": "Perennial", "is_default": False},
]

def init_db(db: Session) -> None:
    # 1. Create tables
    Base.metadata.create_all(bind=engine)

    # 2. Seed default crops catalog if not present
    existing_crop_count = db.query(Crop).count()
    if existing_crop_count == 0:
        for crop_data in DEFAULT_CROPS:
            crop = Crop(**crop_data)
            db.add(crop)
        db.commit()
        logger.info("Default crops initialized.")

    # 3. Seed Demo Farmers (Raj Patil for standard 10-digit numbers and legacy numbers)
    from datetime import date
    demo_phones = [
        ("usr_demo_raj_patil", "86524525856"),
        ("usr_demo_raj_patil_10", "9876543210"),
        ("usr_demo_raj_patil_short", "8652452585"),
    ]

    for uid, ph in demo_phones:
        existing = db.query(User).filter(User.phone == ph).first()
        if not existing:
            demo_user = User(id=uid, phone=ph)
            db.add(demo_user)
            db.flush()

            profile = Profile(
                id=f"prof_{uid}",
                user_id=demo_user.id,
                name="Raj Patil",
                location="Pune, MH",
                age=42,
                land_location="Plot No. 124/2, Kothrud",
                primary_crop="Cotton",
                land_size="20 acres",
                irrigation_type="Rain Fed",
                livestock="Cow, Goat, Buffalo",
                crops_grown='["Cotton", "Wheat", "Ragi"]'
            )
            db.add(profile)

            onboarding = OnboardingPreference(
                id=f"onb_{uid}",
                user_id=demo_user.id,
                preferred_language="mr",
                voice_confirmed=True,
                onboarding_completed=True
            )
            db.add(onboarding)

            # Figma Screen 12 & Screen 14/15 Production Data
            production_samples = [
                {"id": f"prod_cot_21_{uid}", "crop_id": "crop_cotton", "year": 2021, "month": 10, "quantity_quintals": 10.0, "revenue_inr": 60000.0},
                {"id": f"prod_cot_22_{uid}", "crop_id": "crop_cotton", "year": 2022, "month": 10, "quantity_quintals": 12.0, "revenue_inr": 78000.0},
                {"id": f"prod_cot_23_{uid}", "crop_id": "crop_cotton", "year": 2023, "month": 10, "quantity_quintals": 15.0, "revenue_inr": 105000.0},
                {"id": f"prod_cot_24_{uid}", "crop_id": "crop_cotton", "year": 2024, "month": 10, "quantity_quintals": 18.0, "revenue_inr": 135000.0},
                {"id": f"prod_cot_25_{uid}", "crop_id": "crop_cotton", "year": 2025, "month": 10, "quantity_quintals": 21.0, "revenue_inr": 168000.0},
                {"id": f"prod_wht_24_{uid}", "crop_id": "crop_wheat", "year": 2024, "month": 4, "quantity_quintals": 25.0, "revenue_inr": 62500.0},
                {"id": f"prod_wht_25_{uid}", "crop_id": "crop_wheat", "year": 2025, "month": 4, "quantity_quintals": 28.0, "revenue_inr": 75600.0},
                {"id": f"prod_rag_24_{uid}", "crop_id": "crop_ragi", "year": 2024, "month": 11, "quantity_quintals": 14.0, "revenue_inr": 49000.0},
            ]
            for p in production_samples:
                record = ProductionRecord(user_id=demo_user.id, **p)
                db.add(record)

            # Figma Screen 14/15 Expense Data:
            # Total = 100,000 INR -> Labor: 40%, Seeds: 25%, Fertilizer: 20%, Pesticides: 15%
            expenses = [
                {"id": f"exp_1_{uid}", "crop_id": "crop_cotton", "category": "labor", "amount_inr": 40000.0, "expense_date": date(2025, 6, 15), "notes": "मजुरी - कापणी व निंदणी"},
                {"id": f"exp_2_{uid}", "crop_id": "crop_cotton", "category": "seeds", "amount_inr": 25000.0, "expense_date": date(2025, 5, 10), "notes": "बियाणे - बीटी कापूस बियाणे"},
                {"id": f"exp_3_{uid}", "crop_id": "crop_cotton", "category": "fertilizer", "amount_inr": 20000.0, "expense_date": date(2025, 6, 1), "notes": "खत - डीएपी आणि युरिया"},
                {"id": f"exp_4_{uid}", "crop_id": "crop_cotton", "category": "pesticides", "amount_inr": 15000.0, "expense_date": date(2025, 7, 20), "notes": "कीटकनाशके - सेंद्रिय कीटकनाशक फवारणी"},
            ]
            for e in expenses:
                exp_rec = ExpenseRecord(user_id=demo_user.id, **e)
                db.add(exp_rec)

            # Recent Conversations
            demo_queries = [
                {
                    "id": f"qry_demo_1_{uid}",
                    "query_text": "माझ्या कापूस उत्पादनाची माहिती",
                    "query_language": "mr",
                    "intent": "production_summary",
                    "answer_text": "तुमचे कापूस उत्पादन 2022 मध्ये 12 क्विंटलवरून 2025 मध्ये 21 क्विंटलपर्यंत वाढले आहे. ही 75% वाढ आहे.",
                    "is_saved": True,
                    "share_token": f"sh_cotton_demo_{uid}"
                },
                {
                    "id": f"qry_demo_2_{uid}",
                    "query_text": "पिकांवर झालेला एकूण खर्च",
                    "query_language": "mr",
                    "intent": "expense_breakdown",
                    "answer_text": "तुमच्या शेतीचा एकूण खर्च ₹1,00,000 आहे, ज्यामध्ये सर्वाधिक 40% खर्च मजुरीवर झाला आहे.",
                    "is_saved": True,
                    "share_token": f"sh_expense_demo_{uid}"
                }
            ]
            for q in demo_queries:
                query_rec = QueryHistory(user_id=demo_user.id, **q)
                db.add(query_rec)

    db.commit()
    logger.info("Demo farmer data initialized.")

if __name__ == "__main__":
    db = SessionLocal()
    init_db(db)
    db.close()
    print("Database initialization complete.")
