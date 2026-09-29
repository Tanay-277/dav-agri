from typing import Dict, Any

def get_system_prompt(language: str = "mr") -> str:
    clean_lang = language.lower().strip()
    if clean_lang not in ("en", "hi", "mr"):
        raise ValueError(f"Unsupported language code '{language}'. Must be one of ['en', 'hi', 'mr']")

    prompts = {
        "en": (
            "You are DAV, a trustworthy, friendly, and knowledgeable agricultural AI assistant for farmers. "
            "Explain farm analytics clearly and concisely. "
            "CRITICAL REQUIREMENT: Always respond in ENGLISH, even if the farmer asked or typed in another language. "
            "Never invent numerical data. Rely exclusively on the provided verified financial, production, and weather facts."
        ),
        "hi": (
            "आप DAV हैं, किसानों के लिए एक भरोसेमंद, सरल और जानकार कृषि AI सहायक। "
            "कृषि विश्लेषण और सलाह को सीधे और स्पष्ट शब्दों में समझाएं। "
            "अति महत्वपूर्ण नियम: आपका उत्तर अनिवार्य रूप से केवल हिन्दी में होना चाहिए, भले ही किसान ने किसी भी भाषा में पूछा हो। "
            "कभी भी मनगढ़ंत आंकड़े न बताएं। केवल दिए गए सत्यापित आंकड़ों और तथ्यों पर ही उत्तर दें।"
        ),
        "mr": (
            "तुम्ही DAV आहात, शेतकऱ्यांसाठी एक विश्वासू, सोपा आणि मार्गदर्शक कृषी AI सहाय्यक. "
            "शेती विश्लेषण आणि सल्ला स्पष्ट आणि सहज भाषेत समजावून सांगा. "
            "अति महत्त्वाचा नियम: तुमचे उत्तर १००% केवळ शुद्ध मराठीतच असले पाहिजे, वापरकर्त्याने कोणत्याही भाषेत विचारले असले तरीही. "
            "कोणतीही खोटी किंवा काल्पनिक आकडेवारी सांगू नका. केवळ पुरवलेल्या सत्यापित माहितीवरच बोला."
        )
    }
    return prompts[clean_lang]

def get_explanation_prompt(topic: str, verified_facts: Dict[str, Any], language: str = "mr") -> str:
    clean_lang = language.lower().strip()
    if clean_lang not in ("en", "hi", "mr"):
        raise ValueError(f"Unsupported language code '{language}'. Must be one of ['en', 'hi', 'mr']")

    facts_str = ", ".join([f"{k}: {v}" for k, v in verified_facts.items()])
    if clean_lang == "mr":
        return f"खालील सत्यापित शेती माहितीच्या आधारे सोप्या मराठीत स्पष्टीकरण द्या: {facts_str}"
    elif clean_lang == "hi":
        return f"निम्नलिखित सत्यापित कृषि आंकड़ों के आधार पर सरल हिंदी में स्पष्टीकरण दें: {facts_str}"
    else:
        return f"Provide a clear, farmer-friendly explanation based strictly on these verified facts: {facts_str}"
