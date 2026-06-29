from intents import detect_intent
from faq import get_response
from gemini_service import get_ai_response


def chatbot_response(user_message):

    intent = detect_intent(user_message)

    faq_response = get_response(intent)

    if faq_response:
        return intent, faq_response, "FAQ"

    ai_response = get_ai_response(user_message)

    return "ai", ai_response, "Gemini"