import React, { useState } from "react";
import BehaviorForm from "./BehaviorForm";
import SettingsForm from "./SettingsForm";
import ActionsForm from "./ActionsForm";
import Preview from "./Preview";

export default function App() {
  const [activeTab, setActiveTab] = useState("behavior");

  const [config, setConfig] = useState({
    prompt: "",
    model: "gpt-4o",
    temperature: 0.7,
    language: "pl",
    actions: []
  });

  const updateConfig = (updates) => {
    setConfig((prev) => ({ ...prev, ...updates }));
  };

  const renderTab = () => {
    switch (activeTab) {
      case "behavior":
        return <BehaviorForm config={config} updateConfig={updateConfig} />;
      case "settings":
        return <SettingsForm config={config} updateConfig={updateConfig} />;
      case "actions":
        return <ActionsForm config={config} updateConfig={updateConfig} />;
      case "preview":
        return <Preview config={config} />;
      default:
        return null;
    }
  };

  const handleSave = async () => {
    await fetch("/api/agent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config)
    });
    alert("Saved!");
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* Sidebar */}
      <div style={{ width: 200, borderRight: "1px solid #eee", padding: 16 }}>
        {["behavior", "settings", "actions", "preview"].map((tab) => (
          <div
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: 8,
              cursor: "pointer",
              fontWeight: activeTab === tab ? "bold" : "normal"
            }}
          >
            {tab}
          </div>
        ))}
        <button onClick={handleSave} style={{ marginTop: 20 }}>
          Save
        </button>
      </div>

      {/* Main */}
      <div style={{ flex: 1, padding: 24 }}>{renderTab()}</div>
    </div>
  );
}