// Shares "is the user logged in?" across the whole app without
// passing props through every component. Holds the token in React
// state (so the UI re-renders on login/logout) and mirrors it to
// localStorage via the token helpers (so a page refresh keeps you in).

import { createContext, useContext, useState } from "react";
import { getToken, saveToken, clearToken } from "../lib/token";
import { login as apiLogin } from "../lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Initialize from localStorage so a refresh doesn't log the user out.
  const [token, setToken] = useState(() => getToken());

  const isAuthenticated = Boolean(token);

  async function login(email, password) {
    const data = await apiLogin(email, password); // throws ApiError on bad creds
    saveToken(data.access_token);
    setToken(data.access_token);
  }

  function logout() {
    clearToken();
    setToken(null);
  }

  return (
    <AuthContext.Provider value={{ token, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// Convenience hook so components can do: const { isAuthenticated, login } = useAuth();
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside <AuthProvider>");
  }
  return ctx;
}
