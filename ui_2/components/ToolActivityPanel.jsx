import React, { useEffect, useRef, useState } from "react";

export default function ToolActivityPanel({ toolActivity }) {
  const ref = useRef(null);
  const [scrollLocked, setScrollLocked] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element || scrollLocked) {
      return;
    }
    element.scrollTop = element.scrollHeight;
  }, [toolActivity, scrollLocked]);

  const handleScroll = () => {
    const element = ref.current;
    if (!element) {
      return;
    }

    const nearBottom =
      element.scrollHeight - element.scrollTop - element.clientHeight < 48;
    setScrollLocked(!nearBottom);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: 0 }}>
      <div
        style={{
          height: 52,
          borderBottom: "1px solid #172436",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 18px"
        }}
      >
        <div>
          <div
            style={{
              color: "#60a5fa",
              fontSize: 11,
              textTransform: "uppercase",
              letterSpacing: 1.1
            }}
          >
            Tool activity
          </div>
          <div style={{ color: "#64748b", fontSize: 12 }}>
            Database checks and booking actions
          </div>
        </div>
        <div
          style={{
            padding: "6px 10px",
            borderRadius: 999,
            background: scrollLocked
              ? "rgba(245,158,11,0.12)"
              : "rgba(34,197,94,0.12)",
            color: scrollLocked ? "#f59e0b" : "#22c55e",
            fontSize: 11
          }}
        >
          {scrollLocked ? "Scroll lock" : "Auto-scroll"}
        </div>
      </div>
      <div
        ref={ref}
        onScroll={handleScroll}
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "16px 18px",
          display: "grid",
          gap: 10,
          minHeight: 0
        }}
      >
        {toolActivity.length === 0 ? (
          <EmptyState />
        ) : (
          toolActivity.map((item, index) => (
            <ToolEventCard key={`${item.kind}-${item.ts || index}-${index}`} item={item} />
          ))
        )}
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div
      style={{
        padding: 18,
        borderRadius: 18,
        background: "rgba(255,255,255,0.03)",
        border: "1px dashed rgba(255,255,255,0.08)",
        color: "#94a3b8",
        fontSize: 13,
        lineHeight: 1.6
      }}
    >
      Waiting for the agent to call a tool. Database lookups and bookings will appear here.
    </div>
  );
}

function ToolEventCard({ item }) {
  const isCall = item.kind === "call";
  const accent =
    isCall
      ? "#60a5fa"
      : item.success === true
        ? "#22c55e"
        : item.success === false
          ? "#ef4444"
          : "#94a3b8";
  const title = isCall ? "Tool call" : "Tool result";
  const payload = isCall ? item.arguments : item.result;

  return (
    <div
      style={{
        padding: "12px 14px",
        borderRadius: 16,
        background: "rgba(255,255,255,0.03)",
        border: `1px solid ${accent}33`
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 12,
          marginBottom: 8,
          fontSize: 10,
          fontFamily: '"IBM Plex Mono", monospace'
        }}
      >
        <span style={{ color: accent, textTransform: "uppercase" }}>{title}</span>
        <span style={{ color: "#64748b" }}>{item.ts || "--:--:--"}</span>
      </div>
      <div style={{ color: "#e5edf8", fontWeight: 700, marginBottom: 8 }}>
        {item.name}
      </div>
      <pre
        style={{
          margin: 0,
          padding: 12,
          borderRadius: 12,
          background: "rgba(2,6,23,0.55)",
          color: "#cbd5e1",
          fontSize: 11,
          lineHeight: 1.5,
          fontFamily: '"IBM Plex Mono", monospace',
          overflowX: "auto",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word"
        }}
      >
        {formatPayload(payload)}
      </pre>
    </div>
  );
}

function formatPayload(payload) {
  if (!payload || Object.keys(payload).length === 0) {
    return "{}";
  }

  try {
    return JSON.stringify(payload, null, 2);
  } catch {
    return String(payload);
  }
}
