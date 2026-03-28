import React from "react";

const statusStyles = {
  connected: { label: "Connected", color: "#22c55e" },
  connecting: { label: "Connecting", color: "#f59e0b" },
  disconnected: { label: "Disconnected", color: "#94a3b8" },
  error: { label: "Error", color: "#ef4444" }
};

export default function ConnectionStatus({ status }) {
  const config = statusStyles[status] || statusStyles.disconnected;

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 8,
        padding: "8px 12px",
        borderRadius: 999,
        background: `${config.color}14`,
        border: `1px solid ${config.color}33`,
        color: config.color,
        fontSize: 12
      }}
    >
      <span
        style={{
          width: 8,
          height: 8,
          borderRadius: "50%",
          background: config.color,
          boxShadow: `0 0 12px ${config.color}`
        }}
      />
      {config.label}
    </div>
  );
}
