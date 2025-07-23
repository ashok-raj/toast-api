import subprocess
import time

# Menu groups to scan
group_list = [
    "Drinks",
    "Beer",
    "Vegetarian Appetizers",
    "Non-Vegetarian Appetizers",
    "Dosa",
    "Vegetarian Curries",
    "Non-Veg Curries"
]

# Flags
include_csv = False       # Set True to export each group to CSV
exclude_3pd = True        # Set True to skip 3PD menus

# Iterate and run the script with delay
for group in group_list:
    cmd = ["python", "menu_group_items.py", group]
    if include_csv:
        cmd.append("--csv")
    if exclude_3pd:
        cmd.append("--no-menu-3pd")

    print(f"\n🔍 Running for menu group: {group}")
    subprocess.run(cmd)

    print("⏳ Waiting 2 seconds before next group...\n")
    time.sleep(2)

