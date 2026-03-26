"""Gemini AI service — symptom checker with graceful fallback."""

import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Try to initialize Gemini
_model = None
try:
    if settings.GEMINI_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _model = genai.GenerativeModel("gemini-2.0-flash-exp")
        logger.info("Gemini AI initialized successfully")
    else:
        logger.warning("GEMINI_API_KEY not set — AI features will use fallback")
except Exception as e:
    logger.warning(f"Gemini init failed: {e} — using fallback")


def _build_prompt(
    symptoms: str, language: str,
    patient_age: int | None, known_conditions: list[str] | None
) -> str:
    conditions_str = ", ".join(known_conditions) if known_conditions else "None"
    return f"""You are a medical assistant helping rural patients in India.
Patient language: {language}
Patient age: {patient_age if patient_age else 'unknown'}
Known conditions: {conditions_str}
Symptoms: {symptoms}

Respond ONLY in valid JSON, no markdown, no extra text:
{{
  "possible_condition": "specific condition name in English",
  "urgency": "low|medium|high",
  "urgency_color": "green|yellow|red",
  "advice": "specific practical advice in {language} language — minimum 2-3 sentences with actual steps the patient should take",
  "see_doctor_now": true or false,
  "call_emergency": true or false,
  "disclaimer": "short disclaimer in {language}"
}}

Rules:
- urgency=high and call_emergency=true ONLY for life-threatening symptoms like heart attack, stroke, severe bleeding, difficulty breathing
- For heart attack symptoms: urgency=high, call_emergency=true, advice must say call 112 immediately
- For fever: urgency=low or medium, give specific advice like rest, drink fluids, take paracetamol if above 38C
- For nosebleed: urgency=low, advice must say pinch nose for 10 minutes, lean forward, apply cold cloth
- advice must ALWAYS be specific and practical, never just say "consult a doctor" without real guidance
- Respond in the patient's language ({language}) for the advice and disclaimer fields"""


def _get_fallback_response(symptoms: str, language: str) -> dict:
    """Fallback when Gemini is unavailable."""
    advice_map = {
        "hi": "कृपया नजदीकी डॉक्टर से मिलें। यह AI सलाह है, पेशेवर चिकित्सा परामर्श का विकल्प नहीं है।",
        "en": "Please visit a nearby doctor. This is AI advice, not a substitute for professional medical consultation.",
        "ta": "அருகிலுள்ள மருத்துவரை அணுகவும். இது AI ஆலோசனை, தொழில்முறை மருத்துவ ஆலோசனைக்கு மாற்று அல்ல.",
        "te": "దయచేసి సమీపంలోని వైద్యుడిని సందర్శించండి. ఇది AI సలహా, వృత్తిపరమైన వైద్య సంప్రదింపునకు ప్రత్యామ్నాయం కాదు.",
        "mr": "कृपया जवळच्या डॉक्टरांना भेटा. हा AI सल्ला आहे, व्यावसायिक वैद्यकीय सल्ल्याचा पर्याय नाही.",
    }
    disclaimer_map = {
        "hi": "यह AI-आधारित सुझाव है। कृपया डॉक्टर से परामर्श लें।",
        "en": "This is an AI-based suggestion. Please consult a doctor.",
        "ta": "இது AI அடிப்படையிலான பரிந்துரை. மருத்துவரை அணுகவும்.",
        "te": "ఇది AI ఆధారిత సూచన. దయచేసి వైద్యుడిని సంప్రదించండి.",
        "mr": "हा AI-आधारित सल्ला आहे. कृपया डॉक्टरांचा सल्ला घ्या.",
    }
    return {
        "possible_condition": "Requires professional assessment",
        "urgency": "medium",
        "urgency_color": "yellow",
        "advice": advice_map.get(language, advice_map["en"]),
        "see_doctor_now": True,
        "call_emergency": False,
        "disclaimer": disclaimer_map.get(language, disclaimer_map["en"]),
    }


async def check_symptoms(
    symptoms: str,
    language: str = "hi",
    patient_age: int | None = None,
    known_conditions: list[str] | None = None,
) -> dict:
    """Run symptom check via Gemini, fallback if unavailable."""
    if not _model:
        return _get_fallback_response(symptoms, language)

    try:
        prompt = _build_prompt(symptoms, language, patient_age, known_conditions)
        response = await _model.generate_content_async(prompt)
        text = response.text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        return json.loads(text)
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return _get_fallback_response(symptoms, language)
