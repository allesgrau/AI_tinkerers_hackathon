import React, { useMemo, useState } from "react";
import BehaviorForm from "./BehaviorForm";
import SettingsForm from "./SettingsForm";
import ActionsForm from "./ActionsForm";
import Preview from "./Preview";
import DashboardHome from "./DashboardHome";
import PromptStudio from "./PromptStudio";
import VisitsDashboard from "./VisitsDashboard";
import SkillsBuilder from "./SkillsBuilder";
import { getIndustryPreset } from "./industryConfig";

const tabs = [
  { id: "dashboard", label: "Dashboard", hint: "Calls, KPIs, and status" },
  { id: "behavior", label: "Agent setup", hint: "Institution brief and behavior" },
  { id: "settings", label: "Settings", hint: "Model, language, and auth" },
  { id: "actions", label: "Prompt studio", hint: "Prompt and business actions" },
  { id: "skills", label: "Skills builder", hint: "Visual skill configuration" },
  { id: "appointments", label: "Appointments", hint: "Records and filtering" },
  { id: "preview", label: "Live preview", hint: "Real-time prompt output" }
];

const initialConfig = {
  ...getIndustryPreset("clinic"),
  model: "gpt-4o",
  temperature: 0.5,
  authSteps: {
    pesel: true,
    sms: true,
    voice: true
  },
  conversationSummary: true
};

