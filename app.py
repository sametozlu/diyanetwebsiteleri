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
from services.guide_service import get_spiritual_guides, create_video_session
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
        "hijri_date": "",
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
    return render_template("pages/kuran.html", verse=get_verse_of_day(get_lang()))


@app.route("/hadis")
def hadis():
    return render_template("pages/hadis.html", hadith=get_hadith_of_day(get_lang()))


@app.route("/fetva")
def fetva():
    return render_template("pages/fetva.html")


@app.route("/ramazan")
def ramazan():
    city = request.args.get("city", "Ankara")
    lang = get_lang()
    monthly = get_monthly_timings(city)
    return render_template("pages/ramazan.html", monthly=monthly, city=city)


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
    return render_template("pages/haberler.html")


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


@app.route("/api/guides/<guide_id>/session", methods=["POST"])
def api_guide_session(guide_id):
    data = request.get_json(silent=True) or {}
    name = data.get("name", "")
    session = create_video_session(guide_id, name)
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
