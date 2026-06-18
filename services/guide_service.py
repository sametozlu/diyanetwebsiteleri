import json
import os
import re
import secrets
from datetime import datetime

from services.i18n import normalize_lang

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _load_guides():
    path = os.path.join(DATA_DIR, "manevi_rehberler.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _localized(guide, lang):
    lang = normalize_lang(lang)
    suffix = lang if lang in ("tr", "en", "ar") else "tr"
    return {
        "id": guide["id"],
        "name": guide.get(f"name_{suffix}", guide["name_tr"]),
        "title": guide.get(f"title_{suffix}", guide["title_tr"]),
        "specialty": guide.get(f"specialty_{suffix}", guide["specialty_tr"]),
        "experience": guide["experience"],
        "languages": guide.get("languages", ["TR"]),
        "available": guide.get("available", False),
        "avatar_color": guide.get("avatar_color", "#b81616"),
        "initials": "".join(part[0] for part in guide["name_tr"].split()[:2]).upper(),
    }


def get_spiritual_guides(lang="tr"):
    return [_localized(g, lang) for g in _load_guides()]


def get_guide(guide_id, lang="tr"):
    for guide in _load_guides():
        if guide["id"] == guide_id:
            return _localized(guide, lang)
    return None


def create_video_session(guide_id, visitor_name=""):
    guide = get_guide(guide_id)
    if not guide:
        return None
    if not guide["available"]:
        return {"error": "unavailable", "guide": guide}

    safe_id = re.sub(r"[^a-z0-9-]", "", guide_id.lower())
    token = secrets.token_hex(4)
    room = f"DiyanetManevi-{safe_id}-{token}"
    visitor = (visitor_name or "Ziyaretci").strip()[:40]

    return {
        "guide": guide,
        "room": room,
        "join_url": f"https://meet.jit.si/{room}",
        "embed_url": (
            f"https://meet.jit.si/{room}"
            f"#userInfo.displayName={visitor}"
            f"&config.prejoinPageEnabled=true"
            f"&config.startWithAudioMuted=false"
            f"&config.startWithVideoMuted=false"
        ),
        "created_at": datetime.now().isoformat(),
        "duration_minutes": 30,
    }
