import React from "react";
import { getIndustryPreset } from "./industryConfig";

const organizationOptions = [
  {
    id: "clinic",
    label: "Clinic / hospital",
    description: "Patient registration, scheduling, and medical support."
  },
  {
    id: "bank",
    label: "Bank",
    description: "Secure customer support, card operations, and account help."
  },
  {
    id: "office",
    label: "Public office",
    description: "Case status, appointments, forms, and document guidance."
  }
];

const industryPromptIdeas = {
  clinic: [
    "Use calm and reassuring language for patients.",
    "After failed authentication, offer a human handoff.",
    "Summarize every call for CRM and patient history.",
    "Always propose the nearest available appointment slots."
  ],
  bank: [
    "Keep every answer security-first and highly structured.",
    "Never reveal internal fraud procedures or sensitive details.",
    "Escalate risky or suspicious requests to a specialist.",
    "Explain next steps in short, confidence-building sentences."
  ],
  office: [
    "Explain public procedures step by step in plain language.",
    "List required documents before booking or updating a case.",
    "Escalate exceptional administrative situations to a clerk.",
    "Always confirm the exact next action the resident should take."
  ]
};

const toneOptions = {
  clinic: ["Warm and professional", "Calm and reassuring", "Friendly and clear"],
  bank: [
    "Confident and professional",
    "Formal and precise",
    "Security-first and clear"
  ],
  office: ["Clear and formal", "Helpful and structured", "Patient and professional"]
};

const cardStyles = {
  sectionTitle: {
    marginTop: 0,
    marginBottom: 8,
    fontSize: 28
  },
  sectionLead: {
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
  textarea: {
    width: "100%",
    minHeight: 140,
    padding: "14px 16px",
    borderRadius: 16,
    border: "1px solid rgba(255, 255, 255, 0.08)",
    background: "rgba(255, 255, 255, 0.03)",
    color: "#f5f7fb",
    fontSize: 15,
    lineHeight: 1.5,
    boxSizing: "border-box",
    resize: "vertical"
  },
  optionGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
    gap: 12,
    marginBottom: 24
  },
  optionCard: (active) => ({
    padding: 16,
    borderRadius: 18,
    border: active
      ? "1px solid rgba(117, 255, 163, 0.28)"
      : "1px solid rgba(255, 255, 255, 0.08)",
    background: active
      ? "linear-gradient(180deg, rgba(18, 27, 36, 0.96), rgba(11, 18, 27, 0.96))"
      : "rgba(255,255,255,0.03)",
    color: active ? "#f8f4eb" : "#f5f7fb",
    cursor: "pointer",
    boxShadow: active ? "0 18px 40px rgba(0, 0, 0, 0.28)" : "none"
  }),
  chipRow: {
    display: "flex",
    flexWrap: "wrap",
    gap: 10,
    marginTop: 12
  },
  chip: {
    padding: "10px 12px",
    borderRadius: 999,
    border: "1px solid rgba(100, 217, 255, 0.16)",
    background: "rgba(100, 217, 255, 0.07)",
    color: "#cfe9ff",
    cursor: "pointer"
  }
};

export default function BehaviorForm({ config, updateConfig }) {
  const promptIdeas =
    industryPromptIdeas[config.organizationType] || industryPromptIdeas.clinic;
  const availableTones = toneOptions[config.organizationType] || toneOptions.clinic;

  const addPromptIdea = (idea) => {
    const nextPrompt = config.prompt ? `${config.prompt} ${idea}` : idea;
    updateConfig({ prompt: nextPrompt });
  };

  const applyIndustryPreset = (industry) => {
    updateConfig(getIndustryPreset(industry));
  };

  return (
    <div>
      <h2 style={cardStyles.sectionTitle}>Define agent behavior</h2>
      <p style={cardStyles.sectionLead}>
        This section turns business needs into an agent brief. When you switch
        industries, the fields adapt to that institution type.
      </p>

      <div style={cardStyles.field}>
        <div style={cardStyles.label}>Institution type</div>
        <div style={cardStyles.optionGrid}>
          {organizationOptions.map((option) => {
            const active = option.id === config.organizationType;
            return (
              <div
                key={option.id}
                onClick={() => applyIndustryPreset(option.id)}
                style={cardStyles.optionCard(active)}
              >
                <div style={{ fontWeight: 700, marginBottom: 8 }}>{option.label}</div>
                <div style={{ fontSize: 14, lineHeight: 1.45, opacity: 0.84 }}>
                  {option.description}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div style={cardStyles.grid}>
        <div style={cardStyles.field}>
          <label style={cardStyles.label}>Organization name</label>
          <input
            style={cardStyles.input}
            placeholder="For example: NorthRiver Bank"
            value={config.organizationName}
            onChange={(e) => updateConfig({ organizationName: e.target.value })}
          />
        </div>

        <div style={cardStyles.field}>
          <label style={cardStyles.label}>Agent tone</label>
          <select
            style={cardStyles.input}
            value={config.tone}
            onChange={(e) => updateConfig({ tone: e.target.value })}
          >
            {availableTones.map((tone) => (
              <option key={tone} value={tone}>
                {tone}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div style={{ ...cardStyles.field, marginTop: 20 }}>
        <label style={cardStyles.label}>Institution description</label>
        <textarea
          style={cardStyles.textarea}
          placeholder="Describe the institution, audience, and the kind of service it wants to automate..."
          value={config.institutionDescription}
          onChange={(e) =>
            updateConfig({ institutionDescription: e.target.value })
          }
        />
      </div>

      <div style={{ ...cardStyles.field, marginTop: 20 }}>
        <label style={cardStyles.label}>Primary business goal</label>
        <textarea
          style={cardStyles.textarea}
          placeholder="Describe what the agent should help users accomplish..."
          value={config.goal}
          onChange={(e) => updateConfig({ goal: e.target.value })}
        />
      </div>

      <div style={{ ...cardStyles.field, marginTop: 20 }}>
        <label style={cardStyles.label}>Behavior instructions</label>
        <textarea
          style={cardStyles.textarea}
          placeholder="Describe how the agent should speak, guide the user, and escalate edge cases..."
          value={config.prompt}
          onChange={(e) => updateConfig({ prompt: e.target.value })}
        />

        <div style={cardStyles.chipRow}>
          {promptIdeas.map((idea) => (
            <button
              key={idea}
              type="button"
              style={cardStyles.chip}
              onClick={() => addPromptIdea(idea)}
            >
              + {idea}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
