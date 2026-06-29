import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

SYSTEM_PROMPT = """
You are SupportGenie AI.

You are a smart AI assistant capable of answering:

• Customer support questions
• Programming questions
• Python, Java, C++
• AI and Machine Learning
• Web Development
• Database
• Cloud Computing
• Interview preparation
• Aptitude explanations
• General knowledge

Rules:

1. Be polite and professional.
2. Give accurate answers.
3. Format answers using Markdown.
4. Use code blocks whenever writing code.
5. Use bullet points when appropriate.
6. Explain concepts in simple language.
7. If the question is about customer support, answer like a support agent.
8. If the question is technical, answer like an experienced software engineer.
9. If you don't know something, say so instead of inventing information.
"""


def get_ai_response(user_message, history=None):

    if history is None:
        history = []

    conversation = SYSTEM_PROMPT + "\n\n"

    for chat in history:

        sender = "Customer" if chat["sender"] == "user" else "SupportGenie AI"

        conversation += f"{sender}: {chat['message']}\n"

    conversation += f"\nCustomer: {user_message}\nSupportGenie AI:"

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=conversation
        )

        return response.text

    except Exception as e:

        error = str(e)

        if "503" in error:
            return "⚠️ AI is currently busy. Please try again in a few moments."

        return f"AI Error: {error}"