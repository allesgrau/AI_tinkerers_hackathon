import React, { useState } from "react";
import ConnectionStatus from "./components/ConnectionStatus";
import ReasoningPanel from "./components/ReasoningPanel";
import SessionOverlay from "./components/SessionOverlay";
import SessionSidebar from "./components/SessionSidebar";
import ToolActivityPanel from "./components/ToolActivityPanel";
import TranscriptPanel from "./components/TranscriptPanel";
import { useVoiceGuard } from "./useVoiceGuard";

export default function App() {
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [summaryVisible, setSummaryVisible] = useState(true);
  const {
    mode,
    activeSessionId,
    availableSessions,
    connectionStatus,
    transcript,
    toolActivity,
    reasoning,
    scenarios,
    currentScenario,
    sessionComplete,
    callDetails,
    setSessionComplete,
    startScenario,
    subscribeToLiveSession,
    refreshSessions
  } = useVoiceGuard();

  const availableScenarios =
    scenarios.length > 0
      ? scenarios
      : ["happy_path", "wrong_voice", "brute_force", "replay_attack"];

  const summaryCards = [
    {
      label: "Call status",
      value: prettifyValue(callDetails.status || "idle")
    },
    {
      label: "Caller",
      value: callDetails.from_number || "Waiting for Twilio"
    },
    {
      label: "Model",
      value: callDetails.model || "Not connected"
    },
    {
      label: "Tools used",
      value: String(
        toolActivity.filter((item) => item.kind === "call").length
      )
    }
  ];

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html, body, #root { height: 100%; }
        body {
          background: #060b14;
          color: #e5edf8;
          font-family: "Sora", sans-serif;
        }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 999px; }
        .workspace-grid {
          display: grid;
          min-width: 0;
        }
        .dashboard-header {
          border-bottom: 1px solid #172436;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 22px;
          gap: 16px;
        }
        .header-brand {
          display: flex;
          align-items: center;
          gap: 14px;
          min-width: 0;
        }
        .brand-mark {
          width: 42px;
          height: 42px;
          border-radius: 14px;
          display: grid;
          place-items: center;
          background: radial-gradient(circle at top, rgba(56,189,248,0.4), rgba(37,99,235,0.15));
          border: 1px solid rgba(56,189,248,0.2);
          color: #dbeafe;
          font-weight: 700;
          letter-spacing: 0.08em;
        }
        .brand-copy {
          min-width: 0;
        }
        .session-badges {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
          margin-top: 8px;
        }
        .session-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 7px 10px;
          border-radius: 999px;
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.08);
          color: #cbd5e1;
          font-size: 11px;
        }
        .header-actions {
          display: flex;
          align-items: center;
          gap: 10px;
          flex-wrap: wrap;
          justify-content: flex-end;
        }
        .dashboard-summary {
          padding: 18px 22px 14px;
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 12px;
        }
        .summary-card {
          padding: 16px;
          border-radius: 18px;
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.08);
          min-width: 0;
        }
        .summary-label {
          color: #64748b;
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 1.1px;
          margin-bottom: 8px;
        }
        .summary-value {
          color: #e5edf8;
          font-size: 18px;
          font-weight: 700;
          line-height: 1.3;
          word-break: break-word;
        }
        .dashboard-main {
          display: grid;
          grid-template-columns: minmax(360px, 1.1fr) minmax(340px, 0.9fr);
          min-height: 0;
          border-top: 1px solid #172436;
          border-bottom: 1px solid #172436;
        }
        .right-column {
          display: grid;
          grid-template-rows: minmax(260px, 0.95fr) minmax(220px, 1fr);
          min-height: 0;
          border-left: 1px solid #172436;
        }
        .dashboard-footer {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 22px;
          color: #64748b;
          font-size: 11px;
          gap: 12px;
        }
        @media (max-width: 1180px) {
          .dashboard-summary {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            padding: 16px 18px 12px;
          }
          .dashboard-header {
            padding: 12px 18px;
            min-height: 88px;
          }
        }
        @media (max-width: 980px) {
          .dashboard-main {
            grid-template-columns: 1fr;
          }
          .right-column {
            border-left: none;
            border-top: 1px solid #172436;
          }
          .dashboard-footer {
            padding: 10px 18px;
            min-height: 42px;
            flex-wrap: wrap;
          }
        }
        @media (max-width: 860px) {
          .dashboard-header {
            align-items: flex-start;
            flex-direction: column;
          }
          .header-actions {
            width: 100%;
            justify-content: flex-start;
          }
        }
        @media (max-width: 640px) {
          .dashboard-summary {
            grid-template-columns: 1fr;
          }
        }
      `}</style>

      <div
        style={{
          height: "100vh",
          display: "grid",
          gridTemplateColumns: sidebarVisible ? "280px 1fr" : "1fr",
          background:
            "radial-gradient(circle at top left, rgba(56,189,248,0.08), rgba(6,11,20,0) 24%), linear-gradient(180deg, #060b14 0%, #09111f 100%)"
        }}
      >
        {sidebarVisible ? (
          <SessionSidebar
            mode={mode}
            activeSessionId={activeSessionId}
            availableSessions={availableSessions}
            scenarios={availableScenarios}
            currentScenario={currentScenario}
            startScenario={startScenario}
            subscribeToLiveSession={subscribeToLiveSession}
            refreshSessions={refreshSessions}
            connectionStatus={connectionStatus}
            sessionComplete={sessionComplete}
          />
        ) : null}

        <div
          className="workspace-grid"
          style={{
            gridTemplateRows: summaryVisible ? "92px auto 1fr 26px" : "92px 1fr 26px"
          }}
        >
          <header className="dashboard-header">
            <div className="header-brand">
              <div className="brand-mark">VG</div>
              <div className="brand-copy">
                <div style={{ fontSize: 22, fontWeight: 700 }}>VoiceGuard Live Ops</div>
                <div style={{ color: "#64748b", fontSize: 12 }}>
                  Twilio phone call monitor with live transcript and tool usage.
                </div>
                <div className="session-badges">
                  <span className="session-badge">
                    Session: {activeSessionId || "not connected"}
                  </span>
                  <span className="session-badge">
                    {mode === "live" ? "Live phone call" : "Demo mode"}
                  </span>
                  <span className="session-badge">
                    To: {callDetails.to_number || "Twilio number not attached yet"}
                  </span>
                </div>
              </div>
            </div>

            <div className="header-actions">
              <button
                onClick={() => setSidebarVisible((value) => !value)}
                style={toggleButtonStyle}
              >
                {sidebarVisible ? "Hide sidebar" : "Show sidebar"}
              </button>
              <button
                onClick={() => setSummaryVisible((value) => !value)}
                style={toggleButtonStyle}
              >
                {summaryVisible ? "Hide summary" : "Show summary"}
              </button>
              <ConnectionStatus status={connectionStatus} />
            </div>
          </header>

          {summaryVisible ? (
            <section className="dashboard-summary">
              {summaryCards.map((card) => (
                <div key={card.label} className="summary-card">
                  <div className="summary-label">{card.label}</div>
                  <div className="summary-value">{card.value}</div>
                </div>
              ))}
            </section>
          ) : null}

          <main className="dashboard-main">
            <TranscriptPanel transcript={transcript} />
            <div className="right-column">
              <ToolActivityPanel toolActivity={toolActivity} />
              <ReasoningPanel reasoning={reasoning} />
            </div>
          </main>

          <footer className="dashboard-footer">
            <span>Powered by VoiceGuard + Gemini Live + Twilio Media Streams</span>
            <span>
              {sessionComplete
                ? `Session result: ${sessionComplete.result}`
                : callDetails.error
                  ? `Call error: ${callDetails.error}`
                  : "Call in progress"}
            </span>
          </footer>
        </div>
      </div>

      <SessionOverlay
        sessionComplete={sessionComplete}
        onClose={() => setSessionComplete(null)}
      />
    </>
  );
}

function prettifyValue(value) {
  return String(value).replaceAll("_", " ");
}

const toggleButtonStyle = {
  padding: "10px 14px",
  borderRadius: 999,
  border: "1px solid rgba(255,255,255,0.1)",
  background: "rgba(255,255,255,0.03)",
  color: "#dbe7f7",
  fontSize: 12,
  fontWeight: 600,
  cursor: "pointer"
};
