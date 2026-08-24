import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

@app.route("/")
def home():
    # Serves the frontend UI from templates/index.html
    return render_template("index.html")

@app.route("/summarize", methods=["POST"])
def summarize():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        text = data.get("text", "")
        format_type = data.get("format", "bullets")
        length = data.get("length", "medium")
        tone = data.get("tone", "professional")

        if not text.strip():
            return jsonify({"error": "No text provided"}), 400

        system_instruction = (
            f"You are a skilled AI text summarizer. "
            f"Format requirements: {format_type}. "
            f"Length: {length}. "
            f"Tone: {tone}. "
            f"Be precise, clear, and direct."
        )

        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
            ]
        )

        summary = response.choices[0].message.content
        return jsonify({"summary": summary})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)