const shellStyles = {
  app: {
    minHeight: "100vh",
    display: "grid",
    gridTemplateColumns: "280px 1fr",
    background:
      "radial-gradient(circle at top center, rgba(79, 209, 122, 0.16) 0%, rgba(8, 10, 16, 0) 26%), linear-gradient(180deg, #07090f 0%, #090d14 46%, #05070d 100%)",
    color: "#f5f7fb",
    fontFamily: '"SF Pro Display", "Inter", "Segoe UI", Arial, sans-serif'
  },
  sidebar: {
    padding: 28,
    borderRight: "1px solid rgba(255, 255, 255, 0.08)",
    background: "rgba(9, 13, 20, 0.8)",
    backdropFilter: "blur(22px)",
    boxShadow: "inset -1px 0 0 rgba(255,255,255,0.04)"
  },
  badge: {
    display: "inline-flex",
    padding: "7px 12px",
    borderRadius: 999,
    background: "rgba(117, 255, 163, 0.12)",
    color: "#8bf5b2",
    fontSize: 12,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    border: "1px solid rgba(117, 255, 163, 0.22)"
  },
  title: {
    fontSize: 34,
    lineHeight: 1.02,
    margin: "18px 0 10px"
  },
  subtitle: {
    margin: 0,
    color: "rgba(228, 232, 241, 0.68)",
    lineHeight: 1.5
  },
  nav: {
    display: "grid",
    gap: 12,
    marginTop: 28
  },
  navItem: (active) => ({
    padding: 16,
    borderRadius: 20,
    cursor: "pointer",
    border: active
      ? "1px solid rgba(117, 255, 163, 0.28)"
      : "1px solid rgba(255, 255, 255, 0.08)",
    background: active
      ? "linear-gradient(180deg, rgba(19, 29, 39, 0.96), rgba(12, 18, 27, 0.92))"
      : "rgba(255,255,255,0.03)",
    color: active ? "#f5f7fb" : "rgba(245, 247, 251, 0.88)",
    boxShadow: active ? "0 18px 40px rgba(0, 0, 0, 0.34)" : "none"
  }),
  navHint: (active) => ({
    display: "block",
    marginTop: 6,
    fontSize: 13,
    color: active ? "rgba(139, 245, 178, 0.85)" : "rgba(228, 232, 241, 0.48)"
  }),
  saveButton: {
    width: "100%",
    marginTop: 24,
    padding: "14px 18px",
    borderRadius: 16,
    border: "none",
    background:
      "linear-gradient(135deg, #8bf5b2 0%, #64d9ff 52%, #9d9bff 100%)",
    color: "#081018",
    fontSize: 15,
    fontWeight: 700,
    cursor: "pointer",
    boxShadow: "0 18px 40px rgba(100, 217, 255, 0.22)"
  },
  main: {
    padding: 32
  },
  hero: {
    display: "grid",
    gap: 18,
    gridTemplateColumns: "minmax(0, 1.4fr) minmax(280px, 0.8fr)",
    alignItems: "stretch"
  },
  heroCard: {
    borderRadius: 30,
    padding: 28,
    background:
      "linear-gradient(180deg, rgba(15, 19, 28, 0.9), rgba(10, 13, 20, 0.86))",
    border: "1px solid rgba(255,255,255,0.08)",
    boxShadow: "0 24px 60px rgba(0, 0, 0, 0.36)"
  },
  metricGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
    gap: 12,
    marginTop: 20
  },
  metricCard: {
    padding: 16,
    borderRadius: 18,
    background: "rgba(255,255,255,0.03)",
    border: "1px solid rgba(255,255,255,0.08)"
  },
  metricValue: {
    fontSize: 22,
    fontWeight: 700,
    marginBottom: 4,
    color: "#8bf5b2"
  },
  panel: {
    marginTop: 24,
    borderRadius: 30,
    padding: 28,
    background:
      "linear-gradient(180deg, rgba(13, 16, 25, 0.88), rgba(9, 12, 19, 0.92))",
    border: "1px solid rgba(255,255,255,0.08)",
    boxShadow: "0 24px 60px rgba(0, 0, 0, 0.34)"
  }
};

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [config, setConfig] = useState(initialConfig);
  const [saveState, setSaveState] = useState("idle");
  const [saveMessage, setSaveMessage] = useState("");
  const [appointmentFilters, setAppointmentFilters] = useState({
    specialty: "all",
    status: "all",
    query: ""
  });

  const updateConfig = (updates) => {
    setConfig((prev) => ({ ...prev, ...updates }));
  };

  const enabledAuthCount = useMemo(
    () => Object.values(config.authSteps).filter(Boolean).length,
    [config.authSteps]
  );

  const renderTab = () => {
    switch (activeTab) {
      case "dashboard":
        return <DashboardHome config={config} setActiveTab={setActiveTab} />;
      case "behavior":
        return <BehaviorForm config={config} updateConfig={updateConfig} />;
      case "settings":
        return <SettingsForm config={config} updateConfig={updateConfig} />;
      case "actions":
        return (
          <PromptStudio config={config} updateConfig={updateConfig}>
            <ActionsForm config={config} updateConfig={updateConfig} />
          </PromptStudio>
        );
      case "skills":
        return <SkillsBuilder config={config} updateConfig={updateConfig} />;
      case "appointments":
        return (
          <VisitsDashboard
            config={config}
            filters={appointmentFilters}
            setFilters={setAppointmentFilters}
          />
        );
      case "preview":
        return <Preview config={config} />;
      default:
        return null;
    }
  };

  const handleSave = async () => {
    setSaveState("saving");
    setSaveMessage("Saving configuration...");

    try {
      const response = await fetch("/api/agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config)
      });

      if (!response.ok) {
        throw new Error("Could not save configuration.");
      }

      setSaveState("saved");
      setSaveMessage("Configuration saved.");
    } catch (error) {
      setSaveState("saved");
      setSaveMessage(
        "Backend is not connected yet, but your configuration is ready for demo use."
      );
    }
  };

  return (
    <div style={shellStyles.app}>
      <aside style={shellStyles.sidebar}>
        <span style={shellStyles.badge}>Admin UI</span>
        <h1 style={shellStyles.title}>Voice agent control center</h1>
        <p style={shellStyles.subtitle}>
          A product-style workspace for institutions that want to configure
          voice agents without writing prompts or technical rules by hand.
        </p>

        <div style={shellStyles.nav}>
          {tabs.map((tab) => {
            const active = activeTab === tab.id;
            return (
              <div
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={shellStyles.navItem(active)}
              >
                <div style={{ fontWeight: 700 }}>{tab.label}</div>
                <span style={shellStyles.navHint(active)}>{tab.hint}</span>
              </div>
            );
          })}
        </div>

        <button
          onClick={handleSave}
          style={{
            ...shellStyles.saveButton,
            opacity: saveState === "saving" ? 0.8 : 1
          }}
        >
          {saveState === "saving" ? "Saving..." : "Save configuration"}
        </button>

        <p
          style={{
            marginTop: 12,
            color: "rgba(228, 232, 241, 0.56)",
            lineHeight: 1.45
          }}
        >
          {saveMessage ||
            "Move across sections and prepare the full product demo even before the backend is connected."}
        </p>
      </aside>

      <main style={shellStyles.main}>
        <section style={shellStyles.hero}>
          <div style={shellStyles.heroCard}>
            <div
              style={{
                color: "#8bf5b2",
                fontWeight: 700,
                marginBottom: 10,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                fontSize: 12
              }}
            >
              Voice Ops Dashboard
            </div>
            <h2 style={{ margin: 0, fontSize: 34, lineHeight: 1.08 }}>
              {config.organizationName}
            </h2>
            <p
              style={{
                margin: "14px 0 0",
                color: "rgba(228, 232, 241, 0.72)",
                lineHeight: 1.6
              }}
            >
              {config.goal}
            </p>

            <div style={shellStyles.metricGrid}>
              <div style={shellStyles.metricCard}>
                <div style={shellStyles.metricValue}>{config.calls.length}</div>
                <div>Active calls</div>
              </div>
              <div style={shellStyles.metricCard}>
                <div style={shellStyles.metricValue}>{enabledAuthCount}/3</div>
                <div>Auth layers</div>
              </div>
              <div style={shellStyles.metricCard}>
                <div style={shellStyles.metricValue}>{config.appointments.length}</div>
                <div>Records in dashboard</div>
              </div>
            </div>
          </div>

          <div
            style={{
              ...shellStyles.heroCard,
              background:
                "radial-gradient(circle at top left, rgba(100, 217, 255, 0.18), rgba(9, 12, 19, 0) 42%), linear-gradient(180deg, rgba(12, 18, 27, 0.96), rgba(8, 12, 18, 0.92))",
              color: "#f8f4eb"
            }}
          >
            <div style={{ fontSize: 14, opacity: 0.8, color: "#8bf5b2" }}>
              Product-style preview
            </div>
            <h3 style={{ margin: "10px 0 12px", fontSize: 26, lineHeight: 1.1 }}>
              Configure your voice agent like a modern SaaS product
            </h3>
            <p
              style={{
                margin: 0,
                lineHeight: 1.6,
                opacity: 0.9,
                color: "rgba(245, 247, 251, 0.82)"
              }}
            >
              The interface now adapts across healthcare, banking, and public
              office scenarios so your demo feels like a real multi-industry AI
              platform.
            </p>
          </div>
        </section>

        <section style={shellStyles.panel}>{renderTab()}</section>
      </main>
    </div>
  );
}
