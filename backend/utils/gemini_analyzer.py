import os
import json
import time
import base64
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.environ.get('GEMINI_API_KEY')
)

# ============================================================
# MODEL FALLBACK CHAIN
# If the first model is unavailable/rate-limited,
# automatically try the next one in order.
# gemini-2.5-flash  → newest, fastest, hits limits first
# gemini-2.0-flash  → stable fallback
# gemini-1.5-flash  → older but very reliable
# gemini-1.5-flash-8b → lightest model, almost never fails
# ============================================================
FALLBACK_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
]

OCR_PROMPT = """
You are an OCR engine. Your ONLY job is to extract
data from this receipt image and return it as JSON.

DO NOT analyze fraud. DO NOT give risk levels.
ONLY extract what you visually see.

Return ONLY this JSON format, nothing else:
{
    "is_receipt": true or false,
    "document_type": "receipt/bank_statement/payment_screenshot/qr_payment/unknown",
    "amount": <number or null>,
    "currency": "INR or USD etc or null",
    "date": "YYYY-MM-DD or null",
    "time": "HH:MM or null",
    "vendor_name": "string or null",
    "vendor_category": "grocery/restaurant/fuel/medical/construction/electronics/transfer/unknown",
    "transaction_id": "string or null",
    "payment_platform": "UPI/NEFT/IMPS/card/cash/unknown",
    "sender": "string or null",
    "receiver": "string or null",
    "tax_amount": <number or null>,
    "tax_percentage": <number or null>,
    "line_items_count": <number or null>,
    "image_quality": "good/poor/unreadable",
    "editing_artifacts": true or false,
    "taxable_amount": <number or null>,
    "missing_fields": ["list of fields that should exist but are absent"]
}

If any field is not visible, use null.
Return ONLY valid JSON. No explanation. No markdown fences.
"""

# ============================================================
# SINGLE MODEL ATTEMPT
# Returns parsed dict on success, raises exception on failure
# ============================================================
def _try_model(model_name: str, image_data: str, mime_type: str) -> dict:

    print(f"Trying model: {model_name}")

    image_part = types.Part.from_bytes(
        data      = base64.b64decode(image_data),
        mime_type = mime_type
    )

    response = client.models.generate_content(
        model    = model_name,
        contents = [OCR_PROMPT, image_part]
    )

    raw = response.text.strip()

    # Strip markdown fences if model adds them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())


# ============================================================
# MAIN FUNCTION WITH FALLBACK CHAIN
# Tries each model in order, stops at first success
# ============================================================
def extract_receipt_data(image_data: str, mime_type: str) -> dict:

    last_error = None

    for model_name in FALLBACK_MODELS:
        try:
            parsed = _try_model(model_name, image_data, mime_type)

            print(f"SUCCESS with model: {model_name}")

            return {
                'success': True,
                'data'   : parsed,
                'model'  : model_name
            }

        except Exception as e:
            error_str = str(e)
            last_error = error_str

            print(f"Model {model_name} failed: {error_str[:120]}")

            # 503 / 429 / UNAVAILABLE / RESOURCE_EXHAUSTED
            # → try next model immediately
            is_overload = any(code in error_str for code in [
                '503', '429',
                'UNAVAILABLE',
                'RESOURCE_EXHAUSTED',
                'quota',
                'rate limit',
                'high demand'
            ])

            if is_overload:
                time.sleep(1)
                continue

            # Any other error (bad API key, invalid image, etc.)
            # → no point trying other models, fail immediately
            print(f"Non-retryable error: {error_str[:200]}")
            return {
                'success': False,
                'error'  : f'OCR failed: {error_str[:200]}'
            }

    # All 4 models exhausted
    print(f"All models failed. Last error: {last_error}")
    return {
        'success': False,
        'error'  : (
            'All Gemini models are currently unavailable. '
            'Please try again in a few minutes.'
        )
    }