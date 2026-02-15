import requests
import json
import os
import sys

def test_minimax_v1(api_key, group_id):
    # Minimax V1 API Endpoint (often more stable for some account types)
    url = f"https://api.minimax.chat/v1/text/chatcompletion?GroupId={group_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "abab6.5s-chat",
        "messages": [{"sender_type": "USER", "sender_name": "User", "text": "OK?"}],
        "tokens_to_generate": 10
    }
    
    print(f"Testing Minimax V1 API (Group: {group_id})...")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        print(f"Status Code: {response.status_code}")
        print("Response:", response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 test_minimax_v1.py <API_KEY> <GROUP_ID>")
    else:
        test_minimax_v1(sys.argv[1], sys.argv[2])
