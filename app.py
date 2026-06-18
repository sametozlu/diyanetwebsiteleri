import requests
from urllib.parse import quote, urljoin
from flask import Flask, render_template, request, jsonify, Response, url_for
from config import SECRET_KEY, CITIES, IMAGE_ASSETS, PORT
from services.prayer_service import get_today_timings, get_monthly_timings
from services.content_service import (
    get_daily_reminder,
    get_hourly_reminder,
    get_verse_of_day,
    get_hadith_of_day,
    get_esma_of_day,
    get_hijri_date,
)
from services.radio_service import get_radio_stations, get_station
from services.notification_service import get_spiritual_bundle
from services.guide_service import (
    get_spiritual_guides,
    create_video_session,
    get_available_slots,
    book_appointment,
)
from services.qibla_service import calculate_qibla
from services.quran_service import get_surah_list, get_surah
from services.news_service import get_news
from services.fetva_service import get_faq, search_faq
from services.mosque_service import get_mosques
from services.ramadan_service import get_ramadan_status
from services.i18n import normalize_lang, t, SUPPORTED_LANGS, get_page_meta, get_js_strings

app = Flask(__name__)
app.secret_key = SECRET_KEY
HEADERS_USER_AGENT = "DiyanetWebPortal/2.0 (Mozilla/5.0 compatible)"
UPSTREAM_HEADERS = {
    "User-Agent": HEADERS_USER_AGENT,
    "Referer": "https://www.diyanetradyo.com/",
}


def get_lang():
    return normalize_lang(request.cookies.get("lang") or request.args.get("lang", "tr"))


@app.context_processor
def inject_globals():
    lang = get_lang()
    resolved_images = {
        key: url_for("static", filename=path) for key, path in IMAGE_ASSETS.items()
    }
    return {
        "cities": CITIES,
        "images": resolved_images,
        "current_city": request.args.get("city", "Ankara"),
        "radio_stations": get_radio_stations(lang),
        "hijri_date": get_hijri_date(lang),
        "lang": lang,
        "dir": "rtl" if lang == "ar" else "ltr",
        "page": get_page_meta(request.endpoint, lang),
        "js_strings": get_js_strings(lang),
        "t": lambda key, **kw: t(key, lang, **kw),
        "supported_langs": SUPPORTED_LANGS,
    }


@app.route("/set-language/<lang_code>")
def set_language(lang_code):
    from flask import make_response, redirect
    from urllib.parse import urlparse

    lang = normalize_lang(lang_code)
    referrer = request.referrer
    if referrer:
        parsed = urlparse(referrer)
        if parsed.netloc and parsed.netloc != request.host:
            referrer = "/"
    target = referrer or "/"
    resp = make_response(redirect(target))
    resp.set_cookie("lang", lang, max_age=60 * 60 * 24 * 365, path="/", samesite="Lax")
    return resp


@app.route("/")
def index():
    city = request.args.get("city", "Ankara")
    lang = get_lang()
    return render_template(
        "pages/index.html",
        prayer=get_today_timings(city, lang),
        verse=get_verse_of_day(lang),
        hadith=get_hadith_of_day(lang),
        esma=get_esma_of_day(lang),
        daily=get_daily_reminder(lang),
        city=city,
        news=get_news(lang, 3),
    )


@app.route("/namaz-vakitleri")
def namaz_vakitleri():
    city = request.args.get("city", "Ankara")
    lang = get_lang()
    return render_template(
        "pages/namaz.html",
        prayer=get_today_timings(city, lang),
        monthly=get_monthly_timings(city),
        city=city,
    )


@app.route("/kuran")
def kuran():
    lang = get_lang()
    return render_template(
        "pages/kuran.html",
        verse=get_verse_of_day(lang),
        surahs=get_surah_list(),
    )


@app.route("/hadis")
def hadis():
    return render_template("pages/hadis.html", hadith=get_hadith_of_day(get_lang()))


@app.route("/fetva")
def fetva():
    lang = get_lang()
    return render_template("pages/fetva.html", faq=get_faq(lang))


@app.route("/ramazan")
def ramazan():
    city = request.args.get("city", "Ankara")
    lang = get_lang()
    lang = get_lang()
    monthly = get_monthly_timings(city)
    ramadan = get_ramadan_status(city, lang)
    return render_template("pages/ramazan.html", monthly=monthly, city=city, ramadan=ramadan)


