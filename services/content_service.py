import json
import os
import requests
from datetime import datetime
from functools import lru_cache

from services.i18n import normalize_lang, surah_name, t

TIMEOUT = 10
HEADERS = {"User-Agent": "DiyanetWebPortal/2.0"}
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# Günlük hadis için sabit Türkçe havuz (API yedek)
TURKISH_HADITH_POOL = [
    {"text": "Ameller niyetlere göredir. Herkesin niyet ettiği ne ise eline geçecek olan odur.", "collection": "Buhârî", "number": "1"},
    {"text": "Müslüman, elinden ve dilinden Müslümanların emin olduğu kimsedir.", "collection": "Buhârî", "number": "10"},
    {"text": "Kolaylaştırınız, zorlaştırmayınız; müjdeleyiniz, nefret ettirmeyiniz.", "collection": "Buhârî", "number": "69"},
    {"text": "İman yetmiş küsur şubedir. En üstünü 'Lâ ilâhe illallah' demek, en düşüğü yoldan eziyet veren şeyi kaldırmaktır.", "collection": "Müslim", "number": "35"},
    {"text": "Hiçbiriniz kendisi için istediğini kardeşi için de istemedikçe gerçek anlamda iman etmiş olmaz.", "collection": "Buhârî", "number": "13"},
]

ENGLISH_HADITH_POOL = [
    {"text": "Actions are judged by intentions, and every person will get what they intended.", "collection": "Bukhari", "number": "1"},
    {"text": "A Muslim is one from whose tongue and hand other Muslims are safe.", "collection": "Bukhari", "number": "10"},
    {"text": "Make things easy, do not make them difficult; give glad tidings and do not repel people.", "collection": "Bukhari", "number": "69"},
    {"text": "Faith has seventy-odd branches. The highest is saying 'There is no god but Allah'.", "collection": "Muslim", "number": "35"},
    {"text": "None of you truly believes until he loves for his brother what he loves for himself.", "collection": "Bukhari", "number": "13"},
]

