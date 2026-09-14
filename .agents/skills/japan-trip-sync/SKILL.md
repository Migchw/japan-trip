---
name: japan-trip-sync
description: >-
  Standard workflow for adding new places, scraping authentic review photos,
  extracting travel spots from social videos (TikTok/Reels/Shorts), and deploying
  to the live Japan Trip GitHub Pages catalog.
---

# Japan Trip Catalog Synchronization Skill

Use this skill whenever adding new spots, extracting locations from social media videos, updating review photos, or synchronizing the Japan Trip database and website.

## Core Project Architecture

- **Live URL**: `https://migchw.github.io/japan-trip/`
- **Database (CSV)**: `japan_trip_places.csv` (Source of truth)
- **Google Sheets TSV**: `japan_trip_places_with_images.tsv` (with `=IMAGE()` & `=HYPERLINK()`)
- **Web App**: `index.html` (Mobile-responsive interactive catalog with Card view & Table view)
- **Automation Scripts**:
  - `src/fetch_review_photos.py`: Yahoo Japan Image Search scraper for authentic customer review photos.
  - `src/video_extractor.py`: `uvx yt-dlp` and `ffmpeg` wrapper to download video/audio & extract frames.
  - `src/catalog_builder.py`: Pipeline that synchronizes CSV, TSV, HTML, and Google Apps Script.
  - `src/copy_to_clipboard.py`: Copies TSV directly into Windows clipboard with UTF-16LE.

---

## Standard Runbook

### 1. Extracting Spots from Videos (TikTok / YouTube Shorts / Reels)
When the user shares a video link to extract spots:
```bash
python src/video_extractor.py "<VIDEO_URL>" scratch/video_temp
```
- Inspect frames in `scratch/video_temp/frames/` using `view_file` to find shop signboards, Google Maps pins, and menu boards.
- Extract shop name (Kanji + Romanized), area, opening hours, signature dishes, and creator notes.

### 2. Fetching Real Review Photos
Avoid stock photos or generic logos. Use Yahoo Japan image search via `src/fetch_review_photos.py`:
```bash
python src/fetch_review_photos.py "<Japanese Shop Name> <Signature Dish / Area>"
```
Fetch 3-4 distinct photos per place.

### 3. Adding New Places to Database
Append new rows to `japan_trip_places.csv` following the 11 columns:
1. `ID`: Next integer (e.g. 72, 73...)
2. `City`: Tokyo, Osaka, Kyoto, Yamanashi, etc.
3. `Area`: Sub-district (e.g. `Uji (Byodoin Omotesando)`)
4. `Name`: Official Name (English + Japanese)
5. `Category`: Main category (e.g. `คาเฟ่ / ขนมหวาน`, `ร้านอาหาร`, `สถานที่ท่องเที่ยว`, `ช้อปปิ้ง`)
6. `Type`: Specific subtype in Thai + English (e.g. `คาเฟ่ชาเขียวมัทฉะวิวแม่น้ำอุจิ (Matcha Riverview Cafe)`)
7. `Hours`: Standardized hours (e.g. `10:00 – 17:00`)
8. `Signature`: Best-seller menu items and notes
9. `ReviewPhotos`: Pipe-separated URLs: `url1 | url2 | url3 | url4`
10. `MapsURL`: Google Maps search URL (`https://www.google.com/maps/search/?api=1&query=...`)
11. `ImageSearchURL`: Google Image search query URL

### 4. Running the Build Pipeline
Once `japan_trip_places.csv` is updated, run:
```bash
python src/catalog_builder.py
```
This automatically:
- Generates `japan_trip_places_with_images.tsv` with formatted formulas
- Updates city filter counters and `placesData` array in `index.html` and `japan_trip_visual.html`
- Updates `google_apps_script.js`

### 5. Copying to Clipboard for Google Sheets
```bash
python src/copy_to_clipboard.py
```
The user can now simply switch to Google Sheets and press `Ctrl + V` in cell A1.

### 6. Deploying to Live Website
Commit and push to `origin main`:
```bash
git add .
git commit -m "Update trip catalog: <details>"
git push origin main
```
GitHub Pages automatically deploys the update within ~25 seconds. Verify with:
```bash
gh api repos/Migchw/japan-trip/pages/builds/latest
```
