import React from "react";

const formStyles = {
  title: {
    marginTop: 0,
    marginBottom: 8,
    fontSize: 28
  },
  lead: {
    marginTop: 0,
    marginBottom: 24,
    color: "rgba(228, 232, 241, 0.66)",
    lineHeight: 1.6
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
    gap: 18
  },
  field: {
    display: "grid",
    gap: 8
  },
  label: {
    fontWeight: 700
  },
  input: {
    width: "100%",
    padding: "14px 16px",
    borderRadius: 16,
    border: "1px solid rgba(255, 255, 255, 0.08)",
    background: "rgba(255, 255, 255, 0.03)",
    color: "#f5f7fb",
    fontSize: 15,
    boxSizing: "border-box"
  },
  checkGrid: {
    display: "grid",
    gap: 12,
    marginTop: 12
  },
  checkCard: {
    display: "flex",
    alignItems: "flex-start",
    gap: 12,
    padding: 14,
    borderRadius: 18,
    background: "rgba(255,255,255,0.03)",
    border: "1px solid rgba(255,255,255,0.08)"
  }
};

export default function SettingsForm({ config, updateConfig }) {
  const toggleAuthStep = (key) => {
    updateConfig({
      authSteps: {
        ...config.authSteps,
        [key]: !config.authSteps[key]
      }
    });
  };

  return (
    <div>
      <h2 style={formStyles.title}>Technical settings</h2>
      <p style={formStyles.lead}>
        Configure the runtime model and identity checks. The experience stays
        readable for non-technical operators.
      </p>

      <div style={formStyles.grid}>
        <div style={formStyles.field}>
          <label style={formStyles.label}>Model</label>
          <select
            style={formStyles.input}
            value={config.model}
            onChange={(e) => updateConfig({ model: e.target.value })}
          >
            <option value="gpt-4o">gpt-4o</option>
            <option value="gpt-4.1">gpt-4.1</option>
            <option value="gpt-4">gpt-4</option>
          </select>
        </div>

        <div style={formStyles.field}>
          <label style={formStyles.label}>Conversation language</label>
          <select
            style={formStyles.input}
            value={config.language}
            onChange={(e) => updateConfig({ language: e.target.value })}
          >
            <option value="en">English</option>
            <option value="pl">Polish</option>
          </select>
        </div>
      </div>

      <div style={{ ...formStyles.field, marginTop: 20 }}>
        <label style={formStyles.label}>
          Model temperature: {config.temperature.toFixed(1)}
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={config.temperature}
          onChange={(e) =>
            updateConfig({ temperature: parseFloat(e.target.value) })
          }
        />
      </div>

      <div style={{ marginTop: 26 }}>
        <div style={formStyles.label}>Authentication layers</div>
        <div style={formStyles.checkGrid}>
          <label style={formStyles.checkCard}>
            <input
              type="checkbox"
              checked={config.authSteps.pesel}
              onChange={() => toggleAuthStep("pesel")}
            />
            <span>
              <strong>PESEL</strong>
              <br />
              Primary identity verification before the agent takes action.
            </span>
          </label>

          <label style={formStyles.checkCard}>
            <input
              type="checkbox"
              checked={config.authSteps.sms}
              onChange={() => toggleAuthStep("sms")}
            />
            <span>
              <strong>SMS code</strong>
              <br />
              Extra verification for sensitive operations.
            </span>
          </label>

          <label style={formStyles.checkCard}>
            <input
              type="checkbox"
              checked={config.authSteps.voice}
              onChange={() => toggleAuthStep("voice")}
            />
            <span>
              <strong>Voice biometrics</strong>
              <br />
              Silent comparison against previous voice history.
            </span>
          </label>
        </div>
      </div>

      <label style={{ ...formStyles.checkCard, marginTop: 24 }}>
        <input
          type="checkbox"
          checked={config.conversationSummary}
          onChange={() =>
            updateConfig({ conversationSummary: !config.conversationSummary })
          }
        />
        <span>
          <strong>Automatic call summary</strong>
          <br />
          Generate a short CRM-style summary after each call.
        </span>
      </label>
    </div>
  );
}
