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
        matches.insert(0, {
            "id": "error",
            "title": "Note: Using Demo Mode",
            "company": "System",
            "location": "N/A",
            "salary_range": "N/A",
            "match_reason": f"AI Engine returned: {error_msg}. Showing demo data."
        })
    return matches

# Multi-Engine AI Matching Logic
def match_jobs(linkedin_url, profile_data=None, profile_text=None):
    openai_key = os.environ.get("OPENAI_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    minimax_key = os.environ.get("MINIMAX_API_KEY")
    
    # 🔍 DEBUG: Build context
    context = f"LinkedIn URL: {linkedin_url}"
    if profile_data and isinstance(profile_data, dict):
        context = f"Structured Profile Data: {json.dumps(profile_data)}"
    elif profile_text:
        context = f"Raw Resume Text: {profile_text}"

    print(f"--- DEBUG: Context used for AI ---\n{context[:500]}...\n--- END DEBUG ---")

    prompt = f"""
    Context: {context}
    Task: This is a LinkedIn profile or resume. Identify 3 high-impact job opportunities in Paris.
    If the person is in Real Estate/Investment, find roles in Real Estate funds or Proptech.
    If the person is in Tech, find roles in Startups/Big Tech.
    
    Return ONLY a JSON object with a 'matches' list containing objects with: 
    title, company, location, salary_range, match_reason.
    """

    # 1. Try OpenAI (GPT-4o)
    if openai_key:
        try:
            print("Trying OpenAI GPT-4o...")
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
                print(f"OpenAI raw response: {content[:200]}")
                matches = json.loads(content).get('matches', [])
                for m in matches: m['id'] = str(uuid.uuid4())
                return matches
            print(f"OpenAI Error: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"OpenAI Exception: {e}")

    # 2. Try Gemini 2.0 Flash
    if gemini_key:
        try:
            print("Trying Gemini 2.0...")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"response_mime_type": "application/json"}}
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                res_json = resp.json()
                content = res_json['candidates'][0]['content']['parts'][0]['text']
                matches = json.loads(content).get('matches', [])
                for m in matches: m['id'] = str(uuid.uuid4())
                return matches
            print(f"Gemini Error: {resp.status_code}")
        except Exception as e:
            print(f"Gemini Exception: {e}")

    # 3. Try Minimax Fallback
    if minimax_key:
        try:
            print("Trying Minimax...")
            url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
            headers = {"Authorization": f"Bearer {minimax_key}", "Content-Type": "application/json"}
            payload = {"model": "abab6.5s-chat", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                content = resp.json()['choices'][0]['message']['content'].replace('```json', '').replace('```', '').strip()
                matches = json.loads(content).get('matches', [])
                for m in matches: m['id'] = str(uuid.uuid4())
                return matches
            print(f"Minimax Error: {resp.status_code}")
        except Exception as e:
            print(f"Minimax Exception: {e}")

    return get_mock_matches(linkedin_url, "AI Engines Unreachable")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/match', methods=['POST'])
def get_match():
    data = request.json
    linkedin_url = data.get('linkedin_url', '')
    profile_data = data.get('profile_data')
    profile_text = data.get('profile_text') # From textarea
    
    print(f"API Request: URL={linkedin_url}, TextLength={len(profile_text) if profile_text else 0}")
    
    matches = match_jobs(linkedin_url, profile_data, profile_text)
    return jsonify({"matches": matches})

@app.route('/api/alert', methods=['POST'])
def save_alert():
    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
