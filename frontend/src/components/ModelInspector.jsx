import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { AlertTriangle, Search, ShieldCheck } from "lucide-react";
import { formatAttackLabel } from "../utils/attackLabels";

const BASE = "http://localhost:8000/api";

const MODEL_META = {
  xgboost: {
    title: "XGBoost Output Check",
    subtitle: "Structured feature classifier predictions from the latest run.",
    scoreLabel: "Confidence",
    detectLabel: "Attack Type",
    emptyLabel: "No non-benign XGBoost detections in this run.",
  },
  bert: {
    title: "BERT Output Check",
    subtitle:
      "Text-based transformer predictions generated from flow summaries.",
    scoreLabel: "Confidence",
    detectLabel: "Attack Type",
    emptyLabel: "No non-benign BERT detections in this run.",
  },
  autoencoder: {
    title: "Autoencoder Output Check",
    subtitle: "Reconstruction-error anomaly results from the latest run.",
    scoreLabel: "Anomaly Score",
    detectLabel: "Status",
    emptyLabel: "No anomalies were flagged by the autoencoder in this run.",
  },
};

function getRows(debugData, modelKey) {
  const layers = debugData?.layers || {};
  const ips = layers?.ingestion?.ips || [];

  if (modelKey === "autoencoder") {
    const rows = layers?.autoencoder?.results || [];
    return rows.map((row) => ({
      index: Number(row.index ?? 0),
      ip: ips[Number(row.index ?? 0)] || "unknown",
      detection: row.is_anomaly ? "ANOMALY" : "NORMAL",
      score: Number(row.anomaly_score ?? 0),
      isDetected: Boolean(row.is_anomaly),
    }));
  }

  const rows =
    modelKey === "bert"
      ? layers?.bert?.predictions || []
      : layers?.xgboost?.predictions || [];

  return rows.map((row) => ({
    index: Number(row.index ?? 0),
    ip: ips[Number(row.index ?? 0)] || "unknown",
    detection:
      row.attack_type || formatAttackLabel(row.label, `Class ${row.label}`),
    score: Number(row.confidence ?? 0),
    isDetected: Number(row.label ?? 0) !== 0,
  }));
}

