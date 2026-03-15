import { useEffect, useState } from "react";
import { api } from "../api/client";
import CacheBadge from "../components/CacheBadge";

export default function Courses() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    api.getCourses()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loader"><div className="spinner" /><span>Loading courses…</span></div>;
  if (error) return <div className="error-box">Error: {error}</div>;

  const courses = data?.data || [];

  return (
    <div>
      <div className="page-header">
        <div className="page-title">📚 Courses</div>
        <div className="page-subtitle">UNC Chapel Hill course catalog — {courses.length} courses loaded</div>
      </div>

      <CacheBadge hit={data?.cache_hit} />

      {data?.shard_distribution && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="card-title" style={{ marginBottom: 12 }}>Shard Distribution</div>
          <div className="shard-bars">
            {Object.entries(data.shard_distribution).map(([shard, count]) => {
              const max = Math.max(...Object.values(data.shard_distribution));
              return (
                <div key={shard} className="shard-row">
                  <span className="shard-name">{shard}</span>
                  <div className="shard-track">
                    <div className="shard-fill" style={{ width: `${(count / max) * 100}%` }} />
                  </div>
                  <span className="shard-count">{count}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="card-grid">
        {courses.map((course) => (
          <div key={course.id} className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <span className="badge badge-shard">{course.code}</span>
              <span style={{ fontSize: "0.75rem", color: "var(--gray-400)" }}>
                {course.credits} cr · {course.seats_available}/{course.total_seats} seats
              </span>
            </div>
            <div className="card-title" style={{ marginTop: 10 }}>{course.title}</div>
            <div className="card-meta">{course.department} · {course.instructor}</div>
            <div className="card-desc">{course.description}</div>
            <div style={{ marginTop: 8, fontSize: "0.8rem", color: "var(--gray-600)" }}>
              🕐 {course.schedule} &nbsp;|&nbsp; 📍 {course.location}
            </div>
            <div className="tags">
              {(course.tags || []).map((t) => (
                <span key={t} className="badge badge-tag">{t}</span>
              ))}
              {course.seats_available === 0 && (
                <span className="badge" style={{ background: "var(--red-bg)", color: "var(--red)" }}>Full</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
