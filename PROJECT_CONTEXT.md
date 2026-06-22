# PROJECT_CONTEXT.md — Ignivox AI

> **Last Updated:** 2026-06-22
> **Maintainer:** @ashuthoshreddy10
> **Repository:** `ignivox-ai`

---

## 1. Vision & Purpose

Ignivox AI is a **production-grade, multi-agent AI platform** that acts as an autonomous startup co-founder. A user submits a startup idea; the system orchestrates 10 specialized AI agents that research, reason, validate, and synthesize a complete, investor-ready **Startup Blueprint** — typically in under 5 minutes.

**Core Differentiators:**
- Full NVIDIA Agentic AI stack (NIM inference, NeMo Retriever RAG, NeMo Guardrails safety)
- Evidence-grounded claims with source lineage and verifiable URLs
- Frontier/speculative market detection that dynamically adjusts confidence thresholds
- Human-in-the-loop approval gates for phased decision-making
- Dual-mode operation: live NVIDIA NIM inference *or* deterministic demo mode

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React 18 / Vite)              │
│  ┌───────────┐ ┌──────────────┐ ┌───────────┐ ┌─────────────┐  │
│  │ IdeaInput │ │ CommandCenter│ │ Blueprint │ │InvestorMode │  │
│  └─────┬─────┘ └──────────────┘ │ Workspace │ └─────────────┘  │
│        │  WebSocket / REST       └───────────┘                  │
└────────┼────────────────────────────────────────────────────────┘
         │  /api/ws/generate   /api/generate   /api/blueprint/:id
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI / Python 3.12)             │
│                                                                 │
│  ┌──────────────────┐     ┌──────────────────────────────────┐  │
│  │  API Routes       │────▶│  WorkflowOrchestrator            │  │
│  │  (routes.py)      │     │  (orchestration/workflow.py)     │  │
│  └──────────────────┘     └───────────┬──────────────────────┘  │
│                                       │                         │
│                           ┌───────────▼───────────┐             │
│                           │   Agent Execution Loop │             │
│                           │   (BaseAgent.run())    │             │
│                           └───────────┬───────────┘             │
│                                       │                         │
│        ┌──────────────────────────────┼──────────────────┐      │
│        ▼                              ▼                  ▼      │
│  ┌───────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ NIM LLM   │  │ NeMo         │  │ NeMo         │             │
│  │ Service   │  │ Retriever    │  │ Guardrails   │             │
│  │ (OpenAI)  │  │ (Vector RAG) │  │ (Safety)     │             │
│  └───────────┘  └──────────────┘  └──────────────┘             │
│        │                │                                       │
│        ▼                ▼                                       │
│  ┌───────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │ Live      │  │ Knowledge    │  │ Evidence Utils            │ │
│  │ Research  │  │ Base (JSON)  │  │ (grounding, lineage,     │ │
│  │ (DDG)     │  │              │  │  classification, scoring)│ │
│  └───────────┘  └──────────────┘  └──────────────────────────┘ │
│                                                                 │
│  ┌───────────┐  ┌──────────────┐                                │
│  │ Memory    │  │ Scoring      │                                │
│  │ Service   │  │ Engine       │                                │
│  └───────────┘  └──────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Repository Structure

