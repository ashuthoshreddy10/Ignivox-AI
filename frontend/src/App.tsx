import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Rocket, Brain, BarChart3, Users, Code, Calendar,
  Presentation, ShieldCheck, Network, ChevronRight, TrendingUp,
} from 'lucide-react';
import { AGENT_COLORS, AGENT_LABELS } from './lib/types';
import Header from './components/Header';
import IdeaInput from './components/IdeaInput';
import AgentCommandCenter from './components/AgentCommandCenter';
import AgentGraph from './components/AgentGraph';
import BlueprintWorkspace from './components/BlueprintWorkspace';
import ScoreCard from './components/ScoreCard';
import InvestorMode from './components/InvestorMode';
import WorkflowTimeline from './components/WorkflowTimeline';
import { useAgentStatus } from './hooks/useAgentStatus';
import { useGenerationFlow } from './hooks/useGenerationFlow';

const EXAMPLE_IDEAS = [
  'Build an AI platform for college students to improve placement preparation',
  'Create an AI healthcare startup for preventive diagnostics',
  'Design a SaaS product for small business workflow automation',
  'Generate a fintech startup for millennial personal finance',
];

type Tab = 'command' | 'blueprint' | 'investor' | 'graph';

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('command');

  const { agents, nvidiaMode, setAgents, loadAgents } = useAgentStatus();

  const {
    isGenerating,
    progress,
    events,
    blueprint,
    activeAgent,
    handleGenerate,
  } = useGenerationFlow({
    loadAgents,
    setAgents,
    setActiveTab,
  });

  const tabs: { id: Tab; label: string; icon: typeof Rocket }[] = [
    { id: 'command', label: 'Command Center', icon: Brain },
    { id: 'graph', label: 'Agent Graph', icon: Network },
    { id: 'blueprint', label: 'Blueprint', icon: BarChart3 },
    { id: 'investor', label: 'Investor Mode', icon: Presentation },
  ];

  return (
    <div className="min-h-screen bg-surface">
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-ignivox-900/20 via-surface to-surface pointer-events-none" />

      <div className="relative z-10">
        <Header nvidiaMode={nvidiaMode} />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Hero */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h1 className="text-4xl sm:text-6xl font-bold mb-4">
              <span className="gradient-text">Ignivox AI</span>
            </h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Your autonomous startup co-founder. Transform any idea into a complete,
              investor-ready business blueprint in minutes.
            </p>
          </motion.div>

          {/* Input */}
          <IdeaInput
            onGenerate={handleGenerate}
            isGenerating={isGenerating}
            examples={EXAMPLE_IDEAS}
          />

          {/* Progress bar */}
          <AnimatePresence>
            {isGenerating && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-6"
              >
                <div className="card">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">
                      {activeAgent ? `${AGENT_LABELS[activeAgent] || activeAgent} working...` : 'Initializing...'}
                    </span>
                    <span className="text-sm font-mono text-ignivox-400">{Math.round(progress)}%</span>
                  </div>
                  <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-ignivox-500 to-emerald-400 rounded-full"
                      animate={{ width: `${progress}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Tabs */}
          {(isGenerating || blueprint) && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-8"
            >
              <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
                {tabs.map(({ id, label, icon: Icon }) => (
                  <button
                    key={id}
                    onClick={() => setActiveTab(id)}
                    className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${
                      activeTab === id
                        ? 'bg-ignivox-500/20 text-ignivox-400 border border-ignivox-500/30'
                        : 'glass-hover text-gray-400'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {label}
                  </button>
                ))}
              </div>

              {activeTab === 'command' && (
                <div className="grid lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2">
                    <AgentCommandCenter agents={agents} activeAgent={activeAgent} isGenerating={isGenerating} />
                  </div>
                  <div>
                    <WorkflowTimeline events={events} />
                    {blueprint?.score && <ScoreCard score={blueprint.score} />}
                  </div>
                </div>
              )}

              {activeTab === 'graph' && <AgentGraph agents={agents} activeAgent={activeAgent} />}
              {activeTab === 'blueprint' && blueprint && <BlueprintWorkspace blueprint={blueprint} />}
              {activeTab === 'investor' && blueprint && <InvestorMode blueprint={blueprint} />}
            </motion.div>

          )}

          {/* Agent showcase when idle */}
          {!isGenerating && !blueprint && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="mt-16"
            >
              <h2 className="text-2xl font-bold text-center mb-8">Your AI Founding Team</h2>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {[
                  { icon: Brain, name: 'Orchestrator', desc: 'Coordinates the entire workflow', color: AGENT_COLORS.orchestrator },
                  { icon: BarChart3, name: 'Market Research', desc: 'Discovers opportunities & TAM', color: AGENT_COLORS.market_research },
                  { icon: Users, name: 'Competitor Intel', desc: 'Analyzes competition & gaps', color: AGENT_COLORS.competitor },
                  { icon: Rocket, name: 'Product Strategy', desc: 'Defines MVP & roadmap', color: AGENT_COLORS.product_strategy },
                  { icon: TrendingUp, name: 'Business Strategy', desc: 'Revenue model & GTM', color: AGENT_COLORS.business_strategy },
                  { icon: Code, name: 'Tech Architect', desc: 'System design & stack', color: AGENT_COLORS.technical_architect },
                  { icon: Calendar, name: 'Execution Plan', desc: 'Sprints & launch timeline', color: AGENT_COLORS.execution_planning },
                  { icon: Presentation, name: 'Investor Pitch', desc: 'Pitch deck & funding', color: AGENT_COLORS.investor_pitch },
                  { icon: ShieldCheck, name: 'Validation', desc: 'Quality & feasibility', color: AGENT_COLORS.validation },
                ].map(({ icon: Icon, name, desc, color }) => (
                  <div key={name} className="glass-hover p-5 group cursor-default">
                    <div className="flex items-start gap-4">
                      <div
                        className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
                        style={{ backgroundColor: `${color}20`, color }}
                      >
                        <Icon className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-white group-hover:text-ignivox-400 transition-colors">{name}</h3>
                        <p className="text-sm text-gray-500 mt-1">{desc}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-12 text-center">
                <p className="text-gray-500 text-sm mb-4">Try an example idea</p>
                <div className="flex flex-wrap justify-center gap-3">
                  {EXAMPLE_IDEAS.map((ex) => (
                    <button
                      key={ex}
                      onClick={() => handleGenerate(ex)}
                      className="glass-hover px-4 py-2 text-sm text-gray-300 flex items-center gap-2"
                    >
                      {ex.slice(0, 50)}...
                      <ChevronRight className="w-3 h-3" />
                    </button>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </main>
      </div>
    </div>
  );
}
