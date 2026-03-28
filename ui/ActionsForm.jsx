import React from "react";

const actionTemplates = [
  {
    name: "Reschedule appointment",
    endpoint: "/api/appointments/reschedule",
    method: "POST",
    description: "Updates the date and time of an existing booking."
  },
  {
    name: "Cancel booking",
    endpoint: "/api/appointments/cancel",
    method: "POST",
    description: "Cancels a booking after identity verification."
  },
  {
    name: "Create authorization",
    endpoint: "/api/authorizations",
    method: "POST",
    description: "Stores a permission or delegation for another person."
  }
];

const styles = {
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
  templateRow: {
    display: "flex",
    flexWrap: "wrap",
    gap: 10,
    marginBottom: 20
  },
  templateButton: {
    padding: "10px 14px",
    borderRadius: 999,
    border: "1px solid rgba(100, 217, 255, 0.16)",
    background: "rgba(100, 217, 255, 0.07)",
    color: "#d7ecff",
    cursor: "pointer"
  },
  actionCard: {
    border: "1px solid rgba(255, 255, 255, 0.08)",
    borderRadius: 22,
    padding: 18,
    marginBottom: 14,
    background: "rgba(255,255,255,0.03)"
  },
  row: {
    display: "grid",
    gridTemplateColumns: "1.2fr 1fr 120px",
    gap: 12
  },
  input: {
    width: "100%",
    padding: "13px 15px",
    borderRadius: 14,
    border: "1px solid rgba(255, 255, 255, 0.08)",
    background: "rgba(255,255,255,0.02)",
    color: "#f5f7fb",
    fontSize: 15,
    boxSizing: "border-box"
  },
  textarea: {
    width: "100%",
    minHeight: 88,
    padding: "13px 15px",
    borderRadius: 14,
    border: "1px solid rgba(255, 255, 255, 0.08)",
    background: "rgba(255,255,255,0.02)",
    color: "#f5f7fb",
    fontSize: 15,
    lineHeight: 1.5,
    boxSizing: "border-box",
    resize: "vertical",
    marginTop: 12
  },
  buttonRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 14
  },
  primaryButton: {
    padding: "12px 18px",
    borderRadius: 14,
    border: "none",
    background:
      "linear-gradient(135deg, rgba(139,245,178,1) 0%, rgba(100,217,255,1) 100%)",
    color: "#081018",
    cursor: "pointer",
    fontWeight: 700
  },
  deleteButton: {
    padding: "10px 14px",
    borderRadius: 12,
    border: "1px solid rgba(255, 122, 122, 0.18)",
    background: "rgba(255, 122, 122, 0.08)",
    color: "#ffb1b1",
    cursor: "pointer"
  }
};

export default function ActionsForm({ config, updateConfig }) {
  const addAction = (template) => {
    const nextAction =
      template || { name: "", endpoint: "", method: "POST", description: "" };

    updateConfig({
      actions: [...config.actions, nextAction]
    });
  };

  const updateAction = (index, field, value) => {
    const updated = [...config.actions];
    updated[index] = { ...updated[index], [field]: value };
    updateConfig({ actions: updated });
  };

  const removeAction = (index) => {
    updateConfig({
      actions: config.actions.filter((_, actionIndex) => actionIndex !== index)
    });
  };

  return (
    <div>
      <h2 style={styles.title}>Business actions</h2>
      <p style={styles.lead}>
        This is where the agent moves from conversation to execution. Define
        what APIs or workflows it can trigger.
      </p>

      <div style={styles.templateRow}>
        {actionTemplates.map((template) => (
          <button
            key={template.name}
            type="button"
            style={styles.templateButton}
            onClick={() => addAction(template)}
          >
            + {template.name}
          </button>
        ))}
      </div>

      {config.actions.map((action, index) => (
        <div key={`${action.name}-${index}`} style={styles.actionCard}>
          <div style={styles.row}>
            <input
              style={styles.input}
              placeholder="Action name"
              value={action.name}
              onChange={(e) => updateAction(index, "name", e.target.value)}
            />

            <input
              style={styles.input}
              placeholder="/api/endpoint"
              value={action.endpoint}
              onChange={(e) => updateAction(index, "endpoint", e.target.value)}
            />

            <select
              style={styles.input}
              value={action.method}
              onChange={(e) => updateAction(index, "method", e.target.value)}
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PATCH">PATCH</option>
              <option value="DELETE">DELETE</option>
            </select>
          </div>

          <textarea
            style={styles.textarea}
            placeholder="When should the agent trigger this action?"
            value={action.description || ""}
            onChange={(e) => updateAction(index, "description", e.target.value)}
          />

          <div style={styles.buttonRow}>
            <span style={{ color: "rgba(228, 232, 241, 0.5)" }}>
              Action {index + 1} of {config.actions.length}
            </span>
            <button
              type="button"
              style={styles.deleteButton}
              onClick={() => removeAction(index)}
            >
              Delete action
            </button>
          </div>
        </div>
      ))}

      <button type="button" style={styles.primaryButton} onClick={() => addAction()}>
        Add empty action
      </button>
    </div>
  );
}
