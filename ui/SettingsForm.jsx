import React from "react";

export default function SettingsForm({ config, updateConfig }) {
  return (
    <div>
      <h2>Settings</h2>

      <div>
        <label>Model:</label>
        <select
          value={config.model}
          onChange={(e) => updateConfig({ model: e.target.value })}
        >
          <option value="gpt-4o">gpt-4o</option>
          <option value="gpt-4">gpt-4</option>
        </select>
      </div>

      <div>
        <label>Temperature: {config.temperature}</label>
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

      <div>
        <label>Language:</label>
        <select
          value={config.language}
          onChange={(e) => updateConfig({ language: e.target.value })}
        >
          <option value="pl">PL</option>
          <option value="en">EN</option>
        </select>
      </div>
    </div>
  );
}