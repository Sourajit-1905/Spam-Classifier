from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pickle
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.preprocess import transform_message

# Point Flask to the frontend folder for static files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, 'model', 'model.pkl'), 'rb') as f:
    model = pickle.load(f)

with open(os.path.join(BASE_DIR, 'model', 'vectorizer.pkl'), 'rb') as f:
    vectorizer = pickle.load(f)

with open(os.path.join(BASE_DIR, 'model', 'threshold.json'), 'r') as f:
    threshold_data = json.load(f)
    THRESHOLD = threshold_data['threshold']


# Serve landing page as the homepage
@app.route('/')
def serve_landing():
    return send_from_directory(FRONTEND_DIR, 'landing.html')


# Serve any other frontend file (index.html, css, js, assets)
@app.route('/<path:filename>')
def serve_static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400

    message = data['message'].strip()

    if not message:
        return jsonify({"error": "Message is empty"}), 400

    cleaned = transform_message(message)
    vector = vectorizer.transform([cleaned]).toarray()  # convert sparse -> dense
    probability = model.predict_proba(vector)[0][1]
    prediction = 1 if probability >= THRESHOLD else 0

    return jsonify({
        "prediction": prediction,
        "probability": round(float(probability), 4)
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)