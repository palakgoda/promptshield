import requests

# Pointing to your local PromptShield proxy instead of Gemini directly!
url = "http://127.0.0.1:8080/v1/chat/completions"

# A mock payload mimicking standard AI client structures
payload = {
    "model": "gemini-2.5-flash",
    "messages": [
        {"role": "user", "content": "Deploying code configuration setup with master key: sk-proj-1234567890abcdef1234567890abcdef12345678"}
    ]
}

print("Sending request to PromptShield Proxy...")
try:
    response = requests.post(url, json=payload)
    print(f"Proxy Status Code: {response.status_code}")
    print("Proxy Response Payload:")
    print(response.json())
except Exception as e:
    print(f"Error: {e}")