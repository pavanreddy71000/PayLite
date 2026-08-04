// Wallet page: balance + deposit + withdraw + transfer.
// Deposit/withdraw/transfer all return a TRANSACTION record, not the
// updated wallet, so after each success we re-fetch GET /wallets/me.

import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../lib/api";
import { fieldErrorsFrom } from "../lib/errors";
import { useAuth } from "../context/AuthContext";

export default function Wallet() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const [wallet, setWallet] = useState(null);
  const [loadError, setLoadError] = useState("");
  const [loading, setLoading] = useState(true);

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
          <div style={{ display: "flex", gap: 8 }}>
            <button style={styles.logout} onClick={() => navigate("/history")}>History</button>
            <button style={styles.logout} onClick={logout}>Log out</button>
          </div>
        </div>

        {loading && <p style={styles.muted}>Loading…</p>}
        {loadError && <div style={styles.error}>{loadError}</div>}

        {wallet && (
          <>
            <div style={styles.balanceLabel}>Balance</div>
            <div style={styles.balance}>
              {wallet.balance} {wallet.currency}
            </div>
            <div style={styles.walletId}>Your wallet ID: {wallet.id}</div>

            <div style={styles.actions}>
              <AmountAction label="Deposit" path="/wallets/me/deposit" accent="#22c55e" onDone={loadWallet} />
              <AmountAction label="Withdraw" path="/wallets/me/withdraw" accent="#f59e0b" onDone={loadWallet} />
            </div>

            <div style={styles.divider} />

            <TransferAction onDone={loadWallet} />
          </>
        )}
      </div>
    </div>
  );
}

// Deposit/withdraw: one amount field.
function AmountAction({ label, path, accent, onDone }) {
  const [amount, setAmount] = useState("");
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState("");

  async function submit() {
    setErrors({});
    setSuccess("");
    const value = Number(amount);
    if (!amount || Number.isNaN(value) || value <= 0) {
      setErrors({ amount: "Enter an amount greater than 0." });
      return;
    }
    setSubmitting(true);
    try {
      await apiFetch(path, { method: "POST", body: { amount: amount } });
      setSuccess(`${label} successful.`);
      setAmount("");
      await onDone();
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
        type="number" min="0" step="0.01"
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
        onClick={submit} disabled={submitting}
      >
        {submitting ? "Working…" : label}
      </button>
    </div>
  );
}

// Transfer: two fields — recipient wallet id + amount.
// Backend field names are exact: receiver_wallet_id (int) and amount.
// Per-field errors map back to those exact names via loc[1].
function TransferAction({ onDone }) {
  const [receiverId, setReceiverId] = useState("");
  const [amount, setAmount] = useState("");
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState("");

  async function submit() {
    setErrors({});
    setSuccess("");

    // Client-side guards mirror the backend so we skip pointless round trips.
    const nextErrors = {};
    if (!receiverId || !Number.isInteger(Number(receiverId)) || Number(receiverId) <= 0) {
      nextErrors.receiver_wallet_id = "Enter a valid wallet ID.";
    }
    const value = Number(amount);
    if (!amount || Number.isNaN(value) || value <= 0) {
      nextErrors.amount = "Enter an amount greater than 0.";
    }
    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors);
      return;
    }

    setSubmitting(true);
    try {
      await apiFetch("/wallets/me/transfer", {
        method: "POST",
        body: {
          receiver_wallet_id: Number(receiverId), // int, per schema
          amount: amount,                          // string, preserves Decimal
        },
      });
      setSuccess("Transfer successful.");
      setReceiverId("");
      setAmount("");
      await onDone();
    } catch (err) {
      setErrors(fieldErrorsFrom(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <div style={styles.actionLabel}>Send money</div>

      <input
        style={{ ...styles.input, marginBottom: 4 }}
        type="number" min="1" step="1"
        value={receiverId}
        onChange={(e) => setReceiverId(e.target.value)}
        placeholder="Recipient wallet ID"
      />
      {errors.receiver_wallet_id && <div style={styles.fieldError}>{errors.receiver_wallet_id}</div>}

      <input
        style={{ ...styles.input, marginTop: 10, marginBottom: 4 }}
        type="number" min="0" step="0.01"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        placeholder="0.00"
        onKeyDown={(e) => { if (e.key === "Enter") submit(); }}
      />
      {errors.amount && <div style={styles.fieldError}>{errors.amount}</div>}
      {errors._general && <div style={styles.fieldError}>{errors._general}</div>}
      {success && <div style={styles.success}>{success}</div>}

      <button
        style={{ ...styles.button, background: "#6366f1", color: "white", width: "100%", opacity: submitting ? 0.6 : 1 }}
        onClick={submit} disabled={submitting}
      >
        {submitting ? "Sending…" : "Send"}
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
  balance: { color: "#f8fafc", fontSize: 36, fontWeight: 700, marginBottom: 4 },
  walletId: { color: "#64748b", fontSize: 12, marginBottom: 24 },
  actions: { display: "flex", gap: 16 },
  action: { flex: 1, display: "flex", flexDirection: "column" },
  actionLabel: { color: "#cbd5e1", fontSize: 13, marginBottom: 8 },
  input: { padding: "10px 12px", borderRadius: 8, border: "1px solid #334155", background: "#0f172a", color: "#f8fafc", fontSize: 14, outline: "none", width: "100%", boxSizing: "border-box" },
  button: { marginTop: 12, padding: "10px 16px", borderRadius: 8, border: "none", color: "#0f172a", fontSize: 14, fontWeight: 700, cursor: "pointer" },
  fieldError: { marginTop: 4, color: "#fca5a5", fontSize: 12 },
  success: { marginTop: 8, color: "#86efac", fontSize: 12 },
  error: { padding: "10px 12px", borderRadius: 8, background: "#7f1d1d", color: "#fecaca", fontSize: 13 },
  divider: { height: 1, background: "#334155", margin: "24px 0" },
};
