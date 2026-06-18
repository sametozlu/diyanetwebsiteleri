import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime

import requests

from services.i18n import normalize_lang

TIMEOUT = 10
HEADERS = {"User-Agent": "DiyanetWebPortal/2.0"}
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

RSS_URLS = [
    "https://www.diyanet.gov.tr/tr/rss",
    "https://www.diyanet.gov.tr/rss",
]


def _load_fallback():
    path = os.path.join(DATA_DIR, "news_fallback.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _strip_html(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _parse_rss(xml_text):
    items = []
    try:
        root = ET.fromstring(xml_text)
        for item in root.iter("item"):
            title = _strip_html(item.findtext("title", ""))
            link = item.findtext("link", "")
            desc = _strip_html(item.findtext("description", ""))
            pub = item.findtext("pubDate", "")
            if title:
                items.append({
                    "title": title,
                    "summary": desc[:280] if desc else "",
                    "link": link,
                    "date": pub[:16] if pub else datetime.now().strftime("%d %b %Y"),
                    "category": "Diyanet",
                    "image": None,
                })
    except Exception:
        pass
    return items


def _fetch_rss():
    for url in RSS_URLS:
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            if r.status_code == 200 and "<rss" in r.text[:500].lower():
                items = _parse_rss(r.text)
                if items:
                    return items[:12]
        except Exception:
            continue
    return []


def get_news(lang="tr", limit=8):
    lang = normalize_lang(lang)
    live = _fetch_rss()
    if live:
        return live[:limit]

    fallback = _load_fallback()
    return fallback.get(lang, fallback.get("tr", []))[:limit]
