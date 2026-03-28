export const industryPresets = {
  clinic: {
    organizationName: "Aurora Medical Center",
    organizationType: "clinic",
    language: "en",
    institutionDescription:
      "A private medical provider that wants to automate incoming calls, identity verification, appointment scheduling, rescheduling, and escalation to a human operator when needed.",
    goal:
      "Book and reschedule appointments, answer simple patient questions, and route more complex issues to a staff member.",
    prompt:
      "The agent should sound calm, clear, and reassuring. It must verify identity first, then help the caller complete the task using simple non-technical language.",
    tone: "Warm and professional",
    actions: [
      {
        name: "Book appointment",
        endpoint: "/api/appointments/book",
        method: "POST",
        description: "Books an appointment after successful identity verification."
      },
      {
        name: "Check available slots",
        endpoint: "/api/appointments/slots",
        method: "GET",
        description: "Returns the nearest available appointment slots."
      }
    ],
    skills: [
      {
        id: "identity-check",
        name: "Identity verification",
        enabled: true,
        category: "Auth",
        description: "PESEL, SMS code, and voice verification before sensitive actions."
      },
      {
        id: "booking",
        name: "Appointment booking",
        enabled: true,
        category: "Appointments",
        description: "Searches availability and books or reschedules visits."
      },
      {
        id: "handoff",
        name: "Human handoff",
        enabled: true,
        category: "Ops",
        description: "Transfers the call to staff when the case is complex."
      }
    ],
    calls: [
      {
        id: "CALL-7841",
        caller: "Anna Kowalska",
        topic: "Appointment booking",
        status: "Completed",
        duration: "03:24",
        auth: "PESEL + SMS + Voice"
      },
      {
        id: "CALL-7842",
        caller: "Private number",
        topic: "Lab results question",
        status: "In progress",
        duration: "01:18",
        auth: "PESEL + SMS"
      },
      {
        id: "CALL-7843",
        caller: "Peter Zielinski",
        topic: "Reschedule request",
        status: "Needs follow-up",
        duration: "04:02",
        auth: "PESEL + Voice"
      }
    ],
    appointments: [
      {
        id: "APT-1042",
        patient: "Anna Kowalska",
        doctor: "Dr. Novak",
        specialty: "Cardiology",
        date: "2026-03-29",
        time: "09:30",
        status: "Confirmed"
      },
      {
        id: "APT-1043",
        patient: "Peter Zielinski",
        doctor: "Dr. Wozniak",
        specialty: "Dermatology",
        date: "2026-03-29",
        time: "12:10",
        status: "Pending"
      },
      {
        id: "APT-1044",
        patient: "Maria Adams",
        doctor: "Dr. Lewandowska",
        specialty: "Internal Medicine",
        date: "2026-03-30",
        time: "08:45",
        status: "Rescheduled"
      }
    ]
  },
  bank: {
    organizationName: "NorthRiver Bank",
    organizationType: "bank",
    language: "en",
    institutionDescription:
      "A retail bank that wants to automate customer authentication, card support, account access requests, transaction guidance, and secure escalation for sensitive cases.",
    goal:
      "Authenticate customers, handle card and account support, guide routine banking requests, and escalate blocked or high-risk operations to a live advisor.",
    prompt:
      "The agent should sound trustworthy, concise, and security-first. It must explain next steps clearly, avoid jargon, and never disclose sensitive internal details.",
    tone: "Confident and professional",
    actions: [
      {
        name: "Block card",
        endpoint: "/api/cards/block",
        method: "POST",
        description: "Blocks a debit or credit card after successful authentication."
      },
      {
        name: "Check account status",
        endpoint: "/api/accounts/status",
        method: "GET",
        description: "Returns account status, issue flags, and support eligibility."
      }
    ],
    skills: [
      {
        id: "identity-check",
        name: "Secure authentication",
        enabled: true,
        category: "Security",
        description: "Multi-step customer verification before account operations."
      },
      {
        id: "card-support",
        name: "Card operations",
        enabled: true,
        category: "Banking",
        description: "Handles card blocking, issue reporting, and urgent support."
      },
      {
        id: "fraud-handoff",
        name: "Fraud escalation",
        enabled: true,
        category: "Risk",
        description: "Routes suspicious or high-risk cases to a specialist."
      }
    ],
    calls: [
      {
        id: "CALL-9101",
        caller: "Emily Turner",
        topic: "Lost card",
        status: "Completed",
        duration: "02:54",
        auth: "SMS + Voice"
      },
      {
        id: "CALL-9102",
        caller: "Michael Reed",
        topic: "Account locked",
        status: "In progress",
        duration: "02:11",
        auth: "SMS + Voice"
      },
      {
        id: "CALL-9103",
        caller: "Unknown number",
        topic: "Wire transfer issue",
        status: "Escalated",
        duration: "05:08",
        auth: "SMS"
      }
    ],
    appointments: [
      {
        id: "CASE-301",
        patient: "Emily Turner",
        doctor: "Advisor Chen",
        specialty: "Cards",
        date: "2026-03-29",
        time: "10:00",
        status: "Confirmed"
      },
      {
        id: "CASE-302",
        patient: "Michael Reed",
        doctor: "Advisor Moore",
        specialty: "Accounts",
        date: "2026-03-29",
        time: "11:40",
        status: "Pending"
      },
      {
        id: "CASE-303",
        patient: "Laura King",
        doctor: "Fraud Desk",
        specialty: "Fraud",
        date: "2026-03-30",
        time: "14:15",
        status: "Rescheduled"
      }
    ]
  },
  office: {
    organizationName: "City Services Office",
    organizationType: "office",
    language: "en",
    institutionDescription:
      "A local public office that wants to automate resident authentication, appointment scheduling, case status questions, and document guidance for non-technical users.",
    goal:
      "Guide residents through office services, explain required documents, help them check case status, and book appointments when needed.",
    prompt:
      "The agent should sound formal, patient, and easy to understand. It should explain procedures step by step and escalate unclear administrative cases to a clerk.",
    tone: "Clear and formal",
    actions: [
      {
        name: "Book office visit",
        endpoint: "/api/office-visits/book",
        method: "POST",
        description: "Books a resident visit for a selected office service."
      },
      {
        name: "Check case status",
        endpoint: "/api/cases/status",
        method: "GET",
        description: "Returns the current status of an administrative case."
      }
    ],
    skills: [
      {
        id: "identity-check",
        name: "Resident verification",
        enabled: true,
        category: "Auth",
        description: "Validates resident identity before sharing case details."
      },
      {
        id: "case-guidance",
        name: "Case guidance",
        enabled: true,
        category: "Public services",
        description: "Explains procedures, required documents, and next steps."
      },
      {
        id: "clerk-handoff",
        name: "Clerk escalation",
        enabled: true,
        category: "Ops",
        description: "Escalates complex or exceptional office cases to staff."
      }
    ],
    calls: [
      {
        id: "CALL-6201",
        caller: "Sophie Martin",
        topic: "Passport appointment",
        status: "Completed",
        duration: "04:12",
        auth: "PESEL + SMS"
      },
      {
        id: "CALL-6202",
        caller: "Daniel Walker",
        topic: "Case status request",
        status: "In progress",
        duration: "02:43",
        auth: "PESEL + SMS + Voice"
      },
      {
        id: "CALL-6203",
        caller: "Emma Lewis",
        topic: "Required documents",
        status: "Needs follow-up",
        duration: "03:36",
        auth: "PESEL"
      }
    ],
    appointments: [
      {
        id: "OFF-501",
        patient: "Sophie Martin",
        doctor: "Desk A",
        specialty: "Passport services",
        date: "2026-03-29",
        time: "13:00",
        status: "Confirmed"
      },
      {
        id: "OFF-502",
        patient: "Daniel Walker",
        doctor: "Desk C",
        specialty: "Case support",
        date: "2026-03-30",
        time: "09:20",
        status: "Pending"
      },
      {
        id: "OFF-503",
        patient: "Emma Lewis",
        doctor: "Front desk",
        specialty: "Document intake",
        date: "2026-03-30",
        time: "15:10",
        status: "Rescheduled"
      }
    ]
  }
};

export function getIndustryPreset(industry) {
  return industryPresets[industry] || industryPresets.clinic;
}
