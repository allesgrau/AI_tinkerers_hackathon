import React, { useEffect, useMemo, useState } from "react";

const commandScenarios = {
  clinic: [
    {
      type: "agent",
      title: "Incoming call detected",
      message: "Patient identified as Anna Kowalska. Starting authentication flow.",
      time: "09:41"
    },
    {
      type: "tool",
      title: "collect-pesel()",
      message: "Captured PESEL and opened the auth session for this call.",
      time: "09:41"
    },
    {
      type: "tool",
      title: "send-sms()",
      message: "Sent a one-time code to the verified mobile number.",
      time: "09:42"
    },
    {
      type: "tool",
      title: "verify-sms()",
      message: "SMS code accepted. Waiting for voice verification status.",
      time: "09:42"
    },
    {
      type: "tool",
      title: "book_appointment()",
      message: "Booked cardiology appointment for March 29 at 09:30.",
      time: "09:43"
    }
  ],
  bank: [
    {
      type: "agent",
      title: "Incoming support request",
      message: "Caller reports a lost card. Launching secure banking workflow.",
      time: "11:08"
    },
    {
      type: "tool",
      title: "authenticate_customer()",
      message: "Customer identity challenge passed. Account session unlocked.",
      time: "11:08"
    },
    {
      type: "tool",
      title: "block_card()",
      message: "Card ending in 4821 blocked successfully.",
      time: "11:09"
    },
    {
      type: "tool",
      title: "create_case()",
      message: "Fraud review case opened and linked to customer profile.",
      time: "11:09"
    },
    {
      type: "agent",
      title: "Resolution sent",
      message: "Caller informed about the block and the next secure steps.",
      time: "11:10"
    }
  ],
  office: [
    {
      type: "agent",
      title: "Resident call connected",
      message: "Resident asks about a passport appointment and required documents.",
      time: "13:22"
    },
    {
      type: "tool",
      title: "verify_resident()",
      message: "Identity record matched and resident case context loaded.",
      time: "13:23"
    },
    {
      type: "tool",
      title: "check_case_status()",
      message: "Current passport application status fetched from the system.",
      time: "13:23"
    },
    {
      type: "tool",
      title: "book_office_visit()",
      message: "Resident booked for passport services on March 29 at 13:00.",
      time: "13:24"
    },
    {
      type: "agent",
      title: "Call summary prepared",
      message: "Next steps and required documents were summarized for the resident.",
      time: "13:24"
    }
  ]
};

const styles = {
  title: { marginTop: 0, marginBottom: 8, fontSize: 28 },
  lead: {
    marginTop: 0,
    marginBottom: 24,
    color: "rgba(228, 232, 241, 0.66)",
    lineHeight: 1.6
  },
  layout: {
    display: "grid",
    gridTemplateColumns: "1.2fr 0.8fr",
    gap: 18
  },
  card: {
    borderRadius: 24,
    padding: 22,
    background: "rgba(255,255,255,0.03)",
    border: "1px solid rgba(255,255,255,0.08)"
  },
  sectionLabel: {
    marginBottom: 12,
    color: "#8bf5b2",
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    fontSize: 12,
    fontWeight: 700
  },
  feed: {
    display: "grid",
    gap: 12,
    marginTop: 14
  },
  bubbleRow: (isTool) => ({
    display: "flex",
    justifyContent: isTool ? "flex-end" : "flex-start"
  }),
  bubble: (isTool) => ({
    maxWidth: "78%",
    padding: "14px 16px",
    borderRadius: isTool ? "18px 18px 6px 18px" : "18px 18px 18px 6px",
    background: isTool
      ? "linear-gradient(135deg, rgba(100,217,255,0.18), rgba(139,245,178,0.12))"
      : "rgba(255,255,255,0.045)",
    border: isTool
      ? "1px solid rgba(100,217,255,0.2)"
      : "1px solid rgba(255,255,255,0.07)",
    boxShadow: isTool ? "0 16px 30px rgba(0,0,0,0.22)" : "none"
  }),
  meta: {
    display: "flex",
    justifyContent: "space-between",
    gap: 14,
    marginBottom: 8,
    fontSize: 12,
    color: "rgba(228,232,241,0.52)"
  },
  voicePanel: {
    display: "grid",
    placeItems: "center",
    minHeight: 260
  },
  voiceOrb: {
    width: 188,
    height: 188,
    borderRadius: "50%",
    display: "grid",
    placeItems: "center",
    background:
      "radial-gradient(circle at 30% 30%, rgba(139,245,178,0.32), rgba(100,217,255,0.12) 35%, rgba(24,33,48,0.98) 70%)",
    border: "1px solid rgba(139,245,178,0.22)",
    boxShadow:
      "0 0 0 14px rgba(139,245,178,0.04), 0 0 0 32px rgba(100,217,255,0.03), 0 28px 60px rgba(0,0,0,0.38)"
  },
  bars: {
    display: "flex",
    alignItems: "flex-end",
    gap: 8,
    height: 64
  },
  bar: (height, delay) => ({
    width: 9,
    height,
    borderRadius: 999,
    background: "linear-gradient(180deg, #8bf5b2 0%, #64d9ff 100%)",
    animation: `voicePulse 1.1s ease-in-out ${delay}s infinite`
  }),
  statusPill: {
    display: "inline-flex",
    alignItems: "center",
    gap: 8,
    padding: "7px 12px",
    borderRadius: 999,
    background: "rgba(139,245,178,0.08)",
    border: "1px solid rgba(139,245,178,0.18)",
    color: "#bff7d1",
    fontSize: 13
  },
  quickGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
    gap: 14,
    marginTop: 18
  },
  quickCard: {
    padding: 16,
    borderRadius: 18,
    background: "rgba(255,255,255,0.03)",
    border: "1px solid rgba(255,255,255,0.08)",
    cursor: "pointer"
  }
};

