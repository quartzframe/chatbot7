import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from google import genai

from chatbot_config import MODEL_NAME, SYSTEM_PROMPT

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not configured in the environment.")

client = genai.Client(api_key=api_key)


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Please enter a study-related question."}), 400

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=message,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "temperature": 0.2,
            },
        )

        answer = (response.text or "").strip()

        if not answer:
            answer = "I couldn't generate an answer. Please try your study question again."

        return jsonify({"answer": answer})

    except Exception:
        return jsonify({
            "error": "Sorry, I couldn't process your question right now. Please try again."
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