```
ignivox-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI app entry, lifespan, CORS
│   │   ├── config.py                    # Pydantic Settings, env loading
│   │   ├── agents/
│   │   │   ├── __init__.py              # AGENT_REGISTRY, AGENT_ORDER, AGENT_DEPENDENCIES
│   │   │   ├── base.py                  # BaseAgent ABC, NIM call, post-processing, grounding
│   │   │   ├── orchestrator.py          # Workflow plan generation
│   │   │   ├── novelty_detection.py     # Market maturity & frontier classification
│   │   │   ├── market_research.py       # TAM/SAM/SOM, pain points, growth
│   │   │   ├── competitor.py            # Competitor matrix, SWOT, differentiation
│   │   │   ├── product_strategy.py      # MVP, personas, roadmap
│   │   │   ├── business_strategy.py     # Revenue model, pricing, unit economics
│   │   │   ├── technical_architect.py   # System architecture, tech stack, infra
│   │   │   ├── execution_planning.py    # Sprint roadmap, milestones, launch plan
│   │   │   ├── investor_pitch.py        # Pitch deck slides, funding ask, narrative
│   │   │   └── validation.py            # Cross-agent consistency, evidence scoring
│   │   ├── api/
│   │   │   └── routes.py                # REST + WebSocket endpoints
│   │   ├── models/
│   │   │   └── schemas.py               # Pydantic models (Blueprint, AgentOutput, etc.)
│   │   ├── orchestration/
│   │   │   └── workflow.py              # WorkflowOrchestrator (5-phase pipeline)
│   │   └── services/
│   │       ├── nvidia_nim.py            # NIM LLM inference (OpenAI-compatible)
│   │       ├── nemo_retriever.py        # Vector RAG retrieval + domain filtering
│   │       ├── nemo_guardrails.py       # Output safety checks, hallucination markers
│   │       ├── evidence_utils.py        # Core grounding logic (~1660 lines)
│   │       ├── live_research.py         # DuckDuckGo live web search
│   │       ├── memory.py               # Persistent analysis history & insights
│   │       └── scoring.py              # 5-dimension startup viability scorer
│   ├── knowledge/
│   │   └── startup_knowledge.json       # 40+ RAG knowledge documents
│   ├── data/
│   │   └── memory/                      # Persistent memory database
│   ├── tests/
│   │   └── test_evidence_utils.py       # Unit tests for grounding logic
│   ├── scripts/
│   │   ├── grounding_regression_suite.py
│   │   └── retrieval_benchmark.py
│   ├── run_helios_validation_metrics_v2.py  # Benchmark runner (Helios Grid idea)
│   ├── run_helios_live.py
│   ├── run_custom_idea.py
│   ├── run_5_ideas.py
│   ├── workflow.yml                     # NeMo Agent Toolkit config (optional)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx                      # Main SPA layout, tabs, generation flow
│   │   ├── main.tsx                     # React entry point
│   │   ├── index.css                    # Global styles
│   │   ├── components/
│   │   │   ├── Header.tsx               # NVIDIA mode badge, branding
│   │   │   ├── IdeaInput.tsx            # Startup idea text input
│   │   │   ├── AgentCommandCenter.tsx   # Real-time agent status grid
│   │   │   ├── AgentGraph.tsx           # Agent dependency visualization
│   │   │   ├── BlueprintWorkspace.tsx   # Full blueprint renderer (largest component)
│   │   │   ├── ScoreCard.tsx            # 5-dimension viability score display
│   │   │   ├── InvestorMode.tsx         # Pitch deck slides, funding strategy
│   │   │   └── WorkflowTimeline.tsx     # Event timeline during generation
│   │   ├── lib/
│   │   │   ├── api.ts                   # REST + WebSocket client with fallback
│   │   │   └── types.ts                 # TypeScript interfaces (mirrors schemas.py)
│   │   ├── hooks/                       # (empty — reserved)
│   │   └── pages/                       # (empty — SPA uses tabs in App.tsx)
│   ├── index.html
│   ├── vite.config.ts                   # Dev server proxy: /api → :8000
│   ├── tailwind.config.js               # Custom color palette, Inter font
│   ├── tsconfig.json
│   ├── package.json
│   ├── nginx.conf                       # Production reverse proxy
│   └── Dockerfile                       # Multi-stage build (Node → Nginx)
├── docker-compose.yml                   # Full-stack orchestration
├── .gitignore
├── README.md
└── PROJECT_CONTEXT.md                   # ← This file
```

---

## 4. Agent System

### 4.1 Agent Registry & Execution Order

All agents are singletons registered in `app/agents/__init__.py`:

