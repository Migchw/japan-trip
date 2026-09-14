# 🇯🇵 AGENTS.md - Japan Trip 2026 Developer & Agent Guide

Welcome to the **Japan Trip 2026** repository. This guide provides AI agents and human developers with complete instructions on the project architecture, data formats, tooling workflows, and deployment procedures.

---

## 📌 Project Overview

This repository powers an interactive travel and dining catalog for a trip across **Tokyo, Osaka, Kyoto (including Uji Matcha Trail), and Yamanashi**, totaling **71 curated destinations**.

### Key Deliverables & Interfaces:
1. **Live Interactive Web App (GitHub Pages)**:
   - URL: [https://migchw.github.io/japan-trip/](https://migchw.github.io/japan-trip/)
   - Features: Real-time search, city filtering (Tokyo / Osaka / Kyoto / Yamanashi), dual display (Mobile-first Card View with thumbnail switcher + Detailed Table View), image lightbox modal, and direct Google Maps navigation.
2. **Google Sheets Sync**:
   - Supported via `japan_trip_places_with_images.tsv` using native `=IMAGE("...")` and `=HYPERLINK("...", "📍 แผนที่")` formulas.
   - 1-click clipboard paste script (`python src/copy_to_clipboard.py`).
   - Standalone Google Apps Script automation (`google_apps_script.js`).
3. **Structured Datasets**:
   - `japan_trip_places.csv`: Single source of truth.
   - `japan_trip_places_with_images.tsv`: Spreadsheet-ready formatted data.

---

## 🗂️ Directory & File Structure

```text
japan-trip/
├── .agents/
│   └── skills/
│       └── japan-trip-sync/
│           └── SKILL.md            # Antigravity skill specification for trip synchronization
├── src/
│   ├── fetch_review_photos.py      # Scrapes authentic customer review photos via Yahoo Japan
│   ├── video_extractor.py          # Downloads & extracts keyframes/audio from TikTok/Reels/Shorts
│   ├── catalog_builder.py          # Central pipeline syncing CSV -> TSV, HTML, and Apps Script
│   └── copy_to_clipboard.py        # Copies TSV directly to Windows clipboard with UTF-16LE
├── index.html                      # Primary web app deployed on GitHub Pages (root)
├── japan_trip_visual.html          # Standalone visual reference app
├── japan_trip_places.csv           # Master CSV database (71 places)
├── japan_trip_places_with_images.tsv # Formatted TSV for Google Sheets paste
├── japan_trip_places.tsv           # Plain TSV
├── google_apps_script.js           # Apps Script snippet to regenerate sheet programmatically
└── AGENTS.md                       # This developer & agent guide
```

---

## 📊 Data Schema (`japan_trip_places.csv`)

Every place in `japan_trip_places.csv` must follow this 11-column specification:

| Column | Name | Type | Description / Example |
| :--- | :--- | :--- | :--- |
| 1 | `ID` | Integer | Consecutive numerical ID (1, 2, ... 71). |
| 2 | `City` | String | `Tokyo`, `Osaka`, `Kyoto`, `Yamanashi`. |
| 3 | `Area` | String | Specific district, e.g., `Uji (Byodoin Omotesando)`, `Ginza`, `Namba`. |
| 4 | `Name` | String | Bilingual name: English + Kanji/Kana, e.g., `Masuda Chaho (ますだ茶舗 - มาสึดะ ชาโฮะ)`. |
| 5 | `Category` | String | Thai primary category: `ร้านอาหาร`, `คาเฟ่ / ขนมหวาน`, `สถานที่ท่องเที่ยว`, `ช้อปปิ้ง`. |
| 6 | `Type` | String | Detailed culinary/activity type (Thai + English). |
| 7 | `Hours` | String | Clean hours format, e.g., `10:00 – 18:00 (L.O. 17:30)`. |
| 8 | `Signature` | String | Signature dishes and highlights. Personal notes enclosed in `(⭐ Note)`. |
| 9 | `ReviewPhotos` | String | Pipe-separated real review image URLs: `url1 \| url2 \| url3 \| url4`. |
| 10 | `MapsURL` | String | Google Maps URL with lat/long or place search parameters. |
| 11 | `ImageSearchURL` | String | Google Image search query URL for user convenience. |

---

## 🛠️ Workflows & Agent Runbooks

### 1. Adding New Places from User Prompt or Links
1. Format place details matching the schema.
2. Append new row(s) to `japan_trip_places.csv`.
3. Fetch authentic photos (see step 2).
4. Run `python src/catalog_builder.py`.
5. Run `python src/copy_to_clipboard.py`.
6. Commit and push to Git.

### 2. Scraping Authentic Japanese Review Photos
Do **NOT** use generic stock photos or unverified Google image scrapers. Use:
```bash
python src/fetch_review_photos.py "<Japanese Name> <Area or Menu>"
```
This fetches real review images from Yahoo Japan's food media index (`msp.c.yimg.jp`), guaranteeing:
- High reliability without CAPTCHAs or API keys.
- Real dishes photographed by actual diners.
- 3 to 4 distinct images per destination.

### 3. Extracting Places from Video Reviews (TikTok, Shorts, Reels)
When the user supplies a video link:
```bash
python src/video_extractor.py "<VIDEO_URL>" scratch/video_temp
```
- `uvx yt-dlp` fetches the full resolution video without installing global packages.
- `ffmpeg` extracts frames at 1 fps into `scratch/video_temp/frames/`.
- Inspect frames with `view_file` to capture store facades, menu cards, and map overlays.

### 4. Running the Build Pipeline
Whenever `japan_trip_places.csv` is modified, run:
```bash
python src/catalog_builder.py
```
This automatically updates:
- `japan_trip_places_with_images.tsv` (with `=IMAGE()` and `=HYPERLINK()`).
- `index.html` (updates filter counters, e.g., `เกียวโต (17)` and `placesData` array).
- `japan_trip_visual.html`.
- `google_apps_script.js`.

### 5. Syncing to Google Sheets via Clipboard
```bash
python src/copy_to_clipboard.py
```
- Uses Win32 API `OpenClipboard` with `CF_UNICODETEXT` (UTF-16LE).
- Allows the user to simply press `Ctrl + V` in cell `A1` on Google Sheets to immediately see text, links, and embedded images.

### 6. Deploying to GitHub Pages
GitHub Pages is configured to serve from the `main` branch root (`/`). Any push to `main` automatically triggers deployment:
```bash
git add .
git commit -m "Add new destinations: <summary>"
git push origin main
```
Deployment takes ~20-30 seconds. Verify status with:
```bash
gh api repos/Migchw/japan-trip/pages/builds/latest
```

---

## 💡 Quality Guidelines for Future Agents

- **Documentation Integrity**: Keep existing comments, categories, and bilingual place names intact.
- **Mobile First**: `index.html` is designed to be fully usable on mobile screens during the trip. Ensure images are lazily loaded (`loading="lazy"`) and click targets remain at least 44x44px.
- **No Stock Photos**: Always preserve the 3-4 real review photos requirement.
- **Formulas**: Keep Google Sheets formula syntax intact (`=IMAGE("...")` and `=HYPERLINK("...", "...")`).
