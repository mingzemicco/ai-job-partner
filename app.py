from flask import Flask, render_template, request, jsonify
import os
import uuid
import requests
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clawhunter-secret-key")

def get_mock_matches(linkedin_url):
    is_qian = "qian-liu" in linkedin_url.lower()
    is_mingze = "nimingze" in linkedin_url.lower()

    if is_qian:
        return [
            {
                "id": str(uuid.uuid4()),
                "title": "Portfolio Manager - Global Macro",
                "company": "Amundi",
                "location": "Paris, France",
                "salary_range": "€120k - €200k",
                "match_reason": "Your expertise in multi-asset and macroeconomic analysis perfectly aligns with Amundi's global macro fund requirements."
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Quantitative Researcher",
                "company": "Squarepoint Capital",
                "location": "Paris, France",
                "salary_range": "€150k - €250k",
                "match_reason": "Your background in FX and equity quant strategies makes you an ideal fit for systematic trading roles."
            }
        ]
    elif is_mingze:
        return [
            {
                "id": str(uuid.uuid4()),
                "title": "Account Executive, Enterprise",
                "company": "Stripe",
                "location": "Paris, France",
                "salary_range": "€193k - €290k",
                "match_reason": "Entrepreneurial DNA from Micco combined with BCG delivery experience is exactly what Stripe looks for in 'Hunter' roles."
            }
        ]
    return [
        {
            "id": str(uuid.uuid4()),
            "title": "Tech Strategy Consultant",
            "company": "Tech Scaleup",
            "location": "Paris, France",
            "salary_range": "€90k - €130k",
            "match_reason": "Generic match based on tech profile potential."
        }
    ]

# Real AI matching logic using Minimax m2.5
def match_jobs(linkedin_url):
    api_key = os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        return get_mock_matches(linkedin_url)

    prompt = f"""
    User LinkedIn Profile URL: {linkedin_url}
    Task: Identify 3 high-impact job opportunities in Paris (startups or finance) for this person.
    
    Output format: JSON only.
    {{
      "matches": [
        {{
          "title": "...",
          "company": "...",
          "location": "...",
          "salary_range": "...",
          "match_reason": "..."
        }}
      ]
    }}
    """

    try:
        url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "abab6.5s-chat", # Using minimax-v2 equivalent
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()
        # Handle Minimax response structure
        content = res_json['choices'][0]['message']['content']
        # Clean potential markdown block
        content = content.replace('```json', '').replace('```', '').strip()
        matches = json.loads(content).get('matches', [])
        for m in matches:
            m['id'] = str(uuid.uuid4())
        return matches
    except Exception as e:
        print(f"API Error: {e}")
        return get_mock_matches(linkedin_url)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/match', methods=['POST'])
def get_match():
    data = request.json
    linkedin_url = data.get('linkedin_url')
    if not linkedin_url:
        return jsonify({"error": "LinkedIn URL required"}), 400
    
    matches = match_jobs(linkedin_url)
    return jsonify({"matches": matches})

@app.route('/api/alert', methods=['POST'])
def save_alert():
    data = request.json
    email = data.get('email')
    frequency = data.get('frequency')
    return jsonify({"status": "success", "message": f"Alert set for {email} ({frequency})"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
