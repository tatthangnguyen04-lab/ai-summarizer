import os
import io
import re
import requests
from bs4 import BeautifulSoup
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
            for page in reader.pages:
                text = page.extract_text() or ""
                if text.strip():
                    pages_text.append(text)
            
            extracted_text = "\n\n".join(pages_text)
            
        elif filename.endswith(".txt") or filename.endswith(".md"):
            extracted_text = file.read().decode("utf-8", errors="ignore")
        else:
            return jsonify({"error": "Unsupported file type. Please upload a PDF or TXT file."}), 400

        if not extracted_text.strip():
            return jsonify({"error": "Could not extract text from document (file may be empty or scanned image)."}), 400

        return jsonify({
            "filename": file.filename,
            "text": extracted_text,
            "pageCount": page_count,
            "wordCount": len(extracted_text.split())
        })

    except Exception as e:
        print(f"Document parsing error: {e}")
        return jsonify({"error": f"Failed to parse document: {str(e)}"}), 500

@app.route("/scrape-url", methods=["POST"])
def scrape_url():
    """Fetch and parse clean body text from any public webpage URL."""
    try:
        data = request.get_json()
        if not data or "url" not in data:
            return jsonify({"error": "No URL provided"}), 400

        target_url = data["url"].strip()
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url

        # Standard browser headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9"
        }

        response = requests.get(target_url, headers=headers, timeout=12)
        
        if response.status_code in (401, 403):
            return jsonify({
                "error": "This webpage is protected by anti-bot verification or a paywall. Please copy and paste the text directly into the Text tab."
            }), 400

        if response.status_code != 200:
            return jsonify({
                "error": f"Unable to reach webpage (HTTP {response.status_code}). Please verify the link or paste the text directly."
            }), 400

        soup = BeautifulSoup(response.text, "html.parser")

        # Strip unneeded elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside", "form", "svg", "noscript", "iframe"]):
            element.decompose()

        # Extract title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find("h1"):
            title = soup.find("h1").get_text().strip()

        # Extract paragraphs from main content container
        article_container = soup.find("article") or soup.find("main") or soup.find("body")

        paragraphs = []
        if article_container:
            for p in article_container.find_all(["p", "h2", "h3", "li"]):
                p_text = p.get_text().strip()
                if len(p_text.split()) > 4:
                    paragraphs.append(p_text)

        cleaned_text = "\n\n".join(paragraphs)
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)

        if not cleaned_text.strip() or len(cleaned_text.split()) < 20:
            return jsonify({
                "error": "Could not extract readable article text from this page. Please copy and paste the text directly into the Text tab."
            }), 400

        return jsonify({
            "title": title or "Web Article",
            "url": target_url,
            "text": cleaned_text,
            "wordCount": len(cleaned_text.split())
        })

    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out while fetching webpage. Please try again or paste the text directly."}), 408
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network error: {str(e)}"}), 400
    except Exception as e:
        print(f"Scraping error: {e}")
        return jsonify({"error": f"Failed to extract article: {str(e)}"}), 500

    
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