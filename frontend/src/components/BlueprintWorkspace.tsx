import { useState } from 'react';
import {
  BarChart3, Users, Rocket, DollarSign, Code, Calendar,
  ChevronDown, ChevronUp, Lightbulb, ShieldCheck, ExternalLink
} from 'lucide-react';
import type { StartupBlueprint, AgentOutput, SourceInfo } from '../lib/types';

interface Props {
  blueprint: StartupBlueprint;
}

const SECTIONS = [
  { key: 'novelty_detection', label: 'Novelty Detection', icon: Lightbulb, color: '#6366f1' },
  { key: 'market_research', label: 'Market Research', icon: BarChart3, color: '#3b82f6' },
  { key: 'competitor_analysis', label: 'Competitor Analysis', icon: Users, color: '#f59e0b' },
  { key: 'product_strategy', label: 'Product Strategy', icon: Rocket, color: '#8b5cf6' },
  { key: 'business_strategy', label: 'Business Strategy', icon: DollarSign, color: '#ec4899' },
  { key: 'technical_architecture', label: 'Technical Architecture', icon: Code, color: '#06b6d4' },
  { key: 'execution_plan', label: 'Execution Plan', icon: Calendar, color: '#f97316' },
  { key: 'investor_pitch', label: 'Investor Pitch', icon: DollarSign, color: '#eab308' },
  { key: 'validation', label: 'Validation Report', icon: ShieldCheck, color: '#10b981' },
] as const;

function isGroundedClaim(val: unknown): val is { 
  claim: string; 
  sources: SourceInfo[]; 
  confidence: number;
  retrieval_status?: string;
  claim_type?: string;
  verification?: string;
  source_count?: number;
  evidence_strength?: string;
  assumptions?: string[];
  assumption_confidence?: number;
} {
  return (
    val !== null &&
    typeof val === 'object' &&
    'claim' in val &&
    'sources' in val &&
    Array.isArray((val as any).sources)
  );
}

function renderClaimBadges(claim: any, isFrontierMode?: boolean) {
  return (
    <div className="flex flex-wrap gap-1.5 mt-1.5">
      {/* Confidence */}
      <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-gray-300 font-semibold shrink-0">
        Conf: {(claim.confidence * 100).toFixed(0)}%
      </span>
      
      {/* Retrieval Status */}
      {claim.retrieval_status && (
        <span className={`text-[10px] px-1.5 py-0.5 rounded border font-semibold shrink-0 ${
          claim.retrieval_status === 'success' 
            ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' 
            : 'bg-rose-500/10 border-rose-500/20 text-rose-400'
        }`}>
          Retrieval: {claim.retrieval_status === 'success' ? 'Success' : 'Failed'}
        </span>
      )}

      {/* Claim Type */}
      {claim.claim_type && (
        <span className={`text-[10px] px-1.5 py-0.5 rounded border font-semibold shrink-0 ${
          claim.verification === 'unverified' && claim.evidence_strength === 'low'
            ? 'bg-amber-500/10 border-amber-500/20 text-amber-400'
            : claim.claim_type === 'retrieved' 
            ? 'bg-blue-500/10 border-blue-500/20 text-blue-400' 
            : 'bg-purple-500/10 border-purple-500/20 text-purple-400'
        }`}>
          {claim.verification === 'unverified' && claim.evidence_strength === 'low'
            ? (isFrontierMode ? 'Hypothesis' : 'Projection')
            : claim.claim_type === 'retrieved' ? 'Fact' : 'Reasoning'}
        </span>
      )}

      {/* Verification */}
      {claim.verification && (
        <span className={`text-[10px] px-1.5 py-0.5 rounded border font-semibold shrink-0 ${
          claim.verification === 'verified' 
            ? 'bg-teal-500/10 border-teal-500/20 text-teal-400' 
            : 'bg-amber-500/10 border-amber-500/20 text-amber-400'
        }`}>
          {claim.verification === 'verified' ? 'Verified' : 'Unverified'}
        </span>
      )}

      {/* Evidence Strength */}
      {claim.evidence_strength && (
        <span className={`text-[10px] px-1.5 py-0.5 rounded border font-semibold shrink-0 ${
          claim.evidence_strength === 'high' 
            ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' 
            : claim.evidence_strength === 'medium' 
            ? 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400'
            : 'bg-white/5 border-white/5 text-gray-500'
        }`}>
          Strength: {claim.evidence_strength.toUpperCase()}
        </span>
      )}

      {/* Source Count */}
      {claim.source_count !== undefined && claim.source_count > 0 && (
        <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 border border-white/5 text-gray-400 font-semibold shrink-0">
          Sources: {claim.source_count}
        </span>
      )}
    </div>
  );
}

