"""
catalog_builder.py
Central build pipeline to synchronize:
1. `japan_trip_places.csv`
2. `japan_trip_places_with_images.tsv`
3. `japan_trip_places.tsv`
4. `index.html` (live on GitHub Pages)
5. `japan_trip_visual.html`
6. `google_apps_script.js`
"""

import csv
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "japan_trip_places.csv")
TSV_IMG_PATH = os.path.join(BASE_DIR, "japan_trip_places_with_images.tsv")
TSV_PLAIN_PATH = os.path.join(BASE_DIR, "japan_trip_places.tsv")
INDEX_HTML = os.path.join(BASE_DIR, "index.html")
VISUAL_HTML = os.path.join(BASE_DIR, "japan_trip_visual.html")
GAS_PATH = os.path.join(BASE_DIR, "google_apps_script.js")

def load_places_from_csv(csv_path: str = CSV_PATH) -> list[dict]:
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    places = []
    for r in rows:
        if not r or not r[0].isdigit():
            continue
        pid = int(r[0])
        city = r[1]
        area = r[2]
        name = r[3]
        category = r[4]
        cuisine = r[5]
        hours = r[6]
        signature_raw = r[7]
        photos_raw = r[8] if len(r) > 8 else ""
        maps_url = r[9] if len(r) > 9 else ""
        photo_search_url = r[10] if len(r) > 10 else ""

        # Extract personal note if present
        note = ""
        sig_match = re.search(r'\(⭐\s*(.*?)\)$', signature_raw)
        if sig_match:
            note = sig_match.group(1).strip()
            signature = signature_raw[:sig_match.start()].strip()
        else:
            signature = signature_raw

        photos = [p.strip() for p in photos_raw.split(" | ") if p.strip()]
        cover = photos[0] if photos else ""

        places.append({
            "id": pid,
            "city": city,
            "area": area,
            "name": name,
            "type": category,
            "cuisine": cuisine,
            "hours": hours,
            "signature": signature,
            "note": note,
            "maps_url": maps_url,
            "photo_search_url": photo_search_url,
            "photos": photos,
            "cover": cover
        })
    return places

def build_tsv(places: list[dict]):
    header = "ลำดับ\tรูปภาพ (IMAGE)\tเมือง (City)\tย่าน (Area)\tชื่อร้าน / สถานที่\tประเภท\tอาหาร / จุดเด่น\tเวลาเปิด-ปิด\tเมนูเด็ด / ไฮไลต์\tโน้ตส่วนตัว\tGoogle Maps"
    lines = [header]
    for p in places:
        img = f'=IMAGE("{p["cover"]}")' if p.get("cover") else ""
        link = f'=HYPERLINK("{p["maps_url"]}", "📍 แผนที่")' if p.get("maps_url") else ""
        row = [
            str(p["id"]),
            img,
            p["city"],
            p["area"],
            p["name"],
            p["type"],
            p["cuisine"],
            p["hours"],
            p["signature"],
            p.get("note", ""),
            link
        ]
        lines.append("\t".join(row))
    with open(TSV_IMG_PATH, 'w', encoding='utf-8', newline='') as f:
        f.write("\n".join(lines) + "\n")
    print(f"[OK] Generated {TSV_IMG_PATH} ({len(places)} items)")

def sync_html_file(filepath: str, places: list[dict]):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    total_count = len(places)
    city_counts = {}
    for p in places:
        c = p["city"]
        city_counts[c] = city_counts.get(c, 0) + 1

    content = re.sub(
        r'<title>🇯🇵 Japan Trip 2026 - รวมภาพรีวิวจริง \d+.*?</title>',
        f'<title>🇯🇵 Japan Trip 2026 - รวมภาพรีวิวจริง {total_count} ร้านอาหาร & สถานที่ท่องเที่ยว</title>',
        content
    )
    content = re.sub(
        r'คัดสรร \d+ ร้านเด็ด',
        f'คัดสรร {total_count} ร้านเด็ด',
        content
    )
    content = re.sub(r'ทั้งหมด \(\d+\)', f'ทั้งหมด ({total_count})', content)
    content = re.sub(r'🗼 โตเกียว \(\d+\)', f'🗼 โตเกียว ({city_counts.get("Tokyo", 0)})', content)
    content = re.sub(r'🐙 โอซาก้า \(\d+\)', f'🐙 โอซาก้า ({city_counts.get("Osaka", 0)})', content)
    content = re.sub(r'⛩️ เกียวโต \(\d+\)', f'⛩️ เกียวโต ({city_counts.get("Kyoto", 0)})', content)
    content = re.sub(r'🗻 ยามานาชิ \(\d+\)', f'🗻 ยามานาชิ ({city_counts.get("Yamanashi", 0)})', content)

    m = re.search(r'const placesData = (\[.*?\]);', content, re.DOTALL)
    if m:
        new_places_json = json.dumps(places, ensure_ascii=False)
        content = content[:m.start()] + f"const placesData = {new_places_json};" + content[m.end():]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OK] Synced HTML: {filepath} ({total_count} places)")

def sync_gas(places: list[dict]):
    if not os.path.exists(GAS_PATH):
        return
    with open(GAS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    total_count = len(places)
    content = re.sub(r'รวม \d+ ร้านอาหาร', f'รวม {total_count} ร้านอาหาร', content)

    header_row = ["ลำดับ", "ภาพรีวิวจริง", "เมือง", "ย่าน", "ชื่อร้าน / สถานที่", "ประเภท", "อาหาร / จุดเด่น", "เวลาเปิด-ปิด", "เมนูเด็ด / ไฮไลต์", "โน้ตส่วนตัว", "Google Maps"]
    data_matrix = [header_row]
    for p in places:
        img_formula = f'=IMAGE("{p["cover"]}")' if p.get("cover") else ""
        maps_formula = f'=HYPERLINK("{p["maps_url"]}", "📍 แผนที่")' if p.get("maps_url") else ""
        data_matrix.append([
            str(p["id"]),
            img_formula,
            p["city"],
            p["area"],
            p["name"],
            p["type"],
            p["cuisine"],
            p["hours"],
            p["signature"],
            p.get("note", ""),
            maps_formula
        ])

    m = re.search(r'var data = (\[\[.*?\]\]);', content, re.DOTALL)
    if m:
        new_data_json = json.dumps(data_matrix, ensure_ascii=False)
        content = content[:m.start()] + f"var data = {new_data_json};" + content[m.end():]

    with open(GAS_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OK] Synced Google Apps Script: {GAS_PATH} ({total_count} places)")

def build_all():
    print("Building and synchronizing Japan Trip project...")
    places = load_places_from_csv()
    build_tsv(places)
    sync_html_file(INDEX_HTML, places)
    sync_html_file(VISUAL_HTML, places)
    sync_gas(places)
    print("Build complete!")

if __name__ == "__main__":
    build_all()
