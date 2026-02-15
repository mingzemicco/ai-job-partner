from flask import Flask, render_template, request, jsonify
import os
import uuid
import requests
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clawhunter-secret-key")

# Improved Matching Logic
def match_jobs(linkedin_url, profile_data=None):
    api_key = os.environ.get("MINIMAX_API_KEY")
    
    # Context building: Use scraped data if available, otherwise just the URL
    if profile_data:
        context = f"""
        Profile Name: {profile_data.get('name')}
        Headline: {profile_data.get('headline')}
        Location: {profile_data.get('location')}
        Top Experience: {json.dumps(profile_data.get('experience', [])[:3])}
        """
    else:
        context = f"LinkedIn URL: {linkedin_url}"

    if not api_key:
        return [{"id": str(uuid.uuid4()), "title": "Please configure MINIMAX_API_KEY", "company": "System", "match_reason": "API Key Missing"}]

    prompt = f"""
    User Context: {context}
    Task: Find 3 high-impact job opportunities in Paris. 
    Focus on prestigious startups (A-D round), Hedge Funds, or Large Tech firms.
    
    Output format: JSON only.
    {{
      "matches": [
        {{
          "title": "...",
          "company": "...",
          "location": "Paris, France",
          "salary_range": "...",
          "match_reason": "..."
        }}
      ]
    }}
    """

    try:
        url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "abab6.5s-chat",
            "messages": [{"role": "user", "content": prompt}]
        }
        
        print(f"Calling Minimax API with model {payload['model']}...")
        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()
        
        if response.status_code != 200:
            error_msg = res_json.get('base_resp', {}).get('status_msg', 'Unknown API Error')
            print(f"Minimax API Error ({response.status_code}): {error_msg}")
            return [{"title": "API Error", "company": f"Status {response.status_code}", "match_reason": error_msg}]

        if 'choices' not in res_json:
            print(f"Unexpected API Response: {json.dumps(res_json)}")
            return [{"title": "API Format Error", "company": "Minimax", "match_reason": "Response missing 'choices' field."}]

        content = res_json['choices'][0]['message']['content']
        # Remove markdown markers if present
        content = content.replace('```json', '').replace('```', '').strip()
        
        try:
            matches = json.loads(content).get('matches', [])
        except json.JSONDecodeError:
            # Handle cases where AI returns text instead of pure JSON
            print(f"Failed to parse JSON from content: {content}")
            return [{"title": "AI Parsing Error", "company": "Logic", "match_reason": "The AI response was not in valid JSON format."}]

        for m in matches:
            m['id'] = str(uuid.uuid4())
        return matches
    except Exception as e:
        print(f"System Exception: {str(e)}")
        return [{"title": "AI Match Failed", "company": str(e), "match_reason": "Internal Server Error"}]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/match', methods=['POST'])
def get_match():
    data = request.json
    linkedin_url = data.get('linkedin_url', '')
    profile_data = data.get('profile_data') # Accepting structured data from agent/frontend
    
    matches = match_jobs(linkedin_url, profile_data)
    return jsonify({"matches": matches})

@app.route('/api/alert', methods=['POST'])
def save_alert():
    data = request.json
    return jsonify({"status": "success", "message": f"Alert set for {data.get('email')}"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