| Order | Agent Type              | Class                    | NVIDIA Component       |
|-------|-------------------------|--------------------------|------------------------|
| 0     | `orchestrator`          | `OrchestratorAgent`      | NIM Reasoning          |
| 1     | `novelty_detection`     | `NoveltyDetectionAgent`  | NIM Reasoning          |
| 2     | `market_research`       | `MarketResearchAgent`    | NIM + NeMo Retriever   |
| 3     | `competitor`            | `CompetitorAgent`        | NIM + NeMo Retriever   |
| 4     | `product_strategy`      | `ProductStrategyAgent`   | NIM Reasoning          |
| 5     | `business_strategy`     | `BusinessStrategyAgent`  | NIM Reasoning          |
| 6     | `technical_architect`   | `TechnicalArchitectAgent`| NIM Reasoning          |
| 7     | `execution_planning`    | `ExecutionPlanningAgent` | NIM Reasoning          |
| 8     | `investor_pitch`        | `InvestorPitchAgent`     | NIM Reasoning          |
| 9     | `validation`            | `ValidationAgent`        | NIM + NeMo Guardrails  |

### 4.2 Agent Dependency DAG

```
AGENT_DEPENDENCIES = {
    novelty_detection:  []
    market_research:    [novelty_detection]
    competitor:         [market_research]
    product_strategy:   [market_research, competitor]
    business_strategy:  [product_strategy]
    technical_architect:[product_strategy]
    execution_planning: [technical_architect, business_strategy]
    investor_pitch:     [business_strategy, market_research]
    validation:         [ALL agents]
}
```

> Despite the dependency graph, agents currently run **sequentially** in the fixed `AGENT_ORDER` to ensure context is fully built before downstream agents execute.

### 4.3 BaseAgent Lifecycle (`base.py`)

```
1. run() called with (idea, context, rag_context, on_event)
2. If NVIDIA mode → _run_nvidia():
   a. Build system_prompt via get_system_prompt()
   b. Build user_prompt with context + rag_context + GROUNDING_INSTRUCTIONS
   c. For late-stage agents (tech_arch, investor, exec, validation):
      compress context via _get_concise_context_summary()
   d. Call nim_service.complete_json() (with retry on failure)
   e. Parse & validate JSON response
3. If demo mode → get_demo_output()
4. _post_process_output():
   a. sanitize_grounded_claims() — enforce URL/source integrity
   b. enforce_competitor_evidence() — (competitor agent only)
   c. detect/fix template architecture — (tech_architect only)
   d. sanitize_investor_pitch() — (investor_pitch only)
   e. enforce_validation_output() — (validation agent only)
   f. remove_edtech_contamination() — cross-domain leakage filter
5. build_insights() → generate ExplainableInsight list
6. NeMo Guardrails validation (safety check)
7. Return AgentOutput with content, insights, confidence, duration
```

### 4.4 Context Compression

Late-stage agents (Technical Architect, Investor Pitch, Execution Planning, Validation) receive a **compressed context summary** instead of the full raw output from prior agents. The `_get_concise_context_summary()` method:

- Preserves source URLs and claim lineage
- Extracts key fields: market opportunity, competitors, differentiation, MVP features, pricing, ARR projections, unit economics
- Builds a `grounding_map` for the Validation Agent
- Reduces prompt length by 40–60% to fit within NIM token limits

---

## 5. Workflow Pipeline (5 Phases)

Defined in `orchestration/workflow.py` → `WorkflowOrchestrator.generate()`:

| Phase | Agents                                   | Purpose                                         |
|-------|------------------------------------------|--------------------------------------------------|
| 0     | Orchestrator → Novelty Detection         | Plan workflow; classify market maturity           |
| 1     | Market Research                          | TAM/SAM/SOM, pain points, growth rates           |
| 2     | Competitor → Product Strategy            | Competition analysis, then MVP + roadmap          |
| 2.5   | *(Optional)* Human approval gate         | Pause for user review before strategy phases      |
| 3     | Business Strategy → Technical Architect  | Revenue model, then system architecture           |
| 4     | Execution Planning → Investor Pitch      | Sprint roadmap, then pitch deck + funding ask     |
| 5     | Validation                               | Cross-agent consistency, evidence quality audit   |

**Per-agent flow:**
1. Build RAG query: `"{idea} {agent.name} {agent.description}"`
2. Retrieve top-5 documents from `NeMoRetriever`
3. Fetch memory insights from `AgentMemory`
4. Run live web search via `LiveResearchService`
5. Merge all context into `structured_context` JSON
6. Execute agent via `BaseAgent.run()`
7. Update cumulative `evidence_registry` and `claim_lineage`

