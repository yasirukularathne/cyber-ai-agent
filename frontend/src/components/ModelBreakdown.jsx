import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import {
  ArrowRight,
  BrainCircuit,
  ShieldAlert,
  Activity,
  Layers3,
} from "lucide-react";
import { Link } from "react-router-dom";
import { formatAttackLabel } from "../utils/attackLabels";

const BASE = "http://localhost:8000/api";

const MODELS = {
  xgboost: {
    label: "XGBoost",
    icon: ShieldAlert,
    accent: "var(--color-warning)",
    note: "Numeric feature classifier",
  },
  bert: {
    label: "BERT",
    icon: BrainCircuit,
    accent: "var(--color-info)",
    note: "Text-based transformer",
  },
  autoencoder: {
    label: "Autoencoder",
    icon: Activity,
    accent: "var(--color-success)",
    note: "Reconstruction anomaly detector",
  },
};

function getLayerData(debugData, modelKey) {
  const layers = debugData?.layers || {};
  if (modelKey === "xgboost") return layers.xgboost?.predictions || [];
  if (modelKey === "bert") return layers.bert?.predictions || [];
  if (modelKey === "autoencoder") return layers.autoencoder?.results || [];
  return [];
}

function getIps(debugData) {
  return debugData?.layers?.ingestion?.ips || [];
}

