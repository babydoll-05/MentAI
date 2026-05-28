from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pickle
import os
from datetime import datetime
from dotenv import load_dotenv
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from groq import Groq

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__)
app.secret_key = 'mentai_secret_key'
app.jinja_env.globals.update(enumerate=enumerate)

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'model.pkl')
LE_PATH = os.path.join(BASE_DIR, 'model', 'label_encoder.pkl')

with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)
with open(LE_PATH, 'rb') as f:
    le = pickle.load(f)

import json
METRICS_PATH = os.path.join(BASE_DIR, 'model', 'metrics.json')
if not os.path.exists(METRICS_PATH):
    import subprocess, sys
    subprocess.run([sys.executable, os.path.join(BASE_DIR, 'model', 'train_model.py')], check=False)
if os.path.exists(METRICS_PATH):
    with open(METRICS_PATH, 'r') as f:
        model_metrics = json.load(f)
else:
    model_metrics = {'accuracy': '-', 'precision': '-', 'recall': '-', 'auc': '-'}

groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def get_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='mentai'
    )

QUESTIONS = [
    "Saya merasa sangat lelah karena tuntutan kuliah saya.",
    "Saya merasa tugas kuliah terlalu banyak dan membuat stres.",
    "Saya merasa kehilangan motivasi untuk belajar.",
    "Saya merasa sulit berkonsentrasi saat mengikuti perkuliahan.",
    "Saya merasa tidak bersemangat ketika memikirkan kegiatan kuliah."
]

# ─── PAGES ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM riwayat WHERE user_id = %s ORDER BY created_at DESC LIMIT 3', (session['user_id'],))
    history = cursor.fetchall()
    cursor.execute('SELECT * FROM riwayat WHERE user_id = %s ORDER BY created_at DESC LIMIT 1', (session['user_id'],))
    last = cursor.fetchone()
    cursor.close()
    db.close()

    days_ago = None
    if last and last.get('created_at'):
        delta = datetime.now() - last['created_at']
        d = delta.days
        days_ago = 'hari ini' if d == 0 else ('kemarin' if d == 1 else f'{d} hari lalu')

    return render_template('dashboard.html', user=session['user'], history=history, last=last, days_ago=days_ago)

@app.route('/survey')
def survey():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('survey.html', questions=QUESTIONS)

@app.route('/result')
def result():
    if 'user_id' not in session or 'last_result' not in session:
        return redirect(url_for('index'))
    return render_template('result.html', result=session['last_result'], metrics=model_metrics)

@app.route('/chatbot')
def chatbot_page():
    return redirect(url_for('dashboard'))

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM riwayat WHERE user_id = %s ORDER BY created_at DESC', (session['user_id'],))
    history = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('history.html', history=history)

# ─── API ──────────────────────────────────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    nama = data.get('nama', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    universitas = data.get('universitas', '').strip()
    prodi = data.get('prodi', '').strip()

    if not all([nama, email, password, universitas, prodi]):
        return jsonify({'status': 'error', 'message': 'Semua field wajib diisi.'}), 400

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO users (nama, email, password, universitas, prodi) VALUES (%s, %s, %s, %s, %s)',
            (nama, email, generate_password_hash(password), universitas, prodi)
        )
        db.commit()
        user_id = cursor.lastrowid
        cursor.close()
        db.close()

        session['user_id'] = user_id
        session['user'] = nama
        return jsonify({'status': 'ok'})
    except mysql.connector.IntegrityError:
        return jsonify({'status': 'error', 'message': 'Email sudah terdaftar.'}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if not user:
        return jsonify({'status': 'error', 'message': 'Email tidak terdaftar.'}), 401
    if not check_password_hash(user['password'], password):
        return jsonify({'status': 'error', 'message': 'Password salah.'}), 401

    session['user_id'] = user['id']
    session['user'] = user['nama']
    return jsonify({'status': 'ok'})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'ok'})

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json
    answers = [data[f'mbi{i}'] for i in range(1, 6)]
    total = sum(answers)

    prediction_encoded = model.predict([answers])[0]
    prediction = le.inverse_transform([prediction_encoded])[0]

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO riwayat (user_id, mbi1, mbi2, mbi3, mbi4, mbi5, total, burnout) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
        (session['user_id'], *answers, total, prediction)
    )
    db.commit()
    cursor.close()
    db.close()

    session['last_result'] = {
        'answers': answers,
        'total': total,
        'burnout': prediction,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return jsonify({'burnout': prediction, 'total': total})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    burnout_level = data.get('burnout', '')
    user_message = data.get('message', '')

    system_prompt = (
        f"You are MinMent, a warm and empathetic mental health companion for university students. "
        f"The user's current burnout level is: {burnout_level}. "
        f"Your default language is Indonesian (bahasa Indonesia). "
        f"CRITICAL RULE: detect the language of the user's message and always reply in that exact same language. "
        f"If the user writes in Indonesian → reply in casual Indonesian. "
        f"If the user writes in English → reply in English. "
        f"If the user writes in Javanese (basa Jawa) → reply in casual Javanese ngoko. "
        f"Never mix languages or switch unless the user switches first. "
        f"Be casual and friendly like a close friend — show empathy, be honest and warm. "
        f"Use relevant emojis occasionally (not every sentence). Never be stiff or formal. "
        f"Keep replies to 2-3 sentences, direct but warm."
    )

    try:
        response = groq_client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message}
            ],
            max_tokens=200,
            timeout=5
        )
        reply = response.choices[0].message.content
    except Exception:
        reply = "Maaf, saya butuh waktu lebih lama dari biasanya. Coba kirim pesanmu lagi ya 😊"
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True)
