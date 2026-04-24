const ICONS = {
  dashboard: `<svg class="w-5 h-5 mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>`,
  inventory: `<svg class="w-5 h-5 mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>`,
  finance: `<svg class="w-5 h-5 mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
  admin: `<svg class="w-5 h-5 mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>`,
  logout: `<svg class="w-5 h-5 mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>`
};

function renderSidebar(activePage) {
  const role = getRole();
  const menuItems = [
    { id: 'dashboard', name: 'Dashboard', icon: ICONS.dashboard, link: 'dashboard.html', roles: ['user'] },
    { id: 'inventory', name: 'Inventory', icon: ICONS.inventory, link: 'inventory.html', roles: ['user'] },
    { id: 'finance', name: 'Finance', icon: ICONS.finance, link: 'finance.html', roles: ['user'] },
    { id: 'admin', name: 'User Management', icon: ICONS.admin, link: 'admin.html', roles: ['admin'] },
  ];

  const html = `
    <aside class="fixed inset-y-0 left-0 w-64 bg-white border-r border-slate-200 z-50 flex flex-col shadow-sm">
        <div class="h-16 flex items-center px-6 border-b border-slate-100 gap-3">
            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-blue to-brand-navy flex items-center justify-center shadow-sm">
                <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            </div>
            <span class="text-xl font-display font-bold text-brand-navy tracking-tight">NexaFlow<span class="text-brand-blue">.</span></span>
        </div>
        <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            ${menuItems.filter(item => item.roles.includes(role)).map(item => {
                const isActive = item.id === activePage;
                const baseClasses = "flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group";
                const activeClasses = isActive ? "bg-primary-50 text-primary-700" : "text-slate-600 hover:bg-slate-50 hover:text-slate-900";
                const iconClasses = isActive ? "text-primary-600" : "text-slate-400 group-hover:text-slate-600";
                
                // Replace the generic text color in the SVG with the specific icon class
                const styledIcon = item.icon.replace('class="', `class="${iconClasses} `);

                return `
                <a href="${item.link}" class="${baseClasses} ${activeClasses}">
                    ${styledIcon}
                    ${item.name}
                </a>`;
            }).join('')}
        </nav>
        <div class="p-4 border-t border-slate-100">
            ${role === 'user' ? `
            <button onclick="deleteAccount()" class="flex w-full items-center px-3 py-2.5 text-sm font-medium text-red-600 rounded-lg hover:bg-red-50 transition-all duration-200 group mb-2">
                <svg class="w-5 h-5 mr-3 flex-shrink-0 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                Delete Company
            </button>
            ` : ''}
            <button onclick="logout()" class="flex w-full items-center px-3 py-2.5 text-sm font-medium text-slate-600 rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-all duration-200 group">
                ${ICONS.logout.replace('class="', 'class="text-slate-400 group-hover:text-slate-500 ')}
                Sign out
            </button>
        </div>
    </aside>
  `;
  const container = document.getElementById('sidebar-container');
  if (container) container.innerHTML = html;
}

function renderTopbar(pageTitle) {
  const username = getUsername() || 'User';
  const role = getRole() || 'guest';
  const initial = username.charAt(0).toUpperCase();

  const html = `
    <header class="h-16 bg-white/80 backdrop-blur-md border-b border-slate-200 flex items-center justify-between px-8 sticky top-0 z-40 transition-all">
        <h1 class="text-xl font-display font-semibold text-slate-800 tracking-tight">
          ${pageTitle}
          ${role === 'admin' ? '<span class="ml-3 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-brand-orange text-white">Admin Mode</span>' : ''}
        </h1>
        <div class="flex items-center gap-6">
            <div class="relative">
              <button id="notification-btn" onclick="toggleNotifications()" class="text-slate-400 hover:text-brand-blue transition-colors relative p-1 focus:outline-none">
                  <svg class="w-6 h-6 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
                  <span id="notification-badge" class="absolute top-1 right-1 block h-2 w-2 rounded-full bg-brand-orange ring-2 ring-white" style="display: none;"></span>
              </button>
              <div id="notifications-dropdown" class="hidden absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-lg border border-slate-100 z-50 overflow-hidden transform origin-top-right transition-all">
                <div class="bg-slate-50 px-4 py-3 border-b border-slate-100 flex justify-between items-center">
                  <h3 class="text-sm font-semibold text-slate-800">Notifications</h3>
                </div>
                <div id="notifications-container" class="max-h-96 overflow-y-auto">
                  <div class="p-4 text-center text-sm text-slate-500">Loading...</div>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-3 pl-6 border-l border-slate-200">
                <div class="text-right hidden sm:block">
                    <p class="text-sm font-semibold text-slate-700 leading-tight">${username}</p>
                </div>
                <div class="h-9 w-9 rounded-full bg-gradient-to-br from-brand-blue to-brand-navy flex items-center justify-center text-white font-semibold shadow-sm ring-2 ring-white">
                    ${initial}
                </div>
            </div>
        </div>
    </header>
  `;
  const container = document.getElementById('topbar-container');
  if (container) container.innerHTML = html;
}

// Ensure init function available globally
window.initLayout = function(pageId, pageTitle) {
    renderSidebar(pageId);
    renderTopbar(pageTitle);
    if (checkAuth()) {
      loadNotifications();
    }
};

let _notifications = [];
let _isNotificationOpen = false;

async function loadNotifications() {
  try {
    _notifications = await apiFetch('/api/invoice/notifications', { headers: authHeaders() }) || [];
    renderNotifications();
  } catch (err) {
    console.error('Failed to load notifications', err);
  }
}

function renderNotifications() {
  const container = document.getElementById('notifications-container');
  if (!container) return;
  const badge = document.getElementById('notification-badge');
  if (badge) {
    badge.style.display = _notifications.length > 0 ? 'block' : 'none';
  }
  if (_notifications.length === 0) {
    container.innerHTML = '<div class="p-4 text-center text-sm text-slate-500">No new notifications.</div>';
    return;
  }
  container.innerHTML = _notifications.map(n => {
    let icon = '';
    let iconBg = '';
    if (n.type === 'success') { icon = '✓'; iconBg = 'bg-green-100 text-green-600'; }
    else if (n.type === 'warning') { icon = '!'; iconBg = 'bg-orange-100 text-orange-600'; }
    else { icon = 'i'; iconBg = 'bg-blue-100 text-blue-600'; }
    
    return `
      <div class="px-4 py-3 hover:bg-slate-50 border-b border-slate-100 flex gap-3 items-start transition-colors cursor-pointer">
        <div class="w-8 h-8 rounded-full ${iconBg} flex items-center justify-center font-bold text-xs shrink-0">${icon}</div>
        <div class="flex-1 min-w-0">
          <p class="text-sm text-slate-800 font-medium">${n.message}</p>
          ${n.time ? `<p class="text-xs text-slate-500 mt-0.5">${fmtDate(n.time)}</p>` : ''}
        </div>
      </div>
    `;
  }).join('');
}

window.toggleNotifications = function() {
  _isNotificationOpen = !_isNotificationOpen;
  const dropdown = document.getElementById('notifications-dropdown');
  if (dropdown) {
    dropdown.classList.toggle('hidden', !_isNotificationOpen);
  }
};

// Close dropdown on outside click
document.addEventListener('click', (e) => {
  const dropdown = document.getElementById('notifications-dropdown');
  const btn = document.getElementById('notification-btn');
  if (dropdown && btn && !dropdown.contains(e.target) && !btn.contains(e.target)) {
    _isNotificationOpen = false;
    dropdown.classList.add('hidden');
  }
});

window.deleteAccount = async function() {
  if (confirm("Are you sure you want to delete your company account? This action cannot be undone.")) {
    try {
      await apiFetch('/api/auth/auth/delete', { method: 'DELETE', headers: authHeaders() });
      logout();
    } catch (err) {
      alert("Could not delete account: " + err.message);
    }
  }
};
