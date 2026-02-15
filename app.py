from flask import Flask, render_template, request, jsonify
import os
import uuid
import requests
import json
import time

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clawhunter-secret-key")

scrape_tasks = {}

def get_mock_matches():
    return [{"id": str(uuid.uuid4()), "title": "Portfolio Manager", "company": "Amundi", "match_reason": "Demo Match"}]

def ai_rank_jobs(profile, live_jobs):
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        return live_jobs # Return raw if no key

    prompt = f"""
    User Profile: {json.dumps(profile)}
    Market Job Openings: {json.dumps(live_jobs)}
    
    Task: 
    1. Select the top 3 jobs from the 'Market Job Openings' that best fit the user.
    2. Provide a specific 'match_reason' and 'salary_range' for each.
    
    Output format: JSON only.
    {{
      "matches": [
        {{ "title": "...", "company": "...", "url": "...", "match_reason": "...", "salary_range": "..." }}
      ]
    }}
    """
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        resp = requests.post(url, headers=headers, json=payload)
        return json.loads(resp.json()['choices'][0]['message']['content']).get('matches', [])
    except:
        return live_jobs

@app.route('/health')
def health():
    return "OK", 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/match', methods=['POST'])
def handle_match():
    data = request.json
    magic_mode = data.get('magic_mode', False)
    linkedin_url = data.get('linkedin_url', '')
    
    if magic_mode:
        task_id = str(uuid.uuid4())
        scrape_tasks[task_id] = {"url": linkedin_url, "status": "pending"}
        return jsonify({"task_id": task_id, "status": "pending"})
    
    # Non-magic mode logic here...
    return jsonify({"matches": get_mock_matches()})

@app.route('/api/tasks/pending', methods=['GET'])
def get_pending():
    return jsonify({tid: t['url'] for tid, t in scrape_tasks.items() if t['status'] == 'pending'})

@app.route('/api/tasks/complete/<task_id>', methods=['POST'])
def complete_task(task_id):
    if task_id in scrape_tasks:
        result_data = request.json # Contains {profile, live_jobs}
        matches = ai_rank_jobs(result_data['profile'], result_data['live_jobs'])
        scrape_tasks[task_id]['status'] = 'completed'
        scrape_tasks[task_id]['matches'] = matches
        return jsonify({"status": "ok"})
    return jsonify({"error": "not found"}), 404

@app.route('/api/tasks/poll/<task_id>', methods=['GET'])
def poll_task(task_id):
    return jsonify(scrape_tasks.get(task_id, {"status": "error"}))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
