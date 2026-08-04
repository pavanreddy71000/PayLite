// Login form. Collects email + password, calls the auth context's
// login(), and on success navigates to the dashboard. Handles the
// three async UI states: idle, submitting, error.
//
// NOTE: no HTML <form> element with onSubmit here — we use a button
// onClick to keep control explicit and avoid full-page reloads.

import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // If we arrived here right after registering, prefill the email.
  const [email, setEmail] = useState(location.state?.email || "");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleLogin() {
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
      navigate("/"); // success → dashboard
    } catch (err) {
      // err is an ApiError; err.data holds your backend's envelope.
      // For a 401 (bad creds) your backend sends {error_type, message}.
      setError(err.data?.message || "Login failed. Check your credentials.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={styles.wrap}>
      <div style={styles.card}>
        <h1 style={styles.title}>PayLite</h1>
        <p style={styles.subtitle}>Sign in to your wallet</p>

        <label style={styles.label}>Email</label>
        <input
          style={styles.input}
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          autoComplete="username"
        />

        <label style={styles.label}>Password</label>
        <input
          style={styles.input}
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
          autoComplete="current-password"
          onKeyDown={(e) => {
            if (e.key === "Enter") handleLogin();
          }}
        />

        {error && <div style={styles.error}>{error}</div>}

        <button
          style={{ ...styles.button, opacity: submitting ? 0.6 : 1 }}
          onClick={handleLogin}
          disabled={submitting}
        >
          {submitting ? "Signing in…" : "Sign in"}
        </button>

        <div style={styles.footer}>
          No account?{" "}
          <span style={styles.link} onClick={() => navigate("/register")}>Create one</span>
        </div>
      </div>
    </div>
  );
}

const styles = {
  wrap: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#0f172a",
  },
  card: {
    width: 320,
    padding: 32,
    borderRadius: 12,
    background: "#1e293b",
    boxShadow: "0 10px 30px rgba(0,0,0,0.3)",
    display: "flex",
    flexDirection: "column",
  },
  title: { color: "#f8fafc", margin: 0, fontSize: 28, fontWeight: 700 },
  subtitle: { color: "#94a3b8", marginTop: 4, marginBottom: 24, fontSize: 14 },
  label: { color: "#cbd5e1", fontSize: 13, marginBottom: 6, marginTop: 12 },
  input: {
    padding: "10px 12px",
    borderRadius: 8,
    border: "1px solid #334155",
    background: "#0f172a",
    color: "#f8fafc",
    fontSize: 14,
    outline: "none",
  },
  button: {
    marginTop: 24,
    padding: "11px 16px",
    borderRadius: 8,
    border: "none",
    background: "#6366f1",
    color: "white",
    fontSize: 15,
    fontWeight: 600,
    cursor: "pointer",
  },
  error: {
    marginTop: 16,
    padding: "10px 12px",
    borderRadius: 8,
    background: "#7f1d1d",
    color: "#fecaca",
    fontSize: 13,
  },
  footer: { marginTop: 20, color: "#94a3b8", fontSize: 13, textAlign: "center" },
  link: { color: "#818cf8", cursor: "pointer", fontWeight: 600 },
};
