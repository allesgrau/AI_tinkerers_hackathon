import React from "react";

export default function ActionsForm({ config, updateConfig }) {
  const addAction = () => {
    updateConfig({
      actions: [
        ...config.actions,
        { name: "", endpoint: "", method: "POST" }
      ]
    });
  };

  const updateAction = (index, field, value) => {
    const updated = [...config.actions];
    updated[index][field] = value;
    updateConfig({ actions: updated });
  };

  const removeAction = (index) => {
    const updated = config.actions.filter((_, i) => i !== index);
    updateConfig({ actions: updated });
  };

  return (
    <div>
      <h2>Actions</h2>

      {config.actions.map((action, index) => (
        <div key={index} style={{ border: "1px solid #ddd", padding: 10, marginBottom: 10 }}>
          <input
            placeholder="Name"
            value={action.name}
            onChange={(e) => updateAction(index, "name", e.target.value)}
          />

          <input
            placeholder="Endpoint"
            value={action.endpoint}
            onChange={(e) => updateAction(index, "endpoint", e.target.value)}
          />

          <select
            value={action.method}
            onChange={(e) => updateAction(index, "method", e.target.value)}
          >
            <option value="GET">GET</option>
            <option value="POST">POST</option>
          </select>

          <button onClick={() => removeAction(index)}>Delete</button>
        </div>
      ))}

      <button onClick={addAction}>+ Add Action</button>
    </div>
  );
}