@app.route("/kurban")
def kurban():
    return render_template("pages/kurban.html")


@app.route("/radyo")
def radyo():
    return render_template("pages/radyo.html")


@app.route("/hac-umre")
def hac_umre():
    return render_template("pages/hac_umre.html")


@app.route("/kurumsal")
def kurumsal():
    return render_template("pages/kurumsal.html")


@app.route("/haberler")
def haberler():
    lang = get_lang()
    return render_template("pages/haberler.html", news=get_news(lang))


@app.route("/iletisim")
def iletisim():
    return render_template("pages/iletisim.html")


@app.route("/manevi-rehber")
def manevi_rehber():
    city = request.args.get("city", "Ankara")
    lang = get_lang()
    return render_template(
        "pages/manevi_rehber.html",
        bundle=get_spiritual_bundle(city, lang),
        guides=get_spiritual_guides(lang),
        city=city,
    )


@app.route("/api/guides")
def api_guides():
    return jsonify(get_spiritual_guides(get_lang()))


@app.route("/kible")
def kible():
    return render_template("pages/kible.html")


@app.route("/zikir")
def zikir():
    return render_template("pages/zikir.html")


@app.route("/cami-bul")
def cami_bul():
    city = request.args.get("city", "Ankara")
    return render_template("pages/cami_bul.html", city=city, mosques=get_mosques(city))


@app.route("/manifest.json")
def manifest():
    return app.send_static_file("manifest.json")


@app.route("/sw.js")
def service_worker():
    resp = app.send_static_file("sw.js")
    resp.headers["Content-Type"] = "application/javascript"
    resp.headers["Service-Worker-Allowed"] = "/"
    return resp


@app.route("/api/guides/<guide_id>/slots")
def api_guide_slots(guide_id):
    slots = get_available_slots(guide_id, get_lang())
    if not slots:
        return jsonify({"error": "not_found"}), 404
    return jsonify(slots)


@app.route("/api/guides/<guide_id>/book", methods=["POST"])
def api_guide_book(guide_id):
    data = request.get_json(silent=True) or {}
    result = book_appointment(guide_id, data, get_lang())
    if not result:
        return jsonify({"error": "not_found"}), 404
    if result.get("error"):
        return jsonify(result), 400
    return jsonify(result)


@app.route("/api/qibla")
def api_qibla():
    try:
        lat = float(request.args.get("lat", 0))
        lon = float(request.args.get("lon", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "invalid_coords"}), 400
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return jsonify({"error": "invalid_coords"}), 400
    return jsonify(calculate_qibla(lat, lon))


@app.route("/api/news")
def api_news():
    return jsonify(get_news(get_lang()))


@app.route("/api/fetva/search")
def api_fetva_search():
    q = request.args.get("q", "")
    return jsonify(search_faq(q, get_lang()))


@app.route("/api/quran/surahs")
def api_quran_surahs():
    return jsonify(get_surah_list())


@app.route("/api/quran/surah/<int:number>")
def api_quran_surah(number):
    return jsonify(get_surah(number, get_lang()))


@app.route("/api/mosques")
def api_mosques():
    city = request.args.get("city")
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    lat_f = float(lat) if lat else None
    lon_f = float(lon) if lon else None
    return jsonify(get_mosques(city, lat_f, lon_f))


@app.route("/api/ramadan/status")
def api_ramadan_status():
    city = request.args.get("city", "Ankara")
    return jsonify(get_ramadan_status(city, get_lang()))


@app.route("/api/guides/<guide_id>/session", methods=["POST"])
def api_guide_session(guide_id):
    data = request.get_json(silent=True) or {}
    name = data.get("name", "")
    prep = data.get("prep") or {}
    session = create_video_session(guide_id, name, prep)
    if not session:
        return jsonify({"error": "not_found"}), 404
    if session.get("error") == "unavailable":
        return jsonify(session), 409
    return jsonify(session)


# --- API Endpoints ---

@app.route("/api/prayer/today")
def api_prayer_today():
    city = request.args.get("city", "Ankara")
    return jsonify(get_today_timings(city, get_lang()))


@app.route("/api/prayer/monthly")
def api_prayer_monthly():
    city = request.args.get("city", "Ankara")
    return jsonify(get_monthly_timings(city))


@app.route("/api/content/daily")
def api_content_daily():
    return jsonify(get_daily_reminder(get_lang()))


