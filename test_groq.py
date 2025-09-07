import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "model": "llama3-70b-8192",  # stable Groq model
    "messages": [
        {"role": "user", "content": "Write a 2-sentence summary of why Python is good for data science."}
    ],
    "max_tokens": 150
}

response = requests.post(url, headers=headers, json=payload)
print("Status:", response.status_code)
print("Response:", response.text)
