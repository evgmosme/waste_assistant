"""
WasteAssistant backend.

Flask app that combines:
• OpenAI Vision + Chat (gpt-4o-mini)
• Session-scoped conversation memory
• Optional image upload (JPEG compressed on the fly)

Env vars (loaded from .env or injected by Cloud Run):
    api_key      – OpenAI key (sk-…)
    secret_key   – Flask session secret
"""

from datetime import timedelta
import base64
import io
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session
from flask_session import Session
from PIL import Image
import openai
import tiktoken

# ── configuration ───────────────────────────────────────────────────────

load_dotenv()  # read .env if present

api_key = os.getenv("api_key")
secret_key = os.getenv("secret_key")

app = Flask(__name__)

if not secret_key:  # fail fast in container logs
    raise ValueError("No secret key set in the environment variables.")
app.secret_key = secret_key

app.config.update(
    SESSION_TYPE="filesystem",
    SESSION_PERMANENT=False,
    SESSION_FILE_DIR="./flask_session",
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
)
Session(app)

client = openai.OpenAI(api_key=api_key)

# ── system prompts ──────────────────────────────────────────────────────

with open("./model_instructions/gpt_instructions_en.txt") as f:
    instructions_en = f.read()
with open("./model_instructions/gpt_instructions_fi.txt") as f:
    instructions_fi = f.read()


def get_instructions(lang: str) -> str:
    """Return the system prompt matching the UI language."""
    return instructions_fi if lang == "fi" else instructions_en


# ── helpers ─────────────────────────────────────────────────────────────


def compress_image(file_storage, max_size=(500, 500), quality=75) -> io.BytesIO:
    """
    Resize & recompress an uploaded image to save tokens/bandwidth.

    Returns an in-memory JPEG (BytesIO).
    """
    img = Image.open(file_storage)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    return buf


def count_tokens(messages, model: str = "gpt-4o-mini") -> int:
    """
    Approximate token usage for a list of OpenAI messages.

    Only used for debugging – not required by the main flow.
    """
    enc = tiktoken.encoding_for_model(model)
    total = 0
    for m in messages:
        content = m["content"]
        if isinstance(content, list):
            txt = next((item["text"] for item in content if "text" in item), "")
            total += len(enc.encode(txt))
        elif isinstance(content, str):
            total += len(enc.encode(content))
    return total


# ── routes ──────────────────────────────────────────────────────────────


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    """
    Handle a question (text and/or image).

    Expects multipart/form-data with:
        • query   – text (optional when image present)
        • image   – file upload (optional)
        • language– UI language code ('en' default)
    Returns JSON string with the assistant reply.
    """
    query = request.form.get("query")

    if not query and "image" not in request.files:
        return jsonify({"error": "No query or image provided"}), 400

    session.setdefault("language", request.form.get("language", "en"))
    session.setdefault("conversation", [])  # start or resume history

    if query:
        session["conversation"].append({"role": "user", "content": query})

    messages = [{"role": "system", "content": get_instructions(session["language"])}]
    messages.extend(session["conversation"])

    if "image" in request.files:
        img_b64 = base64.b64encode(
            compress_image(request.files["image"]).read()
        ).decode()
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": query or "Image provided."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_b64}", "detail": "low"},
                    },
                ],
            }
        )
    else:
        messages.append({"role": "user", "content": query})

    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=messages, temperature=1, max_tokens=400
    )
    answer = response.choices[0].message.content

    session["conversation"].append({"role": "assistant", "content": answer})
    return jsonify(answer)


@app.route("/reset", methods=["POST"])
def reset_conversation():
    """Clear session memory (conversation + settings)."""
    session.clear()
    return jsonify({"message": "Conversation reset."})


# ── entry-point ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8086)
