# Data Quality Report: agriculture.csv
Generated: 2026-08-21T10:22:00.859582

## Summary
- **Total rows:** 600
- **Valid rows:** 600
- **Invalid rows:** 0
- **Duplicate rows:** 1
- **Outlier rows:** 103

## Missing Values
- record_date: 0
- state: 0
- district: 0
- crop: 0
- rainfall_mm: 0
- temperature_c: 0
- humidity_pct: 0
- soil_moisture_pct: 0
- yield_kg_per_ha: 0
- production_tonnes: 0
- area_ha: 0
- fertilizer_kg: 0
- irrigation_pct: 0
- location_id: 0
- latitude: 0
- longitude: 0
- timestamp: 0
- is_duplicate: 0
- validation_flags: 0
- is_invalid: 0
- is_outlier: 0
- data_classification: 0
- source: 0
- source_row_id: 0

## Invalid Values

## Outliers
- production_tonnes: 77
- rainfall_mm: 35
- yield_kg_per_ha: 55

## Processing Log
- Input rows: 600
- Columns after normalization: ['record_date', 'state', 'district', 'crop', 'rainfall_mm', 'temperature_c', 'humidity_pct', 'soil_moisture_pct', 'yield_kg_per_ha', 'production_tonnes', 'area_ha', 'fertilizer_kg', 'irrigation_pct']
- Duplicates detected: 1
- Outliers detected: 103 rows
- Output rows: 600

## Normalized Sample
```json
[
  {
    "timestamp": "2022-09-08 00:00:00",
    "record_date": "2022-09-08",
    "state": "Maharashtra",
    "district": "Pune",
    "crop": "Maize",
    "rainfall_mm": 117.9,
    "temperature_c": 27.4,
    "humidity_pct": 77.1,
    "soil_moisture_pct": 50.0,
    "yield_kg_per_ha": 320.0,
    "production_tonnes": 305.0,
    "area_ha": 63.4,
    "fertilizer_kg": 117.2,
    "irrigation_pct": 60.3,
    "location_id": "maharashtra_pune",
    "latitude": 18.5204,
    "longitude": 73.8567,
    "data_classification": "historical",
    "source": "agriculture.csv",
    "source_row_id": 0,
    "is_duplicate": false,
    "is_outlier": false,
    "is_invalid": false,
    "validation_flags": [],
    "raw": {
      "record_date": "2022-09-08 00:00:00",
      "state": "Maharashtra",
      "district": "Pune",
      "crop": "Maize",
      "rainfall_mm": 117.9,
      "temperature_c": 27.4,
      "humidity_pct": 77.1,
      "soil_moisture_pct": 50.0,
      "yield_kg_per_ha": 320,
      "production_tonnes": 305,
      "area_ha": 63.4,
      "fertilizer_kg": 117.2,
      "irrigation_pct": 60.3,
      "location_id": "maharashtra_pune",
      "latitude": 18.5204,
      "longitude": 73.8567,
      "timestamp": "2022-09-08 00:00:00",
      "is_duplicate": false,
      "validation_flags": [],
      "is_invalid": false,
      "is_outlier": false,
      "data_classification": "historical",
      "source": "agriculture.csv",
      "source_row_id": 0
    }
  },
  {
    "timestamp": "2023-10-28 00:00:00",
    "record_date": "2023-10-28",
    "state": "Karnataka",
    "district": "Shimoga",
    "crop": "Cotton",
    "rainfall_mm": 96.1,
    "temperature_c": 28.5,
    "humidity_pct": 52.6,
    "soil_moisture_pct": 43.8,
    "yield_kg_per_ha": 335.0,
    "production_tonnes": 295.0,
    "area_ha": 121.8,
    "fertilizer_kg": 151.8,
    "irrigation_pct": 46.7,
    "location_id": "karnataka_shimoga",
    "latitude": 13.9299,
    "longitude": 75.5681,
    "data_classification": "historical",
    "source": "agriculture.csv",
    "source_row_id": 1,
    "is_duplicate": false,
    "is_outlier": false,
    "is_invalid": false,
    "validation_flags": [],
    "raw": {
      "record_date": "2023-10-28 00:00:00",
      "state": "Karnataka",
      "district": "Shimoga",
      "crop": "Cotton",
      "rainfall_mm": 96.1,
      "temperature_c": 28.5,
      "humidity_pct": 52.6,
      "soil_moisture_pct": 43.8,
      "yield_kg_per_ha": 335,
      "production_tonnes": 295,
      "area_ha": 121.8,
      "fertilizer_kg": 151.8,
      "irrigation_pct": 46.7,
      "location_id": "karnataka_shimoga",
      "latitude": 13.9299,
      "longitude": 75.5681,
      "timestamp": "2023-10-28 00:00:00",
      "is_duplicate": false,
      "validation_flags": [],
      "is_invalid": false,
      "is_outlier": false,
      "data_classification": "historical",
      "source": "agriculture.csv",
      "source_row_id": 1
    }
  },
  {
    "timestamp": "2022-04-05 00:00:00",
    "record_date": "2022-04-05",
    "state": "Punjab",
    "district": "Jalandhar",
    "crop": "Rice",
    "rainfall_mm": 70.4,
    "temperature_c": 27.4,
    "humidity_pct": 50.8,
    "soil_moisture_pct": 38.7,
    "yield_kg_per_ha": 362.0,
    "production_tonnes": 406.0,
    "area_ha": 106.2,
    "fertilizer_kg": 236.8,
    "irrigation_pct": 34.7,
    "location_id": "punjab_jalandhar",
    "latitude": 31.326,
    "longitude": 75.5762,
    "data_classification": "historical",
    "source": "agriculture.csv",
    "source_row_id": 2,
    "is_duplicate": false,
    "is_outlier": false,
    "is_invalid": false,
    "validation_flags": [],
    "raw": {
      "record_date": "2022-04-05 00:00:00",
      "state": "Punjab",
      "district": "Jalandhar",
      "crop": "Rice",
      "rainfall_mm": 70.4,
      "temperature_c": 27.4,
      "humidity_pct": 50.8,
      "soil_moisture_pct": 38.7,
      "yield_kg_per_ha": 362,
      "production_tonnes": 406,
      "area_ha": 106.2,
      "fertilizer_kg": 236.8,
      "irrigation_pct": 34.7,
      "location_id": "punjab_jalandhar",
      "latitude": 31.326,
      "longitude": 75.5762,
      "timestamp": "2022-04-05 00:00:00",
      "is_duplicate": false,
      "validation_flags": [],
      "is_invalid": false,
      "is_outlier": false,
      "data_classification": "historical",
      "source": "agriculture.csv",
      "source_row_id": 2
    }
  }
]
```