import React, { useEffect, useRef, useState } from "react";

export default function ReasoningPanel({ reasoning }) {
  const ref = useRef(null);
  const [scrollLocked, setScrollLocked] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element || scrollLocked) {
      return;
    }
    element.scrollTop = element.scrollHeight;
  }, [reasoning, scrollLocked]);

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
    <div style={{ flex: 0.58, display: "flex", flexDirection: "column", minWidth: 0 }}>
      <div style={{ height: 52, borderBottom: "1px solid rgba(255,255,255,0.08)", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 18px" }}>
        <div>
          <div style={{ color: "#64d9ff", fontSize: 11, textTransform: "uppercase", letterSpacing: 1.1 }}>Reasoning panel</div>
          <div style={{ color: "rgba(228, 232, 241, 0.48)", fontSize: 12 }}>Agent notes, transport logs, and backend events</div>
        </div>
        <div
          style={{
            padding: "6px 10px",
            borderRadius: 999,
            background: scrollLocked ? "rgba(245,158,11,0.12)" : "rgba(34,197,94,0.12)",
            color: scrollLocked ? "#f59e0b" : "#22c55e",
            fontSize: 11
          }}
        >
          {scrollLocked ? "Scroll lock" : "Auto-scroll"}
        </div>
      </div>
      <div ref={ref} onScroll={handleScroll} style={{ flex: 1, overflowY: "auto", padding: "16px 18px", display: "grid", gap: 10 }}>
        {reasoning.map((item, index) => (
          <div
            key={`${item.ts || index}-${index}`}
            style={{
              padding: "12px 14px",
              borderRadius: 18,
              background: "linear-gradient(180deg, rgba(19, 29, 39, 0.96), rgba(12, 18, 27, 0.92))",
              border: `1px solid ${
                item.level === "error"
                  ? "rgba(239,68,68,0.2)"
                  : item.level === "warn"
                    ? "rgba(245,158,11,0.2)"
                    : "rgba(255,255,255,0.06)"
              }`,
              transition: "all 180ms ease",
              boxShadow: "0 16px 36px rgba(0,0,0,0.18)"
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12, marginBottom: 8, fontSize: 10, fontFamily: '"IBM Plex Mono", monospace' }}>
              <span
                style={{
                  color:
                    item.level === "error"
                      ? "#ef4444"
                      : item.level === "warn"
                        ? "#f59e0b"
                        : "#60a5fa",
                  textTransform: "uppercase"
                }}
              >
                {item.level}
              </span>
              <span style={{ color: "rgba(228, 232, 241, 0.48)" }}>{item.ts}</span>
            </div>
            <div style={{ color: "#f5f7fb", lineHeight: 1.6, fontFamily: '"IBM Plex Mono", monospace', fontSize: 12 }}>
              {item.text}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
