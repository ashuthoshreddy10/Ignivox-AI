import { motion } from 'framer-motion';
import { Brain, CheckCircle2, Loader2, Circle, AlertCircle } from 'lucide-react';
import type { AgentInfo } from '../lib/types';
import { AGENT_COLORS, AGENT_LABELS } from '../lib/types';

interface Props {
  agents: AgentInfo[];
  activeAgent: string | null;
  isGenerating: boolean;
}

const PARALLEL_WAVES = [
  ['business_strategy', 'technical_architect'],
  ['execution_planning', 'investor_pitch']
];

export default function AgentCommandCenter({ agents, activeAgent, isGenerating }: Props) {
  const defaultAgents = Object.entries(AGENT_LABELS).map(([type, name]) => ({
    type,
    name,
    description: '',
    status: 'idle',
  }));

  const displayAgents = agents.length > 0 ? agents : defaultAgents;

  const renderAgentCard = (agent: AgentInfo, index: number) => {
    const isActive = activeAgent === agent.type;
    const isComplete = agent.status === 'complete';
    const isError = agent.status === 'error';
    const isWorking = agent.status === 'working' || isActive;
    const isParallel = PARALLEL_WAVES.some(w => w.includes(agent.type));

    return (
      <motion.div
        key={agent.type}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: index * 0.05 }}
        className={`flex items-center gap-4 p-4 rounded-xl transition-all duration-300 ${
          isWorking
            ? 'bg-white/10 border border-white/20'
            : isComplete
            ? 'bg-ignivox-500/5 border border-ignivox-500/20'
            : isError
            ? 'bg-amber-500/5 border border-amber-500/20'
            : 'bg-white/5 border border-transparent'
        }`}
      >
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
          style={{
            backgroundColor: isError ? '#f59e0b20' : `${AGENT_COLORS[agent.type] || '#666'}20`,
            color: isError ? '#f59e0b' : AGENT_COLORS[agent.type] || '#666',
          }}
        >
          {isWorking ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : isComplete ? (
            <CheckCircle2 className="w-5 h-5" />
          ) : isError ? (
            <AlertCircle className="w-5 h-5" />
          ) : (
            <Circle className="w-5 h-5 opacity-30" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-medium text-sm">{agent.name}</h3>
            {isParallel && (
              <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/25 uppercase tracking-wider">
                Parallel
              </span>
            )}
            {isWorking && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-ignivox-500/20 text-ignivox-400">
                Working
              </span>
            )}
            {isComplete && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-green-500/20 text-green-400">
                Complete
              </span>
            )}
            {isError && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400">
                Needs Review
              </span>
            )}
          </div>
          {agent.description && (
            <p className="text-xs text-gray-500 mt-0.5 truncate">{agent.description}</p>
          )}
        </div>

        {/* Enhanced progress tracking component with creative cooling indicators */}
        {isWorking && (
          <div className="w-16 h-1 bg-white/10 rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ backgroundColor: isError ? '#f59e0b' : AGENT_COLORS[agent.type] }}
              animate={{ x: ['-100%', '100%'] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
            />
          </div>
        )}
      </motion.div>
    );
  };

  const renderContent = () => {
    const renderedElements: React.ReactNode[] = [];
    const processedTypes = new Set<string>();

    for (let i = 0; i < displayAgents.length; i++) {
      const agent = displayAgents[i];
      if (processedTypes.has(agent.type)) continue;

      const wave = PARALLEL_WAVES.find(w => w.includes(agent.type));
      
      if (wave) {
        const waveAgents = wave
          .map(t => displayAgents.find(a => a.type === t))
          .filter((a): a is AgentInfo => !!a);

        wave.forEach(t => processedTypes.add(t));
        const anyWorking = waveAgents.some(wa => wa.status === 'working' || activeAgent === wa.type);

        renderedElements.push(
          <div key={wave.join('-')} className={`relative border rounded-2xl p-3 bg-white/[0.01] space-y-3 transition-all duration-300 ${anyWorking ? 'border-cyan-500/20 shadow-[0_0_15px_rgba(6,182,212,0.05)]' : 'border-white/5'}`}>
            <div className="flex items-center justify-between px-1">
              <span className={`text-[10px] uppercase tracking-wider font-bold flex items-center gap-1.5 ${anyWorking ? 'text-cyan-400' : 'text-gray-500'}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${anyWorking ? 'bg-cyan-400 animate-pulse' : 'bg-gray-600'}`} />
                Parallel Execution Wave
              </span>
            </div>
            <div className="space-y-3 pl-3 border-l border-dashed border-white/10">
              {waveAgents.map((wa, idx) => renderAgentCard(wa, i + idx))}
            </div>
          </div>
        );
      } else {
        processedTypes.add(agent.type);
        renderedElements.push(renderAgentCard(agent, i));
      }
    }

    return renderedElements;
  };

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-6">
        <Brain className="w-5 h-5 text-ignivox-400" />
        <h2 className="text-lg font-semibold">Startup Command Center</h2>
        {isGenerating && (
          <span className="ml-auto flex items-center gap-2 text-xs text-ignivox-400">
            <span className="w-2 h-2 rounded-full bg-ignivox-400 animate-pulse" />
            Agents Active
          </span>
        )}
      </div>

      <div className="space-y-3">
        {renderContent()}
      </div>
    </div>
  );
}
