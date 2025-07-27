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
if not os.path.exists(MENU_FILE):
    print("📡 menu_v2_out.json not found — fetching from API...")

    token, _ = refresh_token()

    url = f"{os.getenv('TOAST_HOSTNAME')}/menus/v2/menus"
    headers = {
        "Authorization": f"Bearer {token}",
        "Toast-Restaurant-External-Id": os.getenv("TOAST_RESTAURANT_GUID"),
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Error fetching menu: {response.status_code}")
        exit()

    data = response.json()

    with open(MENU_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print("✅ Saved fresh menu data to menu_v2_out.json")
else:
    print("📁 Using existing menu_v2_out.json")
    with open(MENU_FILE, "r") as f:
        data = json.load(f)

# --- Extract menu group names ---
group_names = set()
for menu in data.get("menus", []):
    for group in menu.get("menuGroups", []):
        name = group.get("name")
        if name:
            group_names.add(name)

group_names = sorted(group_names)

# --- Call menu_group_items.py for each group
for group in group_names:
    print(f"\n🔍 Scanning group: '{group}'")
    #subprocess.run(["python", "menu_group_items.py", group, "--no-menu-3pd"])
    subprocess.run(["python", "menu_group_items.py", group, ""])