export default function DashboardHome({ config, setActiveTab }) {
  const scenario = useMemo(
    () => commandScenarios[config.organizationType] || commandScenarios.clinic,
    [config.organizationType]
  );
  const [visibleCount, setVisibleCount] = useState(2);

  useEffect(() => {
    setVisibleCount(2);
  }, [config.organizationType]);

  useEffect(() => {
    if (visibleCount >= scenario.length) {
      return undefined;
    }

    const timeoutId = window.setTimeout(() => {
      setVisibleCount((count) => Math.min(count + 1, scenario.length));
    }, 1100);

    return () => window.clearTimeout(timeoutId);
  }, [visibleCount, scenario]);

  const visibleEvents = scenario.slice(0, visibleCount);

  return (
    <div>
      <h2 style={styles.title}>Operational dashboard</h2>
      <p style={styles.lead}>
        This is the live control surface for the agent. It shows how the voice
        flow progresses, which commands are being called, and how the assistant
        behaves in real time.
      </p>

      <div style={styles.layout}>
        <div style={styles.card}>
          <div style={styles.sectionLabel}>Live command stream</div>
          <div style={styles.statusPill}>
            <span
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: "#8bf5b2",
                boxShadow: "0 0 12px rgba(139,245,178,0.9)"
              }}
            />
            Agent session is active
          </div>

          <div style={styles.feed}>
            {visibleEvents.map((event, index) => {
              const isTool = event.type === "tool";
              return (
                <div key={`${event.title}-${index}`} style={styles.bubbleRow(isTool)}>
                  <div style={styles.bubble(isTool)}>
                    <div style={styles.meta}>
                      <span>{isTool ? "Tool call" : "Agent event"}</span>
                      <span>{event.time}</span>
                    </div>
                    <div style={{ fontWeight: 700, marginBottom: 8 }}>{event.title}</div>
                    <div style={{ lineHeight: 1.6, color: "rgba(235,240,248,0.86)" }}>
                      {event.message}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div style={styles.card}>
          <div style={styles.sectionLabel}>Voice activity</div>
          <div style={styles.voicePanel}>
            <div style={styles.voiceOrb}>
              <div style={styles.bars}>
                <span style={styles.bar(26, 0)} />
                <span style={styles.bar(44, 0.12)} />
                <span style={styles.bar(34, 0.24)} />
                <span style={styles.bar(58, 0.36)} />
                <span style={styles.bar(30, 0.48)} />
              </div>
            </div>
          </div>
          <div style={{ textAlign: "center", color: "rgba(228,232,241,0.64)" }}>
            Real-time voice indicator for the speaking agent
          </div>
        </div>
      </div>

      <div style={styles.quickGrid}>
        <div style={styles.quickCard} onClick={() => setActiveTab("behavior")}>
          <div style={styles.sectionLabel}>Agent setup</div>
          <div>Edit the institution brief and tailor the agent behavior.</div>
        </div>
        <div style={styles.quickCard} onClick={() => setActiveTab("appointments")}>
          <div style={styles.sectionLabel}>Records</div>
          <div>Manage the record dashboard and filter entries.</div>
        </div>
        <div style={styles.quickCard} onClick={() => setActiveTab("skills")}>
          <div style={styles.sectionLabel}>Skills</div>
          <div>Design agent capabilities without editing raw JSON.</div>
        </div>
      </div>
    </div>
  );
}
