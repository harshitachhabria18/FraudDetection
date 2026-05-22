from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os

# Import blueprint
from backend.routes.predict_route import predict_bp
from backend.routes.receipt import receipt_bp
from backend.routes.batch_route import batch_bp
from backend.routes.chatbot_route import chatbot_bp


# Initialize Flask app
app = Flask(__name__,
            template_folder='../templates',  
            static_folder='../static')        

# Enable CORS
CORS(app)

# Register blueprint
app.register_blueprint(predict_bp)
app.register_blueprint(receipt_bp) 
app.register_blueprint(batch_bp)
app.register_blueprint(chatbot_bp)

# Serve Frontend
@app.route('/')
def home():
    return render_template('index.html')

# Health check route
@app.route('/health')
def health():
    return jsonify({
        'status': 'running',
        'message': 'Fraud Detection API is live'
    }), 200

# Handle 404 errors
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Route not found'
    }), 404

# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return jsonify({
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)