import { useEffect, useState } from 'react';
import { Network } from 'lucide-react';
import { fetchAgentGraph } from '../lib/api';
import { AGENT_COLORS, AGENT_LABELS } from '../lib/types';

export default function AgentGraph() {
  const [graph, setGraph] = useState<{ nodes: Array<{ id: string; name: string }>; edges: Array<{ source: string; target: string }> }>({ nodes: [], edges: [] });

  useEffect(() => {
    fetchAgentGraph().then(setGraph).catch(() => {});
  }, []);

  const positions: Record<string, { x: number; y: number }> = {};
  const nodeList = graph.nodes.length > 0 ? graph.nodes : Object.entries(AGENT_LABELS).map(([id, name]) => ({ id, name }));

  nodeList.forEach((node, i) => {
    const angle = (i / nodeList.length) * 2 * Math.PI - Math.PI / 2;
    const radius = 180;
    positions[node.id] = {
      x: 250 + radius * Math.cos(angle),
      y: 250 + radius * Math.sin(angle),
    };
  });

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-6">
        <Network className="w-5 h-5 text-ignivox-400" />
        <h2 className="text-lg font-semibold">Agent Collaboration Graph</h2>
      </div>

      <div className="relative overflow-hidden rounded-xl bg-white/[0.02] border border-white/5">
        <svg viewBox="0 0 500 500" className="w-full max-h-[500px]">
          {/* Edges */}
          {graph.edges.map((edge, i) => {
            const from = positions[edge.source];
            const to = positions[edge.target];
            if (!from || !to) return null;
            return (
              <line
                key={i}
                x1={from.x}
                y1={from.y}
                x2={to.x}
                y2={to.y}
                stroke="rgba(255,255,255,0.1)"
                strokeWidth="1.5"
                markerEnd="url(#arrow)"
              />
            );
          })}

          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="20" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(255,255,255,0.2)" />
            </marker>
          </defs>

          {/* Nodes */}
          {nodeList.map((node) => {
            const pos = positions[node.id];
            const color = AGENT_COLORS[node.id] || '#666';
            return (
              <g key={node.id}>
                <circle cx={pos.x} cy={pos.y} r="28" fill={`${color}30`} stroke={color} strokeWidth="2" />
                <text
                  x={pos.x}
                  y={pos.y + 45}
                  textAnchor="middle"
                  fill="rgba(255,255,255,0.7)"
                  fontSize="10"
                  fontWeight="500"
                >
                  {node.name.split(' ').slice(0, 2).join(' ')}
                </text>
              </g>
            );
          })}

          {/* Center label */}
          <text x="250" y="255" textAnchor="middle" fill="rgba(34,197,94,0.8)" fontSize="12" fontWeight="bold">
            Ignivox
          </text>
        </svg>
      </div>

      <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 gap-2">
        {nodeList.map((node) => (
          <div key={node.id} className="flex items-center gap-2 text-xs text-gray-400">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: AGENT_COLORS[node.id] }} />
            {node.name}
          </div>
        ))}
      </div>
    </div>
  );
}
