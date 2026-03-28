import React from "react";

const stepLabels = {
  pesel: "PESEL",
  otp: "OTP",
  voice: "Voice"
};

const stepColors = {
  idle: "#334155",
  pending: "#f59e0b",
  verified: "#22c55e",
  failed: "#ef4444"
};

export default function StepProgress({ steps }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 10 }}>
      {Object.entries(stepLabels).map(([key, label]) => (
        <div
          key={key}
          style={{
            padding: 14,
            borderRadius: 18,
            border: `1px solid ${(stepColors[steps[key]] || "#334155")}33`,
            background: "rgba(255,255,255,0.03)",
            transition: "all 220ms ease"
          }}
        >
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
          <div style={{ fontWeight: 700, marginBottom: 8 }}>{label}</div>
          <div
            style={{
              display: "inline-flex",
              padding: "5px 9px",
              borderRadius: 999,
              background: `${stepColors[steps[key]] || "#334155"}14`,
              color: stepColors[steps[key]] || "#94a3b8",
              fontSize: 11,
              textTransform: "capitalize"
            }}
          >
            {steps[key]}
          </div>
        </div>
      ))}
    </div>
  );
}
