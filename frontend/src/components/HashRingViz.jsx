import { useEffect, useRef } from "react";

const SHARD_COLORS = {
  "shard-1": "#4B9CD3",   // Carolina Blue
  "shard-2": "#13294B",   // Navy
  "shard-3": "#1a7a4a",   // Dark green
  "shard-4": "#c0622a",   // Dark orange
};

const DEFAULT_COLORS = ["#4B9CD3", "#13294B", "#1a7a4a", "#c0622a"];

function getColor(node, index) {
  return SHARD_COLORS[node] || DEFAULT_COLORS[index % DEFAULT_COLORS.length];
}

/**
 * HashRingViz — SVG visualization of the consistent hash ring.
 * Props:
 *   ringData  { nodes, vnodes: [{hash, position, angle_deg}], node_distribution }
 *   size      number (default 420)
 */
export default function HashRingViz({ ringData, size = 420 }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!ringData || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    const S = size;
    canvas.width = S * dpr;
    canvas.height = S * dpr;
    canvas.style.width = `${S}px`;
    canvas.style.height = `${S}px`;
    ctx.scale(dpr, dpr);

    const cx = S / 2;
    const cy = S / 2;
    const outerR = S / 2 - 20;
    const innerR = outerR - 34;

    ctx.clearRect(0, 0, S, S);

    const { nodes, vnodes } = ringData;
    if (!vnodes || vnodes.length === 0) return;

    // Draw arc segments for each node
    const maxAngle = 2 * Math.PI;
    // Group vnodes by node to draw arcs
    const nodeToColor = Object.fromEntries(
      nodes.map((n, i) => [n, getColor(n, i)])
    );

    // Sort vnodes by angle
    const sorted = [...vnodes].sort((a, b) => a.angle_deg - b.angle_deg);

    for (let i = 0; i < sorted.length; i++) {
      const vn = sorted[i];
      const next = sorted[(i + 1) % sorted.length];
      const startAngle = (vn.angle_deg / 360) * maxAngle - Math.PI / 2;
      const endAngle = (next.angle_deg / 360) * maxAngle - Math.PI / 2;

      ctx.beginPath();
      ctx.arc(cx, cy, outerR, startAngle, endAngle);
      ctx.arc(cx, cy, innerR, endAngle, startAngle, true);
      ctx.closePath();
      ctx.fillStyle = nodeToColor[vn.position] || "#ccc";
      ctx.globalAlpha = 0.85;
      ctx.fill();
      ctx.globalAlpha = 1;
    }

    // Ring border
    ctx.beginPath();
    ctx.arc(cx, cy, outerR, 0, maxAngle);
    ctx.strokeStyle = "rgba(0,0,0,0.08)";
    ctx.lineWidth = 1.5;
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(cx, cy, innerR, 0, maxAngle);
    ctx.strokeStyle = "rgba(0,0,0,0.06)";
    ctx.lineWidth = 1;
    ctx.stroke();

    // Vnode tick marks
    const tickR = outerR + 6;
    for (const vn of sorted) {
      const angle = (vn.angle_deg / 360) * maxAngle - Math.PI / 2;
      ctx.beginPath();
      ctx.moveTo(
        cx + innerR * Math.cos(angle),
        cy + innerR * Math.sin(angle)
      );
      ctx.lineTo(
        cx + outerR * Math.cos(angle),
        cy + outerR * Math.sin(angle)
      );
      ctx.strokeStyle = "rgba(255,255,255,0.5)";
      ctx.lineWidth = 0.5;
      ctx.stroke();
    }

    // Center label
    ctx.fillStyle = "#13294B";
    ctx.font = `bold ${Math.round(S * 0.045)}px Inter, sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("Hash Ring", cx, cy - 10);
    ctx.font = `${Math.round(S * 0.032)}px Inter, sans-serif`;
    ctx.fillStyle = "#94a3b8";
    ctx.fillText(`${vnodes.length} vnodes`, cx, cy + 12);
    ctx.fillText(`${nodes.length} shards`, cx, cy + 30);

    // Node label at top of each arc (center angle)
    const nodeAngles = {};
    for (const n of nodes) {
      const nVnodes = sorted.filter((v) => v.position === n);
      if (nVnodes.length === 0) continue;
      const angles = nVnodes.map((v) => v.angle_deg);
      const avg = angles.reduce((a, b) => a + b, 0) / angles.length;
      nodeAngles[n] = avg;
    }

    const labelR = outerR + 16;
    for (const [n, deg] of Object.entries(nodeAngles)) {
      const angle = (deg / 360) * maxAngle - Math.PI / 2;
      const lx = cx + labelR * Math.cos(angle);
      const ly = cy + labelR * Math.sin(angle);
      ctx.save();
      ctx.translate(lx, ly);
      ctx.font = `bold ${Math.round(S * 0.028)}px Inter, sans-serif`;
      ctx.fillStyle = nodeToColor[n] || "#333";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(n, 0, 0);
      ctx.restore();
    }
  }, [ringData, size]);

  if (!ringData) return null;

  return (
    <div className="ring-container">
      <canvas ref={canvasRef} />
      <div className="ring-legend">
        {(ringData.nodes || []).map((n, i) => (
          <div key={n} className="legend-item">
            <div
              className="legend-dot"
              style={{ background: getColor(n, i) }}
            />
            <span>{n}</span>
            {ringData.node_distribution?.[n] && (
              <span style={{ color: "#94a3b8" }}>
                ({ringData.node_distribution[n].count} vnodes,{" "}
                {ringData.node_distribution[n].percentage}%)
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
