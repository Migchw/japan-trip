"""
fetch_review_photos.py
Utility to search and fetch high-quality, real customer review photos for Japanese food & travel spots
using Yahoo Japan Image Search (avoiding generic stock imagery and bypass API rate-limits).
"""

import urllib.request
import urllib.parse
import re
import sys
import json
import time

sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8'
}

def fetch_photos_for_query(query: str, max_photos: int = 4) -> list[str]:
    """
    Search Yahoo Japan Image Search for authentic food/place review photos.
    Returns a list of image URLs.
    """
    url = f"https://search.yahoo.co.jp/image/search?p={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
        matches = re.findall(r'\"(https://msp\.c\.yimg\.jp/images/v2/[^\"]+?\.(?:jpg|jpeg|png|webp)[^\"]*?)\"', html)
        if not matches:
            matches = re.findall(r'\"(https://[^\"]+?\.(?:jpg|jpeg|png|webp))\"', html)

        filtered = []
        for m in matches:
            if any(x in m for x in ['yimg.jp/c/logo', 's.yimg.jp/images', 'icon', 'favicon', 'badge', 'space.gif']):
                continue
            img_key = m.split('/')[-1]
            if m not in filtered and not any(p.endswith('/' + img_key) for p in filtered):
                filtered.append(m)
            if len(filtered) >= max_photos:
                break
        return filtered
    except Exception as e:
        print(f"Error searching query '{query}': {e}", file=sys.stderr)
        return []

def fetch_photos_for_place(name: str, area: str, keywords: str = "", max_photos: int = 4) -> list[str]:
    """
    Fetches photos trying multiple query fallbacks to guarantee diverse, authentic images.
    """
    clean_name = re.sub(r'\(.*?\)', '', name).strip()
    queries = [
        f"{clean_name} {keywords}".strip(),
        f"{clean_name} {area} グルメ レビュー".strip(),
        f"{name} おすすめ".strip()
    ]
    
    unique_photos = []
    for q in queries:
        photos = fetch_photos_for_query(q, max_photos=max_photos)
        for p in photos:
            img_key = p.split('/')[-1]
            if p not in unique_photos and not any(existing.endswith('/' + img_key) for existing in unique_photos):
                unique_photos.append(p)
            if len(unique_photos) >= max_photos:
                break
        if len(unique_photos) >= max_photos:
            break
        time.sleep(0.3)
        
    return unique_photos[:max_photos]

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"Fetching photos for: {query}")
        results = fetch_photos_for_query(query)
        print(f"Found {len(results)} photos:")
        for idx, r in enumerate(results, 1):
            print(f"  {idx}. {r}")
    else:
        print("Usage: python fetch_review_photos.py <search query>")
