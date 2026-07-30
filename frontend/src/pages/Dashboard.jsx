// Placeholder protected page. Its only job right now is to PROVE the
// full auth loop works: it calls a protected endpoint (/wallets/me)
// using the stored token, and shows the result, a loading state, or
// an error. Once this renders your real balance, the scaffold is done
// and we can build the real wallet UI on top of it.

import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { logout } = useAuth();
  const [wallet, setWallet] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function loadWallet() {
      setLoading(true);
      setError("");
      try {
        const data = await apiFetch("/wallets/me");
        if (!cancelled) setWallet(data);
      } catch (err) {
        if (!cancelled) setError(err.data?.message || "Failed to load wallet.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    loadWallet();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div style={styles.wrap}>
      <div style={styles.card}>
        <div style={styles.header}>
          <h1 style={styles.title}>Wallet</h1>
          <button style={styles.logout} onClick={logout}>
            Log out
          </button>
        </div>

        {loading && <p style={styles.muted}>Loading…</p>}
        {error && <div style={styles.error}>{error}</div>}

        {wallet && (
          <div>
            <div style={styles.balanceLabel}>Balance</div>
            <div style={styles.balance}>
              {wallet.balance} {wallet.currency}
            </div>
            <div style={styles.meta}>Wallet ID: {wallet.id}</div>
          </div>
        )}
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
    width: 360,
    padding: 32,
    borderRadius: 12,
    background: "#1e293b",
    boxShadow: "0 10px 30px rgba(0,0,0,0.3)",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 24,
  },
  title: { color: "#f8fafc", margin: 0, fontSize: 24, fontWeight: 700 },
  logout: {
    padding: "6px 12px",
    borderRadius: 8,
    border: "1px solid #334155",
    background: "transparent",
    color: "#cbd5e1",
    fontSize: 13,
    cursor: "pointer",
  },
  muted: { color: "#94a3b8", fontSize: 14 },
  balanceLabel: { color: "#94a3b8", fontSize: 13, marginBottom: 6 },
  balance: { color: "#f8fafc", fontSize: 36, fontWeight: 700 },
  meta: { color: "#64748b", fontSize: 12, marginTop: 12 },
  error: {
    padding: "10px 12px",
    borderRadius: 8,
    background: "#7f1d1d",
    color: "#fecaca",
    fontSize: 13,
  },
};
