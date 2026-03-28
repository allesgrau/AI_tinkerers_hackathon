import React from "react";

export default function SessionOverlay({ sessionComplete, onClose }) {
  if (!sessionComplete) {
    return null;
  }

  const success =
    sessionComplete.result === "verified" || sessionComplete.result === "review";
  const accent =
    sessionComplete.result === "verified"
      ? "#22c55e"
      : sessionComplete.result === "review"
        ? "#f59e0b"
        : "#ef4444";
  const title =
    sessionComplete.result === "verified"
      ? "Session verified"
      : sessionComplete.result === "review"
        ? "Session requires review"
        : sessionComplete.result === "locked"
          ? "Session locked"
          : "Session rejected";

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(2,6,23,0.72)",
        backdropFilter: "blur(8px)",
        display: "grid",
        placeItems: "center",
        zIndex: 50
      }}
    >
      <div
        style={{
          width: "min(560px, calc(100vw - 32px))",
          borderRadius: 28,
          padding: 28,
          background: "#08111d",
          border: `1px solid ${accent}33`,
          boxShadow: "0 24px 60px rgba(0,0,0,0.45)"
        }}
      >
        <div
          style={{
            width: 64,
            height: 64,
            borderRadius: "50%",
            display: "grid",
            placeItems: "center",
            background: `${accent}18`,
            color: accent,
            fontSize: 28,
            marginBottom: 18
          }}
        >
          {success ? "✓" : "✕"}
        </div>
        <h2 style={{ marginBottom: 10 }}>
          {title}
        </h2>
        <p style={{ color: "#94a3b8", lineHeight: 1.6, marginBottom: 18 }}>
          {sessionComplete.reason ||
            "Verification completed and the session reached a terminal state."}
        </p>
        {sessionComplete.token ? (
          <div
            style={{
              padding: 14,
              borderRadius: 16,
              background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.08)",
              color: "#dbe7f7",
              fontFamily: '"IBM Plex Mono", monospace',
              fontSize: 12,
              wordBreak: "break-all",
              marginBottom: 18
            }}
          >
            {sessionComplete.token}
          </div>
        ) : null}
        <button
          onClick={onClose}
          style={{
            padding: "12px 16px",
            borderRadius: 14,
            border: "none",
            background: accent,
            color: "#04111d",
            fontWeight: 700,
            cursor: "pointer"
          }}
        >
          Close
        </button>
      </div>
    </div>
  );
}
