import React, { useState } from "react";

const statusConfig = {
  verified: { color: "#22c55e", label: "Verified" },
  rejected: { color: "#ef4444", label: "Rejected" },
  locked: { color: "#ef4444", label: "Locked" },
  review: { color: "#f59e0b", label: "Review" },
  active: { color: "#38bdf8", label: "Active" }
};

export default function SessionSidebar({
  mode,
  activeSessionId,
  availableSessions,
  scenarios,
  currentScenario,
  startScenario,
  subscribeToLiveSession,
  refreshSessions,
  connectionStatus,
  sessionComplete
}) {
  const [sessionInput, setSessionInput] = useState("");
  const scenarioLabels = {
    happy_path: "Happy Path",
    wrong_voice: "Wrong Voice",
    brute_force: "Brute Force OTP",
    replay_attack: "Replay Attack"
  };
  const status =
    sessionComplete?.result && statusConfig[sessionComplete.result]
      ? statusConfig[sessionComplete.result]
      : statusConfig.active;
  const modeLabel =
    mode === "live" ? `live · ${activeSessionId || "not connected"}` : currentScenario.replaceAll("_", " ");
  const recentSessions = (availableSessions || []).slice(0, 5);

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
          Live session
        </div>
        <div
          style={{
            padding: 14,
            borderRadius: 18,
            background: "rgba(255,255,255,0.03)",
            border: "1px solid rgba(255,255,255,0.07)"
          }}
        >
          <div style={{ color: "#94a3b8", fontSize: 12, lineHeight: 1.5, marginBottom: 10 }}>
            Connect the dashboard to a real `session_id` from the backend verification flow.
          </div>
          <input
            value={sessionInput}
            onChange={(event) => setSessionInput(event.target.value)}
            placeholder="session_id"
            style={{
              width: "100%",
              borderRadius: 12,
              border: "1px solid rgba(255,255,255,0.08)",
              background: "#0b1220",
              color: "#e5edf8",
              padding: "11px 12px",
              fontSize: 12,
              marginBottom: 10
            }}
          />
          <button
            onClick={() => subscribeToLiveSession(sessionInput.trim())}
            style={{
              width: "100%",
              padding: "11px 12px",
              borderRadius: 12,
              border: "1px solid rgba(56,189,248,0.28)",
              background: "rgba(14,116,144,0.16)",
              color: "#dbeafe",
              fontWeight: 600,
              cursor: "pointer"
            }}
          >
            Watch live session
          </button>
          {activeSessionId && mode === "live" ? (
            <div style={{ color: "#94a3b8", fontSize: 11, lineHeight: 1.5, marginTop: 10 }}>
              Active session: <span style={{ color: "#e5edf8" }}>{activeSessionId}</span>
            </div>
          ) : null}
          <button
            onClick={refreshSessions}
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: 12,
              border: "1px solid rgba(255,255,255,0.08)",
              background: "rgba(255,255,255,0.03)",
              color: "#cbd5e1",
              fontWeight: 600,
              cursor: "pointer",
              marginTop: 10
            }}
          >
            Refresh sessions
          </button>
          {recentSessions.length > 0 ? (
            <div style={{ display: "grid", gap: 8, marginTop: 12 }}>
              {recentSessions.map((session) => (
                <button
                  key={session.session_id}
                  onClick={() => subscribeToLiveSession(session.session_id)}
                  style={{
                    textAlign: "left",
                    padding: "10px 12px",
                    borderRadius: 12,
                    border: "1px solid rgba(255,255,255,0.08)",
                    background:
                      session.session_id === activeSessionId
                        ? "rgba(56,189,248,0.14)"
                        : "rgba(255,255,255,0.02)",
                    color: "#e5edf8",
                    cursor: "pointer"
                  }}
                >
                  <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 4 }}>
                    {session.session_id}
                  </div>
                  <div style={{ fontSize: 11, color: "#94a3b8" }}>
                    OTP tries: {session.otp_attempts} · Completed: {session.completed ? "yes" : "no"}
                  </div>
                </button>
              ))}
            </div>
          ) : null}
        </div>
      </div>

      <div style={{ padding: 16, borderBottom: "1px solid #172436" }}>
        <div style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", letterSpacing: 1.2, marginBottom: 12 }}>
          Demo scenarios
        </div>
        <div
          style={{
            padding: 14,
            borderRadius: 18,
            background: "rgba(255,255,255,0.03)",
            border: "1px solid rgba(255,255,255,0.07)"
          }}
        >
          <div style={{ color: "#94a3b8", fontSize: 12, lineHeight: 1.5, marginBottom: 10 }}>
            Choose a scripted demo flow for jury mode and replay the verification sequence.
          </div>
          <select
            value={currentScenario}
            onChange={(event) => startScenario(event.target.value)}
            style={{
              width: "100%",
              borderRadius: 12,
              border: "1px solid rgba(255,255,255,0.08)",
              background: "#0b1220",
              color: "#e5edf8",
              padding: "11px 12px",
              fontSize: 12,
              marginBottom: 10
            }}
          >
            {scenarios.map((scenario) => (
              <option key={scenario} value={scenario}>
                {scenarioLabels[scenario] || scenario.replaceAll("_", " ")}
              </option>
            ))}
          </select>
          <button
            onClick={() => startScenario(currentScenario)}
            style={{
              width: "100%",
              padding: "11px 12px",
              borderRadius: 12,
              border: "1px solid rgba(37,99,235,0.3)",
              background: "rgba(37,99,235,0.16)",
              color: "#dbeafe",
              fontWeight: 600,
              cursor: "pointer"
            }}
          >
            Run selected scenario
          </button>
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
