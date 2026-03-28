import React from "react";

const statusConfig = {
  verified: { color: "#22c55e", label: "Verified" },
  rejected: { color: "#ef4444", label: "Rejected" },
  locked: { color: "#ef4444", label: "Locked" },
  review: { color: "#f59e0b", label: "Review" },
  active: { color: "#38bdf8", label: "Active" }
};

export default function SessionSidebar({
  scenarios,
  currentScenario,
  startScenario,
  connectionStatus,
  sessionComplete
}) {
  const status =
    sessionComplete?.result && statusConfig[sessionComplete.result]
      ? statusConfig[sessionComplete.result]
      : statusConfig.active;
  const modeLabel = currentScenario.replaceAll("_", " ");

  return (
    <aside
      style={{
        width: 280,
        minWidth: 280,
        borderRight: "1px solid #172436",
        background: "rgba(5,10,18,0.82)",
        backdropFilter: "blur(10px)",
        display: "flex",
        flexDirection: "column"
      }}
    >
      <div style={{ padding: "18px 16px", borderBottom: "1px solid #172436" }}>
        <div style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", letterSpacing: 1.2, marginBottom: 10 }}>
          Control center
        </div>
        <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>VoiceGuard</div>
        <div style={{ color: "#94a3b8", fontSize: 13, lineHeight: 1.5 }}>
          Live verification UI for transcript, reasoning, and risk review.
        </div>
      </div>

      <div style={{ padding: 16, borderBottom: "1px solid #172436" }}>
        <div style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", letterSpacing: 1.2, marginBottom: 12 }}>
          Session status
        </div>
        <div
          style={{
            padding: 14,
            borderRadius: 18,
            background: "rgba(255,255,255,0.03)",
            border: "1px solid rgba(255,255,255,0.07)"
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
            <span
              style={{
                width: 10,
                height: 10,
                borderRadius: "50%",
                background: status.color,
                boxShadow: `0 0 12px ${status.color}`
              }}
            />
            <span style={{ color: status.color, fontWeight: 700 }}>{status.label}</span>
          </div>
          <div style={{ color: "#94a3b8", fontSize: 12, lineHeight: 1.5 }}>
            Connection: <span style={{ color: "#e5edf8" }}>{connectionStatus}</span>
          </div>
          <div style={{ color: "#94a3b8", fontSize: 12, lineHeight: 1.5, marginTop: 4 }}>
            Mode: <span style={{ color: "#e5edf8" }}>{modeLabel}</span>
          </div>
        </div>
      </div>

      <div style={{ padding: 16, borderBottom: "1px solid #172436" }}>
        <div style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", letterSpacing: 1.2, marginBottom: 12 }}>
          Demo scenarios
        </div>
        <div style={{ display: "grid", gap: 8 }}>
          {scenarios.map((scenario) => {
            const active = scenario === currentScenario;
            return (
              <button
                key={scenario}
                onClick={() => startScenario(scenario)}
                style={{
                  textAlign: "left",
                  padding: "12px 14px",
                  borderRadius: 14,
                  border: `1px solid ${active ? "#2563eb" : "rgba(255,255,255,0.07)"}`,
                  background: active ? "rgba(37,99,235,0.14)" : "rgba(255,255,255,0.03)",
                  color: active ? "#dbeafe" : "#e5edf8",
                  cursor: "pointer"
                }}
              >
                {scenario.replaceAll("_", " ")}
              </button>
            );
          })}
        </div>
      </div>

      <div style={{ padding: 16, display: "grid", gap: 10 }}>
        <div style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", letterSpacing: 1.2 }}>
          Notes
        </div>
        <div
          style={{
            padding: 14,
            borderRadius: 16,
            background: "rgba(255,255,255,0.03)",
            border: "1px solid rgba(255,255,255,0.07)",
            color: "#cbd5e1",
            fontSize: 12,
            lineHeight: 1.6
          }}
        >
          The left panel now matches the earlier product direction: sidebar for control
          and context, transcript in the center, reasoning and risk on the right.
        </div>
      </div>
    </aside>
  );
}
