import type { AgentInfo, StartupBlueprint, WorkflowEvent } from './types';

const API_BASE = '/api';

export async function fetchAgents(): Promise<AgentInfo[]> {
  const res = await fetch(`${API_BASE}/agents`);
  const data = await res.json();
  return data.agents;
}

export async function fetchAgentGraph() {
  const res = await fetch(`${API_BASE}/graph/dependencies`);
  return res.json();
}

export async function generateBlueprint(idea: string): Promise<StartupBlueprint> {
  const res = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ idea }),
  });
  if (!res.ok) throw new Error('Generation failed');
  return res.json();
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export function connectWebSocket(
  idea: string,
  onEvent: (event: WorkflowEvent) => void,
  onComplete: (blueprint: StartupBlueprint) => void,
  onError: (error: string) => void,
): WebSocket {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const ws = new WebSocket(`${protocol}//${window.location.host}/api/ws/generate`);
  let finished = false;

  const fail = (message: string) => {
    if (finished) return;
    finished = true;
    onError(message);
  };

  ws.onopen = () => {
    ws.send(JSON.stringify({ idea }));
  };

  ws.onmessage = (msg) => {
    const data = JSON.parse(msg.data);
    if (data.type === 'result') {
      finished = true;
      onComplete(data.blueprint);
    } else if (data.type === 'error') {
      fail(data.message);
    } else {
      onEvent(data as WorkflowEvent);
    }
  };

  ws.onerror = () => fail('WebSocket connection failed');
  ws.onclose = (event) => {
    if (!finished && !event.wasClean) {
      fail(`WebSocket closed unexpectedly (code ${event.code})`);
    }
  };

  return ws;
}

export async function generateWithFallback(
  idea: string,
  onEvent: (event: WorkflowEvent) => void,
  onComplete: (blueprint: StartupBlueprint) => void,
  onError: (error: string) => void,
): Promise<void> {
  return new Promise((resolve) => {
    const ws = connectWebSocket(
      idea,
      onEvent,
      (bp) => {
        onComplete(bp);
        resolve();
      },
      async (wsError) => {
        console.warn('WebSocket failed, falling back to REST:', wsError);
        try {
          onEvent({
            type: 'workflow_start',
            message: 'WebSocket unavailable — running via REST API...',
            progress: 0,
            timestamp: new Date().toISOString(),
          });
          const blueprint = await generateBlueprint(idea);
          onComplete(blueprint);
        } catch (restError) {
          onError(restError instanceof Error ? restError.message : 'Generation failed');
        }
        resolve();
      },
    );

    // Abort WebSocket if no events within 10s and fall back
    setTimeout(() => {
      if (ws.readyState === WebSocket.CONNECTING) {
        ws.close();
      }
    }, 10000);
  });
}
