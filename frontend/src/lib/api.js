// Central API client. Every backend call goes through here so that
// base URL, auth header, and error handling live in ONE place.

import { getToken, clearToken } from "./token";

const BASE_URL = import.meta.env.VITE_API_URL;

// Thrown for any non-OK response. Carries the parsed error body so
// callers (and forms) can read your backend's {error_type, message, details}.
export class ApiError extends Error {
  constructor(status, data) {
    super(data?.message || `Request failed with status ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.data = data; // full parsed envelope: { error_type, message, details? }
  }
}

// The main wrapper. Use this for all JSON endpoints.
//   path:    e.g. "/wallets/me"
//   options: { method, body, auth }  — body is a plain object, we JSON it for you
export async function apiFetch(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };

  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  // 401 = token missing/expired. Clear it and let the app bounce to login.
  if (res.status === 401) {
    clearToken();
    // Full reload to /login guarantees all in-memory state is reset.
    window.location.href = "/login";
    throw new ApiError(401, { message: "Session expired. Please log in again." });
  }

  // 204 No Content or empty body — nothing to parse.
  if (res.status === 204) return null;

  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }

  if (!res.ok) {
    throw new ApiError(res.status, data);
  }

  return data;
}

// Login is SPECIAL: your /auth/token endpoint uses OAuth2PasswordRequestForm,
// which expects form-urlencoded data with fields "username" and "password"
// (NOT JSON). "username" is really the email.
// gets its own function rather than going through apiFetch.
export async function login(email, password) {
  const form = new URLSearchParams();
  form.append("username", email); // backend looks this up as the email
  form.append("password", password);

  const res = await fetch(`${BASE_URL}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form.toString(),
  });

  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }

  if (!res.ok) {
    throw new ApiError(res.status, data);
  }

  return data; // { access_token, token_type }
}