ARABIC_HADITH_POOL = [
    {"text": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ", "collection": "البخاري", "number": "1"},
    {"text": "المُسْلِمُ مَنْ سَلِمَ المُسْلِمُونَ مِنْ لِسَانِهِ وَيَدِهِ", "collection": "البخاري", "number": "10"},
    {"text": "يَسِّرُوا وَلاَ تُعَسِّرُوا، وَبَشِّرُوا وَلاَ تُنَفِّرُوا", "collection": "البخاري", "number": "69"},
    {"text": "الإِيمَانُ بِضْعٌ وَسَبْعُونَ شُعْبَةً", "collection": "مسلم", "number": "35"},
    {"text": "لاَ يُؤْمِنُ أَحَدُكُمْ حَتَّى يُحِبَّ لأَخِيهِ مَا يُحِبُّ لِنَفْسِهِ", "collection": "البخاري", "number": "13"},
]

HADITH_POOLS = {"tr": TURKISH_HADITH_POOL, "en": ENGLISH_HADITH_POOL, "ar": ARABIC_HADITH_POOL}
HADITH_API_LANG = {"tr": "tr", "en": "en", "ar": "ar"}


def _get(url, params=None):
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def _load_esma():
    path = os.path.join(DATA_DIR, "esma_ul_husna.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _day_index():
    return datetime.now().timetuple().tm_yday


def _safe_dict(value):
    return value if isinstance(value, dict) else {}


def _collection_name(collection, lang="tr"):
    if isinstance(collection, dict):
        name = collection.get("name") or collection.get("slug") or ""
    elif isinstance(collection, str):
        name = collection
    else:
        name = ""
    mapping = {"bukhari": "Buhârî", "muslim": "Müslim", "tirmidhi": "Tirmizî", "abudawud": "Ebû Dâvûd"}
    key = name.lower().replace(" ", "").replace("-", "")
    if lang == "tr":
        return mapping.get(key, name.replace("-", " ").title() if name else "Hadis")
    return name.title() if name else "Hadith"


def get_verse_of_day(lang="tr"):
    lang = normalize_lang(lang)
    day = _day_index()
    surah = (day % 114) + 1

    meta = _get(f"https://api.alquran.cloud/v1/surah/{surah}")
    ayah_count = 7
    if meta and meta.get("data"):
        ayah_count = meta["data"].get("numberOfAyahs", 7)

    ayah_num = ((day - 1) % ayah_count) + 1

    single = _get(
        f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah_num}/editions/quran-uthmani,tr.diyanet,en.sahih"
    )
    if single and single.get("data"):
        editions = single["data"]
        arabic = turkish = english = ""
        if isinstance(editions, list):
            for ed in editions:
                ident = ed.get("edition", {}).get("identifier", "")
                text = ed.get("text", "").strip()
                if "uthmani" in ident:
                    arabic = text
                elif ident == "tr.diyanet":
                    turkish = text
                elif "en.sahih" in ident:
                    english = text

        ref_tr = f"{surah_name(surah, 'tr')}, {ayah_num}. ayet"
        ref_en = f"Surah {surah}, verse {ayah_num}"
        ref_ar = f"سورة {surah}، آية {ayah_num}"

        return {
            "chapter": surah,
            "verse": ayah_num,
            "arabic": arabic,
            "turkish": turkish,
            "english": english,
            "ref": ref_tr if lang == "tr" else ref_en if lang == "en" else ref_ar,
            "text": turkish if lang == "tr" else english if lang == "en" else arabic,
        }

    return _fallback_verse(lang)


def get_hadith_of_day(lang="tr"):
    lang = normalize_lang(lang)
    day = _day_index()
    hadith_id = 2962 + (day % 500)
    api_lang = HADITH_API_LANG.get(lang, "tr")
    data = _get(
        "https://hadeethenc.com/api/v1/hadeeths/one/",
        params={"language": api_lang, "id": hadith_id},
    )
    if data and data.get("title"):
        return {
            "text": data["title"].strip(),
            "collection": data.get("attribution", t("nav_hadith", lang)) or t("nav_hadith", lang),
            "number": data.get("id"),
            "arabic": data.get("hadeeth", "") if lang != "ar" else "",
        }

    pool = HADITH_POOLS.get(lang, TURKISH_HADITH_POOL)
    item = pool[day % len(pool)]
    return {
        "text": item["text"],
        "collection": item["collection"],
        "number": item["number"],
        "arabic": item["text"] if lang == "ar" else "",
    }


def get_esma_of_day(lang="tr"):
    lang = normalize_lang(lang)
    names = _load_esma()
    item = names[(_day_index() - 1) % len(names)]
    return {
        "order": item["order"],
        "ar": item["ar"],
        "name": item["tr"] if lang == "tr" else item["en"] if lang == "en" else item["ar"],
        "meaning": item["meaning_tr"] if lang == "tr" else item["meaning_en"] if lang == "en" else item.get("meaning_en", item["ar"]),
    }


def get_daily_reminder(lang="tr"):
    lang = normalize_lang(lang)
    verse = get_verse_of_day(lang)
    hadith = get_hadith_of_day(lang)
    esma = get_esma_of_day(lang)
    return {
        "verse": verse.get("text", ""),
        "hadith": hadith.get("text", ""),
        "name": esma.get("name", ""),
        "name_meaning": esma.get("meaning", ""),
        "hijri": get_hijri_date(lang),
        "message": "",
        "date": datetime.now().strftime("%Y-%m-%d"),
    }


def get_hourly_reminder(lang="tr"):
    lang = normalize_lang(lang)
    hour = datetime.now().hour
    names = _load_esma()
    item = names[hour % len(names)]
    hadith = get_hadith_of_day(lang)
    return {
        "verse": get_verse_of_day(lang).get("text", ""),
        "hadith": hadith.get("text", ""),
        "name": item["tr"] if lang == "tr" else item["en"] if lang == "en" else item["ar"],
        "name_meaning": item["meaning_tr"] if lang == "tr" else item["meaning_en"] if lang == "en" else item.get("meaning_en", ""),
        "updated": datetime.now().strftime("%Y-%m-%dT%H:00:00"),
    }


@lru_cache(maxsize=4)
def _hijri_cached(lang):
    now = datetime.now()
    date_str = f"{now.day:02d}-{now.month:02d}-{now.year}"
    data = _get(f"https://api.islamic.app/v1/hijri/g-to-h/{date_str}")
    if data and data.get("data"):
        h = _safe_dict(data["data"].get("hijri"))
        month_info = _safe_dict(h.get("month"))
        months_tr = {
            1: "Muharrem", 2: "Safer", 3: "Rebiülevvel", 4: "Rebiülahir",
            5: "Cemaziyelevvel", 6: "Cemaziyelahir", 7: "Recep", 8: "Şaban",
            9: "Ramazan", 10: "Şevval", 11: "Zilkade", 12: "Zilhicce",
        }
        month = months_tr.get(month_info.get("number", 1), month_info.get("en", ""))
        if lang == "ar":
            return f"{h.get('day')} {month_info.get('ar', '')} {h.get('year')}"
        if lang == "en":
            return f"{h.get('day')} {month_info.get('en', '')} {h.get('year')}"
        return f"{h.get('day')} {month} {h.get('year')}".strip()
    return ""


def get_hijri_date(lang="tr"):
    return _hijri_cached(normalize_lang(lang))


def _fallback_verse(lang):
    defaults = {
        "tr": "Şüphesiz namaz, müminlere belirli vakitlerde farz kılınmıştır. (Nisâ, 103)",
        "en": "Indeed, prayer has been decreed upon the believers at specified times. (An-Nisa, 103)",
        "ar": "إِنَّ الصَّلَاةَ كَانَتْ عَلَى الْمُؤْمِنِينَ كِتَابًا مَّوْقُوتًا",
    }
    return {
        "chapter": 4,
        "verse": 103,
        "arabic": "إِنَّ الصَّلَاةَ كَانَتْ عَلَى الْمُؤْمِنِينَ كِتَابًا مَّوْقُوتًا",
        "turkish": defaults["tr"],
        "english": defaults["en"],
        "ref": "Nisâ, 103. ayet" if lang == "tr" else "An-Nisa, 103",
        "text": defaults.get(lang, defaults["tr"]),
    }