**Post-workflow:**
- Compute 5-dimension viability score via `ScoringEngine`
- Aggregate recommendations
- Persist to memory
- Write `grounding_audit_log.json` and `audit_diagnostics.json`

---

## 6. NVIDIA Stack Integration

### 6.1 NIM (LLM Inference) — `nvidia_nim.py`

| Setting            | Value                              |
|--------------------|------------------------------------|
| Base URL           | `https://integrate.api.nvidia.com/v1` |
| Model              | `meta/llama-3.3-70b-instruct`     |
| Embedding Model    | `nvidia/nv-embedqa-e5-v5`         |
| Timeout            | 240 seconds                        |
| Max Tokens         | 4096 (8192 for Market Research)    |
| Temperature        | 0.5 for JSON, 0.7 for text        |
| JSON Mode          | Always enabled for agents          |
| Retry              | 1 retry with lower temp + higher token limit |
| Client             | OpenAI-compatible `AsyncOpenAI`    |

**JSON Recovery Pipeline:**
1. Direct `json.loads()`
2. Extract JSON block from surrounding text
3. Repair comma/bracket issues with regex
4. Close truncated JSON structures (balance `{}` and `[]`)
5. Validate schema (for Investor Pitch agent only)

### 6.2 NeMo Retriever — `nemo_retriever.py`

