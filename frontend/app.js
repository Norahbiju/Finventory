// ===== Finventory — Shared JS Utilities =====
// All API calls go through nginx reverse proxy → no hardcoded IPs needed.
// Works on localhost, EC2, or any server without changes.

const AUTH_URL      = '/api/auth';
const INVENTORY_URL = '/api/inventory';
const FINANCE_URL   = '/api/finance';
const INVOICE_URL   = '/api/invoice';
const AI_URL        = '/api/ai';
const ANALYTICS_URL = '/api/invoice'; // merged into invoice_service
const OCR_URL       = '/api/ocr';

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

function enforceRoleAccess(allowedRoles) {
  if (!checkAuth()) return;
  const currentRole = getRole();
  if (!allowedRoles.includes(currentRole)) {
    // Redirect based on their role
    window.location.replace(currentRole === 'admin' ? 'admin.html' : 'dashboard.html');
  }
}

function logout() {
  localStorage.clear();
  window.location.href = 'login.html';
}

// --- Generic fetch helpers ---
async function apiFetch(url, options = {}) {
  let res;
  try {
    const isGet = !options.method || options.method.toUpperCase() === 'GET';
    const finalUrl = isGet ? `${url}${url.includes('?') ? '&' : '?'}t=${Date.now()}` : url;
    res = await fetch(finalUrl, options);
  } catch (networkErr) {
    console.error('Network Error:', networkErr);
    throw new Error('Cannot reach the server. Please check your connection.');
  }

  if (res.status === 401) { logout(); return null; }

  // Safely parse: only attempt JSON if the content-type says so
  const contentType = res.headers.get('content-type') || '';
  let data;
  if (contentType.includes('application/json')) {
    data = await res.json();
  } else {
    const text = await res.text();
    // Surface any readable server error message
    if (!res.ok) throw new Error(text.trim() || `Server error (${res.status})`);
    return text;
  }

  if (!res.ok) throw new Error(data.detail || data.message || `Server error (${res.status})`);
  return data;
}

// --- Format helpers ---
function fmtDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function fmtMoney(n) {
  return '₹' + parseFloat(n || 0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// --- Set active nav link ---
function setActiveNav() {
  const page = location.pathname.split('/').pop();
  document.querySelectorAll('.nav-links a').forEach(a => {
    if (a.getAttribute('href') === page) a.classList.add('active');
  });
}

// --- Modal helpers ---
function openModal(id) {
  document.getElementById(id).classList.add('active');
}

function closeModal(id) {
  document.getElementById(id).classList.remove('active');
}

// Dummy showToast to prevent ReferenceErrors
window.showToast = function(message, type) {
  if (type === 'error') console.error("Toast Error:", message);
  else console.log("Toast:", message);
};
