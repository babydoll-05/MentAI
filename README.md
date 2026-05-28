<div align="center">

# 🌿 MentAI
### *Mental Health AI untuk Mahasiswa*

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-Decision%20Tree-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3%2070B-FF6B35?style=flat-square)](https://groq.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql&logoColor=white)](https://mysql.com)

*Deteksi burnout akademik mahasiswa secara cepat dan personal — dilengkapi chatbot AI multibahasa.*

</div>

---

## ✨ Fitur

- 🧠 **Deteksi Burnout** — Prediksi tingkat burnout (Rendah / Sedang / Tinggi) menggunakan model Decision Tree terlatih
- 📋 **Survei MBI-SS** — 5 pertanyaan Maslach Burnout Inventory berbasis skala 1–5
- 💬 **Chatbot MinMent** — Teman curhat AI berbasis LLaMA 3.3 70B, auto-detect bahasa (Indonesia, Inggris, Jawa)
- 📊 **Riwayat Survei** — Pantau perkembangan burnout dari waktu ke waktu
- 📄 **Export PDF** — Unduh hasil survei sebagai PDF langsung dari browser
- 🔐 **Autentikasi** — Register & login dengan password ter-hash (bcrypt)

---

## 🤖 Model AI

| Komponen | Detail |
|----------|--------|
| Algoritma | Decision Tree Classifier (scikit-learn) |
| Fitur input | MBI1 – MBI5 (skala 1–5) |
| Output | Rendah / Sedang / Tinggi |
| Accuracy | **91.7%** |
| Precision | **93.3%** |
| Recall | **91.7%** |
| AUC | **0.938** |

### Struktur Decision Tree
```
MBI2 ≤ 2.5  →  Rendah
MBI2 > 2.5
  MBI3 ≤ 2.5
    MBI4 ≤ 3.5  →  Rendah
    MBI4 > 3.5  →  Sedang
  MBI3 2.5–3.5  →  Sedang
  MBI3 > 3.5
    MBI5 ≤ 3.5  →  Sedang
    MBI5 > 3.5  →  Tinggi
```

---

## 🚀 Cara Menjalankan

### 1. Clone repository
```bash
git clone https://github.com/babydoll-05/MentAI.git
cd MentAI
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Buat file `.env`
```env
GROQ_API_KEY=gsk_your_api_key_here
```
> Dapatkan API key gratis di [console.groq.com](https://console.groq.com)

### 4. Setup database MySQL
```sql
CREATE DATABASE mentai;
USE mentai;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nama VARCHAR(100),
  email VARCHAR(100) UNIQUE,
  password VARCHAR(255),
  universitas VARCHAR(100),
  prodi VARCHAR(100)
);

CREATE TABLE riwayat (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  mbi1 INT, mbi2 INT, mbi3 INT, mbi4 INT, mbi5 INT,
  total INT,
  burnout VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. Jalankan aplikasi
```bash
python app.py
```
Buka browser di `http://localhost:5000`

> Model Decision Tree akan dilatih otomatis saat pertama kali dijalankan.

---

## 🗂️ Struktur Project

```
MentAI/
├── app.py                  # Flask backend & API routes
├── requirements.txt
├── .env                    # API key (tidak di-commit)
├── dataset/
│   └── burnout.csv         # Dataset MBI-SS
├── model/
│   ├── train_model.py      # Script training Decision Tree
│   ├── model.pkl           # Model tersimpan
│   ├── label_encoder.pkl
│   └── metrics.json        # Hasil evaluasi model
├── static/
│   ├── css/style.css
│   ├── js/
│   │   ├── main.js
│   │   └── shapegrid.js
│   └── img/                # Lottie animations & assets
└── templates/
    ├── index.html          # Landing page & auth
    ├── dashboard.html      # Dashboard + inline chatbot
    ├── survey.html         # Survei MBI-SS
    ├── result.html         # Hasil prediksi & rekomendasi
    ├── history.html        # Riwayat survei
    └── chatbot.html        # Floating chatbot widget
```

---

## 🛠️ Tech Stack

| Layer | Teknologi |
|-------|-----------|
| Backend | Python, Flask |
| Frontend | HTML, CSS, Vanilla JS |
| Machine Learning | scikit-learn, pandas, numpy |
| Database | MySQL |
| Chatbot LLM | Groq API — LLaMA 3.3 70B Versatile |
| Animasi | Lottie Web, Shapegrid Canvas |
| Auth | Werkzeug (bcrypt hash) |

---

<div align="center">

*Dibuat untuk mata kuliah Kecerdasan Buatan — Semester 4*

</div>
