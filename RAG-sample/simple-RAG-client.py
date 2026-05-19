import requests

API_KEY = "your_api_key_here"
BASE_URL = "http://localhost:3001/api/v1" 
WORKSPACE_SLUG = "my-workspace"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

user_message = input("Write your message: ").strip()

data = {
    "message": user_message,
    "mode": "query" 
}

response = requests.post(
    f"{BASE_URL}/workspace/{WORKSPACE_SLUG}/chat", 
    headers=headers, 
    json=data
)

print("[DEBUG] Complete response:")
print(response.json())
print("================================")
print("AI answer:")
print(response.json().get("textResponse"))