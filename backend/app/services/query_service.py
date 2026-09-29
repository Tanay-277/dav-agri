import json
from typing import List, Optional
from sqlalchemy.orm import Session
from app.ai import get_ai_provider
from app.services.analytics_service import AnalyticsService
from app.repositories.query_repo import QueryRepository
from app.schemas.query import QueryRequest, QueryResponse, ConversationItem
from app.schemas.farm import StructuredVisualization

class QueryService:
    def __init__(self, db: Session):
        self.db = db
        self.query_repo = QueryRepository(db)
        self.analytics_service = AnalyticsService(db)
        self.ai_provider = get_ai_provider()

    def process_query(self, user_id: str, request: QueryRequest) -> QueryResponse:
        lang = request.language
        text = request.text.strip()

        # 1. Classify Intent
        intent = self.ai_provider.classify_intent(text)

        visualization: Optional[StructuredVisualization] = None
        verified_facts = {"intent": intent}

        # 2. Deterministic calculations based on intent
        if intent == "production_trend":
            growth_data = self.analytics_service.calculate_production_growth(user_id)
            verified_facts.update(growth_data)
            visualization = self.analytics_service.generate_cotton_stacked_visualization(user_id, language=lang)

        elif intent == "expense_breakdown":
            breakdown_data = self.analytics_service.calculate_expense_breakdown(user_id, language=lang)
            # Find category percentages
            cat_map = {item.category: item.percentage for item in breakdown_data.breakdown}
            verified_facts.update({
                "labor_pct": cat_map.get("labor", 40.0),
                "seeds_pct": cat_map.get("seeds", 25.0),
                "fertilizer_pct": cat_map.get("fertilizer", 20.0),
                "pesticides_pct": cat_map.get("pesticides", 15.0),
                "total_expense": breakdown_data.total_expense_inr
            })
            # Generate donut chart
            from app.schemas.farm import ChartDataset
            donut_title = "Total Cost of My Farming" if lang == "en" else "मेरे खेत का कुल खर्च" if lang == "hi" else "माझ्या शेतीचा एकूण खर्च"
            ds_name = "Expenses" if lang == "en" else "खर्च"
            visualization = StructuredVisualization(
                type="donut",
                title=donut_title,
                unit="percentage" if lang == "en" else "टक्केवारी",
                labels=breakdown_data.labels,
                datasets=[
                    ChartDataset(name=ds_name, color="#8b5cf6", data=breakdown_data.percentages)
                ],
                raw_data={"colors": breakdown_data.colors}
            )

        # 3. AI Generates Explanation Strictly Based on Verified Facts
        explanation = self.ai_provider.generate_explanation(
            prompt=text,
            verified_facts=verified_facts,
            language=lang
        )

        vis_json_str = visualization.model_dump_json() if visualization else None

        # 4. Save to Query History
        record = self.query_repo.create_query(
            user_id=user_id,
            query_text=text,
            query_language=lang,
            intent=intent,
            answer_text=explanation,
            visualization_data=vis_json_str
        )

        return QueryResponse(
            id=record.id,
            query=record.query_text,
            language=record.query_language,
            intent=record.intent or "general",
            answer=record.answer_text,
            source=self.ai_provider.provider_name,
            visualization=visualization,
            sources=["verified_farm_records", "analytics_engine"],
            share_token=record.share_token,
            created_at=record.created_at
        )

    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[ConversationItem]:
        queries = self.query_repo.list_by_user(user_id, limit=limit)
        items = []
        for q in queries:
            vis_dict = None
            if q.visualization_data:
                try:
                    vis_dict = json.loads(q.visualization_data)
                except Exception:
                    pass
            items.append(
                ConversationItem(
                    id=q.id,
                    query_text=q.query_text,
                    query_language=q.query_language,
                    intent=q.intent,
                    answer_text=q.answer_text,
                    visualization_data=vis_dict,
                    is_saved=bool(q.is_saved),
                    share_token=q.share_token,
                    created_at=q.created_at
                )
            )
        return items

    def get_shared_query(self, share_token: str) -> Optional[QueryResponse]:
        record = self.query_repo.get_by_share_token(share_token)
        if not record:
            return None

        vis_obj = None
        if record.visualization_data:
            try:
                vis_dict = json.loads(record.visualization_data)
                vis_obj = StructuredVisualization(**vis_dict)
            except Exception:
                pass

        return QueryResponse(
            id=record.id,
            query=record.query_text,
            language=record.query_language,
            intent=record.intent or "general",
            answer=record.answer_text,
            visualization=vis_obj,
            sources=["shared_record"],
            share_token=record.share_token,
            created_at=record.created_at
        )
