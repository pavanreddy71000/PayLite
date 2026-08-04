// Transfer history: paginated, filterable list of transactions.
// GET /wallets/me/history with query params (page, size, type, sort...).
//
// Unlike deposit/withdraw/transfer (POST + JSON body), this is a GET whose
// filters ride in the URL query string. We build that string from state.
//
// Each item is a raw TransferResponse. Direction (in/out) and kind
// (deposit/withdrawal/transfer) are DERIVED by comparing sender/receiver
// wallet ids against the viewer's own wallet id.

import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../lib/api";

export default function History() {
  const navigate = useNavigate();

  const [myWalletId, setMyWalletId] = useState(null);
  const [data, setData] = useState(null);     // { items, total, page, size, pages }
  const [page, setPage] = useState(1);
  const [type, setType] = useState("");        // "", deposit, withdrawal, transfer
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  // We need our own wallet id to label direction. Fetch it once.
  useEffect(() => {
    apiFetch("/wallets/me")
      .then((w) => setMyWalletId(w.id))
      .catch(() => {});
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams();
      params.set("page", String(page));
      params.set("size", "10");
      if (type) params.set("type", type);
      const result = await apiFetch(`/wallets/me/history?${params.toString()}`);
      setData(result);
    } catch (err) {
      setError(err.data?.message || "Failed to load history.");
    } finally {
      setLoading(false);
    }
  }, [page, type]);

  useEffect(() => {
    load();
  }, [load]);

  function describe(item) {
    const isDeposit = item.sender_wallet_id == null;
    const isWithdrawal = item.receiver_wallet_id == null;
    if (isDeposit) return { kind: "Deposit", sign: "+", color: "#86efac" };
    if (isWithdrawal) return { kind: "Withdrawal", sign: "−", color: "#fca5a5" };
    // transfer: incoming if we're the receiver, outgoing if we're the sender
    const incoming = item.receiver_wallet_id === myWalletId;
    return incoming
      ? { kind: `Transfer from #${item.sender_wallet_id}`, sign: "+", color: "#86efac" }
      : { kind: `Transfer to #${item.receiver_wallet_id}`, sign: "−", color: "#fca5a5" };
  }

  return (
    <div style={styles.wrap}>
      <div style={styles.card}>
        <div style={styles.header}>
          <h1 style={styles.title}>History</h1>
          <button style={styles.link} onClick={() => navigate("/")}>← Wallet</button>
        </div>

        <div style={styles.filters}>
          {["", "deposit", "withdrawal", "transfer"].map((t) => (
            <button
              key={t || "all"}
              style={{
                ...styles.filterBtn,
                ...(type === t ? styles.filterActive : {}),
              }}
              onClick={() => { setType(t); setPage(1); }}
            >
              {t === "" ? "All" : t[0].toUpperCase() + t.slice(1)}
            </button>
          ))}
        </div>

        {loading && <p style={styles.muted}>Loading…</p>}
        {error && <div style={styles.error}>{error}</div>}

        {data && !loading && (
          <>
            {data.items.length === 0 ? (
              <p style={styles.muted}>No transactions yet.</p>
            ) : (
              <div style={styles.list}>
                {data.items.map((item) => {
                  const d = describe(item);
                  return (
                    <div key={item.id} style={styles.row}>
                      <div>
                        <div style={styles.rowKind}>{d.kind}</div>
                        <div style={styles.rowDate}>
                          {new Date(item.created_at).toLocaleString()}
                        </div>
                      </div>
                      <div style={{ ...styles.rowAmount, color: d.color }}>
                        {d.sign}{item.amount}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            <div style={styles.pager}>
              <button
                style={{ ...styles.pageBtn, opacity: page <= 1 ? 0.4 : 1 }}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
              >
                Prev
              </button>
              <span style={styles.pageInfo}>
                Page {data.page} of {data.pages || 1}
              </span>
              <button
                style={{ ...styles.pageBtn, opacity: page >= data.pages ? 0.4 : 1 }}
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= data.pages}
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

const styles = {
  wrap: { minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#0f172a" },
  card: { width: 460, padding: 32, borderRadius: 12, background: "#1e293b", boxShadow: "0 10px 30px rgba(0,0,0,0.3)" },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 },
  title: { color: "#f8fafc", margin: 0, fontSize: 24, fontWeight: 700 },
  link: { padding: "6px 12px", borderRadius: 8, border: "1px solid #334155", background: "transparent", color: "#cbd5e1", fontSize: 13, cursor: "pointer" },
  filters: { display: "flex", gap: 8, marginBottom: 20 },
  filterBtn: { padding: "6px 12px", borderRadius: 8, border: "1px solid #334155", background: "transparent", color: "#94a3b8", fontSize: 13, cursor: "pointer" },
  filterActive: { background: "#6366f1", color: "white", borderColor: "#6366f1" },
  muted: { color: "#94a3b8", fontSize: 14 },
  list: { display: "flex", flexDirection: "column", gap: 8 },
  row: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 14px", borderRadius: 8, background: "#0f172a" },
  rowKind: { color: "#e2e8f0", fontSize: 14, fontWeight: 600 },
  rowDate: { color: "#64748b", fontSize: 12, marginTop: 2 },
  rowAmount: { fontSize: 16, fontWeight: 700 },
  pager: { display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 20 },
  pageBtn: { padding: "8px 16px", borderRadius: 8, border: "1px solid #334155", background: "transparent", color: "#cbd5e1", fontSize: 13, cursor: "pointer" },
  pageInfo: { color: "#94a3b8", fontSize: 13 },
  error: { padding: "10px 12px", borderRadius: 8, background: "#7f1d1d", color: "#fecaca", fontSize: 13 },
};
