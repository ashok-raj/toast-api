import json
import requests
import os
from dotenv import load_dotenv
from auth import refresh_token

# --- Load .env values ---
load_dotenv()

# --- Get token ---
access_token, _ = refresh_token()

# --- Fetch menus ---
url = f"{os.getenv('TOAST_HOSTNAME')}/menus/v2/menus"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Toast-Restaurant-External-Id": os.getenv("TOAST_RESTAURANT_GUID"),
    "Content-Type": "application/json"
}
response = requests.get(url, headers=headers)
if response.status_code != 200:
    print(f"❌ Failed to fetch menu data: {response.status_code}")
    exit()

data = response.json()

# --- Collect and print all menu group names ---
group_set = set()
for menu in data.get("menus", []):
    menu_name = menu.get("name", "")
    for group in menu.get("menuGroups", []):
        group_name = group.get("name", "")
        group_set.add(group_name)

print("\n📚 Available Menu Groups:\n")
for name in sorted(group_set):
    print(f"• {name}")
