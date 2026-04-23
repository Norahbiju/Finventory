// ===== Finventory — Shared JS Utilities =====
// All API calls go through nginx reverse proxy → no hardcoded IPs needed.
// Works on localhost, EC2, or any server without changes.

const AUTH_URL      = '/api/auth';
const INVENTORY_URL = '/api/inventory';
const FINANCE_URL   = '/api/finance';
const INVOICE_URL   = '/api/invoice';

// --- Token helpers ---
function getToken()    { return localStorage.getItem('token'); }
function getRole()     { return localStorage.getItem('role'); }
function getUsername() { return localStorage.getItem('username'); }

function authHeaders() {
  return { 'Content-Type': 'application/json', 'Authorization': `Bearer ${getToken()}` };
}

function checkAuth() {
  if (!getToken()) { window.location.href = 'login.html'; return false; }
  return true;
}

function logout() {
  localStorage.clear();
  window.location.href = 'login.html';
}

// --- Generic fetch helpers ---
async function apiFetch(url, options = {}) {
  try {
    const res = await fetch(url, options);
    if (res.status === 401) { logout(); return null; }
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Request failed');
    return data;
  } catch (err) {
    console.error('API Error:', err);
    throw err;
  }
}

// --- Format helpers ---
function fmtDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function fmtMoney(n) {
  return '$' + parseFloat(n || 0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// --- Set active nav link ---
function setActiveNav() {
  const page = location.pathname.split('/').pop();
  document.querySelectorAll('.nav-links a').forEach(a => {
    if (a.getAttribute('href') === page) a.classList.add('active');
  });
}
