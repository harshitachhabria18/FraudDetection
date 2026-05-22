import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

SYSTEM_PROMPT = """
You are an AI Fraud Detection Assistant.

You ONLY answer questions related to:
- transaction fraud
- financial scams
- phishing
- cyber fraud
- banking fraud
- UPI scams
- online fraud
- suspicious payments
- fraud prevention
- digital payment security
- fraud detection systems

If the user asks anything unrelated,
politely refuse and say:
'I can only help with fraud-related questions.'

Keep answers:
- clear
- professional
- beginner friendly
- concise
"""


def ask_chatbot(user_question):

    try:

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_question
                }
            ],

            temperature=0.3,
            max_tokens=300
        )

        reply = completion.choices[0].message.content

        return {
            "success": True,
            "reply": reply
        }

    except Exception as e:

        print("CHATBOT ERROR:", e)

        return {
            "success": False,
            "reply": "Chatbot is currently unavailable"
        }