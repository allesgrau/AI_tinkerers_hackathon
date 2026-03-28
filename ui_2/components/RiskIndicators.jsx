import React, { useState } from "react";

function RiskCard({ card }) {
  const [hovered, setHovered] = useState(false);

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        position: "relative",
        padding: 14,
        borderRadius: 18,
        background: "rgba(255,255,255,0.03)",
        border: "1px solid rgba(255,255,255,0.07)",
        transition: "transform 180ms ease, border-color 180ms ease",
        transform: hovered ? "translateY(-1px)" : "translateY(0)",
        borderColor: hovered ? `${card.color}55` : "rgba(255,255,255,0.07)"
      }}
    >
      <div style={{ fontSize: 10, color: "#64748b", marginBottom: 8, textTransform: "uppercase", letterSpacing: 1 }}>
        {card.label}
      </div>
      <div style={{ fontSize: 22, fontWeight: 700, color: card.color }}>{card.value}</div>
      {hovered ? (
        <div
          style={{
            position: "absolute",
            left: 10,
            right: 10,
            top: "calc(100% + 8px)",
            zIndex: 20,
            padding: "10px 12px",
            borderRadius: 12,
            background: "#0b1220",
            border: "1px solid rgba(255,255,255,0.08)",
            color: "#cbd5e1",
            fontSize: 12,
            lineHeight: 1.5,
            boxShadow: "0 18px 30px rgba(0,0,0,0.35)"
          }}
        >
          {card.help}
        </div>
      ) : null}
    </div>
  );
}

export default function RiskIndicators({ indicators }) {
  const voiceValue =
    indicators.voice_confidence === null
      ? "n/a"
      : `${Math.round(indicators.voice_confidence * 100)}%`;
  const otpTimingValue = indicators.otp_timing || "unknown";
  const overallRiskValue = indicators.overall_risk || "unknown";
  const cards = [
    {
      label: "Voice confidence",
      value: voiceValue,
      color:
        indicators.voice_confidence === null
          ? "#94a3b8"
          : indicators.voice_confidence >= 0.8
            ? "#22c55e"
            : indicators.voice_confidence >= 0.72
              ? "#f59e0b"
              : "#ef4444",
      help: "Compares the live speaker embedding against the enrolled voiceprint."
    },
    {
      label: "OTP timing",
      value: otpTimingValue,
      color:
        otpTimingValue === "normal"
          ? "#22c55e"
          : otpTimingValue === "suspicious" || otpTimingValue === "abnormal"
            ? "#ef4444"
            : "#f59e0b",
      help: "Flags suspiciously fast or slow OTP confirmation behavior."
    },
    {
      label: "Attempts",
      value: String(indicators.attempt_history),
      color: indicators.attempt_history > 2 ? "#ef4444" : "#22c55e",
      help: "Tracks repeated failures across the verification flow."
    },
    {
      label: "Overall risk",
      value: overallRiskValue,
      color:
        overallRiskValue === "low"
          ? "#22c55e"
          : overallRiskValue === "medium"
            ? "#f59e0b"
            : overallRiskValue === "high"
              ? "#ef4444"
              : "#94a3b8",
      help: "Combined risk score based on voice, OTP timing, and attempt history."
    }
  ];

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: 10 }}>
      {cards.map((card) => (
        <RiskCard key={card.label} card={card} />
      ))}
    </div>
  );
}
