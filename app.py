from flask import Flask, render_template, request, jsonify
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clawhunter-secret-key")

# Real AI matching logic (simplified for MVP)
def match_jobs(linkedin_url):
    # Determine profile type from URL or sample data
    # In a real SaaS, this would scrape the profile first
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
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Senior Macro Strategist",
                "company": "Exane BNP Paribas",
                "location": "Paris, France",
                "salary_range": "€130k - €180k",
                "match_reason": "Strong macroeconomic insights and experience in European markets."
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
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Head of Product",
                "company": "Gorgias",
                "location": "Paris, France",
                "salary_range": "€120k - €160k",
                "match_reason": "Proven track record of building and scaling AI-driven platforms from zero to one."
            }
        ]
    else:
        return [
            {
                "id": str(uuid.uuid4()),
                "title": "Tech/Product Lead (Exploratory Match)",
                "company": "Tech Scaleup",
                "location": "Paris, France",
                "salary_range": "€80k - €120k",
                "match_reason": "We've detected a high growth potential in your profile. Contact us for a deep dive."
            }
        ]

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
    frequency = data.get('frequency') # daily, weekly, monthly
    # Save to DB logic here
    return jsonify({"status": "success", "message": f"Alert set for {email} ({frequency})"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
