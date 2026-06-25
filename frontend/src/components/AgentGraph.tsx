import { useEffect, useState } from 'react';
import { Network } from 'lucide-react';
import { fetchAgentGraph } from '../lib/api';
import { AGENT_COLORS, AGENT_LABELS, type AgentInfo } from '../lib/types';

interface Props {
  agents: AgentInfo[];
  activeAgent: string | null;
}

export default function AgentGraph({ agents, activeAgent }: Props) {
  const [graph, setGraph] = useState<{ nodes: Array<{ id: string; name: string }>; edges: Array<{ source: string; target: string }> }>({ nodes: [], edges: [] });

  useEffect(() => {
    fetchAgentGraph().then(setGraph).catch(() => {});
  }, []);

  const positions: Record<string, { x: number; y: number }> = {};
  const nodeList = graph.nodes.length > 0 ? graph.nodes : Object.entries(AGENT_LABELS).map(([id, name]) => ({ id, name }));

  // Pure mathematical circular layout distribution matrix
  nodeList.forEach((node, i) => {
    const angle = (i / nodeList.length) * 2 * Math.PI - Math.PI / 2;
    const radius = 170; // Optimized constraint bounds to prevent label edge clipping
    positions[node.id] = {
      x: 250 + radius * Math.cos(angle),
      y: 250 + radius * Math.sin(angle),
    };
  });

  // Safe status verification abstraction layer
  const getAgentStatus = (id: string) => {
    const current = agents.find(a => a.type === id);
    if (current) return current.status;
    return activeAgent === id ? 'working' : 'idle';
  };

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-6">
        <Network className="w-5 h-5 text-ignivox-400" />
        <h2 className="text-lg font-semibold">Agent Collaboration Graph</h2>
      </div>

      <div className="relative overflow-hidden rounded-xl bg-white/[0.01] border border-white/5">
        <svg viewBox="0 0 500 500" className="w-full max-h-[500px]">
          {/* Defs block for custom marker state vector arrows */}
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="5" markerHeight="5" orient="auto">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(255,255,255,0.15)" />
            </marker>
            <marker id="arrow-active" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#22c55e" />
            </marker>
          </defs>

          {/* Dynamic Link Execution Paths */}
          {graph.edges.map((edge, i) => {
            const from = positions[edge.source];
            const to = positions[edge.target];
            if (!from || !to) return null;

            const sourceStatus = getAgentStatus(edge.source);
            const targetStatus = getAgentStatus(edge.target);
            
            // Highlights live active workflow path pipeline channels
            const isActivePath = sourceStatus === 'complete' && targetStatus === 'working';

            return (
              <line
                key={i}
                x1={from.x}
                y1={from.y}
                x2={to.x}
                y2={to.y}
                stroke={isActivePath ? "#22c55e" : "rgba(255,255,255,0.06)"}
                strokeWidth={isActivePath ? "2.5" : "1.5"}
                strokeDasharray={isActivePath ? "5,5" : "none"}
                className={isActivePath ? "animate-[dash_30s_linear_infinite]" : ""}
                markerEnd={isActivePath ? "url(#arrow-active)" : "url(#arrow)"}
              />
            );
          })}

          {/* Node Graphic Layers */}
          {nodeList.map((node) => {
            const pos = positions[node.id];
            if (!pos) return null;

            const color = AGENT_COLORS[node.id] || '#666';
            const status = getAgentStatus(node.id);
            
            const isWorking = status === 'working';
            const isComplete = status === 'complete';
            const isError = status === 'error';

            return (
              <g key={node.id} className="transition-all duration-300">
                {/* Real-time agent status ping wrapper */}
                {isWorking && (
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r="34"
                    fill="none"
                    stroke={color}
                    strokeWidth="1"
                    className="animate-ping opacity-20"
                    style={{ transformOrigin: `${pos.x}px ${pos.y}px` }}
                  />
                )}
                
                {/* Base Node Container layout element */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r="26"
                  fill={isError ? '#f59e0b15' : isComplete ? `${color}15` : '#121214'}
                  stroke={isError ? '#f59e0b' : isWorking ? '#fff' : isComplete ? '#22c55e' : 'rgba(255,255,255,0.1)'}
                  strokeWidth={isWorking ? "2.5" : "1.5"}
                  className="transition-all duration-300"
                />

                {/* Core Node Flavor Dot */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r="5"
                  fill={isError ? '#f59e0b' : isComplete ? '#22c55e' : color}
                  opacity={isWorking ? 1 : 0.6}
                />

                <text
                  x={pos.x}
                  y={pos.y + 40}
                  textAnchor="middle"
                  fill={isWorking ? "#fff" : "rgba(255,255,255,0.5)"}
                  fontSize="10"
                  fontWeight={isWorking ? "600" : "500"}
                  className="select-none transition-colors duration-300"
                >
                  {node.name.split(' ').slice(0, 2).join(' ')}
                </text>
              </g>
            );
          })}

          {/* Central Branded Canvas Label Identifier */}
          <circle cx="250" cy="250" r="35" fill="#09090b" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
          <text x="250" y="254" textAnchor="middle" fill="#22c55e" fontSize="11" fontWeight="bold" className="tracking-widest uppercase select-none">
            Vox
          </text>
        </svg>
      </div>
    </div>
  );
}
