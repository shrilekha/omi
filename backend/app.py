import os
import sys
from flask import Flask, send_from_directory, request, jsonify
from dotenv import load_dotenv

# Load .env from project root (one level up from backend/)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from db import init_db, save_submission
from email_sender import send_report_email

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')


@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.get_json(silent=True) or {}
    try:
        save_submission(data)
        send_report_email(data)
    except Exception as e:
        app.logger.error(f'Submission error: {e}')
    return jsonify({'status': 'ok'})


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'env': os.getenv('ENV', 'development')})


if __name__ == '__main__':
    init_db()
    debug = os.getenv('ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5050))
    print(f'\n  OMI running at http://localhost:{port}\n')
    app.run(debug=debug, port=port)
