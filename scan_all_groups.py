import json
import os
import subprocess
import requests
from auth import refresh_token
from dotenv import load_dotenv
from get_menu_data import load_menu_data

# 🌱 Load .env values
load_dotenv()

# --- Load or fetch menu data ---

data = load_menu_data()

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

