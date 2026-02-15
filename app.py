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
            "match_reason": "Based on your high-level financial background."
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
            "match_reason": f"AI Engine (Minimax M2.5) returned: {error_msg}. Showing demo data."
        })
    return matches

# AI Matching Logic focused on Minimax M2.5
def match_jobs(linkedin_url, profile_data=None):
    minimax_key = os.environ.get("MINIMAX_API_KEY")
    # For older accounts, GroupId might be required
    group_id = os.environ.get("MINIMAX_GROUP_ID") 
    
    context = f"LinkedIn URL: {linkedin_url}"
    if profile_data:
        context = f"Name: {profile_data.get('name')}\nHeadline: {profile_data.get('headline')}\nExp: {json.dumps(profile_data.get('experience', [])[:2])}"

    prompt = f"Context: {context}\nTask: Find 3 high-impact job opportunities in Paris. Return ONLY a JSON object with a 'matches' list containing objects with: title, company, location, salary_range, match_reason."

    if minimax_key:
        try:
            # Minimax V2 API Endpoint
            url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
            headers = {
                "Authorization": f"Bearer {minimax_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "abab6.5s-chat", # Minimax M2.5
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            }
            
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            res_json = resp.json()
            
            if resp.status_code == 200 and 'choices' in res_json:
                content = res_json['choices'][0]['message']['content']
                # Sometimes models wrap JSON in markdown
                content = content.replace('```json', '').replace('```', '').strip()
                matches = json.loads(content).get('matches', [])
                for m in matches: m['id'] = str(uuid.uuid4())
                return matches
            else:
                error_info = res_json.get('base_resp', {}).get('status_msg', 'Unknown Error')
                print(f"Minimax Error: {resp.status_code} - {error_info}")
                return get_mock_matches(linkedin_url, f"{resp.status_code}: {error_info}")
                
        except Exception as e:
            print(f"Minimax Exception: {e}")
            return get_mock_matches(linkedin_url, str(e))

    return get_mock_matches(linkedin_url, "API Key Missing")

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
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
