# intents.py

INTENTS = {

    "greeting": [
        "hello",
        "hi",
        "hey",
        "good morning",
        "good evening"
    ],

    "refund": [
        "refund",
        "money back",
        "return",
        "return my money",
        "refund status"
    ],

    "payment": [
        "payment",
        "upi",
        "credit card",
        "debit card",
        "transaction",
        "failed payment"
    ],

    "cancellation": [
        "cancel order",
        "cancel",
        "delete order",
        "remove order",
        "cancel my order"
    ],

    "order_status": [
        "track order",
        "track my order",
        "where is my order",
        "order status",
        "status of my order"
    ],

    "delivery": [
        "delivery",
        "shipping",
        "dispatch",
        "courier"
    ]

}


def detect_intent(message):

    message = message.lower()

    scores = {}

    for intent, keywords in INTENTS.items():

        scores[intent] = 0

        for keyword in keywords:

            if keyword in message:

                scores[intent] += len(keyword.split())

    best_intent = max(scores, key=scores.get)

    if scores[best_intent] == 0:

        return "unknown"

    return best_intent