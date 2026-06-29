import json

# Load FAQ data
with open("faq.json", "r", encoding="utf-8") as file:
    faq_data = json.load(file)


def get_response(intent):

    # If intent is unknown, let Gemini handle it
    if intent == "unknown":
        return None

    if intent in faq_data:
        return faq_data[intent]["response"]

    return None