export default function ModelBreakdown() {
  const [debugData, setDebugData] = useState(null);
  const [selectedModel, setSelectedModel] = useState("xgboost");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    axios
      .get(`${BASE}/debug/latest`)
      .then((res) => {
        if (res.data && !res.data.error) {
          setDebugData(res.data);
          setError(false);
        } else {
          setError(true);
        }
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, []);

  const selectedModelData = useMemo(
    () => getLayerData(debugData, selectedModel),
    [debugData, selectedModel]
  );
  const ips = useMemo(() => getIps(debugData), [debugData]);

  const summary = useMemo(() => {
    const xgboost = getLayerData(debugData, "xgboost");
    const bert = getLayerData(debugData, "bert");
    const autoencoder = getLayerData(debugData, "autoencoder");

    const xgbDetected = xgboost.filter((row) => row.label !== 0).length;
    const bertDetected = bert.filter((row) => row.label !== 0).length;
    const aeDetected = autoencoder.filter((row) => row.is_anomaly).length;

    return [
      { key: "xgboost", detected: xgbDetected, total: xgboost.length },
      { key: "bert", detected: bertDetected, total: bert.length },
      { key: "autoencoder", detected: aeDetected, total: autoencoder.length },
    ];
  }, [debugData]);

  const rows = useMemo(() => {
    const data = [...selectedModelData];
    if (selectedModel === "autoencoder") {
      return data
        .filter((row) => row.is_anomaly)
        .map((row, index) => ({
          ...row,
          index: Number(row.index ?? index),
          score: row.anomaly_score || 0,
        }))
        .sort((a, b) => b.score - a.score)
        .slice(0, 6);
    }
    return data
      .filter((row) => row.label !== 0)
      .map((row, index) => ({
        ...row,
        index: Number(row.index ?? index),
        score: row.confidence || 0,
      }))
      .sort((a, b) => b.score - a.score)
      .slice(0, 6);
  }, [selectedModel, selectedModelData]);

  if (loading) {
    return (
      <div
        className="card"
        style={{
          padding: "24px",
          minHeight: "220px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <p style={{ color: "var(--text-muted)" }}>
          Loading per-model detections...
        </p>
      </div>
    );
  }

  if (error || !debugData) {
    return (
      <div
        className="card"
        style={{
          padding: "24px",
          minHeight: "220px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column",
          gap: "10px",
        }}
      >
        <Layers3 size={28} color="var(--color-primary)" />
        <h3 style={{ margin: 0 }}>Per-Model Telemetry Unavailable</h3>
        <p
          style={{
            color: "var(--text-muted)",
            textAlign: "center",
            maxWidth: "520px",
            margin: 0,
          }}
        >
          Run an analysis first to see what XGBoost, BERT, and the Autoencoder
          detected individually.
        </p>
      </div>
    );
  }

  const modelMeta = MODELS[selectedModel];
  const Icon = modelMeta.icon;
  const detectionCount =
    summary.find((item) => item.key === selectedModel)?.detected ?? 0;
  const totalCount =
    summary.find((item) => item.key === selectedModel)?.total ?? 0;

  return (
    <div
      className="card"
      style={{
        padding: "24px",
        display: "flex",
        flexDirection: "column",
        gap: "20px",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: "16px",
          flexWrap: "wrap",
        }}
      >
        <div>
          <h3 style={{ fontSize: "1.15rem", marginBottom: "6px" }}>
            Per-Model Detections
          </h3>
          <p
            style={{
              color: "var(--text-muted)",
              fontSize: "0.9rem",
              margin: 0,
            }}
          >
            Compare the non-benign outputs from each model before fusion
            combines them.
          </p>
        </div>
        <Link
          to="/debug"
          style={{
            fontSize: "0.85rem",
            color: "var(--color-primary)",
            textDecoration: "none",
            display: "flex",
            alignItems: "center",
            gap: "4px",
          }}
        >
          <span>Open debug trace</span>
          <ArrowRight size={14} />
        </Link>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "12px",
        }}
      >
        {summary.map((item) => {
          const meta = MODELS[item.key];
          const ModelIcon = meta.icon;
          const isActive = selectedModel === item.key;
          return (
            <button
              key={item.key}
              onClick={() => setSelectedModel(item.key)}
              style={{
                textAlign: "left",
                border: `1px solid ${
                  isActive ? meta.accent : "var(--border-color)"
                }`,
                background: isActive
                  ? "rgba(56,139,253,0.08)"
                  : "rgba(255,255,255,0.02)",
                borderRadius: "12px",
                padding: "14px 16px",
                cursor: "pointer",
                color: "var(--text-main)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "12px",
                }}
              >
                <div
                  style={{ display: "flex", alignItems: "center", gap: "10px" }}
                >
                  <ModelIcon size={18} color={meta.accent} />
                  <div>
                    <div style={{ fontWeight: 700 }}>{meta.label}</div>
                    <div
                      style={{
                        fontSize: "0.75rem",
                        color: "var(--text-muted)",
                      }}
                    >
                      {meta.note}
                    </div>
                  </div>
                </div>
                <span
                  style={{
                    fontSize: "1.2rem",
                    fontWeight: 800,
                    color: meta.accent,
                  }}
                >
                  {item.detected}
                </span>
              </div>
              <div
                style={{
                  marginTop: "10px",
                  fontSize: "0.8rem",
                  color: "var(--text-muted)",
                }}
              >
                {item.detected} detections from {item.total.toLocaleString()}{" "}
                evaluated records
              </div>
            </button>
          );
        })}
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "12px",
          flexWrap: "wrap",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              background: `${modelMeta.accent}20`,
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Icon size={18} color={modelMeta.accent} />
          </span>
          <div>
            <div style={{ fontWeight: 800 }}>{modelMeta.label} Output</div>
            <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
              {selectedModel === "autoencoder"
                ? `${detectionCount} anomalies detected`
                : `${detectionCount} malicious classifications detected`}
            </div>
          </div>
        </div>
        <div style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
          Showing top {Math.min(rows.length, 6)} of{" "}
          {totalCount.toLocaleString()} records
        </div>
      </div>

      <div style={{ overflowX: "auto" }}>
        {rows.length > 0 ? (
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              textAlign: "left",
              fontSize: "0.85rem",
            }}
          >
            <thead>
              <tr
                style={{
                  borderBottom: "1px solid var(--border-color)",
                  color: "var(--text-muted)",
                }}
              >
                <th style={{ padding: "12px 14px", fontWeight: 600 }}>INDEX</th>
                <th style={{ padding: "12px 14px", fontWeight: 600 }}>
                  SOURCE IP
                </th>
                <th style={{ padding: "12px 14px", fontWeight: 600 }}>
                  DETECTION
                </th>
                <th style={{ padding: "12px 14px", fontWeight: 600 }}>SCORE</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, idx) => {
                const ip = ips[row.index] || "unknown";
                const detectionLabel =
                  selectedModel === "autoencoder"
                    ? row.is_anomaly
                      ? "ANOMALY"
                      : "NORMAL"
                    : row.attack_type ||
                      formatAttackLabel(row.label, `Class ${row.label}`);
                const scoreLabel =
                  selectedModel === "autoencoder"
                    ? `${Number(row.anomaly_score || 0).toFixed(4)}`
                    : `${Number(row.confidence || 0).toFixed(4)}`;

                return (
                  <tr
                    key={`${selectedModel}-${row.index}-${idx}`}
                    style={{ borderBottom: "1px solid rgba(48,54,61,0.2)" }}
                  >
                    <td
                      style={{
                        padding: "12px 14px",
                        color: "var(--text-muted)",
                        fontFamily: "var(--font-mono)",
                      }}
                    >
                      #{row.index}
                    </td>
                    <td
                      style={{
                        padding: "12px 14px",
                        fontWeight: 700,
                        fontFamily: "var(--font-mono)",
                      }}
                    >
                      {ip}
                    </td>
                    <td
                      style={{
                        padding: "12px 14px",
                        fontWeight: 700,
                        color:
                          selectedModel === "autoencoder"
                            ? row.is_anomaly
                              ? "var(--color-danger)"
                              : "var(--color-success)"
                            : modelMeta.accent,
                      }}
                    >
                      {detectionLabel}
                    </td>
                    <td
                      style={{
                        padding: "12px 14px",
                        color: "var(--text-muted)",
                      }}
                    >
                      {scoreLabel}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <div
            style={{
              padding: "18px 4px",
              color: "var(--text-muted)",
              fontSize: "0.9rem",
            }}
          >
            No non-benign detections were recorded for {modelMeta.label} in this
            run.
          </div>
        )}
      </div>
    </div>
  );
}
