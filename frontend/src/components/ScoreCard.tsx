import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from 'recharts';
import type { ScoreBreakdown } from '../lib/types';

interface Props {
  score: ScoreBreakdown;
}

export default function ScoreCard({ score }: Props) {
  const data = [
    { metric: 'Market', value: score.market_potential, fullMark: 100 },
    { metric: 'Revenue', value: score.revenue_potential, fullMark: 100 },
    { metric: 'Technical', value: score.technical_feasibility, fullMark: 100 },
    { metric: 'Scale', value: score.scalability, fullMark: 100 },
    { metric: 'Competition', value: 100 - score.competition_intensity, fullMark: 100 },
  ];

  const getScoreColor = (s: number) => {
    if (s >= 80) return 'text-green-400';
    if (s >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getScoreLabel = (s: number) => {
    if (s >= 80) return 'Strong';
    if (s >= 60) return 'Moderate';
    return 'Needs Work';
  };

  return (
    <div className="card mt-6">
      <h2 className="text-lg font-semibold mb-4">Startup Viability Score</h2>

      <div className="text-center mb-4">
        <div className={`text-5xl font-bold ${getScoreColor(score.overall)}`}>
          {score.overall}
        </div>
        <div className="text-sm text-gray-400 mt-1">out of 100 — {getScoreLabel(score.overall)}</div>
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <RadarChart data={data}>
          <PolarGrid stroke="rgba(255,255,255,0.1)" />
          <PolarAngleAxis dataKey="metric" tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} />
          <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
          <Radar
            name="Score"
            dataKey="value"
            stroke="#22c55e"
            fill="#22c55e"
            fillOpacity={0.2}
            strokeWidth={2}
          />
        </RadarChart>
      </ResponsiveContainer>

      <div className="grid grid-cols-2 gap-2 mt-4">
        {data.map(({ metric, value }) => (
          <div key={metric} className="flex justify-between text-xs px-2 py-1 rounded bg-white/5">
            <span className="text-gray-400">{metric}</span>
            <span className={getScoreColor(value)}>{value.toFixed(0)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
