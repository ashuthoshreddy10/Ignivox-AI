import { useState, useCallback } from 'react';
import type { AgentInfo } from '../lib/types';
import { fetchAgents, fetchHealth } from '../lib/api';

export function useAgentStatus() {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [nvidiaMode, setNvidiaMode] = useState(false);

  const loadAgents = useCallback(async () => {
    try {
      const [agentList, health] = await Promise.all([fetchAgents(), fetchHealth()]);
      setAgents(agentList);
      setNvidiaMode(health.nvidia_mode);
    } catch {
      /* backend not running */
    }
  }, []);

  return {
    agents,
    nvidiaMode,
    setAgents,
    loadAgents,
  };
}
