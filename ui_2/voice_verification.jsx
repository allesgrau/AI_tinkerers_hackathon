import React, { useState } from "react";
import ConnectionStatus from "./components/ConnectionStatus";
import StepProgress from "./components/StepProgress";
import RiskIndicators from "./components/RiskIndicators";
import TranscriptPanel from "./components/TranscriptPanel";
import ReasoningPanel from "./components/ReasoningPanel";
import SessionOverlay from "./components/SessionOverlay";
import SessionSidebar from "./components/SessionSidebar";
import { useVoiceGuard } from "./useVoiceGuard";

export default function App() {
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [summaryVisible, setSummaryVisible] = useState(true);
  const {
    mode,
    activeSessionId,
    connectionStatus,
    transcript,
    reasoning,
    steps,
    riskIndicators,
    scenarios,
    currentScenario,
    sessionComplete,
    setSessionComplete,
    startScenario,
    subscribeToLiveSession
  } = useVoiceGuard();

  const availableScenarios =
    scenarios.length > 0
      ? scenarios
      : ["happy_path", "wrong_voice", "brute_force", "replay_attack"];

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
          gap: 12px;
        }
        .dashboard-main {
          display: flex;
          min-height: 0;
          border-top: 1px solid #172436;
          border-bottom: 1px solid #172436;
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
            padding: 16px 18px 12px;
          }
          .dashboard-header {
            padding: 12px 18px;
            min-height: 88px;
          }
        }
        @media (max-width: 980px) {
          .dashboard-main {
            flex-direction: column;
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
            scenarios={availableScenarios}
            currentScenario={currentScenario}
            startScenario={startScenario}
            subscribeToLiveSession={subscribeToLiveSession}
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
                <div style={{ fontSize: 22, fontWeight: 700 }}>VoiceGuard</div>
                <div style={{ color: "#64748b", fontSize: 12 }}>
                  Operational dashboard for transcript, reasoning, and verification risk.
                </div>
                <div className="session-badges">
                  <span className="session-badge">
                    Session: {activeSessionId || "not connected"}
                  </span>
                  <span className="session-badge">
                    {mode === "live" ? "Live session" : "Demo mode"}
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
              <RiskIndicators indicators={riskIndicators} />
              <StepProgress steps={steps} />
            </section>
          ) : null}

          <main className="dashboard-main">
            <TranscriptPanel transcript={transcript} />
            <ReasoningPanel reasoning={reasoning} />
          </main>

          <footer className="dashboard-footer">
            <span>Powered by VoiceGuard</span>
            <span>
              {sessionComplete
                ? `Session result: ${sessionComplete.result}`
                : "Session in progress"}
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
