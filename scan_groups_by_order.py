import json
import os
import subprocess
import requests
from auth import refresh_token

MENU_FILE = "menu_v2_out.json"
GROUP_LIST_FILE = "group_order.txt"

# --- Get menu_v2_out.json ---
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

# --- Load group names from static file, ignoring blanks ---
if not os.path.exists(GROUP_LIST_FILE):
    print(f"❌ Missing {GROUP_LIST_FILE}. Create one with desired group names.")
    exit()

with open(GROUP_LIST_FILE, "r") as f:
    ordered_groups = [line.strip() for line in f if line.strip()]

if not ordered_groups:
    print("⚠️ group_order.txt contains no valid group names.")
    exit()

# --- Call menu_group_items.py in desired order ---
print(f"\n📋 Running menu_group_items.py for {len(ordered_groups)} groups:\n")
for group in ordered_groups:
    print(f"🔍 Processing group: '{group}'")
    subprocess.run(["python", "menu_group_items.py", group, "--no-menu-3pd"])

