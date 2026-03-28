import React from "react";

export default function BehaviorForm({ config, updateConfig }) {
  return (
    <div>
      <h2>Agent Behavior</h2>
      <textarea
        style={{ width: "100%", height: 200 }}
        placeholder="Opisz co ma robić agent..."
        value={config.prompt}
        onChange={(e) => updateConfig({ prompt: e.target.value })}
      />
    </div>
  );
}