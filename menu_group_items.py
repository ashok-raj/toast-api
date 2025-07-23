import json
import sys
import difflib
import csv
from tabulate import tabulate

# --- Load local menu data ---
MENU_FILE = "menu_v2_out.json"
try:
    with open(MENU_FILE, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"❌ Missing {MENU_FILE}. Run scan_groups_by_order.py to generate it.")
    sys.exit()

# --- Parse arguments ---
if len(sys.argv) < 2:
    print("Usage: python menu_group_items.py '<Menu Group Name>' [--csv] [--no-menu-3pd]")
    sys.exit()

target_group = sys.argv[1].strip().lower()
export_csv = "--csv" in sys.argv
exclude_3pd_menus = "--no-menu-3pd" in sys.argv

# --- Resolve group name ---
group_names = []
for menu in data.get("menus", []):
    for group in menu.get("menuGroups", []):
        group_names.append(group.get("name", ""))

exact_match = [g for g in group_names if g.lower() == target_group]
if exact_match:
    resolved_group_name = exact_match[0]
else:
    fuzzy_match = difflib.get_close_matches(target_group, group_names, n=1, cutoff=0.5)
    if not fuzzy_match:
        print(f"😕 No menu group matched '{target_group}'")
        sys.exit()
    resolved_group_name = fuzzy_match[0]

# --- Collect items from matching group ---
matched_items = []
for menu in data.get("menus", []):
    menu_name = menu.get("name", "").strip()

    # Skip unwanted menus
    if any(term in menu_name.lower() for term in ["3pd", "owner", "otter"]):
        continue

    for group in menu.get("menuGroups", []):
        if group.get("name", "") == resolved_group_name:
            for item in group.get("menuItems", []):
                if "3pd" in item.get("name", "").lower():
                    continue
                price = item.get("price")
                formatted = f"${price:.2f}" if price is not None else "—"
                matched_items.append({
                    "Item Name": item.get("name", ""),
                    "Price": formatted
                })

# --- Print result ---
if not matched_items:
    print(f"😕 No items found in group '{resolved_group_name}' after filtering.")
else:
    print(f"\n📋 Menu Group: {resolved_group_name}\n")
    print(tabulate(matched_items, headers="keys", tablefmt="grid"))

    if export_csv:
        with open("filtered_items.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["Item Name", "Price"])
            writer.writeheader()
            writer.writerows(matched_items)
        print("📤 Exported to filtered_items.csv")

