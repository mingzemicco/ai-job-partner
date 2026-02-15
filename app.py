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
        }
    ]
    if error_msg:
        matches.insert(0, {
            "id": "error",
            "title": "AI Engine Status",
            "company": "System",
            "match_reason": f"Note: {error_msg}. Showing high-quality demo matches."
        })
    return matches

def match_jobs(linkedin_url, profile_data=None, profile_text=None):
    openai_key = os.environ.get("OPENAI_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    # 🧩 Context Building
    if profile_data and isinstance(profile_data, dict):
        # We got structured data from the scraper!
        context = f"Structured LinkedIn Profile: {json.dumps(profile_data)}"
    elif profile_text:
        # We got raw pasted text!
        context = f"Raw Professional Summary: {profile_text}"
    else:
        # We only have a URL - least accurate
        context = f"LinkedIn URL: {linkedin_url}. Analyze based on URL features."

    prompt = f"""
    Profile Data: {context}
    
    Task: 
    1. Deeply analyze this profile's professional trajectory.
    2. Identify 3 ambitious next-step roles in the Paris ecosystem (Startups A-D or Finance).
    3. For each, provide a specific 'match_reason' and a high-end salary range.
    
    Return result as JSON object with a 'matches' list.
    """

    # --- OpenAI GPT-4o (Primary) ---
    if openai_key:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                content = resp.json()['choices'][0]['message']['content']
                matches = json.loads(content).get('matches', [])
                for m in matches: m['id'] = str(uuid.uuid4())
                return matches
        except Exception as e:
            print(f"OpenAI Failed: {e}")

    # --- Gemini 2.0 (Secondary) ---
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"response_mime_type": "application/json"}}
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                res_json = resp.json()
                content = res_json['candidates'][0]['content']['parts'][0]['text']
                matches = json.loads(content).get('matches', [])
                for m in matches: m['id'] = str(uuid.uuid4())
                return matches
        except Exception as e:
            print(f"Gemini Failed: {e}")

    return get_mock_matches(linkedin_url, "AI Engines busy or limit reached")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/match', methods=['POST'])
def get_match():
    data = request.json
    linkedin_url = data.get('linkedin_url', '')
    profile_data = data.get('profile_data')
    profile_text = data.get('profile_text')
    
    matches = match_jobs(linkedin_url, profile_data, profile_text)
    return jsonify({"matches": matches})

@app.route('/api/alert', methods=['POST'])
def save_alert():
    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
