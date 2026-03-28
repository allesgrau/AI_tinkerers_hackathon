import React, { useMemo } from "react";

const styles = {
  title: { marginTop: 0, marginBottom: 8, fontSize: 28 },
  lead: {
    marginTop: 0,
    marginBottom: 24,
    color: "rgba(228, 232, 241, 0.66)",
    lineHeight: 1.6
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 18,
    marginBottom: 22
  },
  card: {
    borderRadius: 22,
    padding: 20,
    background: "rgba(255,255,255,0.03)",
    border: "1px solid rgba(255,255,255,0.08)"
  },
  code: {
    whiteSpace: "pre-wrap",
    lineHeight: 1.7,
    color: "#dbe7f7",
    fontFamily: '"SFMono-Regular", Consolas, "Liberation Mono", monospace',
    fontSize: 13
  }
};

export default function PromptStudio({ config, updateConfig, children }) {
  const generatedPrompt = useMemo(() => {
    return [
      `Role: voice agent for ${config.organizationName}.`,
      `Institution type: ${config.organizationType}.`,
      `Institution description: ${config.institutionDescription}`,
      `Primary business goal: ${config.goal}`,
      `Response tone: ${config.tone}.`,
      `Conversation language: ${config.language}.`,
      `Active authentication steps: ${Object.entries(config.authSteps)
        .filter(([, enabled]) => enabled)
        .map(([key]) => key)
        .join(", ")}.`,
      `Enabled skills: ${config.skills
        .filter((skill) => skill.enabled)
        .map((skill) => skill.name)
        .join(", ")}.`,
      `Behavior rules: ${config.prompt}`
    ].join("\n");
  }, [config]);

  return (
    <div>
      <h2 style={styles.title}>Phase 1 + Phase 2: prompt studio</h2>
      <p style={styles.lead}>
        This module connects the institution brief with a real-time generated
        prompt preview.
      </p>

      <div style={styles.grid}>
        <div style={styles.card}>
          <div style={{ color: "#8bf5b2", marginBottom: 10, fontWeight: 700 }}>
            Institution description
          </div>
          <textarea
            value={config.institutionDescription}
            onChange={(e) =>
              updateConfig({ institutionDescription: e.target.value })
            }
            style={{
              width: "100%",
              minHeight: 180,
              borderRadius: 16,
              padding: 16,
              border: "1px solid rgba(255,255,255,0.08)",
              background: "rgba(255,255,255,0.02)",
              color: "#f5f7fb",
              resize: "vertical"
            }}
          />
        </div>

        <div style={styles.card}>
          <div style={{ color: "#8bf5b2", marginBottom: 10, fontWeight: 700 }}>
            Generated prompt
          </div>
          <div style={styles.code}>{generatedPrompt}</div>
        </div>
      </div>

      {children}
    </div>
  );
}
