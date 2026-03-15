/**
 * CacheBadge — shows HIT or MISS and optionally the serving shard.
 * Props:
 *   hit      {boolean}
 *   shard    {string|undefined}
 *   replicas {string[]|undefined}
 */
export default function CacheBadge({ hit, shard, replicas }) {
  return (
    <div className="cache-bar">
      <span className={`badge ${hit ? "badge-hit" : "badge-miss"}`}>
        {hit ? "✓ Cache HIT" : "✗ Cache MISS"}
      </span>
      {shard && (
        <span className="shard-info">
          Shard: <strong>{shard}</strong>
        </span>
      )}
      {replicas && replicas.length > 0 && (
        <span style={{ color: "var(--gray-400)", fontSize: "0.78rem" }}>
          Replicas: {replicas.join(", ")}
        </span>
      )}
      {!hit && (
        <span style={{ color: "var(--gray-400)", fontSize: "0.78rem", marginLeft: "auto" }}>
          (Served from shard, written to cache)
        </span>
      )}
    </div>
  );
}
