/* App shell: auth guard, sidebar render, permission helpers, toast */

function requireAuth() {
  if (!localStorage.getItem('hr_access_token')) {
    window.location.href = '/index.html';
    return false;
  }
  return true;
}

function getUser()        { return JSON.parse(localStorage.getItem('hr_user') || '{}'); }
function getPermissions() { return JSON.parse(localStorage.getItem('hr_permissions') || '{}'); }

function canView(module)   { return !!(getPermissions()[module]?.can_view); }
function canCreate(module) { return !!(getPermissions()[module]?.can_create); }
function canEdit(module)   { return !!(getPermissions()[module]?.can_edit); }
function canDelete(module) { return !!(getPermissions()[module]?.can_delete); }

function logout() {
  localStorage.clear();
  window.location.href = '/index.html';
}

function initials(name) {
  return (name || '?').split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
}

/* ── Toast ──────────────────────────────────────────────────────────────── */
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  const icons = { success: '✓', error: '✕', info: 'ℹ' };
  toast.innerHTML = `<span>${icons[type] || 'ℹ'}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity .4s'; setTimeout(() => toast.remove(), 400); }, 3500);
}

/* ── Sidebar nav definition ─────────────────────────────────────────────── */
const NAV_ITEMS = [
  { section: 'MAIN' },
  { label: 'Dashboard',       icon: '⊞',  href: '/dashboard.html',  module: 'DASHBOARD'       },
  { label: 'Employees',       icon: '👤', href: '/employees.html',  module: 'EMPLOYEES'       },
  { label: 'Departments',     icon: '🏢', href: '/departments.html',module: 'DEPARTMENTS'     },
  { section: 'HR MODULES' },
  { label: 'Payroll',         icon: '💰', href: '#',                module: 'PAYROLL',    soon: true },
  { label: 'Attendance',      icon: '🕐', href: '/attendance.html', module: 'ATTENDANCE' },
  { label: 'Leaves',          icon: '📅', href: '#',                module: 'LEAVES',     soon: true },
  { label: 'Performance',     icon: '📈', href: '#',                module: 'PERFORMANCE',soon: true },
  { label: 'Recruitment',     icon: '💼', href: '#',                module: 'RECRUITMENT',soon: true },
  { label: 'Reports',         icon: '📊', href: '#',                module: 'REPORTS',    soon: true },
  { section: 'ADMIN' },
  { label: 'User Management', icon: '👥', href: '/users.html',      module: 'USER_MANAGEMENT'  },
  { label: 'Roles & Perms',   icon: '🛡', href: '/roles.html',               module: 'ROLE_MANAGEMENT'  },
  { label: 'Emp. Permissions',icon: '🔑', href: '/employee-permissions.html', module: 'ROLE_MANAGEMENT'  },
];

function buildSidebar(activePage) {
  const perms = getPermissions();
  const user  = getUser();

  const nav = document.getElementById('sidebar-nav');
  if (!nav) return;

  let html = '';
  for (const item of NAV_ITEMS) {
    if (item.section) {
      html += `<div class="nav-section-label">${item.section}</div>`;
      continue;
    }
    if (!perms[item.module]) continue;  // hide if no permission
    const active = activePage === item.href ? 'active' : '';
    const soonBadge = item.soon ? ' <span style="font-size:9px;background:rgba(255,255,255,.1);padding:1px 5px;border-radius:4px;margin-left:auto;">soon</span>' : '';
    html += `<a href="${item.href}" class="nav-item ${active}">${item.icon} ${item.label}${soonBadge}</a>`;
  }
  nav.innerHTML = html;

  // User card
  const userCard = document.getElementById('sidebar-user');
  if (userCard) {
    userCard.innerHTML = `
      <div class="user-card">
        <div class="user-avatar">${initials(user.full_name)}</div>
        <div class="user-info">
          <div class="user-name">${user.full_name || 'User'}</div>
          <div class="user-role">${user.role_name || ''}</div>
        </div>
      </div>
      <button class="btn-logout" onclick="logout()">Sign out</button>`;
  }
}

/* ── Number formatter ───────────────────────────────────────────────────── */
function formatCurrency(val) {
  if (!val) return '—';
  return '₹ ' + Number(val).toLocaleString('en-IN');
}
function formatDate(d) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' });
}
function statusBadge(s) {
  const map = { 'Active': 'badge-active', 'Inactive': 'badge-inactive', 'On Leave': 'badge-leave' };
  return `<span class="badge ${map[s] || 'badge-inactive'}">${s}</span>`;
}
function typeBadge(t) {
  const map = { 'Full-Time':'badge-ft','Part-Time':'badge-pt','Contract':'badge-contract','Intern':'badge-intern' };
  return `<span class="badge ${map[t] || ''}">${t || '—'}</span>`;
}
