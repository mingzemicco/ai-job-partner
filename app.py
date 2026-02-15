from flask import Flask, render_template, request, jsonify
import os
import uuid
import requests
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clawhunter-secret-key")

def get_mock_matches(linkedin_url, error_msg=None):
    matches = [
        {
            "id": str(uuid.uuid4()),
            "title": "Portfolio Manager (Demo)",
            "company": "Amundi",
            "location": "Paris, France",
            "salary_range": "€120k - €180k",
            "match_reason": "Your background in high-level finance aligns with Amundi's core strategies."
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Senior AI Strategist (Demo)",
            "company": "Mistral AI",
            "location": "Paris, France",
            "salary_range": "€100k - €150k",
            "match_reason": "Excellent fit for frontier AI application teams."
        }
    ]
    if error_msg:
        # Prepend a notice about the API error
        matches.insert(0, {
            "id": "error",
            "title": "Note: Using Demo Mode",
            "company": "System",
            "location": "N/A",
            "salary_range": "N/A",
            "match_reason": f"AI models are currently unavailable (Error: {error_msg}). Showing high-quality demo matches instead."
        })
    return matches

def match_jobs(linkedin_url, profile_data=None):
    gemini_key = os.environ.get("GEMINI_API_KEY")
    minimax_key = os.environ.get("MINIMAX_API_KEY")
    
    context = f"LinkedIn URL: {linkedin_url}"
    if profile_data:
        context = f"Name: {profile_data.get('name')}\nHeadline: {profile_data.get('headline')}\nExp: {json.dumps(profile_data.get('experience', [])[:2])}"

    prompt = f"Context: {context}\nTask: Find 3 high-impact jobs in Paris. Return ONLY a JSON object with a 'matches' list."

    # 1. Try Gemini 2.0 Flash
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"response_mime_type": "application/json"}}
            resp = requests.post(url, json=payload, timeout=10)
            res_json = resp.json()
            if resp.status_code == 200 and 'candidates' in res_json:
                content = res_json['candidates'][0]['content']['parts'][0]['text']
                matches = json.loads(content).get('matches', [])
                for m in matches: m['id'] = str(uuid.uuid4())
                return matches
            print(f"Gemini Fail ({resp.status_code}): {res_json}")
        except Exception as e:
            print(f"Gemini Exception: {e}")

    # 2. Try Minimax Fallback
    if minimax_key:
        try:
            url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
            headers = {"Authorization": f"Bearer {minimax_key}", "Content-Type": "application/json"}
            payload = {"model": "abab6.5s-chat", "messages": [{"role": "user", "content": prompt}]}
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            res_json = resp.json()
            if resp.status_code == 200 and 'choices' in res_json:
                content = res_json['choices'][0]['message']['content'].replace('```json', '').replace('```', '').strip()
                matches = json.loads(content).get('matches', [])
                for m in matches: m['id'] = str(uuid.uuid4())
                return matches
            print(f"Minimax Fail ({resp.status_code}): {res_json}")
        except Exception as e:
            print(f"Minimax Exception: {e}")

    return get_mock_matches(linkedin_url, "Quota exceeded or API error")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/match', methods=['POST'])
def get_match():
    data = request.json
    matches = match_jobs(data.get('linkedin_url', ''), data.get('profile_data'))
    return jsonify({"matches": matches})

@app.route('/api/alert', methods=['POST'])
def save_alert():
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
