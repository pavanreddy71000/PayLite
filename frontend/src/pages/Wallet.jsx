// Wallet page: shows balance and lets the user deposit or withdraw.
// Replaces the placeholder Dashboard. Demonstrates the full write path:
//   POST deposit/withdraw  ->  then re-fetch GET /wallets/me for new balance.
//
// Why re-fetch? Your deposit/withdraw endpoints return the TRANSACTION
// record (TransferResponse), not the updated wallet. Balance is a derived
// value read from GET /wallets/me. So: mutate, then refetch.

import { useEffect, useState, useCallback } from "react";
import { apiFetch } from "../lib/api";
import { fieldErrorsFrom } from "../lib/errors";
import { useAuth } from "../context/AuthContext";

export default function Wallet() {
  const { logout } = useAuth();

  const [wallet, setWallet] = useState(null);
  const [loadError, setLoadError] = useState("");
  const [loading, setLoading] = useState(true);

  // Load (or reload) the current balance.
  const loadWallet = useCallback(async () => {
    setLoading(true);
    setLoadError("");
    try {
      const data = await apiFetch("/wallets/me");
      setWallet(data);
    } catch (err) {
      setLoadError(err.data?.message || "Failed to load wallet.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadWallet();
  }, [loadWallet]);

  return (
    <div style={styles.wrap}>
      <div style={styles.card}>
        <div style={styles.header}>
          <h1 style={styles.title}>Wallet</h1>
          <button style={styles.logout} onClick={logout}>Log out</button>
        </div>

        {loading && <p style={styles.muted}>Loading…</p>}
        {loadError && <div style={styles.error}>{loadError}</div>}

        {wallet && (
          <>
            <div style={styles.balanceLabel}>Balance</div>
            <div style={styles.balance}>
              {wallet.balance} {wallet.currency}
            </div>

            <div style={styles.actions}>
              <AmountAction
                label="Deposit"
                path="/wallets/me/deposit"
                accent="#22c55e"
                onDone={loadWallet}
              />
              <AmountAction
                label="Withdraw"
                path="/wallets/me/withdraw"
                accent="#f59e0b"
                onDone={loadWallet}
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// One reusable amount form, used for both deposit and withdraw.
// path decides which endpoint it hits; onDone re-fetches the balance.
function AmountAction({ label, path, accent, onDone }) {
  const [amount, setAmount] = useState("");
  const [errors, setErrors] = useState({});   // { amount?: "...", _general?: "..." }
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState("");

  async function submit() {
    setErrors({});
    setSuccess("");

    // Client-side guard: empty or non-positive. The backend enforces this too
    // (Field(gt=0)), but catching it here avoids a pointless round trip.
    const value = Number(amount);
    if (!amount || Number.isNaN(value) || value <= 0) {
      setErrors({ amount: "Enter an amount greater than 0." });
      return;
    }

    setSubmitting(true);
    try {
      // Send as a string to preserve decimal precision; the backend parses
      // it into a Decimal. (Number would risk float rounding on money.)
      await apiFetch(path, { method: "POST", body: { amount: amount } });
      setSuccess(`${label} successful.`);
      setAmount("");
      await onDone();               // re-fetch balance
    } catch (err) {
      setErrors(fieldErrorsFrom(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={styles.action}>
      <div style={styles.actionLabel}>{label}</div>
      <input
        style={styles.input}
        type="number"
        min="0"
        step="0.01"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        placeholder="0.00"
        onKeyDown={(e) => { if (e.key === "Enter") submit(); }}
      />
      {errors.amount && <div style={styles.fieldError}>{errors.amount}</div>}
      {errors._general && <div style={styles.fieldError}>{errors._general}</div>}
      {success && <div style={styles.success}>{success}</div>}
      <button
        style={{ ...styles.button, background: accent, opacity: submitting ? 0.6 : 1 }}
        onClick={submit}
        disabled={submitting}
      >
        {submitting ? "Working…" : label}
      </button>
    </div>
  );
}

const styles = {
  wrap: { minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#0f172a" },
  card: { width: 420, padding: 32, borderRadius: 12, background: "#1e293b", boxShadow: "0 10px 30px rgba(0,0,0,0.3)" },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 },
  title: { color: "#f8fafc", margin: 0, fontSize: 24, fontWeight: 700 },
  logout: { padding: "6px 12px", borderRadius: 8, border: "1px solid #334155", background: "transparent", color: "#cbd5e1", fontSize: 13, cursor: "pointer" },
  muted: { color: "#94a3b8", fontSize: 14 },
  balanceLabel: { color: "#94a3b8", fontSize: 13, marginBottom: 6 },
  balance: { color: "#f8fafc", fontSize: 36, fontWeight: 700, marginBottom: 28 },
  actions: { display: "flex", gap: 16 },
  action: { flex: 1, display: "flex", flexDirection: "column" },
  actionLabel: { color: "#cbd5e1", fontSize: 13, marginBottom: 8 },
  input: { padding: "10px 12px", borderRadius: 8, border: "1px solid #334155", background: "#0f172a", color: "#f8fafc", fontSize: 14, outline: "none" },
  button: { marginTop: 12, padding: "10px 16px", borderRadius: 8, border: "none", color: "#0f172a", fontSize: 14, fontWeight: 700, cursor: "pointer" },
  fieldError: { marginTop: 8, color: "#fca5a5", fontSize: 12 },
  success: { marginTop: 8, color: "#86efac", fontSize: 12 },
  error: { padding: "10px 12px", borderRadius: 8, background: "#7f1d1d", color: "#fecaca", fontSize: 13 },
};