export default function ModelInspector({ modelKey }) {
  const [debugData, setDebugData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [showDetectedOnly, setShowDetectedOnly] = useState(true);

  const meta = MODEL_META[modelKey] || MODEL_META.xgboost;

  useEffect(() => {
    axios
      .get(`${BASE}/debug/latest`)
      .then((res) => {
        if (res.data?.error) {
          setError(res.data.error);
        } else {
          setDebugData(res.data);
        }
      })
      .catch(() => {
        setError("Could not load debug data. Run an analysis first.");
      })
      .finally(() => setLoading(false));
  }, []);

  const rows = useMemo(() => getRows(debugData, modelKey), [
    debugData,
    modelKey,
  ]);

  const filteredRows = useMemo(() => {
    const q = query.trim().toLowerCase();
    return rows
      .filter((row) => (showDetectedOnly ? row.isDetected : true))
      .filter((row) => {
        if (!q) return true;
        return (
          row.ip.toLowerCase().includes(q) ||
          row.detection.toLowerCase().includes(q) ||
          String(row.index).includes(q)
        );
      });
  }, [rows, query, showDetectedOnly]);

  const detectedCount = rows.filter((row) => row.isDetected).length;

  if (loading) {
    return (
      <div
        className="card"
        style={{
          minHeight: "260px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <p style={{ color: "var(--text-muted)" }}>
          Loading {meta.title.toLowerCase()}...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div
        className="card"
        style={{
          minHeight: "260px",
          display: "flex",
          flexDirection: "column",
          gap: "10px",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
        }}
      >
        <AlertTriangle size={26} color="var(--color-warning)" />
        <h3 style={{ margin: 0 }}>{meta.title}</h3>
        <p style={{ margin: 0, color: "var(--text-muted)" }}>{error}</p>
      </div>
    );
  }

  return (
    <div
      className="fade-in"
      style={{ display: "flex", flexDirection: "column", gap: "18px" }}
    >
      <div
        className="card"
        style={{
          padding: "20px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "14px",
        }}
      >
        <div>
          <h2 style={{ fontSize: "1.6rem", marginBottom: "6px" }}>
            {meta.title}
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
            {meta.subtitle}
          </p>
        </div>
        <div style={{ textAlign: "right" }}>
          <p
            style={{
              fontSize: "0.78rem",
              color: "var(--text-muted)",
              marginBottom: "4px",
            }}
          >
            Detected / Total
          </p>
          <p
            style={{
              fontSize: "1.4rem",
              fontWeight: 800,
              color:
                detectedCount > 0
                  ? "var(--color-danger)"
                  : "var(--color-success)",
            }}
          >
            {detectedCount} / {rows.length}
          </p>
        </div>
      </div>

      <div
        className="card"
        style={{
          padding: "14px 16px",
          display: "flex",
          gap: "12px",
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <div style={{ position: "relative", flex: 1, minWidth: "260px" }}>
          <Search
            size={16}
            color="var(--text-muted)"
            style={{
              position: "absolute",
              left: "10px",
              top: "50%",
              transform: "translateY(-50%)",
            }}
          />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by IP, detection, or index"
            style={{
              width: "100%",
              backgroundColor: "var(--bg-primary)",
              color: "var(--text-main)",
              border: "1px solid var(--border-color)",
              borderRadius: "8px",
              padding: "9px 12px 9px 34px",
              fontSize: "0.88rem",
              outline: "none",
            }}
          />
        </div>

        <button
          onClick={() => setShowDetectedOnly((v) => !v)}
          className="btn btn-secondary"
          style={{ fontSize: "0.82rem", padding: "8px 12px" }}
        >
          {showDetectedOnly ? "Showing detected only" : "Showing all rows"}
        </button>
      </div>

      <div className="card" style={{ padding: 0 }}>
        {filteredRows.length > 0 ? (
          <div style={{ overflowX: "auto" }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                fontSize: "0.86rem",
              }}
            >
              <thead>
                <tr
                  style={{
                    borderBottom: "1px solid var(--border-color)",
                    color: "var(--text-muted)",
                    textAlign: "left",
                  }}
                >
                  <th style={{ padding: "14px 16px" }}>Index</th>
                  <th style={{ padding: "14px 16px" }}>Source IP</th>
                  <th style={{ padding: "14px 16px" }}>{meta.detectLabel}</th>
                  <th style={{ padding: "14px 16px" }}>{meta.scoreLabel}</th>
                </tr>
              </thead>
              <tbody>
                {filteredRows.map((row, idx) => (
                  <tr
                    key={`${modelKey}-${row.index}-${idx}`}
                    style={{ borderBottom: "1px solid rgba(48,54,61,0.25)" }}
                  >
                    <td
                      style={{
                        padding: "14px 16px",
                        color: "var(--text-muted)",
                        fontFamily: "var(--font-mono)",
                      }}
                    >
                      #{row.index}
                    </td>
                    <td
                      style={{
                        padding: "14px 16px",
                        fontFamily: "var(--font-mono)",
                        fontWeight: 700,
                      }}
                    >
                      {row.ip}
                    </td>
                    <td
                      style={{
                        padding: "14px 16px",
                        fontWeight: 700,
                        color: row.isDetected
                          ? "var(--color-danger)"
                          : "var(--color-success)",
                      }}
                    >
                      {row.detection}
                    </td>
                    <td
                      style={{
                        padding: "14px 16px",
                        color: "var(--text-muted)",
                      }}
                    >
                      {row.score.toFixed(4)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "8px",
              padding: "50px 20px",
              textAlign: "center",
            }}
          >
            <ShieldCheck
              size={32}
              color="var(--color-success)"
              style={{ opacity: 0.8 }}
            />
            <p style={{ color: "var(--text-main)", fontWeight: 700 }}>
              No records match the current filter.
            </p>
            <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
              {meta.emptyLabel}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
