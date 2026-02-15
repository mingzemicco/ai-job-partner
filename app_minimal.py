from flask import Flask
import os

app = Flask(__name__)

@app.route('/health')
def health():
    return "OK"

@app.route('/')
def index():
    return "ClawHunter MVP is starting..."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
