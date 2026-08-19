from __future__ import annotations

import json

from fastapi.responses import Response

from analytics import charts, engine as kpi_engine
from database import data
from insights import engine as insight_engine
from models.schemas import DashboardFilters
from recommendations import engine as rec_engine


def _collect(filters: dict | None) -> dict:
    df = data.get_filtered(filters or {})
    insights = insight_engine.generate_insights(df)
    recs = rec_engine.generate_recommendations(df)
    story = insight_engine.generate_story(
        df, insights, [r.model_dump() for r in recs]
    )
    return {
        "kpis": [k.model_dump() for k in kpi_engine.compute_kpis(df)],
        "charts": {
            "line": charts.line_chart(df),
            "bar": charts.bar_chart(df),
            "scatter": charts.scatter_chart(df),
            "heatmap": charts.heatmap_data(df),
            "pie": charts.pie_chart(df),
        },
        "story": story,
        "recommendations": [r.model_dump() for r in recs],
        "filters": filters or {},
        "rows": int(len(df)),
    }


def export_dashboard(
    filters: DashboardFilters | None, format: str = "pdf"
) -> Response:
    payload = _collect(filters.model_dump(exclude_none=True) if filters else {})

    if format == "json":
        return Response(
            content=json.dumps(payload, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": 'attachment; filename="dashboard.json"'},
        )

    # PDF export via reportlab
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except ImportError:
        return Response(
            content=json.dumps(payload, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": 'attachment; filename="dashboard.json"'},
        )

    from io import BytesIO

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    flow: list = [
        Paragraph("Agricultural Analytics Dashboard", styles["Title"]),
        Spacer(1, 12),
    ]

    kpi_lines = ", ".join(
        f"{k['label']}: {k['value']} {k.get('unit') or ''}".strip()
        for k in payload["kpis"]
    )
    flow.append(Paragraph(kpi_lines, styles["BodyText"]))
    flow.append(Spacer(1, 12))

    flow.append(Paragraph(f"<b>Story:</b> {payload['story']['story']}", styles["BodyText"]))
    flow.append(Spacer(1, 12))

    flow.append(Paragraph("<b>Recommendations:</b>", styles["Heading3"]))
    for r in payload["recommendations"]:
        flow.append(Paragraph(f"- {r['message']}", styles["BodyText"]))

    doc.build(flow)
    buffer.seek(0)
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="dashboard.pdf"'},
    )
