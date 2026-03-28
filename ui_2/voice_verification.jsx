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
    connectionStatus,
    transcript,
    reasoning,
    steps,
    riskIndicators,
    scenarios,
    currentScenario,
    sessionComplete,
    setSessionComplete,
    startScenario
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
            scenarios={availableScenarios}
            currentScenario={currentScenario}
            startScenario={startScenario}
            connectionStatus={connectionStatus}
            sessionComplete={sessionComplete}
          />
        ) : null}

        <div
          style={{
            display: "grid",
            gridTemplateRows: summaryVisible ? "72px auto 1fr 26px" : "72px 1fr 26px",
            minWidth: 0
          }}
        >
          <header
            style={{
              borderBottom: "1px solid #172436",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "0 22px",
              gap: 16
            }}
          >
            <div>
              <div style={{ fontSize: 22, fontWeight: 700 }}>Operational Dashboard</div>
              <div style={{ color: "#64748b", fontSize: 12 }}>
                Transcript, reasoning stream, and risk monitoring
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", justifyContent: "flex-end" }}>
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
            <section style={{ padding: "18px 22px 14px", display: "grid", gap: 12 }}>
              <RiskIndicators indicators={riskIndicators} />
              <StepProgress steps={steps} />
            </section>
          ) : null}

          <main
            style={{
              display: "flex",
              minHeight: 0,
              borderTop: "1px solid #172436",
              borderBottom: "1px solid #172436"
            }}
          >
            <TranscriptPanel transcript={transcript} />
            <ReasoningPanel reasoning={reasoning} />
          </main>

          <footer
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "0 22px",
              color: "#64748b",
              fontSize: 11
            }}
          >
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
