from __future__ import annotations

from text_to_speech.languages import LANGUAGE_CODE_MAP
from text_to_speech.schemas import InsightType

TEMPLATES: dict[InsightType, dict[str, str]] = {
    InsightType.CURRENT_WEATHER: {
        "en": "Current weather in {location}: {temperature} degrees. Rain probability is {rain_probability} percent.",
        "hi": "{location} mein mausam: temperature {temperature} degree. Barish ki sambhavana {rain_probability} percent.",
        "ta": "{location} lairka nilam: temperature {temperature} digri. Mazhai eivvathu {rain_probability} satam.",
        "te": "{location} lo velli nilam: temperature {temperature} digri. Baga varsham euvathu {rain_probability} sata.",
        "kn": "{location} dalli velli nilam: temperature {temperature} digri. Male baruvadhu {rain_probability} shataka.",
        "mr": "{location} madhye hava: temperature {temperature} degree. Pausachi sambhavana {rain_probability} shatka.",
        "bn": "{location} e er bhalo: temperature {temperature} digri. Barir dar {rain_probability} shotosh.",
    },
    InsightType.FORECAST: {
        "en": "Tomorrow in {location}: {temperature_min} to {temperature_max} degrees. Rain probability is {rain_probability} percent.",
        "hi": "Kal {location} mein: temperature {temperature_min} se {temperature_max} degree tak. Barish ki sambhavana {rain_probability} percent.",
        "ta": "Naalai {location} la: temperature {temperature_min} thadangu {temperature_max} digri. Mazhai eivvathu {rain_probability} satam.",
        "te": "Naalai {location} lo: temperature {temperature_min} nundi {temperature_max} digri. Baga varsham euvathu {rain_probability} sata.",
        "kn": "Naali {location} dalli: temperature {temperature_min} inda {temperature_max} digri. Male baruvadhu {rain_probability} shataka.",
        "mr": "Udya {location} madhye: temperature {temperature_min} pasoon {temperature_max} degree. Pausachi sambhavana {rain_probability} shatka.",
        "bn": "Kal {location} e: temperature {temperature_min} theke {temperature_max} digri. Barir dar {rain_probability} shotosh.",
    },
    InsightType.RAIN_PROBABILITY: {
        "en": "Rain probability in {location} is {rain_probability} percent. Expected rainfall is {rainfall} millimeters.",
        "hi": "{location} mein barish ki sambhavana {rain_probability} percent hai. Ausat barish {rainfall} millimeter hogi.",
        "ta": "{location} la mazhai eivvathu {rain_probability} satam. Neruneru mazhai {rainfall} millimeters.",
        "te": "{location} lo baga varsham euvathu {rain_probability} sata. Nirdishta varsham {rainfall} millimeters.",
        "kn": "{location} dalli male baruvadhu {rain_probability} shataka. Nirdishta male {rainfall} millimeters.",
        "mr": "{location} madhye pausachi sambhavana {rain_probability} shatka aahe. Ausat paus {rainfall} millimeters.",
        "bn": "{location} e barir dar {rain_probability} shotosh. Porjonto baris {rainfall} milimitre.",
    },
    InsightType.TEMPERATURE: {
        "en": "Temperature in {location} is {temperature} degrees. It feels {temperature_feeling}.",
        "hi": "{location} mein temperature {temperature} degree hai. Yaha garam ya thanda mehsoos hota hai.",
        "ta": "{location} la temperature {temperature} digri. Anthu {temperature_feeling} feel aaguthu.",
        "te": "{location} lo temperature {temperature} digri. Akkada {temperature_feeling} anipisthundi.",
        "kn": "{location} dalli temperature {temperature} digri. Alli {temperature_feeling} thorgide.",
        "mr": "{location} madhye temperature {temperature} degree aahe. Titha {temperature_feeling} vatta yeyte.",
        "bn": "{location} e temperature {temperature} digri. Okhane {temperature_feeling} vabte.",
    },
    InsightType.COMPARISON: {
        "en": "{metric} in {location_a} is {value_a}. In {location_b}, it is {value_b}. The difference is {difference}.",
        "hi": "{location_a} mein {metric} {value_a} hai. {location_b} mein yeh {value_b} hai. Antar {difference} hai.",
        "ta": "{location_a} la {metric} {value_a}. {location_b} la athu {value_b}. Vidham {difference}.",
        "te": "{location_a} lo {metric} {value_a}. {location_b} lo adi {value_b}. Varthakam {difference}.",
        "kn": "{location_a} dalli {metric} {value_a}. {location_b} dalli adhu {value_b}. Vellakam {difference}.",
        "mr": "{location_a} madhye {metric} {value_a} aahe. {location_b} madhye he {value_b} aahe. Antar {difference} aahe.",
        "bn": "{location_a} e {metric} {value_a}. {location_b} e ta {value_b}. Fark {difference}.",
    },
    InsightType.TREND: {
        "en": "{metric} is {direction}. {magnitude} over the last {period}.",
        "hi": "{metric} {direction} ja raha hai. Pichle {period} mein {magnitude} hua hai.",
        "ta": "{metric} {direction} poguthu. Munthriya {period} la {magnitude} aayirukku.",
        "te": "{metric} {direction} diguthundi. Gattina {period} lo {magnitude} ayindi.",
        "kn": "{metric} {direction} hoguttade. Kala {period} dalli {magnitude} aagide.",
        "mr": "{metric} {direction} zala aahe. Kala {period} madhye {magnitude} jhala aahe.",
        "bn": "{metric} {direction} hocche. Shoshor {period} e {magnitude} hoyeche.",
    },
    InsightType.WARNING: {
        "en": "Warning: {message}. Please take action: {action}.",
        "hi": "Satarkee: {message}. Kripya karein: {action}.",
        "ta": "Ehozhai: {message}. Dayai seyyum: {action}.",
        "te": "Hethur: {message}. Daye chestu: {action}.",
        "kn": "Ecchari: {message}. Dayavittu: {action}.",
        "mr": "Satarkee: {message}. Krupa karee: {action}.",
        "bn": "Chetona: {message}. Daya kore: {action}.",
    },
    InsightType.CLARIFICATION: {
        "en": "Please clarify: {question}. Options: {options}.",
        "hi": "Kripya spasht karein: {question}. Vikalp: {options}.",
        "ta": "Dayai therivu seyyum: {question}. Vivasthigal: {options}.",
        "te": "Krupayina gurthinandi: {question}. Aayakam: {options}.",
        "kn": "Krpavagi spashtapadisi: {question}. Vasyakthigalu: {options}.",
        "mr": "Krpaya spasht karee: {question}. Parikarma: {options}.",
        "bn": "Krupa kore sposto kore: {question}. Bikalpo: {options}.",
    },
    InsightType.UNSUPPORTED: {
        "en": "I cannot answer that. I can help with weather, rainfall, soil moisture, yield, and recommendations.",
        "hi": "Main iska jawab nahi de sakta. Main mausam, barish, mitti, output aur salah mein madad kar sakta hoon.",
        "ta": "Adhan pathil katti vendam. Nilam, mazhai, man, varavu matrum aalochana thavari enak kavalayam.",
        "te": "Adi javab echadam valla. Velli, varsham, manam, samputo, salaha ivatalaku sahaya cheyagalanu.",
        "kn": "Adakke uttara nidala. Velli, male, bhoomi, output, salahe ivugalige sahayavannu maadabahudu.",
        "mr": "Hee uttar dete nahi. Hava, paus, mati, utpanna, salahyat madat karu shakto.",
        "bn": "Shei uttor dite parchi na. Hoyar, baris, mati, fal, salah e jogotay sahajjo kore pari.",
    },
    InsightType.RECOMMENDATION: {
        "en": "Recommendation: {action}. Reason: {reason}.",
        "hi": "Salah: {action}. Kaaran: {reason}.",
        "ta": "Aalochana: {action}. Kaaranam: {reason}.",
        "te": "Salaha: {action}. Karanam: {reason}.",
        "kn": "Salahe: {action}. Kaaran: {reason}.",
        "mr": "Salaha: {action}. Kaaran: {reason}.",
        "bn": "Salah: {action}. Karone: {reason}.",
    },
    InsightType.YIELD_REPORT: {
        "en": "{crop} yield in {location} is {yield_value} kilograms per hectare. {comparison}.",
        "hi": "{location} mein {crop} ki utpatti {yield_value} kilo prati hectare hai. {comparison}.",
        "ta": "{location} la {crop} varavu {yield_value} kilo prati hectare. {comparison}.",
        "te": "{location} lo {crop} samputo {yield_value} kilo prati hectare. {comparison}.",
        "kn": "{location} dalli {crop} output {yield_value} kilo prati hectare. {comparison}.",
        "mr": "{location} madhye {crop} chi utpatti {yield_value} kilo prati hectare. {comparison}.",
        "bn": "{location} e {crop} fal {yield_value} kilo prati hectare. {comparison}.",
    },
    InsightType.SOIL_MOISTURE: {
        "en": "Soil moisture in {location} is {moisture_value} percent. {status}.",
        "hi": "{location} mein mitti mein paani {moisture_value} percent hai. {status}.",
        "ta": "{location} la man nilam {moisture_value} sathamaanam. {status}.",
        "te": "{location} lo manam nilam {moisture_value} sathamaanam. {status}.",
        "kn": "{location} dalli bhoomi niraya {moisture_value} shataka. {status}.",
        "mr": "{location} madhye matitil paani {moisture_value} shatka aahe. {status}.",
        "bn": "{location} e matir pani {moisture_value} shotosh. {status}.",
    },
}

