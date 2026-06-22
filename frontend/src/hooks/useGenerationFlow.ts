import { useState, useCallback, Dispatch, SetStateAction } from 'react';
import type { StartupBlueprint, WorkflowEvent, AgentInfo } from '../lib/types';
import { generateWithFallback } from '../lib/api';

interface UseGenerationFlowProps {
  loadAgents: () => Promise<void>;
  setAgents: Dispatch<SetStateAction<AgentInfo[]>>;
  setActiveTab: (tab: 'command' | 'blueprint' | 'investor' | 'graph') => void;
}

export function useGenerationFlow({
  loadAgents,
  setAgents,
  setActiveTab,
}: UseGenerationFlowProps) {
  const [idea, setIdea] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [events, setEvents] = useState<WorkflowEvent[]>([]);
  const [blueprint, setBlueprint] = useState<StartupBlueprint | null>(null);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);

  const handleGenerate = useCallback(async (inputIdea: string) => {
    setIdea(inputIdea);
    setIsGenerating(true);
    setProgress(0);
    setEvents([]);
    setBlueprint(null);
    setActiveTab('command');
    await loadAgents();
    setAgents((prev) => prev.map((a) => ({ ...a, status: 'idle' })));

    await generateWithFallback(
      inputIdea,
      (event) => {
        setEvents((prev) => [...prev, event]);
        setProgress(event.progress);
        if (event.agent) setActiveAgent(event.agent);
        if (event.type === 'agent_complete') loadAgents();
      },
      (bp) => {
        setBlueprint(bp);
        setIsGenerating(false);
        setProgress(100);
        setActiveTab('blueprint');
      },
      (error) => {
        console.error(error);
        setIsGenerating(false);
      },
    );
  }, [loadAgents, setAgents, setActiveTab]);

  return {
    idea,
    isGenerating,
    progress,
    events,
    blueprint,
    activeAgent,
    handleGenerate,
  };
}
