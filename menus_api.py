import json
import requests
from auth import refresh_token
from tabulate import tabulate

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

# Get access token
access_token, _ = refresh_token(config)

# API request
url = f"{config['hostname']}/menus/v2/menus"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Toast-Restaurant-External-Id": config["restaurantGuid"],
    "Content-Type": "application/json"
}
response = requests.get(url, headers=headers)
if response.status_code != 200:
    print(f"❌ Error {response.status_code}: {response.text}")
    exit()

data = response.json()

# ✅ Save full response
with open('menu_v2_out.json', 'w') as f:
    json.dump(data, f, indent=2)
print("📁 Saved full response to menu_v2_out.json")

# Pricing resolver
def resolve_single_price(item, size_group_id, modifier_groups, modifier_options):
    group = modifier_groups.get(str(size_group_id), {})
    prices = {}
    for opt_id in group.get("modifierOptionReferences", []):
        opt = modifier_options.get(str(opt_id))
        if opt:
            prices[opt["name"]] = opt["price"]
    return prices.get("Large") or prices.get("Small") or None

# Scan for Lassi items
modifier_groups = data.get("modifierGroupReferences", {})
modifier_options = data.get("modifierOptionReferences", {})
lassi_rows = []

for menu in data.get("menus", []):
    for group in menu.get("menuGroups", []):
        for item in group.get("menuItems", []):
            if "lassi" in item["name"].lower():
                strategy = item.get("pricingStrategy")
                if strategy == "SIZE_PRICE":
                    size_group_id = item.get("pricingRules", {}).get("sizeSpecificPricingGuid")
                    price = resolve_single_price(item, size_group_id, modifier_groups, modifier_options)
                else:
                    price = item.get("price")

                formatted = f"${price:.2f}" if price is not None else "—"
                lassi_rows.append({"Item Name": item["name"], "Price": formatted})

# Display table
if not lassi_rows:
    print("😕 No Lassi items found in the menu.")
else:
    print("\n🧋 Lassi Variants and Their Prices:\n")
    print(tabulate(lassi_rows, headers="keys", tablefmt="grid"))

