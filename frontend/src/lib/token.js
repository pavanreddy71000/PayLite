// Single source of truth for how the auth token is stored.
// If you ever switch from localStorage to cookies, this is the ONLY file that changes.

const TOKEN_KEY = "paylite_token";

export function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}
