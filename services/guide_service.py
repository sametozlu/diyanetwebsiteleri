import json
import os
import re
import secrets
from datetime import datetime, timedelta

from services.i18n import normalize_lang, t

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

SLOT_HOURS = [9, 10, 11, 14, 15, 16, 17]


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


def get_available_slots(guide_id, lang="tr"):
    guide = get_guide(guide_id, lang)
    if not guide:
        return None

    lang = normalize_lang(lang)
    slots = []
    today = datetime.now().replace(minute=0, second=0, microsecond=0)
    for day_offset in range(7):
        day = today + timedelta(days=day_offset)
        for hour in SLOT_HOURS:
            slot_time = day.replace(hour=hour)
            if slot_time <= datetime.now():
                continue
            taken = (hash(f"{guide_id}-{slot_time.isoformat()}") % 5) == 0
            slots.append({
                "id": f"{guide_id}-{slot_time.strftime('%Y%m%d%H')}",
                "datetime": slot_time.isoformat(),
                "date": slot_time.strftime("%d.%m.%Y"),
                "time": slot_time.strftime("%H:%M"),
                "available": not taken and guide["available"],
            })
    return {"guide": guide, "slots": slots[:21]}


def book_appointment(guide_id, payload, lang="tr"):
    guide = get_guide(guide_id, lang)
    if not guide:
        return None

    name = (payload.get("name") or "").strip()[:60]
    topic = (payload.get("topic") or "").strip()[:300]
    slot_id = payload.get("slot_id", "")
    prep = {
        "urgency": payload.get("urgency", "normal"),
        "preferred_lang": payload.get("preferred_lang", "TR"),
        "notes": (payload.get("notes") or "").strip()[:500],
        "privacy_accepted": bool(payload.get("privacy_accepted")),
    }

    if not name or not topic or not prep["privacy_accepted"]:
        return {"error": "validation", "message": t("booking_validation", lang)}

    return {
        "ok": True,
        "reference": secrets.token_hex(4).upper(),
        "guide": guide,
        "slot_id": slot_id,
        "visitor": name,
        "topic": topic,
        "prep": prep,
        "message": t("booking_sent", lang),
    }


def create_video_session(guide_id, visitor_name="", prep=None):
    guide = get_guide(guide_id)
    if not guide:
        return None
    if not guide["available"]:
        return {"error": "unavailable", "guide": guide}

    prep = prep or {}
    if prep and not prep.get("privacy_accepted", True):
        return {"error": "validation", "message": t("session_privacy_required", "tr")}

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
        "prep": prep,
    }
