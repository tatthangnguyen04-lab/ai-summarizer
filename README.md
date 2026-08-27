# ⚡ Briefly AI — Full-Stack AI Text, PDF & Web Summarization Engine

 End-to-end AI summarization platform made with **Flask**, **OpenRouter LLM**, **Server-Sent Events (SSE)**, **React 18**, and **Tailwind CSS**.

---

## 🌟 Key Features

- **Multi-Source Ingestion:**
  - **Raw Text:** Real-time text analysis, word counts, sample presets.
  - **PDF & Document Parsing:** Drag-and-drop file upload with in-memory text extraction using `pypdf`.
  - **Web Article Scraper:** Extracts article body text from public URL using `beautifulsoup4` and HTML sanitization (some urls don't work because the HTML is generated after to prevent scrapping -> dynamic SPAs with client-side rendering or anti-bot paywalls).
- **Real-Time Token Streaming:** Low-latency token generation via Server-Sent Events (SSE) + a client-side typewriter buffer for smoother rendering.
- **Customizable Output Control:** Dynamic parameters for output format (Bullet Points, TL;DR, Executive Brief), length (Short, Medium, Detailed), and tone (Professional, Casual, Academic).
- **Responsive Dark UI:** Responsive React 18 interface styled with modern Tailwind CSS utilities + clipboard integration.

---

## 🛠️ Tech Stack

- **Backend:** Python 3, Flask, Gunicorn, `pypdf`, `beautifulsoup4`, `requests`, `openai` SDK
- **Frontend:** React 18, Tailwind CSS, FontAwesome
- **LLM Engine:** OpenRouter Free Tier Inference API

---


## 🚀 Getting Started Locally

### 1. Clone the repository
git clone https://github.com/tatthangnguyen04-lab/ai-summarizer.git
cd ai-summarizer
python -m venv venv
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate
# Dependencies
pip install -r requirements.txt

# If no API key, get a key here, yes sign up  -> https://openrouter.ai/workspaces/default/keys
# Create a .env file in the root directory and put your key in
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Run app
python app.py

# Open http://127.0.0.1:5000 in your browser.




## 📦 Production Deployment (Render)

Deploy this application for free on [Render](https://render.com):

1. **Sign Up / Log In:** Go to [Render](https://render.com) and log in with your GitHub account.
2. **Create New Web Service:** Click the **"New +"** button at the top right and select **"Web Service"**.
3. **Connect Repository:** Select your `ai-summarizer` repository from the list.
4. **Configure Settings:**
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** `Free`
5. **Add Environment Variable:**
   - Click **"Advanced"** or scroll to the **"Environment Variables"** section.
   - Click **"Add Environment Variable"**.
   - Set **Key:** `OPENROUTER_API_KEY`
   - Set **Value:** *(paste your OpenRouter API key `sk-or-v1-...`)*
6. **Deploy:** Click **"Deploy Web Service"**. Render will build the container and provide your live HTTPS URL.


