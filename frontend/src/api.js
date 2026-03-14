const BASE_URL = 'https://rheostatic-leroy-nonganglionic.ngrok-free.dev/api';

function getAuthHeader(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function register({ name, email, password }) {
  const res = await fetch(`${BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password }),
  });
  return res.json();
}

export async function login({ email, password }) {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  return res.json();
}

export async function getProfile(token) {
  const res = await fetch(`${BASE_URL}/auth/profile`, {
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(token),
    },
  });
  return res.json();
}

export async function updateProfile(token, updates) {
  const res = await fetch(`${BASE_URL}/auth/profile`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(token),
    },
    body: JSON.stringify(updates),
  });
  return res.json();
}

export async function refreshToken(token) {
  const res = await fetch(`${BASE_URL}/auth/refresh`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(token),
    },
  });
  return res.json();
}
