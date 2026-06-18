import json
import os
import re

from services.i18n import normalize_lang

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _load_faq():
    path = os.path.join(DATA_DIR, "fetva_faq.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_faq(lang="tr"):
    lang = normalize_lang(lang)
    data = _load_faq()
    return data.get(lang, data.get("tr", []))


def search_faq(query, lang="tr", limit=10):
    lang = normalize_lang(lang)
    q = (query or "").strip().lower()
    if not q:
        return get_faq(lang)[:limit]

    results = []
    for item in get_faq(lang):
        haystack = f"{item.get('question', '')} {item.get('answer', '')} {item.get('tags', '')}".lower()
        if q in haystack or any(word in haystack for word in q.split() if len(word) > 2):
            results.append(item)
    return results[:limit]
