import json


def load_faq():

    with open("faq.json", "r", encoding="utf-8") as file:

        return json.load(file)


faq_data = load_faq()


def get_response(intent):

    if intent in faq_data:

        return faq_data[intent]["response"]

    return faq_data["unknown"]["response"]