- **Knowledge Base:** `knowledge/startup_knowledge.json` — 40+ curated documents across 10+ industry domains
- **Embedding:** NIM embedding API (1024-dim) or local fallback (384-dim character-hash)
- **Search:** Cosine similarity via `np.dot()` on normalized vectors
- **Domain Filtering:** Documents from mismatched domains are excluded (e.g., EdTech docs won't appear for a FinTech query)
- **Relevance Threshold:** `0.35` (configurable via `settings.retrieval_threshold`)
- **Dimension Mismatch Handling:** Auto-reloads and falls back to local embeddings if dimensions don't align

### 6.3 NeMo Guardrails — `nemo_guardrails.py`

- **Safety Patterns:** Detects `hack`, `exploit`, `guaranteed returns`, `pump and dump`
- **Hallucination Markers:** Flags `cannot verify`, `100% certain`, `absolutely guaranteed`
- **Confidence Adjustment:** Deducts 0.05 per warning from base 0.9

### 6.4 Live Research — `live_research.py`

- **Source:** DuckDuckGo HTML search (`html.duckduckgo.com`)
- **URL Cleaning:** Resolves DDG redirect links, strips tracking parameters, truncates to 120 chars
- **Snippets:** Truncated to 150 chars
- **Integration:** Results added to `structured_context.live_sources[]`

---

## 7. Evidence Grounding System (`evidence_utils.py`)

This is the **core integrity engine** of the platform (~1660 lines). It ensures every claim in the blueprint is traceable, classified, and scored.

### 7.1 Claim Categories

| Category          | Description                                                    | Factual? |
|-------------------|----------------------------------------------------------------|----------|
| `Historical Fact` | Verifiable historical event or performance metric              | ✅ Yes   |
| `Retrieved Fact`  | Industry/market fact retrieved from RAG or live research       | ✅ Yes   |
| `Projection`      | Forward-looking prediction (revenue, growth, ARR)              | ❌ No    |
| `Estimate`        | Approximate calculation (TAM/SAM/SOM, CAC, LTV)               | ❌ No    |
| `Assumption`      | Foundational business or user assumption                       | ❌ No    |
| `Strategy`        | Strategic decision, business model, pricing structure          | ❌ No    |
| `Roadmap`         | MVP timeline, sprint milestones, feature phases                | ❌ No    |
| `Hypothesis`      | Unproven speculative theory                                    | ❌ No    |
| `Recommendation`  | Actionable suggestion from agent analysis                      | ❌ No    |

### 7.2 Classification Rules

The `classify_claim()` function determines a claim's category using **word-boundary matching** (not substring). This is critical to avoid collisions like `"narrative"` matching the projection keyword `"arr"`.

**Helper: `_has_word_match(text, keywords)`**
- Tokenizes `text` on whitespace, hyphens, underscores, punctuation
- Checks each token against the keyword set for exact matches
- Example: `"arr"` matches in `"Projected ARR growth"` but NOT in `"narrative structure"`

**Factual Exclusion Paths:**
Fields containing `market_trends`, `pain_points`, `problem_statement`, `differentiation`, `market_gaps`, `swot`, `rationale` are excluded from Projection/Recommendation classification — these are treated as factual context even if they contain forward-looking language.

### 7.3 Verification Rules

In `enforce_validation_output()`:

| Rule | Description |
|------|-------------|
| Only `Historical Fact` and `Retrieved Fact` claims are eligible for `verified` status |
| Claims must have at least one valid `source_url` with `support_score ≥ threshold` |
| Support score threshold: **0.35** for metrics/financial claims, **0.15** for general claims |
| Competitor/website URLs not supported by the grounding map are rejected |
| Sources are preserved for Projection and Recommendation claims (lineage, not verification) |

### 7.4 Key Exported Functions

| Function                         | Purpose                                                   |
|----------------------------------|-----------------------------------------------------------|
| `classify_claim()`              | Assign claim category using word-boundary matching         |
| `_has_word_match()`             | Tokenized keyword matching (no substring collisions)       |
| `enforce_validation_output()`   | Apply verification rules to all claims                     |
| `enforce_competitor_evidence()` | Validate competitor names/URLs against corpus              |
| `sanitize_grounded_claims()`    | Fix URL integrity, normalize sources                       |
| `sanitize_investor_pitch()`     | Clean pitch deck content, fix formatting                   |
| `build_grounding_map()`         | Build claim→source mapping from all agent outputs          |
| `merge_cumulative_registry()`   | Merge evidence sources across agents                       |
| `accumulate_claim_lineage()`    | Track claim origin and transformation history              |
| `normalize_rag_sources()`       | Clean and deduplicate RAG source entries                    |
| `normalize_url()`               | Strip tracking params, resolve redirects, truncate          |
| `detect_template_architecture()`| Detect lazy/template outputs from Tech Architect           |
| `fix_template_architecture()`   | Replace template placeholders with idea-specific content    |
| `remove_edtech_contamination()` | Remove cross-domain leakage from prior runs                 |

### 7.5 Audit Trail

Every claim evaluation is appended to `EVALUATED_CLAIMS` (a global list), which is written to `grounding_audit_log.json` after each workflow run for debugging and regression testing.

---

## 8. Frontier Mode

When the **Novelty Detection Agent** assigns a `novelty_score > 70`, the system activates **Frontier Mode**:

1. **All agents** receive a dynamic prompt injection:
   - Disable verified market sizing unless explicitly supported by RAG evidence
   - Mark unsupported claims as `generated` / `unverified` / `evidence_strength: low`
   - Cap confidence at 0.60 for speculative claims
   - Reframe tone from facts to strategic hypotheses

2. **Validation Agent** receives additional rules:
   - Flag any `verified` claim lacking concrete external URLs
   - Reject fabricated companies, fake repos, fake launch announcements

---

## 9. Scoring Engine (`scoring.py`)

Five-dimension scoring with weighted aggregation:

| Dimension              | Weight | Data Source            |
|------------------------|--------|------------------------|
| Market Potential        | 25%    | `market_research`      |
| Revenue Potential       | 20%    | `business_strategy`    |
| Technical Feasibility   | 20%    | `technical_architecture`|
| Scalability            | 15%    | `technical_architecture`|
| Competition Intensity   | 20%    | `competitor_analysis`   |

**Overall = Σ(dimension × weight)**, where competition uses `100 - raw_intensity`.

---

## 10. Data Models (`schemas.py`)

### Core Models

| Model              | Purpose                                                 |
|---------------------|---------------------------------------------------------|
| `StartupBlueprint`  | Root object containing all agent outputs, scores, lineage |
| `AgentOutput`       | Single agent's output: content, insights, confidence     |
| `GroundedClaim`     | Claim with sources, category, verification status        |
| `SourceInfo`        | URL, title, timestamp, confidence for a backing source   |
| `EvidenceQualityReport` | Aggregated evidence metrics                          |
| `ExplainableInsight`| Recommendation with reasoning, sources, confidence       |
| `ScoreBreakdown`    | 5-dimension viability scores                            |
| `WorkflowPlan`      | Agent assignments and step dependencies                  |
| `WorkflowEvent`     | Real-time event for WebSocket streaming                  |
| `GenerateRequest`   | Input: idea, industry, generate_idea flag               |
| `CompareRequest`    | Multi-idea comparison input                             |
| `ApprovalRequest`   | Human-in-the-loop approval                              |

---

## 11. API Endpoints

| Method | Path                      | Description                            |
|--------|---------------------------|----------------------------------------|
| `GET`  | `/`                       | Service info and NVIDIA stack list      |
| `GET`  | `/api/health`             | Health check with mode detection        |
| `GET`  | `/api/agents`             | List all registered agents              |
| `GET`  | `/api/agents/status`      | Current agent states                    |
| `POST` | `/api/generate`           | Generate blueprint (REST, synchronous)  |
| `GET`  | `/api/blueprint/{id}`     | Retrieve blueprint by workflow ID       |
| `POST` | `/api/compare`            | Compare 2–5 ideas side by side          |
| `POST` | `/api/approve`            | Submit human-in-the-loop approval       |
| `GET`  | `/api/memory/history`     | Past analysis history                   |
| `GET`  | `/api/memory/patterns`    | Learned patterns and statistics         |
| `GET`  | `/api/graph/dependencies` | Agent dependency DAG (nodes + edges)    |
| `WS`   | `/api/ws/generate`        | Real-time streaming workflow            |

### WebSocket Protocol

1. Client connects to `/api/ws/generate`
2. Client sends `{"idea": "...", "generate_idea": false, "industry": null, "require_approval": false}`
3. Server streams `WorkflowEvent` messages with `type`, `agent`, `status`, `progress`
4. On completion: `{"type": "result", "blueprint": {...}}`
5. On error: `{"type": "error", "message": "..."}`

---

## 12. Frontend Architecture

| Technology       | Version | Usage                                       |
|------------------|---------|---------------------------------------------|
| React            | 18.3    | UI framework                                |
| TypeScript       | 5.7     | Type safety                                 |
| Vite             | 6.0     | Dev server + build                          |
| TailwindCSS      | 3.4     | Utility-first styling                       |
| Framer Motion    | 11.15   | Animations and transitions                  |
| Recharts         | 2.15    | Score visualization charts                  |
| Lucide React     | 0.469   | Icon library                                |

### UI Tabs

| Tab              | Component                | Description                               |
|------------------|--------------------------|-------------------------------------------|
| Command Center   | `AgentCommandCenter.tsx` | Real-time agent status grid during generation |
| Agent Graph      | `AgentGraph.tsx`         | Visual dependency graph of agents          |
| Blueprint        | `BlueprintWorkspace.tsx` | Full rendered blueprint with all sections  |
| Investor Mode    | `InvestorMode.tsx`       | Pitch deck slides, funding strategy view   |

### Design System

- **Color palette:** Custom `ignivox` green scale (50–900) + dark surface palette
- **Font:** Inter (Google Fonts)
- **Dark mode only** with glassmorphism effects
- **Custom classes:** `glass-hover`, `gradient-text`, `card`, `bg-surface`

### Dev Proxy

Vite proxies `/api` to `http://localhost:8000` (FastAPI) with WebSocket support.

---

## 13. Configuration

### Environment Variables (`.env`)

| Variable          | Default                            | Description                      |
|-------------------|------------------------------------|----------------------------------|
| `NVIDIA_API_KEY`  | *(none)*                           | NVIDIA NIM API key               |
| `NIM_MODEL`       | `meta/llama-3.3-70b-instruct`     | LLM model for reasoning          |
| `NIM_EMBED_MODEL` | `nvidia/nv-embedqa-e5-v5`         | Embedding model for RAG          |
| `DEMO_MODE`       | `true`                            | Use deterministic demo outputs   |
| `HOST`            | `0.0.0.0`                          | Server bind address              |
| `PORT`            | `8000`                             | Server port                      |
| `CORS_ORIGINS`    | `http://localhost:5173,...`         | Allowed CORS origins             |

### Mode Detection

```python
use_nvidia = bool(nvidia_api_key) and not demo_mode
```

- **Live Mode:** `DEMO_MODE=false` + valid `NVIDIA_API_KEY` → real NIM inference
- **Demo Mode:** `DEMO_MODE=true` OR missing API key → deterministic `get_demo_output()`

---

## 14. Deployment

### Local Development

```bash
# Backend
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev     # → http://localhost:5173
```

### Docker Compose

```bash
docker-compose up --build
# Backend: :8000
# Frontend: :5173 (Nginx proxies /api → backend:8000)
```

### Production

- **Frontend:** Multi-stage build (Node 20 → Nginx Alpine), serves static SPA
- **Backend:** Python 3.12-slim, uvicorn, knowledge/ and data/ mounted as volumes
- **Nginx:** Handles WebSocket upgrade headers, 600s proxy timeout

---

## 15. Testing & Benchmarking

### Unit Tests

```bash
cd backend
python -m pytest tests/ -v
```

- `test_evidence_utils.py` — Tests word-boundary matching, source preservation, classification

### Benchmark Scripts

| Script                                  | Purpose                                             |
|-----------------------------------------|------------------------------------------------------|
| `run_helios_validation_metrics_v2.py`   | Full pipeline run with Helios Grid idea + metrics report |
| `run_helios_live.py`                    | Live NIM run with detailed logging                    |
| `run_custom_idea.py`                    | Run pipeline for any custom idea                      |
| `run_5_ideas.py`                        | Batch run across 5 diverse startup ideas              |
| `scripts/grounding_regression_suite.py` | Regression test suite for grounding rules             |
| `scripts/retrieval_benchmark.py`        | RAG retrieval quality benchmark                       |

### Metrics Report Format

After running `run_helios_validation_metrics_v2.py`:

```
Historical Facts            : N
Retrieved Facts             : N
Total Factual Claims        : N
Projection Claims           : N
Recommendation Claims       : N
Competitors                 : N
Evidence Quality Score      : N.N
```

---

## 16. Knowledge Base

The RAG knowledge base (`knowledge/startup_knowledge.json`) contains curated documents organized by domain:

| Domain           | Categories covered                                        |
|------------------|------------------------------------------------------------|
| EdTech           | Market size, competitor landscape, campus placement data   |
| HealthTech       | Digital health market, HIPAA/FHIR architecture, competitors|
| FinTech          | Embedded finance, payment APIs, PCI-DSS compliance         |
| Energy / Smart Grid | Grid modernization, SCADA, VPP, telemetry              |
| Cybersecurity    | SIEM, threat detection, zero-trust, SOC operations         |
| Logistics        | Supply chain visibility, fleet optimization, WMS           |
| ClimateTech      | Carbon accounting, ESG, offset marketplaces                |
| Industrial AI    | Predictive maintenance, digital twins, OPC-UA              |
| Enterprise SaaS  | Multi-tenant architecture, SSO/SAML, B2B SaaS benchmarks  |
| Frontier/DeepTech| Quantum computing, neurotechnology, BCI, HPC               |

Each document has: `title`, `category`, `content`. Domain filtering in the retriever prevents cross-contamination between industries.

---

## 17. Key Invariants & Rules

> These rules are critical constraints that must be preserved during any code modification.

1. **Factual Verification Rule:** Only claims categorized as `Historical Fact` or `Retrieved Fact` are eligible to receive `verified` status. All other categories remain `unverified`.

2. **URL Integrity Rule:** Competitor or website URLs not explicitly supported by a valid, verified URL in the system `grounding_map` must have their verification status rejected.

3. **Factual Count Metric Rule:** `factual_claims_count` must be computed by scanning the **entire blueprint** after grounding/classification — NOT just from `validation_report.verified_claims`.

4. **Word-Boundary Matching Rule:** All claim category matching must use tokenized word-boundary matching via `_has_word_match()` — never substring matching. Example: `"arr"` must NOT match `"narrative"`.

5. **Source Preservation Rule:** Even for Projection and Recommendation claims that are not eligible for verification, their `sources` arrays must be preserved to maintain complete claim lineage.

6. **Cross-Domain Contamination Rule:** RAG retrieval and output post-processing must prevent documents from unrelated domains (e.g., EdTech docs appearing in a FinTech blueprint).

7. **Frontier Mode Rule:** When `novelty_score > 70`, the system must dynamically inject frontier disclaimers into all agent prompts and cap confidence at 0.60 for ungrounded claims.

---

## 18. Common Debugging Scenarios

### Claim Count Is Too Low

1. Check `grounding_audit_log.json` for the full list of evaluated claims
2. Verify `classify_claim()` is not misclassifying due to substring collisions
3. Ensure the metric runner scans the **entire blueprint**, not just `verified_claims`

### Competitors Are Missing (Count = 0)

1. Check `enforce_competitor_evidence()` — are legitimate competitors being filtered?
2. Verify competitor URL matching is relaxed (name/domain in corpus is sufficient)
3. Check RAG domain filtering isn't excluding relevant competitor documents

### Agent Timeout

1. Check prompt length in `audit_diagnostics.json` → `prompt_length_before/after`
2. Late-stage agents should use compressed context (40–60% reduction)
3. NIM timeout is 240s; monitor via `execution_time_after` in diagnostics

### JSON Parse Failure

1. Check `logs/investor_pitch_failures.json` for raw LLM responses
2. The recovery pipeline handles truncation, missing commas, and unbalanced brackets
3. Schema validation failures (Investor Pitch) trigger immediate retry

### Cross-Domain Leakage

1. `remove_edtech_contamination()` strips EdTech-specific terms from non-EdTech blueprints
2. RAG domain filtering in `nemo_retriever.py` uses word-set matching per domain
3. Knowledge base documents have explicit `category` fields for domain routing

---

## 19. File Size Reference

| File                                   | Lines  | Purpose                          |
|----------------------------------------|--------|----------------------------------|
| `evidence_utils.py`                    | ~1,660 | Core grounding/classification    |
| `base.py`                              | ~781   | Agent execution framework        |
| `BlueprintWorkspace.tsx`               | ~930   | Blueprint UI renderer            |
| `workflow.py`                          | ~492   | Orchestration engine             |
| `nemo_retriever.py`                    | ~228   | RAG vector search                |
| `nvidia_nim.py`                        | ~287   | NIM LLM integration              |
| `validation.py`                        | ~318   | Validation agent                 |
| `technical_architect.py`               | ~580   | Tech architecture agent          |
| `market_research.py`                   | ~570   | Market research agent            |
| `competitor.py`                        | ~550   | Competitor intelligence agent    |

---

## 20. Dependencies

### Backend (Python 3.12)

| Package             | Version   | Purpose                         |
|---------------------|-----------|---------------------------------|
| `fastapi`           | 0.115.6   | Web framework                   |
| `uvicorn[standard]` | 0.34.0    | ASGI server                     |
| `websockets`        | 14.1      | WebSocket protocol              |
| `pydantic`          | 2.10.4    | Data validation                 |
| `pydantic-settings`  | 2.7.0    | Environment-based config        |
| `httpx`             | 0.28.1    | Async HTTP client               |
| `openai`            | 1.58.1    | NIM-compatible LLM client       |
| `python-dotenv`     | 1.0.1     | `.env` loading                  |
| `numpy`             | 2.2.1     | Vector math for RAG             |
| `aiofiles`          | 24.1.0    | Async file I/O                  |
| `python-multipart`  | 0.0.20    | Form data parsing               |

### Frontend (Node 18+)

| Package            | Version   | Purpose                          |
|--------------------|-----------|----------------------------------|
| `react`            | ^18.3.1   | UI framework                     |
| `react-dom`        | ^18.3.1   | DOM rendering                    |
| `lucide-react`     | ^0.469.0  | Icon library                     |
| `framer-motion`    | ^11.15.0  | Animations                       |
| `recharts`         | ^2.15.0   | Chart visualizations             |
| `tailwindcss`      | ^3.4.17   | Utility CSS (dev)                |
| `typescript`       | ^5.7.2    | Type safety (dev)                |
| `vite`             | ^6.0.5    | Build tool (dev)                 |
