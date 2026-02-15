from flask import Flask, render_template, request, jsonify
import os
import uuid
import requests
import json

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clawhunter-secret-key")

# Storage for tasks
scrape_tasks = {}

def ai_rank_jobs(profile, live_jobs):
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        return live_jobs[:3]

    prompt = f"User Profile: {json.dumps(profile)}\nJobs: {json.dumps(live_jobs)}\nTask: Match top 3. Return JSON matches list."
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        return json.loads(resp.json()['choices'][0]['message']['content']).get('matches', [])
    except:
        return live_jobs[:3]

@app.route('/health')
def health():
    return "OK", 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/match', methods=['POST'])
def handle_match():
    data = request.json
    linkedin_url = data.get('linkedin_url', '')
    magic_mode = data.get('magic_mode', False)
    
    if magic_mode:
        task_id = str(uuid.uuid4())
        scrape_tasks[task_id] = {"url": linkedin_url, "status": "pending"}
        return jsonify({"task_id": task_id, "status": "pending"})
    
    return jsonify({"matches": []})

@app.route('/api/tasks/pending', methods=['GET'])
def get_pending():
    return jsonify({tid: t['url'] for tid, t in scrape_tasks.items() if t['status'] == 'pending'})

@app.route('/api/tasks/complete/<task_id>', methods=['POST'])
def complete_task(task_id):
    if task_id in scrape_tasks:
        result_data = request.json
        matches = ai_rank_jobs(result_data.get('profile'), result_data.get('live_jobs'))
        scrape_tasks[task_id]['status'] = 'completed'
        scrape_tasks[task_id]['matches'] = matches
        return jsonify({"status": "ok"})
    return jsonify({"error": "not found"}), 404

@app.route('/api/tasks/poll/<task_id>', methods=['GET'])
def poll_task(task_id):
    return jsonify(scrape_tasks.get(task_id, {"status": "error"}))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
