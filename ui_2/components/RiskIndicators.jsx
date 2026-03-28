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
        border: `1px solid ${hovered ? `${card.color}55` : "rgba(255,255,255,0.07)"}`,
        transition: "transform 180ms ease, border-color 180ms ease, box-shadow 220ms ease",
        transform: hovered ? "translateY(-1px)" : "translateY(0)",
        boxShadow: card.emphasis ? `0 0 24px ${card.color}22` : "none"
      }}
    >
      <style>{`
        @keyframes riskPulse {
          0% { transform: scale(1); box-shadow: 0 0 0 0 transparent; }
          50% { transform: scale(1.03); box-shadow: 0 0 0 8px transparent; }
          100% { transform: scale(1); box-shadow: 0 0 0 0 transparent; }
        }
      `}</style>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div
          style={{
            width: 58,
            height: 58,
            borderRadius: "50%",
            display: "grid",
            placeItems: "center",
            border: `2px solid ${card.color}`,
            color: card.color,
            fontSize: 14,
            fontWeight: 700,
            background: `${card.color}10`,
            animation: card.emphasis ? "riskPulse 1.4s ease-in-out infinite" : "none"
          }}
        >
          {card.badge}
        </div>
        <div>
          <div style={{ fontSize: 10, color: "#64748b", marginBottom: 6, textTransform: "uppercase", letterSpacing: 1 }}>
            {card.label}
          </div>
          <div style={{ fontSize: 20, fontWeight: 700, color: card.color }}>{card.value}</div>
        </div>
      </div>
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
      badge:
        indicators.voice_confidence === null
          ? "--"
          : `${Math.round(indicators.voice_confidence * 100)}`,
      color:
        indicators.voice_confidence === null
          ? "#94a3b8"
          : indicators.voice_confidence >= 0.8
            ? "#22c55e"
            : indicators.voice_confidence >= 0.72
              ? "#f59e0b"
              : "#ef4444",
      help: "Compares the live speaker embedding against the enrolled voiceprint.",
      emphasis: indicators.voice_confidence !== null
    },
    {
      label: "OTP timing",
      value: otpTimingValue,
      badge: otpTimingValue === "normal" ? "OK" : otpTimingValue === "unknown" ? "--" : "!",
      color:
        otpTimingValue === "normal"
          ? "#22c55e"
          : otpTimingValue === "suspicious" || otpTimingValue === "abnormal"
            ? "#ef4444"
            : "#f59e0b",
      help: "Flags suspiciously fast or slow OTP confirmation behavior.",
      emphasis: otpTimingValue !== "unknown"
    },
    {
      label: "Attempts",
      value: String(indicators.attempt_history),
      badge: String(indicators.attempt_history),
      color: indicators.attempt_history > 2 ? "#ef4444" : "#22c55e",
      help: "Tracks repeated failures across the verification flow.",
      emphasis: indicators.attempt_history > 0
    },
    {
      label: "Overall risk",
      value: overallRiskValue,
      badge:
        overallRiskValue === "low"
          ? "L"
          : overallRiskValue === "medium"
            ? "M"
            : overallRiskValue === "high"
              ? "H"
              : "--",
      color:
        overallRiskValue === "low"
          ? "#22c55e"
          : overallRiskValue === "medium"
            ? "#f59e0b"
            : overallRiskValue === "high"
              ? "#ef4444"
              : "#94a3b8",
      help: "Combined risk score based on voice, OTP timing, and attempt history.",
      emphasis: overallRiskValue !== "unknown"
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
