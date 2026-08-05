# Product Requirements Document (PRD)

**Project:** Interactive Data Storytelling Dashboard for Agricultural Analytics Using AI-Generated Insights

---

## 1. Project Overview

### Objective

Develop a modern web application that transforms raw agricultural datasets into interactive visualizations, automated insights, and narrative-style data stories. Unlike traditional dashboards that only display charts, this system analyzes the data, identifies significant trends, explains them in plain language, and provides actionable recommendations.

The application should resemble a professional analytics platform rather than a simple college project.

---

## 2. Problem Statement

Agricultural datasets contain valuable information but are often presented through static dashboards requiring manual interpretation.

**Current dashboards answer:**
- "What happened?"

**This system should answer:**
- "What happened?"
- "Why did it happen?"
- "What should the user do next?"

The project combines:
- Data Analytics
- Data Visualization
- Natural Language Insight Generation
- Interactive Dashboard Design

---

## 3. Target Users

**Primary**
- Farmers
- Agriculture students
- Researchers

**Secondary**
- Government agencies
- Agricultural analysts

---

## 4. Technology Stack

| Layer | Stack |
|---|---|
| **Frontend** | React (Vite), TypeScript, Tailwind CSS, Plotly.js, React Router, Axios |
| **Backend** | FastAPI, Python 3.12+ |
| **Analytics** | Pandas, NumPy (optional: Scikit-learn) |
| **AI** | Gemini API (fallback: Rule-based Insight Engine) |
| **Database** | SQLite |
| **Deployment** | Frontend → Vercel, Backend → Render |

---

## 5. Functional Requirements

### Dashboard

Fully interactive. Users can:
- Filter by crop
- Filter by state
- Filter by district
- Filter by date
- Reset filters
- Export dashboard

### Charts

Must include:

- **Line Chart** — Trend Analysis (e.g., Rainfall vs Time, Temperature vs Time)
- **Bar Chart** — Crop Production, State Comparison
- **Scatter Plot** — Temperature vs Yield, Rainfall vs Yield
- **Heatmap** — Correlation Matrix
- **Pie Chart** — Crop Distribution
- **KPI Cards** — Average Rainfall, Average Temperature, Highest Yield, Lowest Yield, Total Production, Average Soil Moisture

---

## 6. Insight Engine

This is the core feature. The system automatically analyzes the selected data.

**Examples:**

| Instead of | Generate |
|---|---|
| Rainfall = 120mm | "Rainfall decreased by 18% compared to the previous month." |
| Yield = 450kg | "Wheat yield is above the yearly average by 12%." |

Insights should regenerate dynamically whenever filters change.

---

## 7. Storytelling Engine

Instead of showing isolated insights, combine them into a coherent paragraph.

**Example:**

> During the last month, rainfall steadily decreased while average temperatures increased. Soil moisture also declined. Historical patterns indicate that reduced rainfall is associated with lower crop yield. Additional irrigation is recommended.

The story should update dynamically with filters.

---

## 8. Recommendation Engine

Generate recommendations based on analytical rules.

**Examples:**

- `IF Rainfall ↓ AND Temperature ↑ → Recommend irrigation`
- `IF Humidity ↓ → Monitor soil moisture`
- `IF Yield ↓ → Inspect fertilizer usage`

---

## 9. AI Integration

Use Gemini **only** for converting analytical results into natural language. **Never send raw datasets.**

**Workflow:**

```
Analytics → JSON Summary → Gemini Prompt → Narrative Story
```

**Example Prompt:**

```
You are an agricultural analyst.
Convert the following analytics into a concise professional summary.

Data:
- Rainfall decreased 15%
- Temperature increased 2°C
- Yield decreased 8%

Return:
- Summary
- Reasons
- Recommendations
```

---

## 10. User Interface

### Sidebar
- **Filters:** Crop, State, Date, District
- **Buttons:** Reset, Export

### Main Dashboard

**Top:** Navbar, KPI Cards (Rainfall, Yield, Temperature, Production)

**Middle:** Charts (Line, Bar, Scatter, Heatmap)

**Bottom:** AI Story, Recommendations, Export

---

## 11. UI Design

**Style:**
- Modern, clean
- Glassmorphism (optional)
- Dark mode
- Rounded cards
- Minimal animations
- Professional analytics dashboard feel

**Inspired by:** Power BI, Tableau, Google Analytics

Not a typical student project.

---

## 12. Backend APIs

### `GET /dashboard`
```json
{
  "charts": {},
  "kpis": {},
  "filters": {}
}
```

### `GET /insights`
```json
{
  "insights": []
}
```

### `GET /story`
```json
{
  "story": "..."
}
```

### `GET /recommendations`
```json
[
  ...
]
```

### `POST /export`
Returns: PDF

---

## 13. Folder Structure

```
project/
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Dashboard/
│       │   ├── Charts/
│       │   ├── KPI/
│       │   ├── StoryPanel/
│       │   ├── RecommendationPanel/
│       │   └── Filters/
│       ├── pages/
│       ├── hooks/
│       ├── services/
│       └── utils/
├── backend/
│   ├── api/
│   ├── analytics/
│   ├── insights/
│   ├── recommendations/
│   ├── models/
│   └── database/
├── dataset/
├── docs/
└── paper/
```

---

## 14. Analytics Workflow

```
Dataset → Cleaning → Preprocessing → Statistical Analysis
       → Visualization Data → Insight Detection
       → Story Generation → Recommendations → Frontend
```

---

## 15. Features by Phase

### Phase 1
- Dataset upload
- Cleaning
- Charts
- Dashboard

### Phase 2
- Interactive filters
- KPIs
- Export

### Phase 3
- Automatic insights
- Story generation
- Recommendations

### Phase 4
- Dark mode
- Responsive design
- Performance optimization
- Deployment

---

## 16. Non-Functional Requirements

- Responsive
- Fast loading
- Professional UI
- Reusable React components
- RESTful architecture
- Proper error handling
- Loading states / skeleton loaders
- Toast notifications
- Empty states
- 404 handling

---

## 17. Research Contribution

```
Existing dashboards → Display charts only

Our system → Interactive dashboard
           → Automatic trend detection
           → Natural-language storytelling
           → Actionable recommendations
```

The contribution lies in improving interpretability and decision support rather than inventing a new chart type.

---

## 18. Deliverables

- Fully responsive React dashboard
- FastAPI backend
- Interactive Plotly visualizations
- Automated insight generation
- AI-powered storytelling
- Recommendation engine
- PDF export
- Research paper
- Source code with documentation
- Deployment (Vercel + Render)

---

## 19. Suggested Enhancements (Stretch Goals)

To make the project feel more production-ready, if time permits:

- Authentication (simple admin login)
- Dataset upload (CSV upload with automatic parsing)
- Dynamic dashboard generation (works with uploaded datasets, not just one hardcoded file)
- Natural language querying (e.g., "Show rainfall trends in Karnataka for 2023")
- Insight history (save generated stories and reports)
- Chart customization (change chart types, colors, download images)
- Role-based views (Admin vs. Viewer, if time permits)

> **Note:** These are lower priority than Phases 1–3. Recommend deferring auth and dynamic uploads until the core insight/story/recommendation pipeline is working end-to-end on a fixed dataset.