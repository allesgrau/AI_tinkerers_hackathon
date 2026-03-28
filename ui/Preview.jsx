import React, { useMemo, useState } from "react";

const previewStyles = {
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
    gridTemplateColumns: "minmax(0, 1fr) minmax(320px, 0.9fr)",
    gap: 18
  },
  card: {
    borderRadius: 22,
    padding: 20,
    background: "rgba(255,255,255,0.03)",
    border: "1px solid rgba(255,255,255,0.08)"
  },
  code: {
    whiteSpace: "pre-wrap",
    margin: 0,
    fontFamily: '"SFMono-Regular", Consolas, "Liberation Mono", monospace',
    fontSize: 13,
    lineHeight: 1.6,
    color: "#dbe7f7"
  },
  button: {
    marginTop: 18,
    padding: "12px 18px",
    borderRadius: 14,
    border: "none",
    background:
      "linear-gradient(135deg, rgba(139,245,178,1) 0%, rgba(100,217,255,1) 100%)",
    color: "#081018",
    cursor: "pointer",
    fontWeight: 700
  },
  response: {
    marginTop: 16,
    padding: 18,
    borderRadius: 18,
    background: "rgba(255,255,255,0.04)",
    border: "1px solid rgba(255,255,255,0.08)",
    lineHeight: 1.6
  }
};

const languageLabels = {
  pl: "Polish",
  en: "English"
};

export default function Preview({ config }) {
  const [response, setResponse] = useState("");
  const [status, setStatus] = useState("idle");

  const summary = useMemo(
    () => ({
      organization: config.organizationName,
      industry: config.organizationType,
      language: languageLabels[config.language] || config.language,
      model: config.model,
      actions: config.actions.map((action) => ({
        name: action.name,
        method: action.method,
        endpoint: action.endpoint
      })),
      authSteps: Object.entries(config.authSteps)
        .filter(([, enabled]) => enabled)
        .map(([step]) => step),
      tone: config.tone
    }),
    [config]
  );

  const buildMockResponse = () => {
    const actionNames = config.actions.map((action) => action.name).join(", ");

    return [
      `The agent for ${config.organizationName} is ready for demo use.`,
      `The conversation will run in ${languageLabels[config.language] || config.language} with a "${config.tone}" tone.`,
      `Active authentication stages: ${summary.authSteps.join(", ") || "none"}.`,
      `Available business actions: ${actionNames || "not configured yet"}.`,
      "Sample reply: Hello, I can help with that. First, let me verify your identity, then I will guide you through the next step."
    ].join("\n\n");
  };

  const testAgent = async () => {
    setStatus("loading");

    try {
      const res = await fetch("/api/test-agent", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(config)
      });

      if (!res.ok) {
        throw new Error("No response from backend.");
      }

      const data = await res.json();
      setResponse(data.response);
      setStatus("done");
    } catch (error) {
      setResponse(buildMockResponse());
      setStatus("done");
    }
  };

  return (
    <div>
      <h2 style={previewStyles.title}>Live preview and demo narrative</h2>
      <p style={previewStyles.lead}>
        This view gives you a compact config snapshot, a prompt-ready story for
        a demo, and a mocked agent response when the backend is missing.
      </p>

      <div style={previewStyles.grid}>
        <div style={previewStyles.card}>
          <h3 style={{ marginTop: 0 }}>Configuration summary</h3>
          <pre style={previewStyles.code}>
            {JSON.stringify(summary, null, 2)}
          </pre>
        </div>

        <div style={previewStyles.card}>
          <h3 style={{ marginTop: 0 }}>What to say during the demo</h3>
          <p style={{ margin: 0, lineHeight: 1.6 }}>
            The institution describes its needs in plain language, and the
            system converts that into a generated prompt, security flow, and a
            set of callable business actions. The agent does not just talk. It
            performs work in the background.
          </p>

          <button type="button" onClick={testAgent} style={previewStyles.button}>
            {status === "loading" ? "Generating..." : "Run agent test"}
          </button>

          {response ? <div style={previewStyles.response}>{response}</div> : null}
        </div>
      </div>
    </div>
  );
}
