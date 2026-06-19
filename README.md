# Ignivox AI — Autonomous Startup Co-Founder

Ignivox AI is a production-grade multi-agent platform that functions as an autonomous startup co-founder. Transform any idea into a complete, investor-ready business blueprint in minutes through collaboration between 9 specialized AI agents powered by NVIDIA's Agentic AI ecosystem.

![Ignivox AI](https://img.shields.io/badge/NVIDIA-Agentic%20AI-76B900?style=for-the-badge&logo=nvidia)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)

## Vision

Entrepreneurs spend weeks validating ideas, researching competitors, designing MVPs, and preparing investor presentations. Ignivox AI reduces this to **minutes** — simulating an elite founding team that researches, reasons, verifies, and executes autonomously.

## Architecture

```
User Input → Orchestrator Agent
                ├── Market Research Agent      (NeMo Retriever RAG)
                ├── Competitor Intel Agent     (NeMo Retriever RAG)
                ├── Product Strategy Agent     (NIM Reasoning)
                ├── Business Strategy Agent    (NIM Reasoning)
                ├── Technical Architect Agent  (NIM Reasoning)
                ├── Execution Planning Agent   (NIM Reasoning)
                ├── Investor Pitch Agent       (NIM Reasoning)
                └── Validation Agent           (NeMo Guardrails)
                          ↓
              Startup Blueprint + Score + Pitch Deck
```

## NVIDIA Integration

| Component | Usage |
|-----------|-------|
| **NVIDIA NIM** | LLM inference for all agent reasoning, planning, and decision-making |
| **NeMo Agent Toolkit** | Multi-agent orchestration and workflow coordination |
| **NeMo Retriever** | RAG-powered knowledge retrieval for market research and competitor intelligence |
| **NeMo Guardrails** | Output validation, safety checks, and hallucination prevention |

## Multi-Agent System

| Agent | Purpose |
|-------|---------|
| **Orchestrator** | Central coordinator — breaks objectives into subtasks, assigns agents, aggregates outputs |
| **Market Research** | TAM/SAM/SOM analysis, pain points, market trends |
| **Competitor Intel** | Competitor matrix, SWOT, differentiation strategy |
| **Product Strategy** | MVP definition, feature roadmap, user personas |
| **Business Strategy** | Revenue model, pricing, GTM strategy, unit economics |
| **Technical Architect** | Tech stack, system architecture, infrastructure blueprint |
| **Execution Planning** | Sprint roadmap, milestones, launch checklist |
| **Investor Pitch** | Pitch deck slides, executive summary, funding strategy |
| **Validation** | Cross-agent consistency checks, feasibility scoring, risk assessment |

## Features

- **Startup Command Center** — Real-time agent status, workflow progress, task timeline
- **Agent Collaboration Graph** — Visualize agent interactions and data flow
- **Blueprint Workspace** — Complete startup analysis with explainable AI insights
- **Investor Mode** — Pitch deck, executive summary, funding recommendations
- **Startup Scoring Engine** — 100-point viability score across 5 dimensions
- **Agent Memory System** — Persistent history and learned patterns
- **Multi-Idea Comparison** — Side-by-side startup idea evaluation
- **Human-in-the-Loop** — Optional approval gates during workflow
- **Explainable AI** — Every recommendation includes reasoning, sources, and confidence

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- NVIDIA API Key (optional — demo mode works without it)

### 1. Clone & Setup

```bash
cd ignivox-ai

# Backend
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env

# Frontend
cd ../frontend
npm install
```

### 2. Configure (Optional)

Edit `backend/.env` to enable live NVIDIA NIM inference:

```env
NVIDIA_API_KEY=your_key_from_build.nvidia.com
DEMO_MODE=false
NIM_MODEL=meta/llama-3.3-70b-instruct
```

### 3. Run

```bash
# Terminal 1 — Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Open **http://localhost:5173**

### Docker

```bash
docker-compose up --build
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/generate` | Generate startup blueprint |
| `GET` | `/api/blueprint/{id}` | Get blueprint by ID |
| `POST` | `/api/compare` | Compare multiple ideas |
| `WS` | `/api/ws/generate` | Real-time workflow streaming |
| `GET` | `/api/agents` | List all agents |
| `GET` | `/api/graph/dependencies` | Agent collaboration graph |
| `GET` | `/api/memory/history` | Analysis history |
| `POST` | `/api/approve` | Human-in-the-loop approval |

## Example Usage

**Input:**
> "Build an AI platform for college students to improve placement preparation."

**Output:**
- Market opportunity analysis with TAM/SAM/SOM
- Competitor matrix with 4+ competitors analyzed
- MVP scope with 8-12 week timeline
- Freemium revenue model with unit economics
- Event-driven microservices architecture
- 6-sprint development roadmap
- 9-slide investor pitch deck
- Viability score out of 100

## Project Structure

```
ignivox-ai/
├── backend/
│   ├── app/
│   │   ├── agents/          # 9 specialized AI agents
│   │   ├── services/        # NVIDIA NIM, Retriever, Guardrails, Memory, Scoring
│   │   ├── orchestration/   # Multi-agent workflow engine
│   │   ├── api/             # FastAPI routes + WebSocket
│   │   └── models/          # Pydantic schemas
│   ├── knowledge/           # RAG knowledge base
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # Dashboard UI components
│   │   └── lib/             # API client & types
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Tech Stack

**Backend:** Python, FastAPI, WebSockets, Pydantic, ChromaDB
**Frontend:** React 18, TypeScript, TailwindCSS, Framer Motion, Recharts
**AI/ML:** NVIDIA NIM, NeMo Agent Toolkit, NeMo Retriever, NeMo Guardrails

## License

MIT
