import requests
from functools import lru_cache

from services.i18n import normalize_lang, surah_name

TIMEOUT = 12
HEADERS = {"User-Agent": "DiyanetWebPortal/2.0"}

EDITIONS = {
    "tr": "tr.diyanet",
    "en": "en.sahih",
    "ar": "quran-uthmani",
}


@lru_cache(maxsize=1)
def get_surah_list():
    try:
        r = requests.get("https://api.alquran.cloud/v1/surah", headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json().get("data", [])
        return [
            {
                "number": s["number"],
                "name": s.get("englishName", ""),
                "arabic": s.get("name", ""),
                "ayahs": s.get("numberOfAyahs", 0),
                "revelation": s.get("revelationType", ""),
            }
            for s in data
        ]
    except Exception:
        return [{"number": i, "name": f"Surah {i}", "arabic": "", "ayahs": 7, "revelation": ""} for i in range(1, 115)]


def get_surah(number, lang="tr"):
    lang = normalize_lang(lang)
    number = max(1, min(114, int(number)))
    edition = EDITIONS.get(lang, "tr.diyanet")
    arabic_ed = "quran-uthmani"

    try:
        r = requests.get(
            f"https://api.alquran.cloud/v1/surah/{number}/editions/{arabic_ed},{edition}",
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        blocks = r.json().get("data", [])
        arabic_ayahs = []
        translation_ayahs = []
        for block in blocks:
            ident = block.get("edition", {}).get("identifier", "")
            ayah_list = block.get("ayahs", [])
            if "uthmani" in ident:
                arabic_ayahs = ayah_list
            else:
                translation_ayahs = ayah_list

        ayahs = []
        for i, ar in enumerate(arabic_ayahs):
            tr_ayah = translation_ayahs[i] if i < len(translation_ayahs) else {}
            ayahs.append({
                "number": ar.get("numberInSurah", i + 1),
                "arabic": ar.get("text", ""),
                "translation": tr_ayah.get("text", ""),
            })

        meta = next((s for s in get_surah_list() if s["number"] == number), {})
        return {
            "number": number,
            "name": surah_name(number, lang),
            "arabic_name": meta.get("arabic", ""),
            "ayahs": ayahs,
            "audio": f"https://cdn.islamic.network/quran/audio-surah/128/ar.alafasy/{number}.mp3",
        }
    except Exception:
        return {
            "number": number,
            "name": surah_name(number, lang),
            "arabic_name": "",
            "ayahs": [],
            "audio": f"https://cdn.islamic.network/quran/audio-surah/128/ar.alafasy/{number}.mp3",
        }
