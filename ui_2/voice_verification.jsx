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
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html, body, #root { height: 100%; }
        body {
          background:
            radial-gradient(circle at top, rgba(139, 245, 178, 0.12), rgba(5, 7, 13, 0) 24%),
            linear-gradient(180deg, #07090f 0%, #090d14 46%, #05070d 100%);
          color: #f5f7fb;
          font-family: "SF Pro Display", "Inter", "Segoe UI", Arial, sans-serif;
        }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 999px; }
        .workspace-grid {
          display: grid;
          min-width: 0;
        }
        .dashboard-header {
          border-bottom: 1px solid rgba(255,255,255,0.08);
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 28px;
          gap: 16px;
          background: rgba(9, 13, 20, 0.44);
          backdrop-filter: blur(16px);
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
          background: radial-gradient(circle at top, rgba(139, 245, 178, 0.32), rgba(100, 217, 255, 0.12));
          border: 1px solid rgba(117, 255, 163, 0.22);
          color: #f5f7fb;
          font-weight: 700;
          letter-spacing: 0.08em;
          box-shadow: 0 12px 30px rgba(100, 217, 255, 0.14);
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
          color: rgba(245, 247, 251, 0.88);
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
          padding: 24px 28px 0;
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 12px;
        }
        .summary-card {
          padding: 16px;
          border-radius: 20px;
          background: linear-gradient(180deg, rgba(15, 19, 28, 0.9), rgba(10, 13, 20, 0.86));
          border: 1px solid rgba(255,255,255,0.08);
          min-width: 0;
          box-shadow: 0 18px 40px rgba(0, 0, 0, 0.24);
        }
        .summary-label {
          color: rgba(228, 232, 241, 0.48);
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 1.1px;
          margin-bottom: 8px;
        }
        .summary-value {
          color: #f5f7fb;
          font-size: 18px;
          font-weight: 700;
          line-height: 1.3;
          word-break: break-word;
        }
        .dashboard-main {
          display: grid;
          grid-template-columns: minmax(360px, 1.1fr) minmax(340px, 0.9fr);
          min-height: 0;
          margin: 24px 28px 0;
          border: 1px solid rgba(255,255,255,0.08);
          border-radius: 30px;
          overflow: hidden;
          background: linear-gradient(180deg, rgba(13, 16, 25, 0.88), rgba(9, 12, 19, 0.92));
          box-shadow: 0 24px 60px rgba(0, 0, 0, 0.34);
        }
        .right-column {
          display: grid;
          grid-template-rows: minmax(260px, 0.95fr) minmax(220px, 1fr);
          min-height: 0;
          border-left: 1px solid rgba(255,255,255,0.08);
        }
        .dashboard-footer {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 28px;
          color: rgba(228, 232, 241, 0.48);
          font-size: 11px;
          gap: 12px;
        }
        @media (max-width: 1180px) {
          .dashboard-summary {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            padding: 16px 18px 0;
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
            "radial-gradient(circle at top center, rgba(79, 209, 122, 0.16) 0%, rgba(8, 10, 16, 0) 26%), linear-gradient(180deg, #07090f 0%, #090d14 46%, #05070d 100%)"
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
                <div style={{ color: "rgba(228, 232, 241, 0.68)", fontSize: 12 }}>
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
  color: "#f5f7fb",
  fontSize: 12,
  fontWeight: 600,
  cursor: "pointer"
};
