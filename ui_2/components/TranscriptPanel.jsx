import React, { useEffect, useRef } from "react";

function HighlightedText({ parts, text }) {
  if (!parts || parts.length === 0) {
    return text;
  }

  return (
    <>
      {parts.map((part, index) => (
        <span
          key={`${part.text}-${index}`}
          style={
            part.flagged
              ? {
                  color: "#fecaca",
                  textDecorationLine: "underline",
                  textDecorationColor: "#ef4444",
                  textDecorationThickness: "2px",
                  textUnderlineOffset: "4px"
                }
              : undefined
          }
        >
          {part.text}
        </span>
      ))}
    </>
  );
}

export default function TranscriptPanel({ transcript }) {
  const ref = useRef(null);

  useEffect(() => {
    if (ref.current) {
      ref.current.scrollTop = ref.current.scrollHeight;
    }
  }, [transcript]);

  return (
    <div style={{ flex: 0.42, display: "flex", flexDirection: "column", minWidth: 0, borderRight: "1px solid rgba(255,255,255,0.08)" }}>
      <div style={{ height: 52, borderBottom: "1px solid rgba(255,255,255,0.08)", display: "flex", alignItems: "center", padding: "0 18px" }}>
        <div>
          <div style={{ color: "#8bf5b2", fontSize: 11, textTransform: "uppercase", letterSpacing: 1.1 }}>Transcript</div>
          <div style={{ color: "rgba(228, 232, 241, 0.48)", fontSize: 12 }}>Live call transcription</div>
        </div>
      </div>
      <div ref={ref} style={{ flex: 1, overflowY: "auto", padding: "16px 18px", display: "flex", flexDirection: "column", gap: 10 }}>
        {transcript.map((item, index) => {
          const isAgent = item.speaker === "agent";
          const isFlagged = item.parts?.some((part) => part.flagged);

          return (
            <div key={`${item.ts || index}-${index}`} style={{ display: "flex", justifyContent: isAgent ? "flex-start" : "flex-end" }}>
              <div
                style={{
                  maxWidth: "82%",
                  padding: "10px 14px",
                  borderRadius: isAgent ? "16px 16px 16px 6px" : "16px 16px 6px 16px",
                  background: isAgent
                    ? "linear-gradient(180deg, rgba(22, 28, 38, 0.88), rgba(14, 18, 27, 0.82))"
                    : isFlagged
                      ? "rgba(127,29,29,0.14)"
                      : "rgba(117, 255, 163, 0.1)",
                  border: isAgent
                    ? "1px solid rgba(255,255,255,0.08)"
                    : isFlagged
                      ? "1px solid rgba(239,68,68,0.28)"
                      : "1px solid rgba(117, 255, 163, 0.18)",
                  color: "#f5f7fb",
                  lineHeight: 1.6,
                  position: "relative",
                  transition: "all 200ms ease",
                  boxShadow: "0 14px 30px rgba(0,0,0,0.18)"
                }}
              >
                {!isAgent && isFlagged ? (
                  <div
                    style={{
                      position: "absolute",
                      top: -9,
                      right: 10,
                      padding: "2px 7px",
                      borderRadius: 999,
                      background: "#3f0b0b",
                      color: "#f87171",
                      border: "1px solid rgba(239,68,68,0.2)",
                      fontSize: 9,
                      textTransform: "uppercase"
                    }}
                  >
                    Voice mismatch
                  </div>
                ) : null}
                <HighlightedText parts={item.parts} text={item.text} />
                <div style={{ marginTop: 8, fontSize: 10, color: "rgba(228, 232, 241, 0.48)", textTransform: "uppercase" }}>
                  {item.speaker} {item.ts ? `· ${item.ts}` : ""}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
