from flask import Flask, render_template, request, jsonify
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clawhunter-secret-key")

# Placeholder for AI matching logic
def match_jobs(linkedin_url):
    # This will eventually call LinkedIn scraper and LLM
    # Mock data for initial dev
    return [
        {
            "id": str(uuid.uuid4()),
            "title": "Senior Product Manager",
            "company": "Mistral AI",
            "location": "Paris, France",
            "salary_range": "€100k - €150k",
            "match_reason": "Based on your experience as a Founder and background in AI at IBM, Mistral's growth stage perfectly matches your leadership profile."
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Head of Engineering",
            "company": "Qonto",
            "location": "Paris, France",
            "salary_range": "€120k - €180k",
            "match_reason": "Your Fintech experience with Micco and scaling teams to 120+ engineers makes you a top candidate for Qonto's expansion."
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
