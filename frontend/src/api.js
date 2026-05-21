/**
 * Simple API helper with auth token management.
 * All backend responses follow: { success, data, message }
 */

const BASE = '/api/v1';

const isDoctorPort = window.location.port === '5174';
const storagePrefix = isDoctorPort ? 'doctor_' : 'patient_';

function getToken() {
  return localStorage.getItem(`${storagePrefix}token`);
}

async function request(method, path, body = null, customHeaders = {}) {
  const headers = { ...customHeaders };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const opts = { method, headers };

  if (body) {
    headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }

  const res = await fetch(`${BASE}${path}`, opts);

  // Handle non-JSON responses
  const contentType = res.headers.get('content-type') || '';
  if (!contentType.includes('application/json')) {
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return null;
  }

  const json = await res.json();

  if (!res.ok) {
    const msg = json?.detail?.message || json?.detail || json?.message || 'Request failed';
    const err = new Error(msg);
    err.status = res.status;
    err.code = json?.detail?.error?.code || json?.error?.code;
    throw err;
  }

  return json;
}

const api = {
  get: (path) => request('GET', path),
  post: (path, body) => request('POST', path, body),
  patch: (path, body) => request('PATCH', path, body),
  put: (path, body) => request('PUT', path, body),
  delete: (path) => request('DELETE', path),
};

export default api;
