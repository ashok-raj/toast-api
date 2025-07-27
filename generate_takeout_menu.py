import json
import sys
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# --- Config ---
MENU_FILE = "menu_v2_out.json"
GROUP_LIST_FILE = "group_order.txt"
LOGO_PATH = "restaurant_logo.jpeg"

#Basename
BASE_PDF_FILE = "takeout_menu"
BASE_TEXT_FILE = "takeout_menu"
BASE_HTML_FILE = "preview_menu"

extension = "_with3pd" if "--filter-3pd" in sys.argv else ""

PDF_FILE = f"{BASE_PDF_FILE}{extension}.pdf"
TEXT_FILE = f"{BASE_TEXT_FILE}{extension}.txt"
HTML_FILE = f"{BASE_HTML_FILE}{extension}.html"

INCLUDE_PRICES = "--with-price" in sys.argv
INCLUDE_3PD = "--filter-3pd" in sys.argv

RESTAURANT_NAME = "ChennaiMasala"
ADDRESS = "2088 NE Stucki Ave, Hillsboro, OR 97124"
PHONE = "503-531-9500"
WEBSITE = "www.chennaimasala.net"
HOURS = "Monday Closed\nTuesday–Sunday 11:00am–2:00pm and 5:00pm–9:00pm"
DISCLAIMER = "Menu items and prices subject to change."

# --- Load data ---
if not os.path.exists(MENU_FILE) or not os.path.exists(GROUP_LIST_FILE):
    print("❌ Missing required files")
    sys.exit()

with open(MENU_FILE, "r") as f:
    data = json.load(f)
with open(GROUP_LIST_FILE, "r") as f:
    group_order = [line.strip() for line in f if line.strip()]

# --- Collect items ---
grouped_items = {}
all_item_names = []

for menu in data.get("menus", []):
    mname = menu.get("name", "").lower()
    
    has_3pd = "3pd" in mname
    #print(f"Menu name: {menu.get('name','')}", flush=True)
    
    if not INCLUDE_3PD and has_3pd:
        continue

    if INCLUDE_3PD and not has_3pd:
        continue

    if any(term in mname for term in ["owner", "otter", "happy", "beer",
    "catering", "weekend"]):
        continue

    #if not INCLUDE_3PD and not has_3pd:
        #continue

    for group in menu.get("menuGroups", []):
        gname = group.get("name", "")
        if gname not in group_order:
            continue

        visibility = group.get("visibility", [])
        if INCLUDE_3PD and "ORDERING_PARTNERS" not in visibility:
            continue

        for item in group.get("menuItems", []):
            iname = item.get("name", "")

            price = item.get("price")
            fprice = f"${price:.2f}" if price is not None else ""

            grouped_items.setdefault(gname, []).append((iname, fprice))
            if INCLUDE_PRICES:
                all_item_names.append(iname)

global_max_len = max((len(name) for name in all_item_names), default=0) if INCLUDE_PRICES else 0

# --- Text Output ---
with open(TEXT_FILE, "w") as f:
    f.write(f"{RESTAURANT_NAME} – Takeout Menu\n{ADDRESS}\n{PHONE} • {WEBSITE}\n\n")
    for group in group_order:
        items = grouped_items.get(group, [])
        if not items: continue
        f.write(f"🌟 {group}\n")
        for name, price in items:
            if INCLUDE_PRICES:
                f.write(f"  • {name.ljust(global_max_len)}   {price}\n")
            else:
                f.write(f"  • {name}\n")
        f.write("\n")
    f.write(f"Hours:\n{HOURS}\n\n{DISCLAIMER}\n")
print(f"📝 Saved: {TEXT_FILE}")

# --- PDF Output ---
c = canvas.Canvas(PDF_FILE, pagesize=letter)
w, h = letter
col_x = [inch * 0.5, w / 2 + inch * 0.2]
price_x = [col_x[0] + 200, w - inch * 0.5]  # Column 1 fixed offset, Column 2 right-aligned
col_y_start = h - inch * 1.8
line_height = 14
column = 0
y = col_y_start

