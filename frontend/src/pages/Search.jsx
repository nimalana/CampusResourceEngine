import { useState, useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import CacheBadge from "../components/CacheBadge";

const TYPE_ICONS = {
  course: "📚",
  club: "🎯",
  research: "🔬",
  event: "📅",
  dining: "🍽️",
};

const TYPE_COLORS = {
  course: "#4B9CD3",
  club: "#9333ea",
  research: "#1a7a4a",
  event: "#c0622a",
  dining: "#d97706",
};

function ResultCard({ item }) {
  const { type, ...rest } = item;
  const title = rest.title || rest.name || rest.code || rest.id;
  const subtitle = rest.department || rest.category || rest.organizer || rest.type || "";
  const desc = rest.description || rest.desc || "";
  const tags = rest.tags || [];

  return (
    <div className="card">
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <span
          className="badge"
          style={{
            background: `${TYPE_COLORS[type] || "#64748b"}18`,
            color: TYPE_COLORS[type] || "#64748b",
          }}
        >
          {TYPE_ICONS[type] || "📄"} {type}
        </span>
        {rest.code && <span style={{ fontSize: "0.8rem", color: "var(--gray-400)" }}>{rest.code}</span>}
      </div>
      <div className="card-title">{title}</div>
      {subtitle && <div className="card-meta">{subtitle}</div>}
      {desc && <div className="card-desc" style={{ marginTop: 4 }}>{desc}</div>}
      <div className="tags">
        {tags.map((t) => (
          <span key={t} className="badge badge-tag">{t}</span>
        ))}
      </div>
    </div>
  );
}

export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get("q") || "");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const doSearch = (q) => {
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    setSearchParams({ q });
    api.search(q)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    const q = searchParams.get("q");
    if (q) {
      setQuery(q);
      doSearch(q);
    }
    inputRef.current?.focus();
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    doSearch(query);
  };

  const groupedResults = {};
  if (data?.results) {
    for (const item of data.results) {
      if (!groupedResults[item.type]) groupedResults[item.type] = [];
      groupedResults[item.type].push(item);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div className="page-title">🔍 Search</div>
        <div className="page-subtitle">Search across all UNC Chapel Hill resources</div>
      </div>

      <form onSubmit={handleSubmit} className="search-bar">
        <input
          ref={inputRef}
          type="text"
          className="search-input"
          placeholder="Search courses, clubs, research, events, dining…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="search-btn">Search</button>
      </form>

      {data && <CacheBadge hit={data.cache_hit} />}

      {loading && (
        <div className="loader"><div className="spinner" /><span>Searching…</span></div>
      )}

      {error && <div className="error-box">Error: {error}</div>}

      {data && !loading && (
        <div>
          <div style={{ marginBottom: 16, fontSize: "0.875rem", color: "var(--gray-600)" }}>
            {data.count} result{data.count !== 1 ? "s" : ""} for{" "}
            <strong>"{data.query}"</strong>
          </div>

          {data.count === 0 && (
            <div className="card" style={{ textAlign: "center", padding: 40, color: "var(--gray-400)" }}>
              No results found. Try different keywords.
            </div>
          )}

          {Object.entries(groupedResults).map(([type, items]) => (
            <div key={type} style={{ marginBottom: 28 }}>
              <div style={{
                fontSize: "0.8rem",
                fontWeight: 700,
                color: TYPE_COLORS[type] || "var(--gray-600)",
                textTransform: "uppercase",
                letterSpacing: "0.06em",
                marginBottom: 12,
              }}>
                {TYPE_ICONS[type]} {type} ({items.length})
              </div>
              <div className="card-grid">
                {items.map((item) => (
                  <ResultCard key={item.id} item={item} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {!data && !loading && (
        <div className="card" style={{ textAlign: "center", padding: 48, color: "var(--gray-400)" }}>
          <div style={{ fontSize: "2rem", marginBottom: 8 }}>🔍</div>
          Enter a search term above to explore UNC resources
        </div>
      )}
    </div>
  );
}
