# Diyanet İşleri Başkanlığı Web Portalı

T.C. Diyanet İşleri Başkanlığı için geliştirilmiş, çok dilli ve etkileşimli demo web portalı. Namaz vakitleri, Kur'an/hadis içerikleri, canlı radyo, manevi rehberlik ve **görüntülü danışmanlık seansları** tek platformda sunulur.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0+-green)
![Dil](https://img.shields.io/badge/Dil-TR%20%7C%20EN%20%7C%20AR-red)

## Özellikler

### Genel
- **12+ sayfa**: Ana sayfa, namaz, Kur'an, hadis, fetva, Ramazan, kurban, hac-umre, radyo, kurumsal, haberler, iletişim, manevi rehber
- **Kırmızı-beyaz kurumsal tema** ve gerçek Diyanet logosu
- **3 dil desteği**: Türkçe, İngilizce, Arapça (RTL)
- Responsive, modern arayüz

### API Entegrasyonları
| Servis | Kullanım |
|--------|----------|
| [AlAdhan](https://aladhan.com) | Namaz vakitleri (Diyanet metodu — 13) |
| [AlQuran Cloud](https://alquran.cloud) | Günün ayeti (Diyanet meal) |
| [HadeethEnc](https://hadeethenc.com) | Günün hadisi |
| [Islamic.app](https://islamic.app) | Hicrî takvim |
| Mediatriple HLS | Diyanet Radyo (3 kanal) |

### Manevi Rehber — Görüntülü Seans
- Diyanet manevi danışman profilleri
- **Görüntülü görüşme** ([Jitsi Meet](https://meet.jit.si) altyapısı)
- Randevu talep formu
- Günlük ayet, hadis ve Esma-ül Hüsna

### Diğer
- Canlı radyo oynatıcı (HLS proxy, kesintisiz yayın)
- Manevi bildirimler (toast + tarayıcı bildirimi)
- 81 il namaz vakitleri

## Kurulum

```bash
git clone https://github.com/sametozlu/diyanetwebsiteleri.git
cd diyanetwebsiteleri
pip install -r requirements.txt
python app.py
```

Tarayıcıda açın: **http://127.0.0.1:8000**

## Proje Yapısı

```
diyanetwebsite/
├── app.py                 # Flask uygulaması ve API rotaları
├── config.py              # Port, şehirler, görsel yolları
├── requirements.txt
├── data/
│   ├── esma_ul_husna.json
│   └── manevi_rehberler.json
├── services/
│   ├── content_service.py
│   ├── prayer_service.py
│   ├── radio_service.py
│   ├── guide_service.py   # Manevi rehber + video seans
│   ├── i18n.py
│   └── notification_service.py
├── static/
│   ├── css/main.css
│   ├── js/
│   └── images/            # Logo ve İslami tema görselleri
└── templates/
    ├── base.html
    ├── partials/
    └── pages/
```

## API Uç Noktaları

| Endpoint | Açıklama |
|----------|----------|
| `GET /api/prayer/today?city=Ankara` | Günlük namaz vakitleri |
| `GET /api/content/verse` | Günün ayeti |
| `GET /api/content/hadith` | Günün hadisi |
| `GET /api/radio/stations` | Radyo kanalları |
| `GET /api/guides` | Manevi rehber listesi |
| `POST /api/guides/<id>/session` | Görüntülü seans odası oluştur |

## Dil Değiştirme

Üst bardaki **TR / AR / EN** butonları dil tercihini cookie'ye kaydeder.

## Görüntülü Seans Nasıl Çalışır?

1. **Manevi Rehber** sayfasına gidin
2. Müsait bir rehber seçin → **Görüntülü Seans Başlat**
3. Adınızı girin → **Görüşmeye Katıl**
4. Kamera/mikrofon izni verin; Jitsi üzerinden güvenli görüntülü görüşme başlar

> Demo ortamıdır. Üretimde kurumsal video altyapısı (WebRTC/SIP) entegre edilebilir.

## Ortam Değişkenleri

| Değişken | Varsayılan | Açıklama |
|----------|------------|----------|
| `PORT` | `8000` | Sunucu portu |
| `SECRET_KEY` | dev key | Flask secret |

## Lisans

Bu proje eğitim ve demo amaçlıdır. Diyanet İşleri Başkanlığı resmi web sitesi değildir.

## Geliştirici

[Samet Özlü](https://github.com/sametozlu)
