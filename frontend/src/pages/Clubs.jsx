import { useEffect, useState } from "react";
import { api } from "../api/client";
import CacheBadge from "../components/CacheBadge";

const CATEGORY_COLORS = {
  "Governance": "#4B9CD3",
  "Academic / Tech": "#13294B",
  "Academic / Professional": "#1a7a4a",
  "Cultural": "#9333ea",
  "Programming": "#c0622a",
  "Advocacy": "#dc2626",
  "Academic": "#0891b2",
  "Pre-Professional": "#d97706",
  "Recreation": "#64748b",
};

export default function Clubs() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getClubs().then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loader"><div className="spinner" /><span>Loading clubs…</span></div>;
  if (error) return <div className="error-box">Error: {error}</div>;

  const clubs = data?.data || [];

  return (
    <div>
      <div className="page-header">
        <div className="page-title">🎯 Student Clubs</div>
        <div className="page-subtitle">UNC Chapel Hill student organizations — {clubs.length} clubs</div>
      </div>

      <CacheBadge hit={data?.cache_hit} />

      <div className="card-grid">
        {clubs.map((club) => (
          <div key={club.id} className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span
                className="badge"
                style={{
                  background: `${CATEGORY_COLORS[club.category] || "#64748b"}18`,
                  color: CATEGORY_COLORS[club.category] || "#64748b",
                }}
              >
                {club.category}
              </span>
              <span style={{ fontSize: "0.75rem", color: "var(--gray-400)" }}>
                {club.member_count} members · est. {club.founded}
              </span>
            </div>
            <div className="card-title" style={{ marginTop: 10 }}>{club.name}</div>
            <div className="card-meta">President: {club.president} · {club.email}</div>
            <div className="card-desc">{club.description}</div>
            <div style={{ marginTop: 8, fontSize: "0.8rem", color: "var(--gray-600)" }}>
              🕐 {club.meeting_schedule} &nbsp;|&nbsp; 📍 {club.location}
            </div>
            <div className="tags">
              {(club.tags || []).map((t) => (
                <span key={t} className="badge badge-tag">{t}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
