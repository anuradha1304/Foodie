
const BASE = '';

function csrfToken() {
  return document.cookie.split('; ')
    .find(c => c.startsWith('XSRF-TOKEN='))?.split('=')[1];
}

class ApiError extends Error {
  constructor(code, message, fieldErrors, status) {
    super(message);
    this.code = code;
    this.fieldErrors = fieldErrors;
    this.status = status;
  }
}

async function request(method, path, body, extraHeaders = {}) {
  const headers = { 'Accept': 'application/json', ...extraHeaders };
  if (body) headers['Content-Type'] = 'application/json';
  if (method !== 'GET') {
    const token = csrfToken();
    if (token) headers['X-XSRF-TOKEN'] = decodeURIComponent(token);
  }

  const res = await fetch(BASE + path, {
    method, headers,
    credentials: 'same-origin',
    body: body ? JSON.stringify(body) : undefined
  });

  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);

  if (!res.ok) {
    if (res.status === 401 && path !== '/api/auth/me' && path !== '/api/auth/login') { 
        window.location.href = '/login.html'; 
        return; 
    }
    throw new ApiError(data?.code ?? 'INTERNAL_ERROR',
                       data?.message ?? 'Something went wrong',
                       data?.fieldErrors, res.status);
  }
  return data;
}

export const api = {
  get:  (p)       => request('GET', p),
  post: (p, b, h) => request('POST', p, b, h),
  put:  (p, b)    => request('PUT', p, b),
  patch:(p, b)    => request('PATCH', p, b),
  del:  (p)       => request('DELETE', p)
};
