# AdDiagnose.AI 🎯 - Streamlit Dashboard

Sebuah dashboard sederhana, elegan, dan interaktif yang dibangun menggunakan **Streamlit**, **Pandas**, dan **Plotly** untuk melakukan standardisasi data performa iklan dari Meta Ads maupun Google Ads, sekaligus mendiagnosis psikologi copywriting iklan.

## Fitur Utama MVP

1. **Auto-Detection & Standardisasi Kolom**: Mendeteksi otomatis sumber data (Meta Ads atau Google Ads) berdasarkan nama kolom (seperti `Amount Spent` atau `Cost`) dan melakukan normalisasi metrik inti (Spend, Impressions, Clicks, Conversions).
2. **Kalkulator Metrik Otomatis**: Menghitung metrik penting secara lokal menggunakan Pandas:
   - **CTR (Click-Through Rate)**: $\frac{\text{Clicks}}{\text{Impressions}} \times 100$
   - **CVR (Conversion Rate)**: $\frac{\text{Conversions}}{\text{Clicks}} \times 100$
   - **CPC (Cost Per Click)** & **CPA (Cost Per Acquisition)**
3. **Copywriting Psychology Diagnoser**: Menganalisis teks copywriting iklan berdasarkan indikator psikologis (Hook pembuka, Urgensi, CTA, Emoji, dan Panjang Kata) serta memberikan skor dan rekomendasi perbaikan.
4. **Visualisasi Premium**: Grafik interaktif menggunakan Plotly untuk menganalisis perbandingan performa antar kampanye.

---

## Cara Menjalankan Project Secara Lokal (Localhost)

### 1. Prasyarat
Pastikan Anda sudah menginstal Python (versi 3.8 ke atas direkomendasikan).

### 2. Instalasi Dependensi
Buka terminal/command prompt di direktori project ini dan jalankan perintah berikut:
```bash
pip install -r requirements.txt
```

### 3. Menjalankan Dashboard Streamlit
Jalankan perintah berikut pada terminal:
```bash
streamlit run app.py
```
Aplikasi secara otomatis akan terbuka di browser Anda pada alamat default: `http://localhost:8501`.

---

## Menguji dengan Data Sampel
Di dalam project ini sudah disediakan dua file CSV sampel untuk pengujian langsung:
- `sample_meta_ads.csv` - Simulasi export data dari Meta Ads Manager.
- `sample_google_ads.csv` - Simulasi export data dari Google Ads.

Anda bisa memilih data sampel tersebut langsung di sidebar aplikasi, atau mengunggah data CSV Anda sendiri.
