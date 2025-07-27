import json
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 🌱 Load .env values
load_dotenv()

def load_cached_token():
    if os.path.exists('token_cache.json'):
        with open('token_cache.json', 'r') as f:
            data = json.load(f)
            expiry = datetime.fromisoformat(data['expiryTime'])
            if expiry > datetime.now():
                return data['accessToken'], expiry
    return None, None

def save_token(token, expiry):
    with open('token_cache.json', 'w') as f:
        json.dump({
            "accessToken": token,
            "expiryTime": expiry.isoformat()
        }, f)

def refresh_token():
    cached_token, expiry = load_cached_token()
    if cached_token:
        print("🔄 Using cached token")
        return cached_token, expiry

    print("🔐 Refreshing token from API")
    url = f"{os.getenv('TOAST_HOSTNAME')}/authentication/v1/authentication/login"
    payload = {
        "clientId": os.getenv("TOAST_CLIENT_ID"),
        "clientSecret": os.getenv("TOAST_CLIENT_SECRET"),
        "userAccessType": "TOAST_MACHINE_CLIENT"
    }
    headers = { "Content-Type": "application/json" }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        token_data = response.json()["token"]
        expiry = datetime.now() + timedelta(seconds=token_data["expiresIn"])
        save_token(token_data["accessToken"], expiry)
        return token_data["accessToken"], expiry
    else:
        raise Exception(f"Authentication failed: {response.text}")

