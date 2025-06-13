from flask import Blueprint, render_template, request, jsonify
import base64, io, os, google.generativeai as genai
from google.generativeai import types

# ── API KEYS ────────────────────────────────────────────────
STT_KEY  = os.getenv("GEMINI_STT_KEY",
                     "AIzaSyAqi76eiT6TrFL5dES37QO1S3i2ElIZLC0")
CHAT_KEY = os.getenv("GEMINI_CHAT_KEY",
                     "AIzaSyCkfF7hsE4V9HcV54Wf_fA5YF-wwmbHRac")

# Configure two separate genai sessions (one for each key)
genai.configure(api_key=STT_KEY)
stt_model = genai.GenerativeModel('gemini-2.0-flash')

chat_genai = genai
chat_genai.configure(api_key=CHAT_KEY)
chat_model = chat_genai.GenerativeModel('gemini-2.0-flash')

bp = Blueprint('voice', __name__, url_prefix='/voice')

@bp.route('/')
def assistant_page():
    """Render the standalone voice-assistant demo page"""
    return render_template('voice/assistant.html')

@bp.route("/process", methods=["POST"])
def process_text():
    prompt = request.form.get("prompt", "").strip()
    if not prompt:
        return jsonify(error="empty prompt"), 400

    chat_reply = chat_model.generate_content(prompt)
    return jsonify(reply_text=chat_reply.text)