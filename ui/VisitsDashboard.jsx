import React, { useMemo } from "react";

const styles = {
  title: { marginTop: 0, marginBottom: 8, fontSize: 28 },
  lead: {
    marginTop: 0,
    marginBottom: 24,
    color: "rgba(228, 232, 241, 0.66)",
    lineHeight: 1.6
  },
  filterRow: {
    display: "grid",
    gridTemplateColumns: "1fr 220px 220px",
    gap: 12,
    marginBottom: 20
  },
  input: {
    width: "100%",
    padding: "13px 15px",
    borderRadius: 14,
    border: "1px solid rgba(255,255,255,0.08)",
    background: "rgba(255,255,255,0.03)",
    color: "#f5f7fb"
  },
  table: {
    borderRadius: 22,
    background: "rgba(255,255,255,0.03)",
    border: "1px solid rgba(255,255,255,0.08)",
    overflow: "hidden"
  },
  head: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr 1fr 110px 140px",
    gap: 12,
    padding: 16,
    borderBottom: "1px solid rgba(255,255,255,0.08)",
    color: "#8bf5b2",
    fontWeight: 700
  },
  row: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr 1fr 110px 140px",
    gap: 12,
    padding: 16,
    borderBottom: "1px solid rgba(255,255,255,0.06)"
  }
};

export default function VisitsDashboard({ config, filters, setFilters }) {
  const specialties = useMemo(
    () => [...new Set(config.appointments.map((item) => item.specialty))],
    [config.appointments]
  );

  const filteredAppointments = useMemo(() => {
    return config.appointments.filter((appointment) => {
      const matchesQuery =
        filters.query === "" ||
        [appointment.patient, appointment.doctor, appointment.id]
          .join(" ")
          .toLowerCase()
          .includes(filters.query.toLowerCase());
      const matchesSpecialty =
        filters.specialty === "all" || appointment.specialty === filters.specialty;
      const matchesStatus =
        filters.status === "all" || appointment.status === filters.status;
      return matchesQuery && matchesSpecialty && matchesStatus;
    });
  }, [config.appointments, filters]);

  return (
    <div>
      <h2 style={styles.title}>Phase 2: record dashboard with filtering</h2>
      <p style={styles.lead}>
        This screen prepares the admin panel for backend integration. It
        already includes search, filters, and a structured records table.
      </p>

      <div style={styles.filterRow}>
        <input
          style={styles.input}
          placeholder="Search by name, owner, or record ID..."
          value={filters.query}
          onChange={(e) => setFilters((prev) => ({ ...prev, query: e.target.value }))}
        />

        <select
          style={styles.input}
          value={filters.specialty}
          onChange={(e) =>
            setFilters((prev) => ({ ...prev, specialty: e.target.value }))
          }
        >
          <option value="all">All categories</option>
          {specialties.map((specialty) => (
            <option key={specialty} value={specialty}>
              {specialty}
            </option>
          ))}
        </select>

        <select
          style={styles.input}
          value={filters.status}
          onChange={(e) => setFilters((prev) => ({ ...prev, status: e.target.value }))}
        >
          <option value="all">All statuses</option>
          <option value="Confirmed">Confirmed</option>
          <option value="Pending">Pending</option>
          <option value="Rescheduled">Rescheduled</option>
        </select>
      </div>

      <div style={styles.table}>
        <div style={styles.head}>
          <div>Customer / resident</div>
          <div>Owner</div>
          <div>Category</div>
          <div>Time</div>
          <div>Status</div>
        </div>

        {filteredAppointments.map((appointment) => (
          <div key={appointment.id} style={styles.row}>
            <div>
              <div style={{ fontWeight: 700 }}>{appointment.patient}</div>
              <div style={{ color: "rgba(228,232,241,0.52)" }}>{appointment.id}</div>
            </div>
            <div>{appointment.doctor}</div>
            <div>{appointment.specialty}</div>
            <div>
              {appointment.date}
              <br />
              {appointment.time}
            </div>
            <div>{appointment.status}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
