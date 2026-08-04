// Registration page. POST /users with { email, full_name, password }.
// Registration does NOT return a token — on success we send the user to
// /login (with their email prefilled) to sign in and get their token.
//
// Per-field validation errors (from your hardened UserCreate schema) map
// straight onto the matching inputs via the envelope's details[].loc.

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../lib/api";
import { fieldErrorsFrom } from "../lib/errors";

export default function Register() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  async function submit() {
    setErrors({});
    setSubmitting(true);
    try {
      await apiFetch("/users", {
        method: "POST",
        auth: false, // no token needed to register
        body: {
          email: email,
          full_name: fullName,
          password: password,
        },
      });
      // Success: registration doesn't log us in, so go to login.
      navigate("/login", { state: { email } });
    } catch (err) {
      // Envelope maps: loc ["body","email"|"full_name"|"password"] -> field
      setErrors(fieldErrorsFrom(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={styles.wrap}>
      <div style={styles.card}>
        <h1 style={styles.title}>Create account</h1>
        <p style={styles.subtitle}>Join PayLite</p>

        <label style={styles.label}>Full name</label>
        <input
          style={styles.input}
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          placeholder="Jane Doe"
        />
        {errors.full_name && <div style={styles.fieldError}>{errors.full_name}</div>}

        <label style={styles.label}>Email</label>
        <input
          style={styles.input}
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
        />
        {errors.email && <div style={styles.fieldError}>{errors.email}</div>}

        <label style={styles.label}>Password</label>
        <input
          style={styles.input}
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="At least 8 characters"
          onKeyDown={(e) => { if (e.key === "Enter") submit(); }}
        />
        {errors.password && <div style={styles.fieldError}>{errors.password}</div>}

        {errors._general && <div style={styles.error}>{errors._general}</div>}

        <button
          style={{ ...styles.button, opacity: submitting ? 0.6 : 1 }}
          onClick={submit}
          disabled={submitting}
        >
          {submitting ? "Creating…" : "Create account"}
        </button>

        <div style={styles.footer}>
          Already have an account?{" "}
          <span style={styles.link} onClick={() => navigate("/login")}>Sign in</span>
        </div>
      </div>
    </div>
  );
}

const styles = {
  wrap: { minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#0f172a" },
  card: { width: 340, padding: 32, borderRadius: 12, background: "#1e293b", boxShadow: "0 10px 30px rgba(0,0,0,0.3)", display: "flex", flexDirection: "column" },
  title: { color: "#f8fafc", margin: 0, fontSize: 26, fontWeight: 700 },
  subtitle: { color: "#94a3b8", marginTop: 4, marginBottom: 20, fontSize: 14 },
  label: { color: "#cbd5e1", fontSize: 13, marginBottom: 6, marginTop: 12 },
  input: { padding: "10px 12px", borderRadius: 8, border: "1px solid #334155", background: "#0f172a", color: "#f8fafc", fontSize: 14, outline: "none" },
  button: { marginTop: 24, padding: "11px 16px", borderRadius: 8, border: "none", background: "#6366f1", color: "white", fontSize: 15, fontWeight: 600, cursor: "pointer" },
  fieldError: { marginTop: 6, color: "#fca5a5", fontSize: 12 },
  error: { marginTop: 16, padding: "10px 12px", borderRadius: 8, background: "#7f1d1d", color: "#fecaca", fontSize: 13 },
  footer: { marginTop: 20, color: "#94a3b8", fontSize: 13, textAlign: "center" },
  link: { color: "#818cf8", cursor: "pointer", fontWeight: 600 },
};
