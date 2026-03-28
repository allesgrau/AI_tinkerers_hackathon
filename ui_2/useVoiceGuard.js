import { useEffect, useRef, useState } from "react";

const initialSteps = {
  pesel: "idle",
  otp: "idle",
  voice: "idle"
};

export function useVoiceGuard() {
  const socketRef = useRef(null);
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const [mode, setMode] = useState("live");
  const [activeSessionId, setActiveSessionId] = useState("");
  const [transcript, setTranscript] = useState([]);
  const [reasoning, setReasoning] = useState([]);
  const [steps, setSteps] = useState(initialSteps);
  const [riskIndicators, setRiskIndicators] = useState({
    voice_confidence: null,
    otp_timing: "unknown",
    attempt_history: 0,
    overall_risk: "unknown"
  });
  const [scenarios, setScenarios] = useState([]);
  const [currentScenario, setCurrentScenario] = useState("happy_path");
  const [sessionComplete, setSessionComplete] = useState(null);

  const resetDashboard = () => {
    setTranscript([]);
    setReasoning([]);
    setSteps(initialSteps);
    setRiskIndicators({
      voice_confidence: null,
      otp_timing: "unknown",
      attempt_history: 0,
      overall_risk: "unknown"
    });
    setSessionComplete(null);
  };

  const replayEvents = (events) => {
    const nextTranscript = [];
    const nextReasoning = [];
    const nextSteps = { ...initialSteps };
    let nextRiskIndicators = {
      voice_confidence: null,
      otp_timing: "unknown",
      attempt_history: 0,
      overall_risk: "unknown"
    };
    let nextSessionComplete = null;

    (events || []).forEach((event) => {
      if (event.type === "transcript.add") {
        nextTranscript.push(normalizeTranscriptEvent(event));
      }
      if (event.type === "reasoning.add") {
        nextReasoning.push(event);
      }
      if (event.type === "step.update" && event.step) {
        nextSteps[event.step] = normalizeStepStatus(event.status);
      }
      if (event.type === "risk.update") {
        nextRiskIndicators = normalizeRiskIndicators({
          ...nextRiskIndicators,
          ...event.indicators
        });
      }
      if (event.type === "session.complete") {
        nextSessionComplete = normalizeSessionComplete(event);
      }
    });

    setTranscript(nextTranscript);
    setReasoning(nextReasoning);
    setSteps(nextSteps);
    setRiskIndicators(nextRiskIndicators);
    setSessionComplete(nextSessionComplete);
  };

  const subscribeToSession = (sessionId, nextMode = "live") => {
    const socket = socketRef.current;
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      return;
    }

    setMode(nextMode);
    setActiveSessionId(sessionId);
    resetDashboard();
    socket.send(JSON.stringify({ action: "subscribe", session_id: sessionId }));
    socket.send(JSON.stringify({ action: "history", session_id: sessionId }));
  };

  useEffect(() => {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(`${protocol}://${window.location.hostname}:8000/ws`);
    socketRef.current = socket;

    socket.onopen = () => {
      setConnectionStatus("connected");
      socket.send(JSON.stringify({ action: "subscribe", session_id: "*" }));
    };

    socket.onclose = () => {
      setConnectionStatus("disconnected");
    };

    socket.onerror = () => {
      setConnectionStatus("error");
    };

    socket.onmessage = (messageEvent) => {
      const payload = JSON.parse(messageEvent.data);

      switch (payload.type) {
        case "connected":
          setConnectionStatus("connected");
          break;
        case "subscribed":
          setConnectionStatus("connected");
          if (payload.session_id) {
            setActiveSessionId(payload.session_id);
          }
          break;
        case "scenario.list":
          setScenarios(payload.items || []);
          break;
        case "history":
          if (payload.session_id) {
            setActiveSessionId(payload.session_id);
          }
          replayEvents(payload.events || []);
          break;
        case "session.reset":
          resetDashboard();
          setMode("demo");
          setCurrentScenario(payload.scenario || "happy_path");
          break;
        case "transcript.add":
          setTranscript((items) => [...items, normalizeTranscriptEvent(payload)]);
          break;
        case "reasoning.add":
          setReasoning((items) => [...items, payload]);
          break;
        case "step.update":
          setSteps((prev) => ({
            ...prev,
            [payload.step]: normalizeStepStatus(payload.status)
          }));
          break;
        case "risk.update":
          setRiskIndicators((prev) =>
            normalizeRiskIndicators({ ...prev, ...payload.indicators })
          );
          break;
        case "session.complete":
          setSessionComplete(normalizeSessionComplete(payload));
          break;
        default:
          break;
      }
    };

    return () => {
      socket.close();
    };
  }, []);

  const startScenario = (scenario) => {
    setCurrentScenario(scenario);
    setMode("demo");
    setActiveSessionId(`demo-${scenario}`);
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: "scenario.start", scenario }));
    }
  };

  const subscribeToLiveSession = (sessionId) => {
    if (!sessionId) {
      return;
    }
    subscribeToSession(sessionId, "live");
  };

  return {
    mode,
    activeSessionId,
    connectionStatus,
    transcript,
    reasoning,
    steps,
    riskIndicators,
    scenarios,
    currentScenario,
    sessionComplete,
    setSessionComplete,
    startScenario,
    subscribeToLiveSession
  };
}

function normalizeStepStatus(status) {
  if (!status) {
    return "idle";
  }

  if (status === "in_progress") {
    return "in_progress";
  }

  return status;
}

function normalizeTranscriptEvent(event) {
  if (event.parts || !event.text) {
    return event;
  }

  return {
    ...event,
    parts: [{ text: event.text, flagged: false }]
  };
}

function normalizeRiskIndicators(indicators) {
  return {
    ...indicators,
    voice_confidence:
      typeof indicators.voice_confidence === "number"
        ? indicators.voice_confidence
        : indicators.voice_confidence === "green"
          ? 0.85
          : indicators.voice_confidence === "yellow"
            ? 0.76
            : indicators.voice_confidence === "red"
              ? 0.41
              : indicators.voice_score ?? null,
    otp_timing:
      typeof indicators.otp_timing === "string"
        ? indicators.otp_timing
        : indicators.otp_status === "verified"
          ? "normal"
          : indicators.otp_status === "locked"
            ? "suspicious"
            : indicators.otp_status || "unknown",
    attempt_history:
      indicators.attempt_history ?? indicators.otp_attempts ?? 0,
    overall_risk:
      indicators.overall_risk ??
      indicators.threat_level ??
      (indicators.voice_confidence === "red" ? "high" : "unknown")
  };
}

function normalizeSessionComplete(payload) {
  if (payload.result) {
    return payload;
  }

  return {
    ...payload,
    result: payload.rejected ? "rejected" : payload.token ? "verified" : "review"
  };
}
