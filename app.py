import os
import io
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload-document", methods=["POST"])
def upload_document():
    """Extract text from uploaded PDF or TXT file."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        filename = file.filename.lower()
        extracted_text = ""
        page_count = 1

        if filename.endswith(".pdf"):
            pdf_stream = io.BytesIO(file.read())
            reader = PdfReader(pdf_stream)
            page_count = len(reader.pages)
            
            pages_text = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages_text.append(text)
            
            extracted_text = "\n\n".join(pages_text)
            
        elif filename.endswith(".txt") or filename.endswith(".md"):
            extracted_text = file.read().decode("utf-8", errors="ignore")
        else:
            return jsonify({"error": "Unsupported file type. Please upload a PDF or TXT file."}), 400

        if not extracted_text.strip():
            return jsonify({"error": "Could not extract text from document (it may be empty or scanned image without selectable text)."}), 400

        return jsonify({
            "filename": file.filename,
            "text": extracted_text,
            "pageCount": page_count,
            "wordCount": len(extracted_text.split())
        })

    except Exception as e:
        print(f"Document parsing error: {e}")
        return jsonify({"error": f"Failed to parse document: {str(e)}"}), 500

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