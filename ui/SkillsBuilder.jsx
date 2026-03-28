import React from "react";

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
    gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
    gap: 14
  },
  card: {
    padding: 18,
    borderRadius: 20,
    background: "rgba(255,255,255,0.03)",
    border: "1px solid rgba(255,255,255,0.08)"
  },
  toggle: {
    width: 18,
    height: 18
  }
};

export default function SkillsBuilder({ config, updateConfig }) {
  const toggleSkill = (id) => {
    updateConfig({
      skills: config.skills.map((skill) =>
        skill.id === id ? { ...skill, enabled: !skill.enabled } : skill
      )
    });
  };

  return (
    <div>
      <h2 style={styles.title}>Visual skills builder</h2>
      <p style={styles.lead}>
        This module lets operators turn capabilities on and off through cards
        instead of editing raw skill files.
      </p>

      <div style={styles.grid}>
        {config.skills.map((skill) => (
          <div key={skill.id} style={styles.card}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                gap: 12
              }}
            >
              <div>
                <div style={{ color: "#8bf5b2", fontSize: 12, marginBottom: 8 }}>
                  {skill.category}
                </div>
                <div style={{ fontWeight: 700, marginBottom: 8 }}>{skill.name}</div>
              </div>
              <input
                type="checkbox"
                style={styles.toggle}
                checked={skill.enabled}
                onChange={() => toggleSkill(skill.id)}
              />
            </div>
            <div style={{ color: "rgba(228,232,241,0.6)", lineHeight: 1.55 }}>
              {skill.description}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
