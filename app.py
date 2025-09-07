from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import traceback
import re

app = Flask(__name__)
CORS(app)

# Load Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("⚠️ GROQ_API_KEY not set!")
else:
    print("Loaded Groq API key:", GROQ_API_KEY[:8] + "****")

@app.route("/feedback", methods=["POST"])
def feedback():
    try:
        data = request.get_json()
        job_role = data.get("job_role", "").strip()
        resume_text = data.get("resume_text", "").strip()
        job_desc = data.get("job_desc", "").strip()

        if not resume_text or not job_role:
            return jsonify({"error": "Resume text and job role are required"}), 400

        # Clean up text: remove multiple spaces/newlines and truncate
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

        # Groq API request
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "groq/compound",  # ✅ correct model for your account
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
                "error": f"Groq error {response.status_code}",
                "details": response.text
            }), 500

        result = response.json()
        if "choices" in result and result["choices"]:
            feedback_text = result["choices"][0]["message"]["content"]
            return jsonify({"feedback": feedback_text})
        else:
            return jsonify({"error": "No choices returned from Groq", "details": result}), 500

    except Exception as e:
        print("Exception occurred:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/ping")
def ping():
    return "pong"

if __name__ == "__main__":
    app.run(debug=True)