TEMPERATURE_FEELING = {
    "en": {"cold": "cold", "hot": "hot", "normal": "normal"},
    "hi": {"cold": "thanda", "hot": "garam", "normal": "normal"},
    "ta": {"cold": "kuliru", "hot": "vechu", "normal": "nilai"},
    "te": {"cold": "enduku", "hot": "veedu", "normal": "samam"},
    "kn": {"cold": "tanna", "hot": "bisi", "normal": "sama"},
    "mr": {"cold": "thanda", "hot": "garam", "normal": "normal"},
    "bn": {"cold": "thanda", "hot": "garam", "normal": "normal"},
}

TREND_DIRECTION = {
    "en": {"up": "increasing", "down": "decreasing", "stable": "stable"},
    "hi": {"up": "badh raha hai", "down": "ghat raha hai", "stable": "sthir hai"},
    "ta": {"up": "peruguthu", "down": "kuraiguthu", "stable": "nilai"},
    "te": {"up": "peruguthundi", "down": "kuraiguthundi", "stable": "sthir"},
    "kn": {"up": "hechchuttade", "down": "kugguttade", "stable": "sthira"},
    "mr": {"up": "vadhtoy", "down": "khadtoy", "stable": "sthir aahe"},
    "bn": {"up": "barteche", "down": "komteche", "stable": "sthira"},
}

