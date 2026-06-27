import { Clock } from 'lucide-react';
import type { WorkflowEvent } from '../lib/types';
import { AGENT_COLORS, AGENT_LABELS } from '../lib/types';

interface Props {
  events: WorkflowEvent[];
}

export default function WorkflowTimeline({ events }: Props) {
  const formatToLocalTime = (utcString: string) => {
    try {
      const date = new Date(utcString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch (e) {
      return utcString;
    }
  };

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-4">
        <Clock className="w-5 h-5 text-ignivox-400" />
        <h2 className="text-lg font-semibold">Workflow Timeline</h2>
      </div>

      <div className="space-y-3 max-h-[400px] overflow-y-auto">
        {events.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-8">Waiting for workflow events...</p>
        ) : (
          events.map((event, i) => (
            <div key={i} className="flex gap-3 text-sm">
              <div className="flex flex-col items-center">
                <div
                  className="w-2 h-2 rounded-full mt-2"
                  style={{ backgroundColor: event.agent ? AGENT_COLORS[event.agent] : '#22c55e' }}
                />
                {i < events.length - 1 && <div className="w-px flex-1 bg-white/10 mt-1" />}
              </div>
              <div className="pb-3">
                <p className="text-gray-300">{event.message}</p>
                <div className="flex items-center gap-2 mt-1">
                  {event.agent && (
                    <span className="text-xs text-gray-500">{AGENT_LABELS[event.agent]}</span>
                  )}
                  <span className="text-xs text-gray-600">
                    {formatToLocalTime(event.timestamp)}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
