import { useEffect, useState } from "react";
import { api } from "../api/client";
import CacheBadge from "../components/CacheBadge";

const CATEGORY_ICONS = {
  Festival: "🎵",
  Tradition: "🏈",
  Career: "💼",
  Academic: "🎓",
  Cultural: "🌍",
  Tech: "💻",
  Educational: "🔭",
  Wellness: "🧘",
};

export default function Events() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getEvents().then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loader"><div className="spinner" /><span>Loading events…</span></div>;
  if (error) return <div className="error-box">Error: {error}</div>;

  const events = data?.data || [];

  return (
    <div>
      <div className="page-header">
        <div className="page-title">📅 Campus Events</div>
        <div className="page-subtitle">UNC Chapel Hill upcoming events — {events.length} events</div>
      </div>

      <CacheBadge hit={data?.cache_hit} />

      <div className="card-grid">
        {events.map((ev) => (
          <div key={ev.id} className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className="badge badge-shard" style={{ background: "var(--blue-light)", color: "var(--navy)" }}>
                {CATEGORY_ICONS[ev.category] || "📌"} {ev.category}
              </span>
              {ev.rsvp_required && (
                <span className="badge" style={{ background: "var(--amber-bg)", color: "var(--amber)" }}>
                  RSVP Required
                </span>
              )}
            </div>
            <div className="card-title" style={{ marginTop: 10 }}>{ev.title}</div>
            <div className="card-meta">By {ev.organizer}</div>
            <div className="card-desc">{ev.description}</div>
            <div style={{ marginTop: 10, fontSize: "0.8rem", color: "var(--gray-600)", display: "flex", flexDirection: "column", gap: 4 }}>
              <span>📅 {ev.date} · {ev.time}</span>
              <span>📍 {ev.location}</span>
              {ev.capacity && <span>👥 Capacity: {ev.capacity.toLocaleString()}</span>}
            </div>
            <div className="tags">
              {(ev.tags || []).map((t) => (
                <span key={t} className="badge badge-tag">{t}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