WARNING_TEMPLATES = {
    "low_rainfall": {
        "en": "Rainfall is below normal. Irrigate your crops.",
        "hi": "Barish normal se kam hai. Khet ko sinchai karein.",
        "ta": "Mazhai nilai kku kku aayirukku. Vayalukku neer seyyum.",
        "te": "Varsham saman kante takkuva. Panta neeru pettandi.",
        "kn": "Male samanakinta kdu. Benki neeru haku.",
        "mr": "Paus normal peksha kami aahe. Shetkachi sinchanee kara.",
        "bn": "Baris normal cheye kom. Dhaner jonno sinchon kore.",
    },
    "high_temperature": {
        "en": "Temperature is high. Work early morning.",
        "hi": "Temperature bahut high hai. Subah kaam karein.",
        "ta": "Temperature adhigama irukku. Kaalai eram seyyum.",
        "te": "Temperature atidiga undi. Udaya seyandi.",
        "kn": "Temperature hechchide. Belleya kelasa maadu.",
        "mr": "Temperature vegal aahe. Sakali kam kara.",
        "bn": "Tap beshi hoyeche. Sokale kaj kore.",
    },
    "low_soil_moisture": {
        "en": "Soil moisture is low. Irrigate now.",
        "hi": "Mitti mein paani kam hai. Abhi sinchai karein.",
        "ta": "Man nilam kammi irukku. Ippadikku neer seyyum.",
        "te": "Manam nilam takkuva. Ippudu neeru pettandi.",
        "kn": "Bhoomi niraya kdu. Ivalu neeru haku.",
        "mr": "Matitil paani kami aahe. Aaj sinchanee kara.",
        "bn": "Matir pani kom. Ekhon sinchon kore.",
    },
}


def get_template(insight_type: InsightType, language: str) -> str:
    lang = LANGUAGE_CODE_MAP.get(language.lower(), language.lower())
    templates = TEMPLATES.get(insight_type, {})
    return templates.get(lang, templates.get("en", ""))
