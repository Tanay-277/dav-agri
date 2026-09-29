import re
from typing import Dict, Any
from app.ai.base import BaseAIProvider

class MockAIProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str:
        return "mock"

    def classify_intent(self, text: str) -> str:
        t = text.lower()
        if any(w in t for w in ["cotton", "कापूस", "कपास", "production", "उत्पादन", "yield", "quintal", "क्विंटल"]):
            return "production_trend"
        elif any(w in t for w in ["expense", "खर्च", "लागत", "cost", "labor", "मजुरी", "fertilizer", "खत"]):
            return "expense_breakdown"
        elif any(w in t for w in ["weather", "हवामान", "मौसम", "rain", "पाऊस", "बारिश"]):
            return "weather"
        elif any(w in t for w in ["protection", "संरक्षण", "disease", "रोग", "pest", "कीड", "कीटकनाशक"]):
            return "crop_protection"
        elif any(w in t for w in ["price", "भाव", "दर", "mandi", "बाजारभाव"]):
            return "crop_prices"
        elif any(w in t for w in ["scheme", "योजना", "subsidy", "अनुदान", "सरकारी"]):
            return "government_schemes"
        return "general_agricultural_query"

    def generate_explanation(
        self,
        prompt: str,
        verified_facts: Dict[str, Any],
        language: str = "mr"
    ) -> str:
        clean_lang = language.lower().strip()
        if clean_lang not in ("en", "hi", "mr"):
            raise ValueError(f"Unsupported language code '{language}'. Must be one of ['en', 'hi', 'mr']")

        intent = verified_facts.get("intent", "production_trend")

        if intent == "production_trend":
            growth = verified_facts.get("total_growth_quintals", 9.0)
            pct = verified_facts.get("percentage_increase", 75.0)
            first_year = verified_facts.get("first_year", 2022)
            last_year = verified_facts.get("last_year", 2025)

            if language == "mr":
                return (
                    f"स्पष्टीकरण: तुम्ही {first_year} च्या तुलनेत {last_year} मध्ये {growth} क्विंटल अधिक उत्पादन घेतले आहे, "
                    f"जी उत्पादनात {pct}% वाढ दर्शवते. ही वाढ योग्य व्यवस्थापन आणि खत नियोजनामुळे झाली आहे."
                )
            elif language == "hi":
                return (
                    f"स्पष्टीकरण: आपने {first_year} की तुलना में {last_year} में {growth} क्विंटल अधिक उत्पादन प्राप्त किया है, "
                    f"जो {pct}% की शुद्ध वृद्धि दर्शाता है। यह पैदावार में एक बड़ा सुधार है।"
                )
            else:
                return (
                    f"Explanation: You produced {growth} more quintals in {last_year} than in {first_year}, "
                    f"which is a {pct}% increase in production. The highest jump was recorded with sustained irrigation."
                )

        elif intent == "expense_breakdown":
            labor_pct = verified_facts.get("labor_pct", 40.0)
            seeds_pct = verified_facts.get("seeds_pct", 25.0)
            fert_pct = verified_facts.get("fertilizer_pct", 20.0)
            pest_pct = verified_facts.get("pesticides_pct", 15.0)

            if language == "mr":
                return (
                    "स्पष्टीकरण:\n"
                    "या पाई चार्टमध्ये तुमच्या शेतीसाठी केलेल्या एकूण खर्चाचे वेगवेगळे भाग दाखवले आहेत. "
                    "प्रत्येक भाग एकूण खर्चातील किती टक्के आहे, हे यातून सहज समजते.\n\n"
                    f"मजुरीवर सर्वाधिक खर्च झाला असून, एकूण खर्चापैकी {labor_pct}% खर्च मजुरीसाठी झाला आहे. "
                    f"त्यानंतर बियाण्यांवर {seeds_pct}%, खतांवर {fert_pct}% आणि कीटकनाशकांवर {pest_pct}% खर्च झाला आहे.\n\n"
                    "यामुळे तुमच्या शेतीच्या खर्चामध्ये मजुरीचा सर्वात मोठा वाटा आहे, तर कीटकनाशकांवरील खर्च तुलनेने कमी आहे."
                )
            elif language == "hi":
                return (
                    "स्पष्टीकरण:\n"
                    "इस चार्ट में आपकी खेती के कुल खर्च का सटीक विभाजन दर्शाया गया है। "
                    f"मजदूरी पर सबसे अधिक {labor_pct}% खर्च हुआ है। इसके बाद बीजों पर {seeds_pct}%, "
                    f"खाद पर {fert_pct}% और कीटनाशकों पर {pest_pct}% खर्च हुआ है।"
                )
            else:
                return (
                    "Explanation:\n"
                    "This chart illustrates the proportional breakdown of your total farm expenditure. "
                    f"Labor accounts for the highest single portion at {labor_pct}%, followed by Seeds ({seeds_pct}%), "
                    f"Fertilizer ({fert_pct}%), and Pesticides ({pest_pct}%)."
                )

        elif intent == "crop_protection":
            if language == "mr":
                return "पिकांच्या संरक्षणासाठी: सध्याच्या ढगाळ हवामानात बुरशीनाशक फवारणी वेळेवर करा आणि शेतात पाण्याचा निचरा योग्य ठेवा."
            elif language == "hi":
                return "फसल सुरक्षा: वर्तमान मौसम को देखते हुए फफूंदनाशक का छिड़काव करें और खेत में जल निकासी सुनिश्चित करें।"
            else:
                return "Crop Protection Advisory: Apply preventive fungicide during humid conditions and ensure proper field drainage."

        elif intent == "crop_prices":
            if language == "mr":
                return "पिकांचे बाजारभाव: आज पुणे बाजार समितीत कापसाचा सरासरी भाव ₹7,200 ते ₹7,800 प्रति क्विंटल आहे."
            elif language == "hi":
                return "मंडी भाव: आज पुणे मंडी में कपास का औसत भाव ₹7,200 से ₹7,800 प्रति क्विंटल है।"
            else:
                return "Market Prices: Current cotton trading average in Pune APMC is ₹7,200 - ₹7,800 per quintal."

        elif intent == "government_schemes":
            if language == "mr":
                return "सरकारी योजना: नमो शेतकरी महासन्मान निधी आणि प्रधानमंत्री पीक विमा योजनेसाठी नोंदणी सुरू आहे. जवळच्या केंद्राशी संपर्क साधा."
            elif language == "hi":
                return "सरकारी योजना: पीएम किसान सम्मान निधि और फसल बीमा योजना के अंतर्गत ऑनलाइन आवेदन चालू हैं।"
            else:
                return "Government Schemes: PM-KISAN 17th installment registration and PMFBY crop insurance portals are active."

        # Default fallback
        if language == "mr":
            return "तुमच्या प्रश्नासाठी आम्ही शेती माहिती तपासत आहोत. कृपया अधिक तपशील द्या."
        elif language == "hi":
            return "आपके प्रश्न के लिए हम कृषि डेटा का विश्लेषण कर रहे हैं। कृपया अधिक जानकारी दें।"
        else:
            return "DAV is analyzing your agricultural records. Please specify your crop or season."
