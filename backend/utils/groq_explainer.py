"""
groq_explainer.py
-----------------
Groq LLM's ONLY job:
  Take the rule engine score + signals and explain
  them in plain, simple English.

  It does NOT re-decide if something is fraud.
  It does NOT override the rule engine score.
  It ONLY explains what the rule engine found.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

def explain_result(receipt_data: dict, engine_result: dict) -> str:

    score   = engine_result.get("score", 0)
    verdict = engine_result.get("verdict", "LOW_RISK")
    signals = engine_result.get("signals", [])

    # Format signals as a readable list
    if signals:
        signals_text = "\n".join(f"- {s}" for s in signals)
    else:
        signals_text = "- No anomalies detected"

    # Format extracted receipt details
    amount   = receipt_data.get("amount")
    category = receipt_data.get("vendor_category", "unknown")
    vendor   = receipt_data.get("vendor_name", "Unknown vendor")
    date     = receipt_data.get("date", "Unknown date")
    platform = receipt_data.get("payment_platform", "Unknown")

    prompt = f"""
You are a fraud analyst assistant for an Indian bank.

A receipt was submitted and our fraud detection system
has already calculated a risk score. Your job is ONLY
to explain these results in simple, friendly language.

DO NOT recalculate or override the score.
DO NOT add new fraud signals that aren't listed.
ONLY explain what is given below.

=== RECEIPT DETAILS ===
Vendor       : {vendor}
Category     : {category}
Amount       : ₹{amount}
Date         : {date}
Platform     : {platform}

=== FRAUD DETECTION RESULT ===
Risk Score   : {score}/100
Verdict      : {verdict}
Triggered Signals:
{signals_text}

=== YOUR TASK ===
Write a clear, simple explanation (under 120 words) for
a bank customer or fraud analyst.

Structure your response exactly like this:

🔍 Receipt Summary:
[One sentence describing what the receipt is]

⚠️ Risk Assessment: {verdict.replace("_", " ")} ({score}/100)
[One sentence explaining what this score means]

📋 Reasons:
[List only the triggered signals in plain English,
 no technical jargon. If no signals, say "No issues found."]

💡 Recommendation:
[One sentence: what should the analyst or customer do next]
"""

    try:
        response = groq_client.chat.completions.create(
            model    = "llama-3.3-70b-versatile",
            messages = [
                {
                    "role"   : "system",
                    "content": (
                        "You are a concise fraud analyst. "
                        "Explain results clearly. "
                        "Never override the given score. "
                        "Keep response under 120 words."
                    )
                },
                {
                    "role"   : "user",
                    "content": prompt
                }
            ],
            max_tokens  = 300,
            temperature = 0.3   # Low temperature = consistent, factual
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Groq Error: {e}")

        # Fallback: return a plain explanation without Groq
        fallback = (
            f"🔍 Receipt Summary: Receipt from {vendor} "
            f"for ₹{amount} on {date} via {platform}.\n\n"
            f"⚠️ Risk Assessment: {verdict.replace('_', ' ')} "
            f"({score}/100)\n\n"
            f"📋 Reasons:\n" +
            "\n".join(f"• {s.split('(')[0].strip()}" for s in signals)
            if signals else "• No issues found."
        )
        return fallback