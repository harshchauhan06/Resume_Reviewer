from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import traceback
import re

app = Flask(__name__, static_folder="docs")
CORS(app)

# Load Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("⚠️ GROQ_API_KEY not set!")
else:
    print("Loaded Groq API key:", GROQ_API_KEY[:8] + "****")

# ----------------------------
# Frontend routes
# ----------------------------
@app.route("/")
def index():
    return send_from_directory("docs", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("docs", path)

# ----------------------------
# Backend API
# ----------------------------
@app.route("/feedback", methods=["POST"])
def feedback():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload provided"}), 400

        job_role = data.get("job_role", "").strip()
        resume_text = data.get("resume_text", "").strip()
        job_desc = data.get("job_desc", "").strip()

        if not resume_text or not job_role:
            return jsonify({"error": "Resume text and job role are required"}), 400

        # Clean text and truncate to safe length
        resume_text_clean = re.sub(r"\s+", " ", resume_text)[:4000]
        job_desc_clean = re.sub(r"\s+", " ", job_desc)[:1000]

        prompt = f"""
You are a career coach AI assistant. Review the following resume text and provide detailed feedback tailored for the job role: {job_role}.

Resume: {resume_text_clean}

Job Description: {job_desc_clean}

Analyze for:
- Missing skills relevant to the role
- Suggestions to improve formatting, clarity, and tone
- Highlight vague or redundant language
- Recommendations to tailor experience & achievements
- Provide section-wise feedback (Education, Experience, Skills, etc.)
"""

        # ✅ Correct Groq API request
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.1-8b-instant",  # ✅ valid Groq model
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800,
            "temperature": 0.7
        }

        # Debug logs
        print("Payload preview:", str(payload)[:500])
        response = requests.post(url, headers=headers, json=payload)
        print("Groq status:", response.status_code)
        print("Groq response preview:", response.text[:500])

        if response.status_code != 200:
            return jsonify({
                "error": f"Groq API error {response.status_code}",
                "details": response.text
            }), 500

        result = response.json()
        feedback_text = ""
        if "choices" in result and result["choices"]:
            feedback_text = result["choices"][0]["message"]["content"]
        else:
            return jsonify({"error": "No choices returned from Groq", "details": result}), 500

        return jsonify({"feedback": feedback_text})

    except Exception as e:
        print("Exception occurred:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/ping")
def ping():
    return "pong"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
