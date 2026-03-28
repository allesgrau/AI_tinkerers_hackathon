import React, { useState } from "react";

const statusConfig = {
  verified: { color: "#22c55e", label: "Verified" },
  rejected: { color: "#ef4444", label: "Rejected" },
  locked: { color: "#ef4444", label: "Locked" },
  review: { color: "#f59e0b", label: "Review" },
  active: { color: "#8bf5b2", label: "Active" }
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
  const [openSections, setOpenSections] = useState({
    status: false,
    live: false,
    demo: false,
    notes: false
  });
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
  const toggleSection = (key) => {
    setOpenSections((current) => ({ ...current, [key]: !current[key] }));
  };

  return (
    <aside
      style={{
        width: 280,
        minWidth: 280,
        padding: 28,
        borderRight: "1px solid rgba(255, 255, 255, 0.08)",
        background: "rgba(9, 13, 20, 0.8)",
        backdropFilter: "blur(22px)",
        boxShadow: "inset -1px 0 0 rgba(255,255,255,0.04)",
        display: "flex",
        flexDirection: "column"
      }}
    >
      <div style={{ borderBottom: "1px solid rgba(255,255,255,0.08)", paddingBottom: 20 }}>
        <div
          style={{
            display: "inline-flex",
            padding: "7px 12px",
            borderRadius: 999,
            background: "rgba(117, 255, 163, 0.12)",
            color: "#8bf5b2",
            fontSize: 12,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            border: "1px solid rgba(117, 255, 163, 0.22)",
            marginBottom: 16
          }}
        >
          Control center
        </div>
        <div style={{ fontSize: 30, lineHeight: 1.02, fontWeight: 700, marginBottom: 10 }}>
          VoiceGuard
        </div>
        <div style={{ color: "rgba(228, 232, 241, 0.68)", fontSize: 13, lineHeight: 1.5 }}>
          Live phone-call dashboard for transcript, agent tools, and scheduling actions.
        </div>
      </div>

      <SidebarSection
        title="Session status"
        open={openSections.status}
        onToggle={() => toggleSection("status")}
      >
        <div
          style={{
            padding: 14,
            borderRadius: 20,
            background: "linear-gradient(180deg, rgba(19, 29, 39, 0.96), rgba(12, 18, 27, 0.92))",
            border: "1px solid rgba(117, 255, 163, 0.14)",
            boxShadow: "0 18px 40px rgba(0, 0, 0, 0.24)"
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
          <div style={{ color: "rgba(228, 232, 241, 0.48)", fontSize: 12, lineHeight: 1.5 }}>
            Connection: <span style={{ color: "#e5edf8" }}>{connectionStatus}</span>
          </div>
          <div style={{ color: "rgba(228, 232, 241, 0.48)", fontSize: 12, lineHeight: 1.5, marginTop: 4 }}>
            Mode: <span style={{ color: "#e5edf8" }}>{modeLabel}</span>
          </div>
        </div>
      </SidebarSection>

      <SidebarSection
        title="Live session"
        open={openSections.live}
        onToggle={() => toggleSection("live")}
      >
        <div style={{ color: "rgba(228, 232, 241, 0.68)", fontSize: 12, lineHeight: 1.5, marginBottom: 10 }}>
          Connect the dashboard to a Twilio call session or any demo session from the backend.
        </div>
        <input
          value={sessionInput}
          onChange={(event) => setSessionInput(event.target.value)}
          placeholder="session_id"
          style={inputStyle}
        />
        <button onClick={() => subscribeToLiveSession(sessionInput.trim())} style={primaryButtonStyle}>
          Watch live session
        </button>
        {activeSessionId && mode === "live" ? (
          <div style={{ color: "rgba(228, 232, 241, 0.48)", fontSize: 11, lineHeight: 1.5, marginTop: 10 }}>
            Active session: <span style={{ color: "#e5edf8" }}>{activeSessionId}</span>
          </div>
        ) : null}
        <button onClick={refreshSessions} style={{ ...secondaryButtonStyle, marginTop: 10 }}>
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
                  border:
                    session.session_id === activeSessionId
                      ? "1px solid rgba(117, 255, 163, 0.24)"
                      : "1px solid rgba(255,255,255,0.08)",
                  background:
                    session.session_id === activeSessionId
                      ? "linear-gradient(180deg, rgba(19, 29, 39, 0.96), rgba(12, 18, 27, 0.92))"
                      : "rgba(255,255,255,0.02)",
                  color: "#e5edf8",
                  cursor: "pointer",
                  boxShadow:
                    session.session_id === activeSessionId
                      ? "0 14px 28px rgba(0, 0, 0, 0.18)"
                      : "none"
                }}
              >
                <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 4 }}>
                  {session.session_id}
                </div>
                <div style={{ fontSize: 11, color: "rgba(228, 232, 241, 0.48)" }}>
                  Status: {session.status || "active"} · Tools: {session.tool_count ?? 0}
                </div>
              </button>
            ))}
          </div>
        ) : null}
      </SidebarSection>

      <SidebarSection
        title="Demo scenarios"
        open={openSections.demo}
        onToggle={() => toggleSection("demo")}
      >
        <div style={{ color: "rgba(228, 232, 241, 0.68)", fontSize: 12, lineHeight: 1.5, marginBottom: 10 }}>
          Choose a scripted demo flow for jury mode and replay the verification sequence.
        </div>
        <select
          value={currentScenario}
          onChange={(event) => startScenario(event.target.value)}
          style={inputStyle}
        >
          {scenarios.map((scenario) => (
            <option key={scenario} value={scenario}>
              {scenarioLabels[scenario] || scenario.replaceAll("_", " ")}
            </option>
          ))}
        </select>
        <button onClick={() => startScenario(currentScenario)} style={demoButtonStyle}>
          Run selected scenario
        </button>
      </SidebarSection>

      <SidebarSection
        title="Notes"
        open={openSections.notes}
        onToggle={() => toggleSection("notes")}
      >
        <div
          style={{
            padding: 14,
            borderRadius: 16,
            background: "rgba(255,255,255,0.03)",
            border: "1px solid rgba(255,255,255,0.08)",
            color: "rgba(245, 247, 251, 0.88)",
            fontSize: 12,
            lineHeight: 1.6
          }}
        >
          Transcript is on the left, while voice activity, agent tools, and backend logs
          stay on the right.
        </div>
      </SidebarSection>
    </aside>
  );
}

