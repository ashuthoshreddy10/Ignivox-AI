"""Competitor Intelligence Agent."""

from datetime import datetime
from typing import Any

from app.agents.base import BaseAgent
from app.models.schemas import AgentType, ExplainableInsight


class CompetitorAgent(BaseAgent):
    agent_type = AgentType.COMPETITOR
    name = "Competitor Intelligence Agent"
    description = "Analyzes competing solutions and identifies market gaps"

    def get_system_prompt(self, context: dict[str, Any] | None = None) -> str:
        is_frontier = bool(context and context.get("is_frontier_mode"))
        if is_frontier:
            competitor_schema = """
  "competitors": {
    "direct_competitors": [
      {
        "name": "Competitor Name",
        "strengths": ["strength 1"],
        "weaknesses": ["weakness 1"],
        "pricing": {
          "claim": "$29/month",
          "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
          "confidence": 0.90
        },
        "market_share": {
          "claim": "12%",
          "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
          "confidence": 0.90
        }
      }
    ],
    "research_alternatives": [
      {
        "name": "Research Initiative or Adjacent Technology",
        "strengths": ["strength 1"],
        "weaknesses": ["weakness 1"],
        "pricing": {
          "claim": "Variable",
          "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
          "confidence": 0.90
        },
        "market_share": {
          "claim": "Variable",
          "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
          "confidence": 0.90
        }
      }
    ],
    "enabling_technologies": [
      {
        "name": "Enabling Technology or Open Source Project",
        "strengths": ["strength 1"],
        "weaknesses": ["weakness 1"],
        "pricing": {
          "claim": "Free / Variable",
          "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
          "confidence": 0.90
        },
        "market_share": {
          "claim": "Variable",
          "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
          "confidence": 0.90
        }
      }
    ]
  }"""
            frontier_rules = """
FRONTIER MODE COMPETITOR RULES:
- Structure 'competitors' with keys: direct_competitors, research_alternatives, enabling_technologies.
- Do NOT use indirect_competitors or alternative_solutions in frontier mode.
- Prioritize adjacent technologies, academic papers, and research organizations over invented companies.
"""
        else:
            competitor_schema = """
  "competitors": {
    "direct_competitors": [
      {
        "name": "Competitor Name",
        "strengths": ["strength 1"],
        "weaknesses": ["weakness 1"],
        "pricing": {
          "claim": "$29/month",
          "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
          "confidence": 0.90
        },
        "market_share": {
          "claim": "12%",
          "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
          "confidence": 0.90
        }
      }
    ],
    "indirect_competitors": [
      {
        "name": "Competitor Name",
        "strengths": ["strength 1"],
        "weaknesses": ["weakness 1"],
        "pricing": {
          "claim": "$29/month",
          "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
          "confidence": 0.90
        },
        "market_share": {
          "claim": "12%",
          "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
          "confidence": 0.90
        }
      }
    ],
    "alternative_solutions": [
      {
        "name": "Solution/Alternative Name",
        "strengths": ["strength 1"],
        "weaknesses": ["weakness 1"],
        "pricing": {
          "claim": "Free / Variable",
          "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
          "confidence": 0.90
        },
        "market_share": {
          "claim": "Variable",
          "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
          "confidence": 0.90
        }
      }
    ]
  }"""
            frontier_rules = ""

        return f"""You are the Competitor Intelligence Agent for Ignivox AI.
Analyze competing products and market positioning. Return JSON with this exact structure:
{{
{competitor_schema},
  "competitive_matrix": {{
    "features": ["Feature A"],
    "our_product": [9],
    "competitor_avg": [5]
  }},
  "swot": {{
    "strengths": ["strength 1"],
    "weaknesses": ["weakness 1"],
    "opportunities": ["opportunity 1"],
    "threats": ["threat 1"]
  }},
  "differentiation": [
    {{
      "claim": "differentiation point",
      "sources": [{{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}}],
      "confidence": 0.90
    }}
  ],
  "market_gaps": [
    {{
      "claim": "gap description",
      "sources": [{{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}}],
      "confidence": 0.90
    }}
  ],
  "positioning_strategy": {{
    "claim": "positioning statement",
    "sources": [{{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}}],
    "confidence": 0.90
  }}
}}

CRITICAL COMPETITOR NAME RULE:
- NEVER invent or generate fake competitors whose names contain or are derived from the startup name (e.g., if the startup name/idea is 'Sentinel Nexus', you are strictly forbidden from outputting competitors like 'SentinelAI', 'Sentinel Project', 'Sentinel Nexus Pro', etc.).
- You must ONLY use real, actual existing organizations, companies, products, open-source repositories, or academic research initiatives.
- If you do not have verified knowledge of a specific direct competitor in the research feeds or your training, search for and list real adjacent companies or technologies (e.g. Palantir, Siemens Grid Software, Schneider Electric, IBM Maximo, Hitachi Vantara, GE Digital) instead of inventing variations of the startup name.

CRITICAL CLASSIFICATION & EXCLUSION RULE:
- EXCLUDE competitors entirely unless backing evidence exists. You must strictly exclude any competitor from your lists (direct, indirect, alternative solutions, research alternatives, or enabling technologies) unless the company explicitly appears in the "Context and Research Feeds" (from retrieved research feeds, local startup_knowledge.json vector context, or historical memory).
- DO NOT output unverified competitors or mock competitors. If no evidence supports a competitor's existence in the provided context, DO NOT list them at all.
- NEVER fabricate websites, domains, or reference sources (e.g., do not generate fake URLs like 'https://preppilot.in' or 'https://prepfree.com'). If a competitor has no backing URL in the context feed, leave the "sources" array empty.

Classify competitors strictly into:
1. Direct Competitors: Products offering a highly similar core value proposition (e.g., for an Academic Operating System, these are LMS platforms like Canvas, Blackboard, or Moodle).
2. Indirect Competitors: Products targeting the same audience/industry but with a different core value proposition or scope (e.g., general EdTech platforms like Coursera, Udemy, or ERPs like Ellucian, Anthology).
3. Alternative Solutions: Workarounds, non-software alternatives, or manual processes currently used by the target customers.
Do NOT mix broad consumer EdTech platforms (like Coursera, BYJU'S, or Unacademy) as direct competitors for enterprise academic systems unless they directly compete in the exact same workspace.
{frontier_rules}"""

    def get_demo_output(self, idea: str, context: dict[str, Any]) -> dict[str, Any]:
        is_edtech = any(w in idea.lower() for w in ["student", "college", "placement", "education", "academic", "university"])
        raw_competitors = self._edtech_competitors(idea) if is_edtech else self._general_competitors(idea)

        timestamp = datetime.utcnow().isoformat() + "Z"
        sources = [
            {"source_url": "https://www.crunchbase.com/discover/organization.companies", "source_title": "Crunchbase Database", "retrieval_timestamp": timestamp, "confidence_score": 0.95},
            {"source_url": "https://www.g2.com/categories", "source_title": "G2 Crowd Comparisons", "retrieval_timestamp": timestamp, "confidence_score": 0.90}
        ]

        competitors = {}
        for category, list_of_comps in raw_competitors.items():
            competitors[category] = []
            for c in list_of_comps:
                competitors[category].append({
                    "name": c["name"],
                    "strengths": c["strengths"],
                    "weaknesses": c["weaknesses"],
                    "pricing": {"claim": c["pricing"], "sources": sources[:1], "confidence": 0.90},
                    "market_share": {"claim": c["market_share"], "sources": sources[1:], "confidence": 0.88}
                })

        # Determine matrix features, SWOT, differentiation, and gaps based on is_edtech
        if is_edtech:
            matrix_features = ["AI Personalization", "Mock Interviews", "Progress Tracking", "Pricing", "Mobile App"]
            matrix_ours = [9, 9, 8, 9, 9]
            matrix_comp = [5, 4, 6, 5, 7]
            swot = {
                "strengths": ["AI-native architecture", "Personalized learning paths", "Affordable pricing", "Real-time feedback"],
                "weaknesses": ["New brand with no track record", "Limited initial content library", "Requires user adoption curve"],
                "opportunities": ["Partnership with colleges", "Corporate placement tie-ups", "International expansion", "B2B licensing"],
                "threats": ["Established players with deep pockets", "Free alternatives", "Regulatory changes in edtech"],
            }
            differentiation_list = [
                "AI co-founder approach vs static content libraries",
                "Adaptive difficulty based on real placement patterns",
                "Integrated mock interview with NLP feedback",
                "Community-driven peer learning network",
            ]
            market_gaps_list = [
                "No platform combines aptitude + coding + soft skills in one AI system",
                "Existing tools lack real-time adaptive difficulty",
                "Premium features locked behind expensive subscriptions",
            ]
            pos_claim = "The AI-native placement co-pilot that adapts to each student's unique preparation journey at 1/10th the cost of coaching centers"
        else:
            idea_lower = idea.lower()
            if any(w in idea_lower for w in ["energy", "electricity", "utility", "grid", "helios", "scada", "iot", "sensor", "telemetry", "maintenance"]):
                matrix_features = ["Real-time Optimization", "Predictive Analytics", "Grid Ingestion Speed", "Pricing Structure", "Security Compliance"]
                matrix_ours = [9, 8, 9, 9, 9]
                matrix_comp = [5, 5, 4, 6, 6]
                swot = {
                    "strengths": ["AI-native optimization algorithms", "Real-time telemetry ingestion", "Predictive maintenance modeling", "Scalable edge deployment"],
                    "weaknesses": ["Long sales cycles with utilities", "High integration costs with legacy SCADA systems", "Strict compliance and cybersecurity standards"],
                    "opportunities": ["Partnerships with grid operators", "Expansion into virtual power plants (VPPs)", "Integration of distributed energy resources (DERs)", "Green energy grid incentives"],
                    "threats": ["Established industrial software incumbents", "Strict grid connection regulations", "Cybersecurity threats to utility systems"],
                }
                differentiation_list = [
                    "AI-driven predictive balancing vs legacy rule-based grid dispatch",
                    "Sub-second anomaly detection at the substation edge",
                    "Unified telemetry dashboard integrating solar, wind, and storage",
                    "Autonomous load-shedding scheduling via multi-agent negotiation",
                ]
                market_gaps_list = [
                    "Incumbent SCADA systems lack proactive machine learning diagnostics",
                    "Existing DERMS platforms fail to optimize real-time battery charging dynamic pricing",
                    "High barrier to entry for virtual power plant orchestration tools",
                ]
                pos_claim = "The AI-powered smart grid co-pilot that optimizes utility load balancing and predictive asset maintenance in real time"
            else:
                matrix_features = ["AI Personalization", "Task Automation", "Progress Analytics", "Integration APIs", "Enterprise Security"]
                matrix_ours = [9, 9, 8, 9, 9]
                matrix_comp = [5, 6, 6, 5, 7]
                swot = {
                    "strengths": ["AI-native multi-agent architecture", "Automated reasoning engine", "Flexible API integration layer", "High capital efficiency"],
                    "weaknesses": ["Early-stage brand awareness", "Initial onboarding friction", "Dependency on public API availability"],
                    "opportunities": ["B2B enterprise licensing", "Vertical-specific solution bundles", "Global developer marketplace expansion", "Strategic channel integrations"],
                    "threats": ["Rapid commoditization of standard AI APIs", "Changing compliance regulations", "Incumbent platform feature replication"],
                }
                differentiation_list = [
                    "Autonomous agent workflow design vs static templates",
                    "Deep context-aware task execution and memory tracking",
                    "Integrated verification and safety guardrails",
                    "Multi-source search grounding and verification",
                ]
                market_gaps_list = [
                    "Existing tools require manual prompt engineering for complex workflows",
                    "Lack of real-time validation and evidence check layers in content generation",
                    "High enterprise costs for customized platform solutions",
                ]
                pos_claim = f"The autonomous multi-agent co-pilot that accelerates operational workflows and guarantees content accuracy for {idea}"

        return {
            "competitors": competitors,
            "competitive_matrix": {
                "features": matrix_features,
                "our_product": matrix_ours,
                "competitor_avg": matrix_comp,
            },
            "swot": swot,
            "differentiation": [
                {"claim": d, "sources": sources[:1], "confidence": 0.90}
                for d in differentiation_list
            ],
            "market_gaps": [
                {"claim": g, "sources": sources[1:], "confidence": 0.88}
                for g in market_gaps_list
            ],
            "positioning_strategy": {
                "claim": pos_claim,
                "sources": sources,
                "confidence": 0.92
            }
        }

    def _edtech_competitors(self, idea: str) -> dict[str, list[dict]]:
        idea_lower = idea.lower()
        if any(w in idea_lower for w in ["academic", "operating system", "college", "attendance", "administrative", "university"]):
            return {
                "direct_competitors": [
                    {"name": "Canvas LMS", "strengths": ["Global LMS standard", "Extensive third-party developer integrations"], "weaknesses": ["Complex, legacy user experience", "Expensive enterprise licensing"], "pricing": "$12/student/year", "market_share": "36%"},
                    {"name": "Moodle", "strengths": ["Open-source flexibility", "Zero baseline license cost"], "weaknesses": ["High maintenance and self-hosting cost", "Outdated default UI/UX"], "pricing": "Free (Self-Hosted)", "market_share": "24%"},
                    {"name": "Blackboard Learn", "strengths": ["Deep institutional features", "Strong security"], "weaknesses": ["Legacy architecture", "Slow feature rollouts"], "pricing": "Enterprise", "market_share": "20%"}
                ],
                "indirect_competitors": [
                    {"name": "Ellucian Banner", "strengths": ["Robust university ERP backbone", "Stable legacy database"], "weaknesses": ["Extremely high setup fee", "Not AI-native", "Difficult customization"], "pricing": "$150k+/year", "market_share": "15%"},
                    {"name": "Anthology Student", "strengths": ["Comprehensive student info system", "Good analytics tools"], "weaknesses": ["Fragmented module structure", "High implementation overhead"], "pricing": "Enterprise", "market_share": "10%"},
                    {"name": "Classter", "strengths": ["All-in-one school management", "Cloud architecture"], "weaknesses": ["Lacks specialized AI agents", "Limited placement modules"], "pricing": "$6/student/year", "market_share": "6%"}
                ],
                "alternative_solutions": [
                    {"name": "Legacy ERPs & Custom Portal Scripts", "strengths": ["No new vendor procurement needed", "Already familiar to staff"], "weaknesses": ["No autonomous workflows", "Siloed data", "High manual labor"], "pricing": "$0 licensing fee", "market_share": "30%"}
                ]
            }
        else:
            return {
                "direct_competitors": [
                    {"name": "InterviewBit", "strengths": ["Company-specific prep", "Strong coding platform"], "weaknesses": ["Coding focused", "Lacks soft skills training"], "pricing": "$25/month", "market_share": "15%"},
                    {"name": "PrepInsta", "strengths": ["Affordable plans", "Wide coverage of company patterns"], "weaknesses": ["Outdated user interface", "Minimal AI adaptation"], "pricing": "$10/month", "market_share": "18%"}
                ],
                "indirect_competitors": [
                    {"name": "Coursera", "strengths": ["Massive university courses", "Industry-recognized certificates"], "weaknesses": ["Passive video watching", "No active placement pipeline"], "pricing": "$39/month", "market_share": "25%"},
                    {"name": "Unacademy", "strengths": ["Live teacher classes", "Huge student community"], "weaknesses": ["Generic coaching format", "High subscription prices"], "pricing": "$20-40/month", "market_share": "22%"}
                ],
                "alternative_solutions": [
                    {"name": "Manual coaching and college mock cells", "strengths": ["Human face-to-face feedback", "Direct college trust"], "weaknesses": ["Not scalable", "Inconsistent feedback quality", "Time-consuming"], "pricing": "Free to students", "market_share": "40%"}
                ]
            }

    def _general_competitors(self, idea: str) -> dict[str, list[dict]]:
        return {
            "direct_competitors": [],
            "indirect_competitors": [],
            "alternative_solutions": [],
            "research_alternatives": [],
            "enabling_technologies": []
        }

    def build_insights(self, content: dict[str, Any]) -> list[ExplainableInsight]:
        rec_val = content.get("positioning_strategy", {})
        rec = rec_val.get("claim", "Differentiate through AI-native approach") if isinstance(rec_val, dict) else str(rec_val)
        
        diff = content.get("differentiation", [])
        evidence = [d.get("claim", str(d)) if isinstance(d, dict) else str(d) for d in diff[:2]]
        
        comps_data = content.get("competitors", {})
        if isinstance(comps_data, dict):
            num_competitors = sum(len(v) for v in comps_data.values() if isinstance(v, list))
        else:
            num_competitors = len(comps_data) if isinstance(comps_data, list) else 0
            
        return [
            ExplainableInsight(
                recommendation=rec,
                reasoning=f"Identified {len(content.get('market_gaps', []))} market gaps and {num_competitors} key competitors",
                data_sources=["competitor websites", "app store reviews", "Crunchbase", "NeMo Retriever"],
                confidence=0.82,
                evidence=evidence,
            )
        ]
