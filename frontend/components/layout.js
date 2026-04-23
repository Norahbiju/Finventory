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
    { id: 'dashboard', name: 'Dashboard', icon: ICONS.dashboard, link: 'dashboard.html', roles: ['user', 'admin'] },
    { id: 'inventory', name: 'Inventory', icon: ICONS.inventory, link: 'inventory.html', roles: ['user', 'admin'] },
    { id: 'finance', name: 'Finance', icon: ICONS.finance, link: 'finance.html', roles: ['user', 'admin'] },
    { id: 'admin', name: 'User Management', icon: ICONS.admin, link: 'admin.html', roles: ['admin'] },
  ];

  const html = `
    <aside class="fixed inset-y-0 left-0 w-64 bg-white border-r border-slate-200 z-50 flex flex-col shadow-sm">
        <div class="h-16 flex items-center px-6 border-b border-slate-100">
            <span class="text-xl font-display font-bold text-slate-800 tracking-tight">Finventory<span class="text-primary-600">.</span></span>
        </div>
        <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            ${menuItems.filter(item => item.roles.includes(role)).map(item => {
                const isActive = item.id === activePage;
                const baseClasses = "flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group";
                const activeClasses = isActive ? "bg-primary-50 text-primary-700" : "text-slate-600 hover:bg-slate-50 hover:text-slate-900";
                const iconClasses = isActive ? "text-primary-600" : "text-slate-400 group-hover:text-slate-600";
                
                // Replace the generic text color in the SVG with the specific icon class
                const styledIcon = item.icon.replace('class="', \`class="\${iconClasses} \`);

                return \`
                <a href="\${item.link}" class="\${baseClasses} \${activeClasses}">
                    \${styledIcon}
                    \${item.name}
                </a>\`;
            }).join('')}
        </nav>
        <div class="p-4 border-t border-slate-100">
            <button onclick="logout()" class="flex w-full items-center px-3 py-2.5 text-sm font-medium text-slate-600 rounded-lg hover:bg-red-50 hover:text-red-600 transition-all duration-200 group">
                \${ICONS.logout.replace('class="', 'class="text-slate-400 group-hover:text-red-500 ')}
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
        <h1 class="text-xl font-display font-semibold text-slate-800 tracking-tight">\${pageTitle}</h1>
        <div class="flex items-center gap-4">
            <div class="flex items-center gap-3">
                <div class="text-right hidden sm:block">
                    <p class="text-sm font-semibold text-slate-700 leading-tight">\${username}</p>
                    <p class="text-xs text-slate-500 capitalize font-medium">\${role}</p>
                </div>
                <div class="h-9 w-9 rounded-full bg-gradient-to-br from-primary-500 to-brand-end flex items-center justify-center text-white font-semibold shadow-sm ring-2 ring-white">
                    \${initial}
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
};
