import { Presentation, DollarSign, TrendingUp, FileText } from 'lucide-react';
import type { StartupBlueprint } from '../lib/types';
import ScoreCard from './ScoreCard';

interface Props {
  blueprint: StartupBlueprint;
}

export default function InvestorMode({ blueprint }: Props) {
  const pitch = blueprint.investor_pitch?.content;
  const slides = (pitch?.pitch_slides as Array<{ title: string; content: string; speaker_notes: string }>) || [];
  const fundingAsk = pitch?.funding_ask as Record<string, unknown> | undefined;
  const execSummary = pitch?.executive_summary as string;

  return (
    <div className="grid lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        {/* Executive Summary */}
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <FileText className="w-5 h-5 text-ignivox-400" />
            <h2 className="text-lg font-semibold">Executive Summary</h2>
          </div>
          <p className="text-gray-300 leading-relaxed">{execSummary}</p>
        </div>

        {/* Pitch Deck */}
        <div className="card">
          <div className="flex items-center gap-3 mb-6">
            <Presentation className="w-5 h-5 text-ignivox-400" />
            <h2 className="text-lg font-semibold">Pitch Deck</h2>
            <span className="ml-auto text-xs text-gray-500">{slides.length} slides</span>
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            {slides.map((slide, i) => (
              <div
                key={i}
                className="p-5 rounded-xl bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10 hover:border-ignivox-500/30 transition-all group"
              >
                <div className="flex items-center gap-2 mb-3">
                  <span className="w-6 h-6 rounded-lg bg-ignivox-500/20 text-ignivox-400 text-xs flex items-center justify-center font-bold">
                    {i + 1}
                  </span>
                  <h3 className="font-semibold text-sm group-hover:text-ignivox-400 transition-colors">
                    {slide.title}
                  </h3>
                </div>
                <p className="text-sm text-gray-400 leading-relaxed">{slide.content}</p>
                {slide.speaker_notes && (
                  <p className="text-xs text-gray-600 mt-3 italic border-t border-white/5 pt-2">
                    📝 {slide.speaker_notes}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Funding Strategy */}
        {fundingAsk && (
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <DollarSign className="w-5 h-5 text-ignivox-400" />
              <h2 className="text-lg font-semibold">Funding Ask</h2>
            </div>
            <div className="grid sm:grid-cols-3 gap-4 mb-4">
              <div className="p-4 rounded-xl bg-white/5 text-center">
                <div className="text-2xl font-bold text-ignivox-400">{String(fundingAsk.amount)}</div>
                <div className="text-xs text-gray-500 mt-1">Raise Amount</div>
              </div>
              <div className="p-4 rounded-xl bg-white/5 text-center">
                <div className="text-2xl font-bold text-emerald-400">{String(fundingAsk.valuation)}</div>
                <div className="text-xs text-gray-500 mt-1">Pre-Money Valuation</div>
              </div>
              <div className="p-4 rounded-xl bg-white/5 text-center">
                <div className="text-2xl font-bold text-blue-400">{String(fundingAsk.runway_months)}mo</div>
                <div className="text-xs text-gray-500 mt-1">Runway</div>
              </div>
            </div>

            {typeof fundingAsk.use_of_funds === 'object' && fundingAsk.use_of_funds !== null ? (
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-2">Use of Funds</h4>
                <div className="space-y-2">
                  {Object.entries(fundingAsk.use_of_funds as Record<string, string>).map(([key, val]) => (
                    <div key={key} className="flex items-center gap-3">
                      <span className="text-xs text-gray-400 w-28 capitalize">{key.replace(/_/g, ' ')}</span>
                      <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-ignivox-500 to-emerald-400 rounded-full"
                          style={{ width: val }}
                        />
                      </div>
                      <span className="text-xs font-mono text-gray-400">{val}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        )}
      </div>

      {/* Sidebar */}
      <div>
        {blueprint.score && <ScoreCard score={blueprint.score} />}

        <div className="card mt-6">
          <div className="flex items-center gap-3 mb-4">
            <TrendingUp className="w-5 h-5 text-ignivox-400" />
            <h3 className="font-semibold">Funding Recommendation</h3>
          </div>
          <div className="space-y-3 text-sm">
            <div className="p-3 rounded-xl bg-green-500/10 border border-green-500/20">
              <p className="text-green-400 font-medium">
                {(blueprint.score?.overall ?? 0) >= 75 ? 'Recommended for Seed Funding' : 'Validate Further Before Fundraising'}
              </p>
              <p className="text-gray-400 mt-1 text-xs">
                Based on viability score of {blueprint.score?.overall ?? 0}/100 across market, revenue, and technical dimensions.
              </p>
            </div>

            {blueprint.validation?.content && (
              <div className="text-xs text-gray-500 space-y-1">
                <p>Feasibility: {String((blueprint.validation.content as Record<string, unknown>).feasibility_score)}/100</p>
                <p>{String((blueprint.validation.content as Record<string, unknown>).validation_summary)?.slice(0, 150)}...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