@app.route("/api/content/hourly")
def api_content_hourly():
    return jsonify(get_hourly_reminder(get_lang()))


@app.route("/api/content/verse")
def api_content_verse():
    return jsonify(get_verse_of_day(get_lang()))


@app.route("/api/content/hadith")
def api_content_hadith():
    return jsonify(get_hadith_of_day(get_lang()))


@app.route("/api/content/bundle")
def api_content_bundle():
    city = request.args.get("city", "Ankara")
    return jsonify(get_spiritual_bundle(city, get_lang()))


@app.route("/api/radio/stations")
def api_radio_stations():
    lang = get_lang()
    stations = get_radio_stations(lang)
    public = {}
    for key, info in stations.items():
        public[key] = {
            **info,
            "playlist": f"/api/radio/playlist/{key}",
        }
    return jsonify(public)


@app.route("/api/radio/playlist/<station>")
def api_radio_playlist(station):
    info = get_station(station, get_lang())
    if not info:
        return jsonify({"error": "İstasyon bulunamadı"}), 404

    try:
        upstream = requests.get(info["stream"], headers=UPSTREAM_HEADERS, timeout=15)
        upstream.raise_for_status()
        base = info["stream"].rsplit("/", 1)[0] + "/"
        lines = []
        for line in upstream.text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                lines.append(line)
            else:
                segment = stripped if stripped.startswith("http") else urljoin(base, stripped)
                lines.append(f"/api/radio/segment/{station}?url={quote(segment, safe='')}")
        return Response(
            "\n".join(lines),
            mimetype="application/vnd.apple.mpegurl",
            headers={"Access-Control-Allow-Origin": "*", "Cache-Control": "no-cache"},
        )
    except Exception as exc:
        return jsonify({"error": "Playlist alınamadı", "detail": str(exc)}), 502


@app.route("/api/radio/segment/<station>")
def api_radio_segment(station):
    if not get_station(station):
        return jsonify({"error": "İstasyon bulunamadı"}), 404

    target = request.args.get("url")
    if not target or not target.startswith("https://"):
        return jsonify({"error": "Geçersiz segment"}), 400

    try:
        upstream = requests.get(target, headers=UPSTREAM_HEADERS, timeout=20)
        upstream.raise_for_status()
        content_type = upstream.headers.get("Content-Type", "application/octet-stream")

        if "mpegurl" in content_type or target.endswith(".m3u8") or "#EXTM3U" in upstream.text[:20]:
            base = target.rsplit("/", 1)[0] + "/"
            lines = []
            for line in upstream.text.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    lines.append(line)
                else:
                    segment = stripped if stripped.startswith("http") else urljoin(base, stripped)
                    lines.append(f"/api/radio/segment/{station}?url={quote(segment, safe='')}")
            return Response(
                "\n".join(lines),
                mimetype="application/vnd.apple.mpegurl",
                headers={"Access-Control-Allow-Origin": "*", "Cache-Control": "no-cache"},
            )

        return Response(
            upstream.content,
            content_type=content_type,
            headers={"Access-Control-Allow-Origin": "*", "Cache-Control": "no-cache"},
        )
    except Exception as exc:
        return jsonify({"error": "Segment alınamadı", "detail": str(exc)}), 502


@app.route("/api/radio/stream/<station>")
def api_radio_stream(station):
    """HLS segment proxy — CORS ve kesintisiz oynatma için."""
    info = get_station(station, get_lang())
    if not info:
        return jsonify({"error": "İstasyon bulunamadı"}), 404

    target = request.args.get("url")
    if not target:
        target = info["stream"]

    if not target.startswith("https://"):
        return jsonify({"error": "Geçersiz yayın adresi"}), 400

    try:
        upstream = requests.get(
            target,
            stream=True,
            headers=UPSTREAM_HEADERS,
            timeout=20,
        )
        upstream.raise_for_status()
        content_type = upstream.headers.get("Content-Type", "application/octet-stream")

        def generate():
            for chunk in upstream.iter_content(chunk_size=16384):
                if chunk:
                    yield chunk

        return Response(
            generate(),
            content_type=content_type,
            headers={
                "Cache-Control": "no-cache",
                "Access-Control-Allow-Origin": "*",
            },
        )
    except Exception as exc:
        return jsonify({"error": "Yayın bağlantısı kurulamadı", "detail": str(exc)}), 502


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