function extractSources(content: unknown): Array<{ url: string; title: string; confidence: number; timestamp: string }> {
  const sourcesMap = new Map<string, { url: string; title: string; confidence: number; timestamp: string }>();
  
  function recurse(obj: unknown) {
    if (obj === null || typeof obj !== 'object') return;
    if (isGroundedClaim(obj)) {
      obj.sources?.forEach((src) => {
        if (src.source_url) {
          const existing = sourcesMap.get(src.source_url);
          if (!existing || src.confidence_score > existing.confidence) {
            sourcesMap.set(src.source_url, {
              url: src.source_url,
              title: src.source_title,
              confidence: src.confidence_score,
              timestamp: src.retrieval_timestamp
            });
          }
        }
      });
      return;
    }
    Object.values(obj).forEach((val) => recurse(val));
  }
  
  recurse(content);
  return Array.from(sourcesMap.values());
}

function renderContent(content: Record<string, unknown>, depth = 0, isFrontierMode = false): React.ReactNode {
  if (depth > 3) return <span className="text-gray-400 text-sm">{JSON.stringify(content)}</span>;

  return (
    <div className={`space-y-3.5 ${depth > 0 ? 'ml-4 border-l border-white/5 pl-4' : ''}`}>
      {/* Custom TAM -> SAM -> SOM Flow rendering */}
      {depth === 0 && 'tam' in content && 'sam' in content && 'som' in content && (
        (() => {
          const tamVal = content.tam as any;
          const samVal = content.sam as any;
          const somVal = content.som as any;

          return (
            <div className="my-5 p-4 rounded-xl bg-white/5 border border-white/10 space-y-4">
              <span className="text-xs font-bold text-ignivox-400 uppercase tracking-wider block border-b border-white/5 pb-2">
                Market Size (TAM / SAM / SOM) Sizing Flow
              </span>
              
              <div className="flex flex-col items-center gap-3">
                {/* TAM */}
                <div className="w-full p-3.5 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors">
                  <div className="flex justify-between items-start">
                    <span className="text-xs font-bold text-blue-400 uppercase tracking-wider">TAM (Total Addressable Market)</span>
                    <div className="flex items-center gap-2">
                      {tamVal.assumption_confidence !== undefined && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/10 border border-blue-500/20 text-blue-400 font-semibold">
                          Assump Conf: {(tamVal.assumption_confidence * 100).toFixed(0)}%
                        </span>
                      )}
                      {tamVal.confidence && (
                        <span className="text-[10px] text-gray-500">Conf: {(tamVal.confidence * 100).toFixed(0)}%</span>
                      )}
                    </div>
                  </div>
                  <p className="text-sm font-semibold text-white mt-1.5">{tamVal.claim}</p>
                  {tamVal.assumptions && Array.isArray(tamVal.assumptions) && tamVal.assumptions.length > 0 && (
                    <div className="mt-2 pl-3 border-l border-blue-500/30 text-xs text-gray-400 space-y-1">
                      <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider block mb-0.5">Calculations & Assumptions:</span>
                      {tamVal.assumptions.map((ass: string, idx: number) => (
                        <div key={idx} className="flex gap-1.5">
                          <span className="text-blue-400 shrink-0">•</span>
                          <span>{ass}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {tamVal.sources?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2.5 pt-2 border-t border-white/5">
                      {tamVal.sources.map((src: any, idx: number) => (
                        <a 
                          key={idx} 
                          href={src.source_url} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="text-[9px] px-1.5 py-0.5 rounded bg-white/5 hover:bg-white/10 text-gray-400 border border-white/5 transition-colors flex items-center gap-1 hover:text-white"
                          title={`${src.source_title} · Retrieved at ${src.retrieval_timestamp}`}
                        >
                          <span>{src.source_title}</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      ))}
                    </div>
                  )}
                </div>

                {/* Arrow */}
                <div className="flex flex-col items-center text-gray-500">
                  <span className="text-[9px] font-bold uppercase tracking-widest text-ignivox-400/50">Narrowing Down</span>
                  <div className="text-sm font-bold">↓</div>
                </div>

                {/* SAM */}
                <div className="w-full p-3.5 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors">
                  <div className="flex justify-between items-start">
                    <span className="text-xs font-bold text-purple-400 uppercase tracking-wider">SAM (Serviceable Addressable Market)</span>
                    <div className="flex items-center gap-2">
                      {samVal.assumption_confidence !== undefined && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/10 border border-purple-500/20 text-purple-400 font-semibold">
                          Assump Conf: {(samVal.assumption_confidence * 100).toFixed(0)}%
                        </span>
                      )}
                      {samVal.confidence && (
                        <span className="text-[10px] text-gray-500">Conf: {(samVal.confidence * 100).toFixed(0)}%</span>
                      )}
                    </div>
                  </div>
                  <p className="text-sm font-semibold text-white mt-1.5">{samVal.claim}</p>
                  {samVal.assumptions && Array.isArray(samVal.assumptions) && samVal.assumptions.length > 0 && (
                    <div className="mt-2 pl-3 border-l border-purple-500/30 text-xs text-gray-400 space-y-1">
                      <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider block mb-0.5">Calculations & Assumptions:</span>
                      {samVal.assumptions.map((ass: string, idx: number) => (
                        <div key={idx} className="flex gap-1.5">
                          <span className="text-purple-400 shrink-0">•</span>
                          <span>{ass}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {samVal.sources?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2.5 pt-2 border-t border-white/5">
                      {samVal.sources.map((src: any, idx: number) => (
                        <a 
                          key={idx} 
                          href={src.source_url} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="text-[9px] px-1.5 py-0.5 rounded bg-white/5 hover:bg-white/10 text-gray-400 border border-white/5 transition-colors flex items-center gap-1 hover:text-white"
                          title={`${src.source_title} · Retrieved at ${src.retrieval_timestamp}`}
                        >
                          <span>{src.source_title}</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      ))}
                    </div>
                  )}
                </div>

                {/* Arrow */}
                <div className="flex flex-col items-center text-gray-500">
                  <span className="text-[9px] font-bold uppercase tracking-widest text-ignivox-400/50">Target Sizing</span>
                  <div className="text-sm font-bold">↓</div>
                </div>

                {/* SOM */}
                <div className="w-full p-3.5 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors bg-gradient-to-r from-ignivox-500/5 to-transparent border-ignivox-500/20">
                  <div className="flex justify-between items-start">
                    <span className="text-xs font-bold text-ignivox-400 uppercase tracking-wider">SOM (Serviceable Obtainable Market)</span>
                    <div className="flex items-center gap-2">
                      {somVal.assumption_confidence !== undefined && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-ignivox-500/10 border border-ignivox-500/20 text-ignivox-400 font-semibold">
                          Assump Conf: {(somVal.assumption_confidence * 100).toFixed(0)}%
                        </span>
                      )}
                      {somVal.confidence && (
                        <span className="text-[10px] text-gray-500">Conf: {(somVal.confidence * 100).toFixed(0)}%</span>
                      )}
                    </div>
                  </div>
                  <p className="text-sm font-semibold text-white mt-1.5">{somVal.claim}</p>
                  {somVal.assumptions && Array.isArray(somVal.assumptions) && somVal.assumptions.length > 0 && (
                    <div className="mt-2 pl-3 border-l border-ignivox-500/30 text-xs text-gray-300 space-y-1">
                      <span className="text-[10px] font-semibold text-ignivox-400 uppercase tracking-wider block mb-0.5">Calculations & Assumptions:</span>
                      {somVal.assumptions.map((ass: string, idx: number) => (
                        <div key={idx} className="flex gap-1.5">
                          <span className="text-ignivox-400 shrink-0">•</span>
                          <span>{ass}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {somVal.sources?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2.5 pt-2 border-t border-white/5">
                      {somVal.sources.map((src: any, idx: number) => (
                        <a 
                          key={idx} 
                          href={src.source_url} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="text-[9px] px-1.5 py-0.5 rounded bg-white/5 hover:bg-white/10 text-gray-400 border border-white/5 transition-colors flex items-center gap-1 hover:text-white"
                          title={`${src.source_title} · Retrieved at ${src.retrieval_timestamp}`}
                        >
                          <span>{src.source_title}</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })()
      )}

      {Object.entries(content).map(([key, value]) => {
        if (key === 'sources' || key === 'confidence' || key === 'claim') {
          return null;
        }

        // Skip rendering tam, sam, som separately if we already rendered them as a custom flow block
        if ((key === 'tam' || key === 'sam' || key === 'som') && depth === 0 && 'tam' in content && 'sam' in content && 'som' in content) {
          return null;
        }
        
        return (
          <div key={key}>
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider block mb-1">
              {key.replace(/_/g, ' ')}
            </span>
            {isGroundedClaim(value) ? (
              <div className="text-sm text-gray-300">
                <span className="text-white font-medium">{value.claim}</span>
                {renderClaimBadges(value, isFrontierMode)}
                {value.assumptions && Array.isArray(value.assumptions) && value.assumptions.length > 0 && (
                  <div className="mt-2 pl-3 border-l border-white/10 text-xs text-gray-400 space-y-1">
                    <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider block">Assumptions & Calculations:</span>
                    {value.assumptions.map((ass, idx) => (
                      <div key={idx} className="flex gap-1.5">
                        <span className="text-ignivox-400 shrink-0">•</span>
                        <span>{ass}</span>
                      </div>
                    ))}
                  </div>
                )}
                {value.sources?.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-1.5">
                    {value.sources.map((src, idx) => (
                      <a
                        key={idx}
                        href={src.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 hover:bg-white/10 text-gray-400 border border-white/5 transition-colors flex items-center gap-1 hover:text-white"
                        title={`${src.source_title} · Retrieved at ${src.retrieval_timestamp}`}
                      >
                        <span>{src.source_title || 'Source'}</span>
                        <ExternalLink className="w-2.5 h-2.5" />
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ) : typeof value === 'string' ? (
              <p className="text-sm text-gray-300">{value}</p>
            ) : Array.isArray(value) ? (
              <ul className="mt-1 space-y-1.5">
                {value.map((item, i) => (
                  <li key={i} className="text-sm text-gray-300 flex gap-2">
                    <span className="text-ignivox-400 shrink-0 mt-1">•</span>
                    {isGroundedClaim(item) ? (
                      <div className="flex-1">
                        <span className="text-white font-medium">{item.claim}</span>
                        {renderClaimBadges(item, isFrontierMode)}
                        {item.assumptions && Array.isArray(item.assumptions) && item.assumptions.length > 0 && (
                          <div className="mt-2 pl-3 border-l border-white/10 text-xs text-gray-400 space-y-1">
                            <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider block">Assumptions & Calculations:</span>
                            {item.assumptions.map((ass, idx) => (
                              <div key={idx} className="flex gap-1.5">
                                <span className="text-ignivox-400 shrink-0">•</span>
                                <span>{ass}</span>
                              </div>
                            ))}
                          </div>
                        )}
                        {item.sources?.length > 0 && (
                          <div className="flex flex-wrap gap-1.5 mt-1.5">
                            {item.sources.map((src, idx) => (
                              <a
                                key={idx}
                                href={src.source_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 hover:bg-white/10 text-gray-400 border border-white/5 transition-colors flex items-center gap-1 hover:text-white"
                                title={`${src.source_title} · Retrieved at ${src.retrieval_timestamp}`}
                              >
                                <span>{src.source_title || 'Source'}</span>
                                <ExternalLink className="w-2.5 h-2.5" />
                              </a>
                            ))}
                          </div>
                        )}
                      </div>
                    ) : typeof item === 'object' && item !== null ? (
                      <div className="flex-1">{renderContent(item as Record<string, unknown>, depth + 1, isFrontierMode)}</div>
                    ) : (
                      String(item)
                    )}
                  </li>
                ))}
              </ul>
            ) : typeof value === 'object' && value !== null ? (
              <div className="mt-1">{renderContent(value as Record<string, unknown>, depth + 1, isFrontierMode)}</div>
            ) : (
              <p className="text-sm text-gray-300">{String(value)}</p>
            )}
          </div>
        );
      })}
    </div>
  );
}

function SectionCard({ output, label, icon: Icon, color, isFrontierMode }: {
  output: AgentOutput;
  label: string;
  icon: typeof BarChart3;
  color: string;
  isFrontierMode: boolean;
}) {
  const [expanded, setExpanded] = useState(true);
  const [sourcesExpanded, setSourcesExpanded] = useState(false);
  
  const sectionSources = extractSources(output.content);

  return (
    <div className="card">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 text-left"
      >
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${color}20`, color }}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-white">{label}</h3>
          <div className="flex items-center gap-3 mt-0.5">
            <p className="text-xs text-gray-500">
              Confidence: {(output.confidence * 100).toFixed(0)}% · {output.duration_ms}ms
            </p>
            <div className="w-20 h-1.5 bg-white/10 rounded-full overflow-hidden">
              <div 
                className="h-full rounded-full transition-all duration-500" 
                style={{ 
                  width: `${output.confidence * 100}%`,
                  backgroundColor: output.confidence > 0.85 ? '#10b981' : output.confidence > 0.7 ? '#f59e0b' : '#ef4444' 
                }}
              />
            </div>
          </div>
        </div>
        {expanded ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
      </button>

      {expanded && (
        <div className="mt-4 pt-4 border-t border-white/5">
          {renderContent(output.content, 0, isFrontierMode)}

          {output.insights?.length > 0 && (
            <div className="mt-4 p-3 rounded-xl bg-ignivox-500/5 border border-ignivox-500/10">
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb className="w-4 h-4 text-ignivox-400" />
                <span className="text-xs font-semibold text-ignivox-400">Explainable AI Insight</span>
              </div>
              {output.insights.map((insight, i) => (
                <div key={i} className="text-sm">
                  <p className="text-gray-300 font-medium">{insight.recommendation}</p>
                  <p className="text-xs text-gray-500 mt-1">{insight.reasoning}</p>
                  <div className="flex gap-2 mt-2 flex-wrap">
                    <span className="text-xs px-2 py-0.5 rounded bg-white/5 text-gray-400">
                      Confidence: {(insight.confidence * 100).toFixed(0)}%
                    </span>
                    {insight.data_sources?.map((src) => (
                      <span key={src} className="text-xs px-2 py-0.5 rounded bg-white/5 text-gray-500">{src}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {sectionSources.length > 0 && (
            <div className="mt-4 pt-3 border-t border-white/5">
              <button
                onClick={() => setSourcesExpanded(!sourcesExpanded)}
                className="flex items-center gap-1.5 text-xs text-ignivox-400 hover:text-ignivox-300 font-semibold transition-colors"
              >
                <span>Sources & Evidence ({sectionSources.length})</span>
                {sourcesExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>
              
              {sourcesExpanded && (
                <div className="mt-2.5 space-y-2 pl-2 border-l border-ignivox-500/10">
                  {sectionSources.map((src, i) => (
                    <div key={i} className="text-xs flex flex-col md:flex-row md:items-center justify-between gap-2 p-2 rounded bg-white/5 border border-white/5">
                      <div>
                        <a
                          href={src.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-medium text-gray-300 hover:text-white hover:underline flex items-center gap-1"
                        >
                          <span>{src.title || src.url}</span>
                          <ExternalLink className="w-3 h-3 text-gray-500" />
                        </a>
                        <span className="text-[10px] text-gray-500 mt-0.5 block">
                          Retrieved: {src.timestamp ? new Date(src.timestamp).toLocaleDateString() : 'N/A'}
                        </span>
                      </div>
                      <span className="text-[10px] self-start md:self-center px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                        Score: {(src.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function BlueprintWorkspace({ blueprint }: Props) {
  const isFrontierMode = (blueprint.novelty_detection?.content?.novelty_score as number || 0) > 70;

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">Startup Blueprint</h2>
        <p className="text-gray-400">{blueprint.idea}</p>
      </div>

      {blueprint.evidence_quality_report && (
        <div className="card mb-6 border border-ignivox-500/20 bg-gradient-to-br from-ignivox-950/20 via-white/5 to-transparent shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-ignivox-500/5 rounded-full blur-3xl pointer-events-none" />
          
          <div className="flex flex-col md:flex-row gap-6 md:items-center justify-between">
            <div className="space-y-2 flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-semibold uppercase tracking-wider text-ignivox-400 bg-ignivox-500/10 px-2 py-0.5 rounded-full">
                  Evidence Grounding System
                </span>
                <span className="text-xs font-medium text-gray-500">
                  Dual-layer Scraper + Fallback Web Engine
                </span>
              </div>
              <h3 className="text-lg font-bold text-white">Evidence Quality Dashboard</h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                {blueprint.evidence_quality_report.quality_summary || 
                 "Analyzing evidence quality score across all sections based on factual grounding, source reputation, and validation checkpoints."}
              </p>
            </div>
            
            <div className="flex items-center gap-4 border-l border-white/5 pl-0 md:pl-6">
              <div className="text-center">
                <div className="text-3xl font-extrabold text-white">
                  {blueprint.evidence_quality_report.evidence_quality_score.toFixed(0)}
                  <span className="text-lg text-gray-500 font-medium">/100</span>
                </div>
                <div className="text-xs font-medium text-gray-500 mt-1 uppercase tracking-wider">
                  Evidence Quality
                </div>
              </div>
              
              <div className="w-1.5 h-12 bg-white/5 rounded-full overflow-hidden">
                <div 
                  className="w-full bg-ignivox-400 rounded-full transition-all duration-500" 
                  style={{ height: `${blueprint.evidence_quality_report.evidence_quality_score}%` }}
                />
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-white/5">
            <div className="p-3 rounded-xl bg-white/5 border border-white/5">
              <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">
                Claims Audited
              </span>
              <p className="text-lg font-bold text-white mt-0.5">
                {blueprint.evidence_quality_report.total_claims_verified}
              </p>
            </div>
            
            <div className="p-3 rounded-xl bg-white/5 border border-white/5">
              <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">
                Unsupported Claims
              </span>
              <p className="text-lg font-bold text-white mt-0.5 flex items-center gap-1.5">
                {blueprint.evidence_quality_report.unsupported_claims_count}
                {blueprint.evidence_quality_report.unsupported_claims_count > 0 && (
                  <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
                )}
              </p>
            </div>
            
            <div className="p-3 rounded-xl bg-white/5 border border-white/5">
              <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">
                Verified Sources
              </span>
              <p className="text-lg font-bold text-white mt-0.5">
                {blueprint.evidence_quality_report.trusted_sources_count}
              </p>
            </div>
            
            <div className="p-3 rounded-xl bg-white/5 border border-white/5">
              <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">
                Section Consensus
              </span>
              <p className="text-lg font-bold text-white mt-0.5">
                {blueprint.confidence_scores ? 
                 (Object.values(blueprint.confidence_scores).reduce((a,b)=>a+b, 0) / Object.values(blueprint.confidence_scores).length).toFixed(0) + '%' : 
                 '90%'}
              </p>
            </div>
          </div>

          {blueprint.novelty_detection?.content && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t border-white/5">
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">
                  Novelty Score
                </span>
                <p className="text-lg font-bold text-white mt-0.5">
                  {String(blueprint.novelty_detection.content.novelty_score ?? '')}/100
                </p>
              </div>
              
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">
                  Market Type
                </span>
                <p className="text-xs md:text-sm font-bold text-white mt-1">
                  {String(blueprint.novelty_detection.content.market_classification ?? '')}
                </p>
              </div>
              
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">
                  Evidence Coverage
                </span>
                <p className="text-lg font-bold text-white mt-0.5">
                  {((blueprint.novelty_detection.content.evidence_coverage_est as number || 0) * 100).toFixed(0)}%
                </p>
              </div>
              
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">
                  Speculative Content
                </span>
                <p className="text-lg font-bold text-white mt-0.5">
                  {((blueprint.novelty_detection.content.speculative_content_ratio as number || 0) * 100).toFixed(0)}%
                </p>
              </div>
            </div>
          )}

          {blueprint.evidence_quality_report.verified_claims?.length > 0 && (
            <div className="mt-5">
              <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2.5">
                Verified Claims Log
              </h4>
              <div className="max-h-40 overflow-y-auto space-y-2 pr-1.5 custom-scrollbar">
                {blueprint.evidence_quality_report.verified_claims.map((log, idx) => (
                  <div key={idx} className="p-2.5 rounded-lg bg-white/5 border border-white/5 flex flex-col md:flex-row md:items-center justify-between gap-2 text-xs">
                    <div className="space-y-1 flex-1">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span className="text-[10px] px-1.5 py-0.5 rounded font-semibold bg-white/10 text-gray-300">
                          {log.agent.replace(/_/g, ' ')}
                        </span>
                        
                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400`}>
                          {log.status.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-gray-300 font-medium">{log.claim}</p>
                      {renderClaimBadges(log)}
                      {log.sources?.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-1.5">
                          {log.sources.map((src, srcIdx) => (
                            <a
                              key={srcIdx}
                              href={src.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 hover:bg-white/10 text-gray-400 border border-white/5 transition-colors flex items-center gap-1 hover:text-white"
                              title={`${src.source_title} · Retrieved at ${src.retrieval_timestamp}`}
                            >
                              <span>{src.source_title || 'Source'}</span>
                              <ExternalLink className="w-2.5 h-2.5" />
                            </a>
                          ))}
                        </div>
                      )}
                    </div>
                    {(!log.sources || log.sources.length === 0) && log.source && log.source !== 'No Source' && (
                      <a 
                        href={log.source} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="text-[10px] text-ignivox-400 hover:underline hover:text-ignivox-300 break-all md:text-right self-start md:self-center"
                      >
                        {log.source.startsWith('http') ? new URL(log.source).hostname : log.source}
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="space-y-4">
        {SECTIONS.map(({ key, label, icon, color }) => {
          const output = blueprint[key as keyof StartupBlueprint] as AgentOutput | undefined;
          if (!output) return null;
          return (
            <SectionCard key={key} output={output} label={label} icon={icon} color={color} isFrontierMode={isFrontierMode} />
          );
        })}
      </div>

      {blueprint.recommendations && blueprint.recommendations.length > 0 && (
        <div className="card mt-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2 text-white">
            <Lightbulb className="w-5 h-5 text-ignivox-400" />
            Autonomous Recommendations
          </h3>
          <div className="space-y-3.5">
            {blueprint.recommendations.map((rec, i) => (
              <div key={i} className="p-4 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors space-y-2.5">
                <div className="flex items-start justify-between gap-4">
                  <p className="text-sm font-semibold text-gray-200">{rec.recommendation}</p>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-ignivox-500/10 border border-ignivox-500/20 text-ignivox-400 font-semibold shrink-0">
                    Conf: {(rec.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                
                <p className="text-xs text-gray-400 leading-relaxed">{rec.reasoning}</p>
                
                {rec.evidence && rec.evidence.length > 0 && (
                  <div className="pt-2 border-t border-white/5">
                    <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold block mb-1">
                      Evidence Summary
                    </span>
                    <ul className="space-y-1">
                      {rec.evidence.map((ev, idx) => (
                        <li key={idx} className="text-xs text-gray-300 flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-ignivox-400 shrink-0" />
                          {ev}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {rec.data_sources && rec.data_sources.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1.5">
                    <span className="text-[10px] text-gray-500 self-center uppercase tracking-wider font-semibold mr-1">
                      Supporting Sources:
                    </span>
                    {rec.data_sources.map((src) => (
                      <span key={src} className="text-[10px] px-2 py-0.5 rounded bg-white/5 border border-white/5 text-gray-400">
                        {src}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
