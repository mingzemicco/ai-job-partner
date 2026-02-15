from flask import Flask, render_template, request, jsonify
import os
import uuid
import requests
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clawhunter-secret-key")

def get_mock_matches(linkedin_url):
    return [
        {
            "id": str(uuid.uuid4()),
            "title": "Portfolio Manager",
            "company": "Amundi",
            "location": "Paris, France",
            "salary_range": "€120k - €180k",
            "match_reason": "Based on your high-level financial background."
        }
    ]

# AI Matching Logic using Gemini or Minimax
def match_jobs(linkedin_url, profile_data=None):
    gemini_key = os.environ.get("GEMINI_API_KEY")
    minimax_key = os.environ.get("MINIMAX_API_KEY")
    
    if profile_data:
        context = f"""
        Profile Name: {profile_data.get('name')}
        Headline: {profile_data.get('headline')}
        Location: {profile_data.get('location')}
        Top Experience: {json.dumps(profile_data.get('experience', [])[:3])}
        """
    else:
        context = f"LinkedIn URL: {linkedin_url}"

    prompt = f"""
    Context: {context}
    Task: Find 3 high-impact job opportunities in Paris (prestigious startups or finance).
    Return ONLY a JSON object with a 'matches' list containing objects with: 
    title, company, location, salary_range, match_reason.
    """

    # Try Gemini 2.0 Flash first
    if gemini_key:
        try:
            # Use v1beta for latest 2.0 flash features
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "response_mime_type": "application/json"
                }
            }
            response = requests.post(url, json=payload)
            res_json = response.json()
            
            if response.status_code != 200:
                print(f"Gemini API Error Response: {res_json}")
                # Log error and fall through to fallback
            elif 'candidates' not in res_json:
                print(f"Gemini Response missing candidates: {res_json}")
            else:
                content = res_json['candidates'][0]['content']['parts'][0]['text']
                matches = json.loads(content).get('matches', [])
                for m in matches: m['id'] = str(uuid.uuid4())
                return matches
        except Exception as e:
            print(f"Gemini Exception: {e}")

    # Fallback to Minimax
    if minimax_key:
        try:
            url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
            headers = {"Authorization": f"Bearer {minimax_key}", "Content-Type": "application/json"}
            payload = {
                "model": "abab6.5s-chat",
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post(url, headers=headers, json=payload)
            content = response.json()['choices'][0]['message']['content']
            content = content.replace('```json', '').replace('```', '').strip()
            matches = json.loads(content).get('matches', [])
            for m in matches: m['id'] = str(uuid.uuid4())
            return matches
        except Exception as e:
            print(f"Minimax API Error: {e}")

    return get_mock_matches(linkedin_url)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/match', methods=['POST'])
def get_match():
    data = request.json
    linkedin_url = data.get('linkedin_url', '')
    profile_data = data.get('profile_data')
    matches = match_jobs(linkedin_url, profile_data)
    return jsonify({"matches": matches})

@app.route('/api/alert', methods=['POST'])
def save_alert():
    data = request.json
    return jsonify({"status": "success", "message": f"Alert set for {data.get('email')}"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
