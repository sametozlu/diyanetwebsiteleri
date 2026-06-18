import os

SECRET_KEY = os.environ.get("SECRET_KEY", "diyanet-dev-key-change-in-production")
PORT = int(os.environ.get("PORT", 8000))

# AlAdhan method 13 = Diyanet İşleri Başkanlığı
PRAYER_METHOD = 13

# Radyo istasyonları radio_service.py içinde dinamik yüklenir
RADIO_STATIONS = {}

CITIES = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Amasya", "Ankara", "Antalya",
    "Artvin", "Aydın", "Balıkesir", "Bilecik", "Bingöl", "Bitlis", "Bolu",
    "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır",
    "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun",
    "Gümüşhane", "Hakkari", "Hatay", "Isparta", "Mersin", "İstanbul", "İzmir",
    "Kars", "Kastamonu", "Kayseri", "Kırklareli", "Kırşehir", "Kocaeli", "Konya",
    "Kütahya", "Malatya", "Manisa", "Kahramanmaraş", "Mardin", "Muğla", "Muş",
    "Nevşehir", "Niğde", "Ordu", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop",
    "Sivas", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Şanlıurfa", "Uşak",
    "Van", "Yozgat", "Zonguldak", "Aksaray", "Bayburt", "Karaman", "Kırıkkale",
    "Batman", "Şırnak", "Bartın", "Ardahan", "Iğdır", "Yalova", "Karabük", "Kilis",
    "Osmaniye", "Düzce",
]

# Yerel görseller — Wikimedia Commons (İslam / Diyanet temalı)
IMAGE_ASSETS = {
    "hero": "images/hero-mosque.jpg",
    "mosque": "images/mosque-interior.jpg",
    "quran": "images/quran-mushaf.jpg",
    "ramadan": "images/ramadan-iftar.jpg",
    "hajj": "images/kaaba.jpg",
    "kurban": "images/kurban-eid.jpg",
    "radio": "images/minaret-ezan.jpg",
    "education": "images/quran-mushaf.jpg",
    "family": "images/ramadan-iftar.jpg",
    "istanbul": "images/istanbul-sultanahmet.jpg",
    "logo": "images/diyanet-logo.svg",
}