# --- Centered Logo & Header ---
if os.path.exists(LOGO_PATH):
    logo_width = 2.5 * inch
    logo_height = 0.9 * inch
    logo_x = (w - logo_width) / 2
    logo_y = h - inch * 1.0
    c.drawImage(LOGO_PATH, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True)

c.setFont("Helvetica-Bold", 16)
c.drawCentredString(w / 2, logo_y - 20, RESTAURANT_NAME)

# Add italic tagline
c.setFont("Helvetica-Oblique", 12)
c.drawCentredString(w/2, logo_y - 40, "Reinvent the Taste of India")
#c.setFont("Helvetica", 10)
#c.drawRightString(w - inch * 0.5, logo_y - 35, ADDRESS)
#c.drawRightString(w - inch * 0.5, logo_y - 50, f"{PHONE} • {WEBSITE}")

# --- Menu Content ---
c.setFont("Helvetica", 10)
for group in group_order:
    items = grouped_items.get(group, [])
    if not items: continue
    y -= line_height  # blank line before new group
    if y < inch + 80:
        column += 1
        if column >= len(col_x): break
        y = col_y_start
        y -= line_height
    c.setFont("Helvetica-Bold", 11)
    c.drawString(col_x[column], y, group)
    y -= line_height
    c.setFont("Helvetica", 9)
    for name, price in items:
        if y < inch + 60:
            column += 1
            if column >= len(col_x): break
            y = col_y_start
            y -= line_height
            c.setFont("Helvetica-Bold", 11)
            c.drawString(col_x[column], y, group)
            y -= line_height
            c.setFont("Helvetica", 9)
        c.drawString(col_x[column], y, f"• {name}")
        if INCLUDE_PRICES and price:
            c.drawRightString(price_x[column], y, price)
        y -= line_height

# --- Footer ---
c.setFont("Helvetica", 8)
footer_y = inch * 0.6
c.drawString(inch * 0.5, footer_y + 28, f"Hours: {HOURS.replace(chr(10), ' • ')}")
c.drawString(inch * 0.5, footer_y + 14, f"Contact: {PHONE} • {WEBSITE}")
c.drawString(inch * 0.5, footer_y, f"Address: {ADDRESS}")
c.drawString(inch * 0.5, footer_y - 14, DISCLAIMER)
c.save()
print(f"📄 Saved: {PDF_FILE}")

# --- HTML Output ---
with open(HTML_FILE, "w") as f:
    f.write(f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{RESTAURANT_NAME} – Takeout Menu</title>
<style>
body {{ font-family: sans-serif; max-width: 800px; margin: auto; padding:2em; background:#fffefb }}
h1 {{ text-align: center; }}
.group {{ margin-top: 2em; }}
.item {{ display: flex; justify-content: space-between; padding: 4px 0; }}
footer {{ margin-top: 3em; font-size: 0.9em; text-align: center; }}
</style></head><body>
<h1>{RESTAURANT_NAME} – Takeout Menu</h1>
<p style="text-align:right">{ADDRESS}<br>{PHONE} • <a href="https://{WEBSITE}">{WEBSITE}</a></p>
""")
    for group in group_order:
        items = grouped_items.get(group, [])
        if not items: continue
        f.write(f'<div class="group"><h2>{group}</h2>\n')
        for name, price in items:
            if INCLUDE_PRICES:
                f.write(f'<div class="item"><span>{name}</span><span>{price}</span></div>\n')
            else:
                f.write(f'<div class="item"><span>{name}</span></div>\n')
        f.write('</div>\n')
    f.write(f"""
<footer>
<p>Hours: Monday Closed • Tuesday–Sunday 11:00am–2:00pm and 5:00pm–9:00pm</p>
<p>{DISCLAIMER}</p>
</footer>
</body></html>""")
print(f"🌐 Saved: {HTML_FILE}")

