from functools import lru_cache
from datetime import datetime

# Diyanet resmi yayınları — doğrulanmış benzersiz HLS adresleri
STATIONS = {
    "diyanet": {
        "name": "Diyanet Radyo",
        "name_ar": "إذاعة الديانة",
        "name_en": "Diyanet Radio",
        "tagline_tr": "Resmî Diyanet yayını",
        "tagline_ar": "البث الرسمي للديانة",
        "tagline_en": "Official Diyanet broadcast",
        "description_tr": "Diyanet İşleri Başkanlığı'nın ana radyo kanalı. Dini sohbetler, ilahiler, hutbe ve güncel programlar.",
        "description_ar": "القناة الإذاعية الرئيسية لرئاسة الشؤون الدينية.",
        "description_en": "Main radio channel of the Presidency of Religious Affairs.",
        "programs_tr": ["Hadis Sohbetleri", "İlahiler", "Güncel Duyurular"],
        "stream": "https://eustr73.mediatriple.net/videoonlylive/mtikoimxnztxlive/broadcast_5e3c1171d7d2a.smil/playlist.m3u8",
        "icon": "🕌",
        "color": "#e31919",
    },
    "kuran": {
        "name": "Diyanet Kur'an Radyo",
        "name_ar": "إذاعة القرآن",
        "name_en": "Diyanet Quran Radio",
        "tagline_tr": "Kur'an tilaveti ve tefsir",
        "tagline_ar": "تلاوة وتفسير القرآن",
        "tagline_en": "Quran recitation and tafsir",
        "description_tr": "Kur'an-ı Kerim tilaveti, hatim, tefsir ve meal yayınları. Diyanet onaylı mushaf okunuşu.",
        "description_ar": "تلاوات القرآن الكريم والتفسير والترجمة.",
        "description_en": "Holy Quran recitation, hatim, tafsir and translation.",
        "programs_tr": ["Kur'an Tilaveti", "Tefsir", "Hatim Programı"],
        "stream": "https://eustr73.mediatriple.net/videoonlylive/mtikoimxnztxlive/broadcast_5e3c14192aa92.smil/playlist.m3u8",
        "icon": "📖",
        "color": "#8b1414",
    },
    "risalet": {
        "name": "Diyanet Risalet Radyo",
        "name_ar": "إذاعة الرسالة",
        "name_en": "Diyanet Risalet Radio",
        "tagline_tr": "Hadis, siyer ve risale",
        "tagline_ar": "الحديث والسيرة والرسالة",
        "tagline_en": "Hadith, seerah and risale",
        "description_tr": "Hadis-i şerifler, siyer-i Nebevi, risale sohbetleri ve peygamber kıssaları.",
        "description_ar": "الأحاديث النبوية والسيرة والرسالة.",
        "description_en": "Prophetic hadiths, seerah and risale programs.",
        "programs_tr": ["Hadis Dersleri", "Siyer-i Nebevi", "Risale Sohbetleri"],
        "stream": "https://eustr73.mediatriple.net/videoonlylive/mtikoimxnztxlive/broadcast_5e3c1520b2626.smil/playlist.m3u8",
        "icon": "📜",
        "color": "#6b0f0f",
    },
}


@lru_cache(maxsize=1)
def _cache_key():
    return datetime.now().strftime("%Y-%m-%d-%H")


def get_radio_stations(lang="tr"):
    _cache_key()
    lang = lang if lang in ("tr", "ar", "en") else "tr"
    result = {}
    for key, info in STATIONS.items():
        name = info.get(f"name_{lang}") if lang != "tr" else info["name"]
        if not name:
            name = info["name"]
        result[key] = {
            "name": name,
            "tagline": info.get(f"tagline_{lang}", info["tagline_tr"]),
            "description": info.get(f"description_{lang}", info["description_tr"]),
            "programs": info.get("programs_tr", []),
            "stream": info["stream"],
            "type": "hls",
            "icon": info["icon"],
            "color": info["color"],
        }
    return result


def get_station(station_id, lang="tr"):
    return get_radio_stations(lang).get(station_id)
