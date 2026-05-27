// TAB SWITCH
function switchTab(tab) {
  document.querySelectorAll('.auth-tab').forEach((t, i) => {
    t.classList.toggle('active', (i === 0 && tab === 'login') || (i === 1 && tab === 'register'));
  });
  document.getElementById('form-login').classList.toggle('active', tab === 'login');
  document.getElementById('form-register').classList.toggle('active', tab === 'register');
}

function showError(id, msg) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.style.display = 'block';
}

// LOGIN
async function login() {
  const email = document.getElementById('login-email')?.value.trim();
  const password = document.getElementById('login-password')?.value.trim();
  if (!email || !password) return showError('login-error', 'Email dan password wajib diisi.');

  const res = await fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await res.json();
  if (data.status === 'ok') window.location.href = '/dashboard';
  else showError('login-error', data.message);
}

// REGISTER
async function register() {
  const nama = document.getElementById('reg-nama')?.value.trim();
  const email = document.getElementById('reg-email')?.value.trim();
  const password = document.getElementById('reg-password')?.value.trim();
  const universitas = document.getElementById('reg-univ')?.value.trim();
  const prodi = document.getElementById('reg-prodi')?.value.trim();
  if (!nama || !email || !password || !universitas || !prodi) return showError('register-error', 'Semua field wajib diisi.');

  const res = await fetch('/api/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nama, email, password, universitas, prodi })
  });
  const data = await res.json();
  if (data.status === 'ok') {
    alert('Registrasi berhasil! Silakan login.');
    switchTab('login');
    document.getElementById('login-email').value = email;
  } else showError('register-error', data.message);
}

// LOGOUT
async function logout() {
  await fetch('/api/logout', { method: 'POST' });
  window.location.href = '/';
}

// SURVEY
const answers = {};

function selectOption(btn) {
  const q = btn.dataset.q;
  const v = parseInt(btn.dataset.v);

  document.querySelectorAll(`.option-btn[data-q="${q}"]`).forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  answers[q] = v;

  document.getElementById(`card-${q}`)?.classList.add('answered');

  const count = Object.keys(answers).length;
  const el = document.getElementById('answeredCount');
  const fill = document.getElementById('progressFill');
  if (el) el.textContent = count;
  if (fill) fill.style.width = (count / 5 * 100) + '%';
}

async function submitSurvey() {
  if (Object.keys(answers).length < 5) return alert('Jawab semua pertanyaan terlebih dahulu.');

  const payload = {};
  for (let i = 0; i < 5; i++) payload[`mbi${i + 1}`] = answers[i];

  const res = await fetch('/api/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (res.ok) window.location.href = '/result';
}

// CHATBOT
function toggleChat() {
  const win = document.getElementById('chatWindow');
  if (win) win.classList.toggle('open');
}

function openChat() {
  const chatbot = document.getElementById('chatbot');
  const win = document.getElementById('chatWindow');
  if (chatbot) chatbot.style.display = 'block';
  if (win) win.classList.add('open');
}

async function sendChat() {
  const input = document.getElementById('chatInput');
  const msg = input?.value.trim();
  if (!msg) return;

  appendMsg(msg, 'user');
  input.value = '';

  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: msg, burnout: window.burnoutLevel || '' })
  });

  const data = await res.json();
  appendMsg(data.reply, 'bot');
}

function appendMsg(text, type) {
  const box = document.getElementById('chatMessages');
  if (!box) return;
  const div = document.createElement('div');
  div.className = `msg msg-${type}`;
  div.textContent = text;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}
