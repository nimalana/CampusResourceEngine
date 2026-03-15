import { useEffect, useState, useCallback } from "react";
import { api } from "../api/client";
import HashRingViz from "../components/HashRingViz";

function StatCard({ value, label, color }) {
  return (
    <div className="stat-card">
      <div className="stat-value" style={color ? { color } : {}}>{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

function ShardTable({ distribution, recordCounts }) {
  const entries = Object.entries(distribution || {});
  const totalVnodes = entries.reduce((s, [, v]) => s + v.count, 0);
  return (
    <div className="table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            <th>Shard</th>
            <th>Virtual Nodes</th>
            <th>Ring %</th>
            <th>Records</th>
          </tr>
        </thead>
        <tbody>
          {entries.map(([shard, info]) => (
            <tr key={shard}>
              <td><span className="badge badge-shard">{shard}</span></td>
              <td>{info.count}</td>
              <td>{info.percentage}%</td>
              <td>{recordCounts?.[shard] ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function CacheStatsPanel({ cache }) {
  if (!cache) return null;
  const hitPct = cache.total_requests > 0
    ? ((cache.hits / cache.total_requests) * 100).toFixed(1)
    : "0.0";
  const barWidth = parseFloat(hitPct);
  return (
    <div className="card">
      <div className="card-title" style={{ marginBottom: 16 }}>Cache Performance</div>
      <div className="stat-grid" style={{ marginBottom: 0 }}>
        <StatCard value={cache.hits} label="Cache Hits" color="var(--green)" />
        <StatCard value={cache.misses} label="Cache Misses" color="var(--red)" />
        <StatCard value={`${hitPct}%`} label="Hit Rate" color="var(--carolina-blue)" />
        <StatCard value={cache.uptime_seconds + "s"} label="Uptime" />
      </div>
      <div style={{ marginTop: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "var(--gray-400)", marginBottom: 4 }}>
          <span>Hit rate</span>
          <span>{hitPct}%</span>
        </div>
        <div className="shard-track" style={{ height: 12 }}>
          <div className="shard-fill" style={{ width: `${barWidth}%`, background: "var(--carolina-blue)" }} />
        </div>
      </div>
      <div style={{ marginTop: 12, fontSize: "0.8rem", color: "var(--gray-600)", display: "flex", gap: 12 }}>
        <span>
          Redis:{" "}
          <span style={{ color: cache.redis_available ? "var(--green)" : "var(--amber)", fontWeight: 600 }}>
            {cache.redis_available ? "Connected" : "Unavailable (memory fallback)"}
          </span>
        </span>
        <span>Total requests: <strong>{cache.total_requests}</strong></span>
      </div>
    </div>
  );
}

export default function SystemDashboard() {
  const [stats, setStats] = useState(null);
  const [ring, setRing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);

  const load = useCallback(() => {
    setLoading(true);
    Promise.all([api.getStats(), api.getRing()])
      .then(([s, r]) => {
        setStats(s);
        setRing(r);
        setLastRefresh(new Date().toLocaleTimeString());
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [load]);

  if (loading && !stats) return <div className="loader"><div className="spinner" /><span>Loading system stats…</span></div>;
  if (error) return <div className="error-box">Error: {error}</div>;

  return (
    <div>
      <div className="page-header">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <div className="page-title">⚙️ System Dashboard</div>
            <div className="page-subtitle">Live hash ring, cache metrics, and shard distribution</div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
            <button
              onClick={load}
              className="search-btn"
              style={{ padding: "6px 14px", fontSize: "0.8rem" }}
            >
              Refresh
            </button>
            {lastRefresh && (
              <span style={{ fontSize: "0.72rem", color: "var(--gray-400)" }}>
                Last refresh: {lastRefresh}
              </span>
            )}
            <span style={{ fontSize: "0.72rem", color: "var(--gray-400)" }}>
              Auto-refreshes every 5s
            </span>
          </div>
        </div>
      </div>

      {/* Top stats row */}
      <div className="stat-grid">
        <StatCard value={stats?.ring?.total_virtual_nodes ?? "—"} label="Total VNodes" color="var(--carolina-blue)" />
        <StatCard value={stats?.ring?.nodes?.length ?? "—"} label="Shards" />
        <StatCard value={stats?.ring?.virtual_nodes_per_node ?? "—"} label="VNodes / Shard" />
        <StatCard value={stats?.shards?.total_records ?? "—"} label="Total Records" />
        <StatCard value={stats?.replication?.factor ?? "—"} label="Replication Factor" />
        <StatCard
          value={stats?.cache?.redis_available ? "Redis" : "Memory"}
          label="Cache Backend"
          color={stats?.cache?.redis_available ? "var(--green)" : "var(--amber)"}
        />
      </div>

      {/* Hash ring visualization */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 20 }}>
        <div>
          <div style={{ fontWeight: 600, color: "var(--navy)", marginBottom: 12 }}>
            Hash Ring — Consistent Hashing Visualization
          </div>
          <HashRingViz ringData={ring} size={400} />
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="card">
            <div className="card-title" style={{ marginBottom: 12 }}>Shard Details</div>
            <ShardTable
              distribution={ring?.node_distribution}
              recordCounts={ring?.shard_record_counts}
            />
          </div>

          <div className="card">
            <div className="card-title" style={{ marginBottom: 12 }}>Architecture</div>
            <div style={{ fontSize: "0.85rem", color: "var(--gray-600)", display: "flex", flexDirection: "column", gap: 8 }}>
              <div>
                <strong>Hash function:</strong> MD5 → 32-bit unsigned int
              </div>
              <div>
                <strong>Virtual nodes:</strong> 150 per physical shard
              </div>
              <div>
                <strong>Replication:</strong> 2-replica write (primary + 1 replica)
              </div>
              <div>
                <strong>Read repair:</strong> Active — stale primaries updated from fresher replicas
              </div>
              <div>
                <strong>Cache pattern:</strong> Cache-aside (lazy population)
              </div>
              <div>
                <strong>Cache TTL:</strong> 300s (search: 60s)
              </div>
              <div>
                <strong>Fallback:</strong> In-memory cache when Redis unavailable
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Cache stats */}
      <CacheStatsPanel cache={stats?.cache} />

      {/* Ring state preview table */}
      {stats?.ring?.vnodes && (
        <div className="card" style={{ marginTop: 20 }}>
          <div className="card-title" style={{ marginBottom: 12 }}>
            Ring State Preview (first 20 virtual nodes)
          </div>
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Hash Position</th>
                  <th>Angle (°)</th>
                  <th>Assigned Shard</th>
                </tr>
              </thead>
              <tbody>
                {stats.ring.vnodes.map((vn, i) => (
                  <tr key={i}>
                    <td>{i + 1}</td>
                    <td style={{ fontFamily: "monospace", fontSize: "0.8rem" }}>
                      {vn.hash?.toLocaleString()}
                    </td>
                    <td>{vn.angle_deg}°</td>
                    <td>
                      <span className="badge badge-shard">{vn.position}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
