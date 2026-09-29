-- =============================================================================
-- Migration 002: Seed Demo Data (Cleanly separated from business logic)
-- Demo Farmer: Raj Patil (Phone: +9186524525856)
-- Matches Figma Screen 12 (12, 15, 18, 21 quintals) & Screen 14/15 (40% labor, etc.)
-- =============================================================================

-- 1. Insert Standard Crops Catalog
INSERT OR IGNORE INTO crops (id, name_en, name_hi, name_mr, season, is_default) VALUES
('crop_cotton', 'Cotton', 'कपास', 'कापूस', 'Kharif', 1),
('crop_wheat', 'Wheat', 'गेहूं', 'गहू', 'Rabi', 1),
('crop_ragi', 'Ragi', 'रागी', 'नाचणी', 'Kharif', 1),
('crop_soybean', 'Soybean', 'सोयाबीन', 'सोयाबीन', 'Kharif', 0),
('crop_sugarcane', 'Sugarcane', 'गन्ना', 'ऊस', 'Perennial', 0);

-- 2. Insert Demo User (Raj Patil)
INSERT OR IGNORE INTO users (id, phone, created_at, updated_at) VALUES
('usr_demo_raj_patil', '86524525856', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- 3. Insert Demo Profile
INSERT OR IGNORE INTO profiles (
    id, user_id, name, location, age, land_location, primary_crop, land_size,
    irrigation_type, livestock, crops_grown, created_at, updated_at
) VALUES (
    'prof_demo_raj_patil',
    'usr_demo_raj_patil',
    'Raj Patil',
    'Pune, MH',
    42,
    'Plot No. 124/2, Kothrud',
    'Cotton',
    '20 acres',
    'Rain Fed',
    'Cow, Goat, Buffalo',
    '["Cotton", "Wheat", "Ragi"]',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- 4. Insert Onboarding State
INSERT OR IGNORE INTO onboarding_preferences (
    id, user_id, preferred_language, voice_confirmed, onboarding_completed, updated_at
) VALUES (
    'onb_demo_raj_patil',
    'usr_demo_raj_patil',
    'mr',
    1,
    1,
    CURRENT_TIMESTAMP
);

-- 5. Insert Production Records for Cotton (Matches Figma Stacked Bar Chart & Processed Result)
-- "My cotton production was 12 quintals in 2022, 15 in 2023, 18 in 2024, and 21 in 2025"
INSERT OR IGNORE INTO production_records (id, user_id, crop_id, year, month, quantity_quintals, revenue_inr) VALUES
('prod_cotton_2021', 'usr_demo_raj_patil', 'crop_cotton', 2021, 10, 10.0, 60000),
('prod_cotton_2022', 'usr_demo_raj_patil', 'crop_cotton', 2022, 10, 12.0, 78000),
('prod_cotton_2023', 'usr_demo_raj_patil', 'crop_cotton', 2023, 10, 15.0, 105000),
('prod_cotton_2024', 'usr_demo_raj_patil', 'crop_cotton', 2024, 10, 18.0, 135000),
('prod_cotton_2025', 'usr_demo_raj_patil', 'crop_cotton', 2025, 10, 21.0, 168000);

-- Insert Multi-Crop Production for Wheat & Ragi
INSERT OR IGNORE INTO production_records (id, user_id, crop_id, year, month, quantity_quintals, revenue_inr) VALUES
('prod_wheat_2024', 'usr_demo_raj_patil', 'crop_wheat', 2024, 4, 25.0, 62500),
('prod_wheat_2025', 'usr_demo_raj_patil', 'crop_wheat', 2025, 4, 28.0, 75600),
('prod_ragi_2024', 'usr_demo_raj_patil', 'crop_ragi', 2024, 11, 14.0, 49000);

-- 6. Insert Expense Records (Matches Figma Screen 14/15: Labor 40%, Seeds 25%, Fertilizer 20%, Pesticides 15%)
-- Total Expenses = 100,000 INR
INSERT OR IGNORE INTO expense_records (id, user_id, crop_id, category, amount_inr, expense_date, notes) VALUES
('exp_1', 'usr_demo_raj_patil', 'crop_cotton', 'labor', 40000, '2025-06-15', 'मजुरी - कापणी व निंदणी'),
('exp_2', 'usr_demo_raj_patil', 'crop_cotton', 'seeds', 25000, '2025-05-10', 'बियाणे - बीटी कापूस बियाणे'),
('exp_3', 'usr_demo_raj_patil', 'crop_cotton', 'fertilizer', 20000, '2025-06-01', 'खत - डीएपी आणि युरिया'),
('exp_4', 'usr_demo_raj_patil', 'crop_cotton', 'pesticides', 15000, '2025-07-20', 'कीटकनाशके - सेंद्रिय कीटकनाशक फवारणी');

-- 7. Insert Initial Conversation / Query History (Matches Figma Screen 13 "माझे संवाद")
INSERT OR IGNORE INTO query_history (
    id, user_id, query_text, query_language, intent, answer_text, is_saved, share_token
) VALUES
(
    'qry_demo_1',
    'usr_demo_raj_patil',
    'माझ्या कापूस उत्पादनाची माहिती',
    'mr',
    'production_summary',
    'तुमचे कापूस उत्पादन 2022 मध्ये 12 क्विंटलवरून 2025 मध्ये 21 क्विंटलपर्यंत वाढले आहे. ही 75% वाढ आहे.',
    1,
    'sh_cotton_demo_01'
),
(
    'qry_demo_2',
    'usr_demo_raj_patil',
    'पिकांवर झालेला एकूण खर्च',
    'mr',
    'expense_breakdown',
    'तुमच्या शेतीचा एकूण खर्च ₹1,00,000 आहे, ज्यामध्ये सर्वाधिक 40% खर्च मजुरीवर झाला आहे.',
    1,
    'sh_expense_demo_02'
);
