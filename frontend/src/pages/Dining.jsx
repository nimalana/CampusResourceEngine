import { useEffect, useState } from "react";
import { api } from "../api/client";
import CacheBadge from "../components/CacheBadge";

const TYPE_ICONS = {
  dining_hall: "🏛",
  cafe: "☕",
  restaurant: "🍽",
  food_truck: "🚚",
};

function StarRating({ rating }) {
  const full = Math.floor(rating);
  const half = rating - full >= 0.5;
  return (
    <span style={{ color: "#f59e0b", fontSize: "0.85rem" }}>
      {"★".repeat(full)}{half ? "½" : ""}
      <span style={{ color: "var(--gray-400)", marginLeft: 4 }}>{rating.toFixed(1)}</span>
    </span>
  );
}

export default function Dining() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getDining().then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loader"><div className="spinner" /><span>Loading dining…</span></div>;
  if (error) return <div className="error-box">Error: {error}</div>;

  const locations = data?.data || [];
  const sorted = [...locations].sort((a, b) => b.rating - a.rating);

  return (
    <div>
      <div className="page-header">
        <div className="page-title">🍽️ Dining</div>
        <div className="page-subtitle">UNC Chapel Hill dining halls, cafes & food trucks — {locations.length} locations</div>
      </div>

      <CacheBadge hit={data?.cache_hit} />

      <div className="card-grid">
        {sorted.map((loc) => (
          <div key={loc.id} className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className="badge badge-shard">
                {TYPE_ICONS[loc.type] || "🍴"} {loc.type.replace("_", " ")}
              </span>
              {loc.meal_plan_accepted && (
                <span className="badge" style={{ background: "var(--green-bg)", color: "var(--green)" }}>
                  Meal Plan
                </span>
              )}
            </div>
            <div className="card-title" style={{ marginTop: 10 }}>{loc.name}</div>
            <div style={{ marginTop: 4 }}>
              <StarRating rating={loc.rating} />
            </div>
            <div className="card-meta" style={{ marginTop: 4 }}>📍 {loc.location}</div>
            <div style={{ fontSize: "0.8rem", color: "var(--gray-600)", marginTop: 4 }}>
              🕐 {loc.hours}
            </div>
            <div style={{ marginTop: 10 }}>
              <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--gray-600)", marginBottom: 4 }}>
                MENU HIGHLIGHTS
              </div>
              <ul style={{ paddingLeft: 16, fontSize: "0.8rem", color: "var(--gray-600)" }}>
                {(loc.menu_highlights || []).map((h) => (
                  <li key={h}>{h}</li>
                ))}
              </ul>
            </div>
            <div className="tags" style={{ marginTop: 10 }}>
              {(loc.cuisine_types || []).map((c) => (
                <span key={c} className="badge badge-tag">{c}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