function SidebarSection({ title, open, onToggle, children }) {
  return (
    <div style={{ paddingTop: 18, paddingBottom: 18, borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
      <button
        onClick={onToggle}
        style={{
          width: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
          background: "transparent",
          border: "none",
          padding: 0,
          marginBottom: open ? 12 : 0,
          cursor: "pointer"
        }}
      >
        <span style={{ fontSize: 11, color: "rgba(228, 232, 241, 0.48)", textTransform: "uppercase", letterSpacing: 1.2 }}>
          {title}
        </span>
        <span
          style={{
            color: "rgba(228, 232, 241, 0.48)",
            fontSize: 14,
            transform: open ? "rotate(0deg)" : "rotate(-90deg)",
            transition: "transform 180ms ease"
          }}
        >
          ▾
        </span>
      </button>
      {open ? children : null}
    </div>
  );
}

const inputStyle = {
  width: "100%",
  borderRadius: 12,
  border: "1px solid rgba(255,255,255,0.08)",
  background: "#0b1220",
  color: "#e5edf8",
  padding: "11px 12px",
  fontSize: 12,
  marginBottom: 10
};

const primaryButtonStyle = {
  width: "100%",
  padding: "11px 12px",
  borderRadius: 12,
  border: "none",
  background:
    "linear-gradient(135deg, #8bf5b2 0%, #64d9ff 52%, #9d9bff 100%)",
  color: "#081018",
  fontWeight: 600,
  cursor: "pointer",
  boxShadow: "0 18px 40px rgba(100, 217, 255, 0.16)"
};

const secondaryButtonStyle = {
  width: "100%",
  padding: "10px 12px",
  borderRadius: 12,
  border: "1px solid rgba(255,255,255,0.08)",
  background: "rgba(255,255,255,0.03)",
  color: "rgba(245, 247, 251, 0.88)",
  fontWeight: 600,
  cursor: "pointer"
};

const demoButtonStyle = {
  width: "100%",
  padding: "11px 12px",
  borderRadius: 12,
  border: "1px solid rgba(255,255,255,0.08)",
  background: "rgba(255,255,255,0.03)",
  color: "rgba(245, 247, 251, 0.88)",
  fontWeight: 600,
  cursor: "pointer"
};
