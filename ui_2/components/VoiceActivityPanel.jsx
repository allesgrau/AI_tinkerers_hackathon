import React from "react";

export default function VoiceActivityPanel({ active }) {
  const bars = [18, 32, 22, 38, 16, 28];

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: 0, height: "100%" }}>
      <style>{`
        @keyframes voiceBarPulse {
          0%, 100% { transform: scaleY(0.42); opacity: 0.6; }
          50% { transform: scaleY(1); opacity: 1; }
        }
      `}</style>
      <div
        style={{
          height: 52,
          borderBottom: "1px solid rgba(255,255,255,0.08)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 18px"
        }}
      >
        <div>
          <div
            style={{
              color: "#64d9ff",
              fontSize: 11,
              textTransform: "uppercase",
              letterSpacing: 1.1
            }}
          >
            Voice activity
          </div>
          <div style={{ color: "rgba(228, 232, 241, 0.48)", fontSize: 12 }}>
            Agent output monitor
          </div>
        </div>
        <div
          style={{
            padding: "6px 10px",
            borderRadius: 999,
            background: active ? "rgba(139, 245, 178, 0.12)" : "rgba(255,255,255,0.04)",
            color: active ? "#8bf5b2" : "rgba(228, 232, 241, 0.48)",
            fontSize: 11
          }}
        >
          {active ? "Speaking" : "Standby"}
        </div>
      </div>

      <div
        style={{
          flex: 1,
          minHeight: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "12px 16px",
          background:
            "radial-gradient(circle at top, rgba(100, 217, 255, 0.08), rgba(10,13,20,0) 38%)"
        }}
      >
        <div
          style={{
            width: "100%",
            maxWidth: 208,
            padding: "12px 14px",
            borderRadius: 18,
            background:
              "linear-gradient(180deg, rgba(19, 29, 39, 0.96), rgba(12, 18, 27, 0.92))",
            border: `1px solid ${active ? "rgba(100, 217, 255, 0.24)" : "rgba(255,255,255,0.08)"}`,
            boxShadow: active
              ? "0 22px 48px rgba(100, 217, 255, 0.12)"
              : "0 18px 40px rgba(0, 0, 0, 0.24)",
            display: "grid",
            justifyItems: "center",
            gap: 10,
            margin: "0 auto"
          }}
        >
          <div
            style={{
              width: 76,
              height: 76,
              borderRadius: "50%",
              display: "grid",
              placeItems: "center",
              background: active
                ? "radial-gradient(circle at top, rgba(139, 245, 178, 0.18), rgba(100, 217, 255, 0.12))"
                : "rgba(255,255,255,0.03)",
              border: `1px solid ${active ? "rgba(139, 245, 178, 0.22)" : "rgba(255,255,255,0.08)"}`
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 5,
                height: 32
              }}
            >
              {bars.map((height, index) => (
                <span
                  key={`${height}-${index}`}
                  style={{
                    width: 4,
                    height: Math.max(12, Math.round(height * 0.78)),
                    borderRadius: 999,
                    background: active
                      ? "linear-gradient(180deg, #8bf5b2 0%, #64d9ff 100%)"
                      : "rgba(228,232,241,0.34)",
                    transformOrigin: "center",
                    animation: active
                      ? `voiceBarPulse ${0.9 + index * 0.08}s ease-in-out infinite`
                      : "none"
                  }}
                />
              ))}
            </div>
          </div>

          <div style={{ textAlign: "center" }}>
            <div style={{ color: "#f5f7fb", fontSize: 13, fontWeight: 700, marginBottom: 4 }}>
              {active ? "Agent is speaking" : "Waiting for response"}
            </div>
            <div style={{ color: "rgba(228, 232, 241, 0.48)", fontSize: 10, lineHeight: 1.4 }}>
              Real-time waveform preview for the voice assistant stream.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
