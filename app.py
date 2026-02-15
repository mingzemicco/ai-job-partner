from flask import Flask, render_template, request, jsonify
import os
import uuid
import requests
import json
import threading
import time

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clawhunter-secret-key")

# --- In-Memory Task Queue for MVP ---
scrape_tasks = {} # { task_id: { url: str, data: dict, status: str } }

def get_mock_matches(linkedin_url, error_msg=None):
    return [{"id": str(uuid.uuid4()), "title": "Portfolio Manager (Demo)", "company": "Amundi", "match_reason": f"Note: {error_msg}. Showing demo data."}]

def match_jobs(context_data):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return get_mock_matches("", "API Key Missing")

    prompt = f"Analyze this profile and find 3 aspirational next-step roles in Paris: {json.dumps(context_data)}"
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        content = resp.json()['choices'][0]['message']['content']
        return json.loads(content).get('matches', [])
    except Exception as e:
        return [{"title": "Match Failed", "company": str(e), "match_reason": "AI Error"}]

@app.route('/')
def index():
    return render_template('index.html')

# --- Agent Interaction Endpoints ---

@app.route('/api/match', methods=['POST'])
def handle_match_request():
    data = request.json
    linkedin_url = data.get('linkedin_url', '')
    profile_text = data.get('profile_text', '')
    magic_mode = data.get('magic_mode', False)
    
    if magic_mode:
        # Create a task for the local agent to pick up
        task_id = str(uuid.uuid4())
        scrape_tasks[task_id] = {
            "url": linkedin_url,
            "status": "pending",
            "data": None,
            "created_at": time.time()
        }
        return jsonify({"task_id": task_id, "status": "pending"})
    
    # Standard mode: process immediately
    matches = match_jobs({"url": linkedin_url, "text": profile_text})
    return jsonify({"matches": matches})

@app.route('/api/tasks/pending', methods=['GET'])
def list_pending_tasks():
    # Local agent calls this to find work
    pending = {tid: task['url'] for tid, task in scrape_tasks.items() if task['status'] == 'pending'}
    return jsonify(pending)

@app.route('/api/tasks/complete/<task_id>', methods=['POST'])
def complete_task(task_id):
    # Local agent calls this to deliver scraped data
    if task_id in scrape_tasks:
        scraped_data = request.json
        matches = match_jobs(scraped_data)
        scrape_tasks[task_id]['status'] = 'completed'
        scrape_tasks[task_id]['matches'] = matches
        return jsonify({"status": "ok"})
    return jsonify({"error": "task not found"}), 404

@app.route('/api/tasks/poll/<task_id>', methods=['GET'])
def poll_task(task_id):
    # Frontend calls this to check if agent finished
    if task_id in scrape_tasks:
        return jsonify(scrape_tasks[task_id])
    return jsonify({"error": "not found"}), 404

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
