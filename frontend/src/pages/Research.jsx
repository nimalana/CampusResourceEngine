import { useEffect, useState } from "react";
import { api } from "../api/client";
import CacheBadge from "../components/CacheBadge";

export default function Research() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getResearch().then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loader"><div className="spinner" /><span>Loading research…</span></div>;
  if (error) return <div className="error-box">Error: {error}</div>;

  const projects = data?.data || [];

  return (
    <div>
      <div className="page-header">
        <div className="page-title">🔬 Research Projects</div>
        <div className="page-subtitle">UNC Chapel Hill research labs & active projects — {projects.length} projects</div>
      </div>

      <CacheBadge hit={data?.cache_hit} />

      <div className="card-grid">
        {projects.map((proj) => (
          <div key={proj.id} className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8 }}>
              <span
                className={`badge badge-status-${proj.status}`}
                style={{ textTransform: "capitalize" }}
              >
                {proj.status}
              </span>
              <span style={{ fontSize: "0.75rem", color: "var(--gray-400)", textAlign: "right" }}>
                {proj.funding_amount}
              </span>
            </div>
            <div className="card-title" style={{ marginTop: 10 }}>{proj.title}</div>
            <div className="card-meta">
              PI: {proj.pi} · {proj.department}
            </div>
            <div className="card-desc">{proj.description}</div>
            <div style={{ marginTop: 8, fontSize: "0.8rem", color: "var(--gray-600)" }}>
              🏛 {proj.lab}
            </div>
            <div style={{ marginTop: 4, fontSize: "0.8rem", color: "var(--gray-600)" }}>
              💰 {proj.funding_source}
            </div>
            <div className="tags">
              {(proj.tags || []).map((t) => (
                <span key={t} className="badge badge-tag">{t}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
