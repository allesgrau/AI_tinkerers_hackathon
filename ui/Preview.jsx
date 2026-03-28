import React, { useState } from "react";

export default function Preview({ config }) {
  const [response, setResponse] = useState("");

  const testAgent = async () => {
    const res = await fetch("/api/test-agent", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(config)
    });

    const data = await res.json();
    setResponse(data.response);
  };

  return (
    <div>
      <h2>Preview</h2>

      <button onClick={testAgent}>Test Agent</button>

      <pre style={{ marginTop: 20 }}>{response}</pre>
    </div>
  );
}