import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";

const NAV_CARDS = [
  { to: "/courses", icon: "📚", label: "Courses", desc: "Explore UNC class catalog" },
  { to: "/clubs", icon: "🎯", label: "Clubs", desc: "Student organizations & groups" },
  { to: "/research", icon: "🔬", label: "Research", desc: "Labs & ongoing projects" },
  { to: "/events", icon: "📅", label: "Events", desc: "Campus events & activities" },
  { to: "/dining", icon: "🍽️", label: "Dining", desc: "Dining halls & cafes" },
  { to: "/search", icon: "🔍", label: "Search", desc: "Search all resources" },
  { to: "/system", icon: "⚙️", label: "System", desc: "Hash ring & cache stats" },
];

export default function Home() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    api.getHealth().then(setHealth).catch(() => null);
  }, []);

  return (
    <div>
      <div className="hero">
        <div className="hero-title">
          <span>UNC</span> Resource Engine
        </div>
        <p className="hero-subtitle">
          A distributed campus resource platform for the University of North Carolina at Chapel Hill —
          powered by consistent hashing, Redis cache-aside, and 2-replica writes across 4 shards.
        </p>
        <div className="hero-chips">
          <span className="hero-chip">4 Shards</span>
          <span className="hero-chip">150 Virtual Nodes / Shard</span>
          <span className="hero-chip">600 Total VNodes</span>
          <span className="hero-chip">2-Replica Writes</span>
          <span className="hero-chip">Read Repair</span>
          <span className="hero-chip">Redis Cache-Aside</span>
        </div>
      </div>

      {health && (
        <div className="cache-bar" style={{ marginBottom: 28 }}>
          <span
            className="badge"
            style={{
              background: health.status === "ok" ? "var(--green-bg)" : "var(--red-bg)",
              color: health.status === "ok" ? "var(--green)" : "var(--red)",
            }}
          >
            {health.status === "ok" ? "✓ API Online" : "✗ API Offline"}
          </span>
          <span className="shard-info">
            Redis: {health.redis ? "connected" : "unavailable (memory fallback)"}
          </span>
        </div>
      )}

      <div className="page-header">
        <div className="page-title">Browse Resources</div>
        <div className="page-subtitle">Select a category to explore UNC Chapel Hill campus data</div>
      </div>

      <div className="nav-card-grid">
        {NAV_CARDS.map(({ to, icon, label, desc }) => (
          <Link key={to} to={to} className="nav-card">
            <span className="nav-card-icon">{icon}</span>
            <span className="nav-card-label">{label}</span>
            <span className="nav-card-desc">{desc}</span>
          </Link>
        ))}
      </div>

      <div style={{ marginTop: 40, padding: "20px 0", borderTop: "1px solid var(--gray-200)" }}>
        <p style={{ fontSize: "0.8rem", color: "var(--gray-400)", textAlign: "center" }}>
          University of North Carolina at Chapel Hill — Est. 1789 · Chapel Hill, NC 27514
        </p>
      </div>
    </div>
  );
}
