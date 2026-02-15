import requests
import json
import os
import sys

def test_minimax(api_key):
    url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Testing with abab6.5s-chat (m2.5 equivalent)
    payload = {
        "model": "abab6.5s-chat",
        "messages": [
            {"role": "user", "content": "Hello, this is a test. Reply with 'OK' if you receive this."}
        ]
    }
    
    print(f"Testing Minimax API with model: {payload['model']}")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        res_json = response.json()
        print("Response JSON:")
        print(json.dumps(res_json, indent=2, ensure_ascii=False))
        
        if response.status_code == 200 and 'choices' in res_json:
            content = res_json['choices'][0]['message']['content']
            print(f"\n✅ SUCCESS! AI Response: {content}")
        else:
            print("\n❌ FAILED: 'choices' field not found in response.")
            if 'base_resp' in res_json:
                print(f"Error Message: {res_json['base_resp'].get('status_msg')}")
                
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    key = os.environ.get("MINIMAX_API_KEY")
    if not key and len(sys.argv) > 1:
        key = sys.argv[1]
    
    if not key:
        print("Please provide MINIMAX_API_KEY as an env var or argument.")
        print("Usage: python3 test_minimax_api.py YOUR_API_KEY")
    else:
        test_minimax(key)
