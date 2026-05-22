from flask import Blueprint, request, jsonify
from backend.utils.gemini_analyzer import extract_receipt_data
from backend.utils.rule_engine import run_rule_engine
from backend.utils.groq_explainer import explain_result
import base64

receipt_bp = Blueprint('receipt', __name__)

@receipt_bp.route('/analyze-receipt', methods=['POST'])
def analyze():

    print("==== ROUTE HIT ====")

    try:

        print("FILES:", request.files)

        # ----------------------------------------
        # Step 1: Validate uploaded file
        # ----------------------------------------
        if 'receipt' not in request.files:
            print("No receipt key found")
            return jsonify({
                'error': 'No receipt image uploaded'
            }), 400

        file = request.files['receipt']

        print("FILE RECEIVED:", file.filename)

        if file.filename == '':
            print("Empty filename")
            return jsonify({
                'error': 'No file selected'
            }), 400

        allowed_types = [
            'image/jpeg',
            'image/png',
            'image/webp',
            'image/jpg'
        ]

        print("CONTENT TYPE:", file.content_type)

        if file.content_type not in allowed_types:
            print("Invalid type")
            return jsonify({
                'error': 'Invalid file type'
            }), 400

        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)

        print("FILE SIZE:", file_size)

        if file_size > 5 * 1024 * 1024:
            print("Too large")
            return jsonify({
                'error': 'File too large'
            }), 400

        # ----------------------------------------
        # Step 2: Read image bytes
        # ----------------------------------------
        image_bytes = file.read()
        image_data  = base64.b64encode(image_bytes).decode('utf-8')
        mime_type   = file.content_type

        print("IMAGE BYTES READ")

        # ----------------------------------------
        # Step 3: Gemini OCR → Structured JSON
        # Gemini's ONLY job here is data extraction
        # It does NOT decide if it's fraud
        # ----------------------------------------
        print("CALLING GEMINI OCR")

        ocr_result = extract_receipt_data(image_data, mime_type)

        print("GEMINI OCR RESULT:", ocr_result)

        if not ocr_result['success']:
            return jsonify({
                'error': ocr_result.get('error', 'OCR failed')
            }), 500

        receipt_data = ocr_result['data']

        # ----------------------------------------
        # Step 4: Rule Engine → Risk Score + Signals
        # Relative scoring, no hardcoded thresholds
        # ----------------------------------------
        print("RUNNING RULE ENGINE")

        engine_result = run_rule_engine(receipt_data)

        print("RULE ENGINE RESULT:", engine_result)

        # ----------------------------------------
        # Step 5: Groq LLM → Plain English Explanation
        # LLM's ONLY job is to explain the score
        # It does NOT re-decide fraud
        # ----------------------------------------
        print("CALLING GROQ EXPLAINER")

        explanation = explain_result(receipt_data, engine_result)

        print("GROQ EXPLANATION:", explanation)

        # ----------------------------------------
        # Step 6: Return full result to frontend
        # ----------------------------------------
        return jsonify({
            'success'     : True,
            'score'       : engine_result['score'],
            'verdict'     : engine_result['verdict'],
            'signals'     : engine_result['signals'],
            'extracted'   : receipt_data,
            'analysis'    : explanation
        }), 200

    except Exception as e:
        print("ROUTE ERROR:", e)
        return jsonify({
            'error': str(e)
        }), 500