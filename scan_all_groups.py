import json
import os
import subprocess
import requests
from auth import refresh_token

# --- Constants ---
MENU_FILE = "menu_v2_out.json"

# --- Load or fetch menu data ---
if not os.path.exists(MENU_FILE):
    print("📡 menu_v2_out.json not found — fetching from API...")

    with open("config.json", "r") as f:
        config = json.load(f)

    token, _ = refresh_token(config)

    url = f"{config['hostname']}/menus/v2/menus"
    headers = {
        "Authorization": f"Bearer {token}",
        "Toast-Restaurant-External-Id": config["restaurantGuid"],
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
    subprocess.run(["python", "menu_group_items.py", group, "--no-menu-3pd"])

