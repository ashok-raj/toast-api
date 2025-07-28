import json
import os
import subprocess
import requests
from auth import refresh_token
from dotenv import load_dotenv

# 🌱 Load .env values
load_dotenv()

# --- Constants ---
MENU_FILE = "menu_v2_out.json"

# --- Load or fetch menu data ---
def load_menu_data():
    if not os.path.exists(MENU_FILE):
        print("📡 menu_v2_out.json not found — fetching from API...", flush=True)

        token, _ = refresh_token()

        url = f"{os.getenv('TOAST_HOSTNAME')}/menus/v2/menus"
        headers = {
	    "Authorization": f"Bearer {token}",
	    "Toast-Restaurant-External-Id": os.getenv("TOAST_RESTAURANT_GUID"),
	    "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Error fetching menu: {response.status_code}", flush=True)
            exit()

        data = response.json()

        with open(MENU_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print("✅ Saved fresh menu data to menu_v2_out.json", flush=True)
    else:
        print("📁 Using existing menu_v2_out.json", flush=True)
        with open(MENU_FILE) as f:
            data = json.load(f)

    return data
