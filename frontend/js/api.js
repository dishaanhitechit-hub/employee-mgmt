/* Centralised API client — adds auth header, handles 401 auto-logout */
const API_BASE = '/api';

async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('hr_access_token');
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    localStorage.clear();
    window.location.href = '/index.html';
    return;
  }

  const json = await res.json();
  if (!json.success) throw new Error(json.message || 'Request failed');
  return json;
}

const api = {
  get:    (path)         => apiFetch(path),
  post:   (path, body)   => apiFetch(path, { method: 'POST',   body: JSON.stringify(body) }),
  put:    (path, body)   => apiFetch(path, { method: 'PUT',    body: JSON.stringify(body) }),
  delete: (path)         => apiFetch(path, { method: 'DELETE' }),
};
