from flask import Blueprint, request, jsonify
from backend.utils.chatbot import ask_chatbot

chatbot_bp = Blueprint('chatbot', __name__)


@chatbot_bp.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'reply': 'No request data received'
            }), 400

        question = data.get('question', '').strip()

        if not question:
            return jsonify({
                'success': False,
                'reply': 'Question cannot be empty'
            }), 400

        result = ask_chatbot(question)

        return jsonify(result)

    except Exception as e:
        print("CHATBOT ROUTE ERROR:", e)

        return jsonify({
            'success': False,
            'reply': 'Internal server error'
        }), 500