import json
import requests
from auth import refresh_token

# --- Load config ---
with open("config.json", "r") as f:
    config = json.load(f)

# --- Get token ---
access_token, _ = refresh_token(config)

# --- Fetch menus ---
url = f"{config['hostname']}/menus/v2/menus"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Toast-Restaurant-External-Id": config["restaurantGuid"],
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

