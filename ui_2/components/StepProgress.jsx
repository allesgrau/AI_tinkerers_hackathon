import React from "react";

const stepLabels = {
  pesel: "PESEL",
  otp: "OTP",
  voice: "Voice"
};

const stepColors = {
  idle: "#334155",
  in_progress: "#f59e0b",
  pending: "#f59e0b",
  sending: "#f59e0b",
  sent: "#38bdf8",
  verified: "#22c55e",
  failed: "#ef4444"
};

const stepLabelsByStatus = {
  idle: "Idle",
  in_progress: "In progress",
  pending: "Pending",
  sending: "Sending",
  sent: "Sent",
  verified: "Verified",
  failed: "Failed"
};

export default function StepProgress({ steps }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 10 }}>
      {Object.entries(stepLabels).map(([key, label]) => (
        <StepCard key={key} label={label} status={steps[key] || "idle"} />
      ))}
    </div>
  );
}

function StepCard({ label, status }) {
  const color = stepColors[status] || "#334155";
  const accent =
    status === "in_progress" || status === "sending"
      ? "stepPulse 1.4s ease-in-out infinite"
      : "none";

  return (
    <div
      style={{
        padding: 14,
        borderRadius: 18,
        border: `1px solid ${color}33`,
        background: "rgba(255,255,255,0.03)",
        transition: "all 220ms ease",
        boxShadow: status !== "idle" ? `0 0 0 1px ${color}14 inset` : "none"
      }}
    >
      <style>{`
        @keyframes stepPulse {
          0% { box-shadow: 0 0 0 0 rgba(245,158,11,0.08); }
          50% { box-shadow: 0 0 0 8px rgba(245,158,11,0.02); }
          100% { box-shadow: 0 0 0 0 rgba(245,158,11,0.08); }
        }
      `}</style>
      <div
        style={{
          fontSize: 10,
          color: "#64748b",
          textTransform: "uppercase",
          letterSpacing: 1.1,
          marginBottom: 8
        }}
      >
        Step
      </div>
      <div style={{ fontWeight: 700, marginBottom: 10 }}>{label}</div>
      <div
        style={{
          width: "100%",
          height: 6,
          borderRadius: 999,
          background: "rgba(255,255,255,0.06)",
          overflow: "hidden",
          marginBottom: 10
        }}
      >
        <div
          style={{
            width:
              status === "idle"
                ? "12%"
                : status === "sent"
                  ? "78%"
                  : status === "verified"
                    ? "100%"
                    : status === "failed"
                      ? "100%"
                      : "58%",
            height: "100%",
            borderRadius: 999,
            background: color,
            transition: "width 260ms ease, background 220ms ease",
            animation: accent
          }}
        />
      </div>
      <div
        style={{
          display: "inline-flex",
          padding: "5px 9px",
          borderRadius: 999,
          background: `${color}14`,
          color,
          fontSize: 11
        }}
      >
        {stepLabelsByStatus[status] || status}
      </div>
    </div>
  );
}
