"""Technical Architect Agent."""

from datetime import datetime
from typing import Any

from app.agents.base import BaseAgent
from app.models.schemas import AgentType, ExplainableInsight


class TechnicalArchitectAgent(BaseAgent):
    agent_type = AgentType.TECHNICAL_ARCHITECT
    name = "Technical Architect Agent"
    description = "Designs scalable technical infrastructure and architecture"

    def get_system_prompt(self, context: dict[str, Any] | None = None) -> str:
        return """You are the Technical Architect Agent for Ignivox AI.
Design system architecture powered by NVIDIA AI stack. Return JSON with this exact structure:
{
  "tech_stack": {
    "frontend": {
      "claim": "Next.js 14, TypeScript, TailwindCSS (domain-specific UI libraries as required)",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    },
    "backend": {
      "claim": "FastAPI, Celery, domain-specific middleware (e.g. LTI 1.3, FHIR, Kafka, MQTT)",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    },
    "ai_ml": {
      "claim": "NVIDIA NIM (Llama 3.3 70B), NeMo Agent Toolkit, NeMo Retriever, domain models",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.95}],
      "confidence": 0.95
    },
    "database": {
      "claim": "PostgreSQL, Redis, and domain stores (TimescaleDB, InfluxDB, Neo4j, ChromaDB as needed)",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    }
  },
  "architecture": {
    "pattern": {
      "claim": "Event-driven microservices with domain-specific integration boundaries",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    },
    "components": [
      {"name": "Component Name (e.g. IoT Telemetry Ingestion Hub, FHIR Connector, LTI Launch Handler)", "role": "Specific role of the component in the custom domain"}
    ],
    "diagram_description": "Data flow mapping among components"
  },
  "database_schema": {
    "schema_description": {
      "claim": "Relational and domain-specific tables aligned to the startup use case",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.85}],
      "confidence": 0.85
    },
    "custom_table_1": "comma-separated columns matching custom domain entities",
    "custom_table_2": "comma-separated columns matching custom domain entities"
  },
  "infrastructure": {
    "provider_and_compute": {
      "claim": "AWS Cloud / Azure / Hybrid hosting with NVIDIA NIM GPU endpoints",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    },
    "estimated_monthly_cost_mvp": {
      "claim": "$800-2500 depending on volume",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.85}],
      "confidence": 0.85
    }
  },
  "mvp_scope": {
    "timeline_and_resources": {
      "claim": "timeline estimate with resources matching the system scale",
      "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
      "confidence": 0.90
    },
    "critical_path": ["Milestone 1", "Milestone 2"]
  },
  "deployment_strategy": {
    "claim": "Docker Compose for development and Kubernetes (EKS/GKE) for production with NVIDIA NIM sidecars",
    "sources": [{"source_url": "...", "source_title": "...", "retrieval_timestamp": "...", "confidence_score": 0.90}],
    "confidence": 0.90
  }
}

DOMAIN ARCHITECTURE RULE:
- NEVER parrot back the bracketed template descriptions or placeholder text from the schema definition (e.g., do NOT output "customized frontend frameworks and libraries...", "customized backend frameworks...", "customized database systems...", "customized pattern description...", "customized schema description...", etc.). You must replace these placeholder values with actual, specific, real-world technologies, architectures, and descriptions.
- Customize the technical stack, database schemas, database types, architecture patterns, and components according to the startup domain:
  - Energy/Infrastructure: Focus on IoT telemetry ingestion, SCADA/ICS integration, digital twins, time-series forecasting databases (InfluxDB/TimescaleDB), Apache Kafka event streaming, Edge AI endpoints, infrastructure graph DB (Neo4j).
  - Healthcare: Focus on HIPAA compliance, HL7/FHIR APIs, secure data vault schemas, medical imaging stores, secure federated learning, and high-trust audit logging.
  - Education: Focus on student database, LMS integration (LTI v1.3 standard), SCORM compliant data models, adaptive learning graphs, and secure assessment lock-downs.
  - Enterprise SaaS: Focus on multi-tenant tenant isolation keys, OAuth2/SSO, Redis cache, Celery worker nodes, and Stripe subscription invoicing.
  - Fintech: Focus on double-entry ledger database schema, PCI-DSS compliance, real-time transaction registers, and audit logs.
  - Cybersecurity: Focus on SIEM event streaming, threat ingestion pipelines, anomaly detection engines, and tamper-proof log storage.
  - Supply Chain: Focus on RFID/IoT tracking, logistics graph queries, inventory ledger schemas, and warehouse sync queues.
- Do NOT always default to the basic React + FastAPI + PostgreSQL stack if the startup is in a specialized domain (like smart grid telemetry, sensor management, or medical diagnostics).
"""

    def get_demo_output(self, idea: str, context: dict[str, Any]) -> dict[str, Any]:
        idea_lower = idea.lower()
        timestamp = datetime.utcnow().isoformat() + "Z"
        sources = [
            {"source_url": "https://developer.nvidia.com/nemo-framework", "source_title": "NVIDIA NeMo Framework Documentation", "retrieval_timestamp": timestamp, "confidence_score": 0.98},
            {"source_url": "https://aws.amazon.com/eks/", "source_title": "AWS Elastic Kubernetes Service", "retrieval_timestamp": timestamp, "confidence_score": 0.95}
        ]

        if any(w in idea_lower for w in ["energy", "electricity", "utility", "grid", "infrastructure", "telemetry", "maintenance", "sensor", "scada", "iot"]):
            frontend_stack = "React 18, TypeScript, TailwindCSS, WebGL/Three.js (for Digital Twins)"
            backend_stack = "Python FastAPI, Apache Kafka / RabbitMQ (for telemetry streaming), Celery, Edge AI agents"
            db_stack = "TimescaleDB / InfluxDB (time-series telemetry), PostgreSQL, Redis, Neo4j (infrastructure graph)"
            pattern = "Lambda architecture (batch + real-time telemetry streaming)"
            components = [
                {"name": "IoT Telemetry Ingestion Hub", "role": "Ingest high-frequency SCADA/sensor streams via MQTT/Kafka"},
                {"name": "Digital Twin Engine", "role": "Maintain state and status of physical utility grid elements"},
                {"name": "Predictive Forecasting Service", "role": "Time-series forecasting models for anomaly and load detection"},
                {"name": "Edge AI Agent Coordinator", "role": "Sync and orchestrate models deployed at the substation edge"},
                {"name": "NIM Inference Service", "role": "LLM reasoning via NVIDIA NIM API"},
                {"name": "RAG Knowledge Service", "role": "NeMo Retriever accessing equipment manuals and operating docs"}
            ]
            schema_desc = "TimescaleDB for high-frequency telemetry tables and PostgreSQL for relational schemas"
            schema_details = {
                "users": "id, email, name, role, created_at",
                "workflows": "id, user_id, idea, status, created_at",
                "telemetry_stream": "timestamp, sensor_id, metric_name, value, anomaly_flag",
                "grid_elements": "id, type, location_lat, location_lng, status, manufacturer_spec",
                "maintenance_logs": "id, element_id, issue_type, priority, assigned_team, status"
            }
        elif any(w in idea_lower for w in ["health", "medical", "patient", "clinic", "hospital", "doctor", "diagnose", "treatment"]):
            frontend_stack = "Next.js 14, TypeScript, TailwindCSS, secure patient portal"
            backend_stack = "FastAPI with HIPAA-compliant encryption, FHIR standard REST APIs, Celery"
            db_stack = "PostgreSQL (encrypted at rest), Redis, Vector DB (ChromaDB for medical RAG)"
            pattern = "Zero-Trust Microservices Architecture"
            components = [
                {"name": "API Gateway with Audit Logger", "role": "Secure HL7/FHIR mapping, authorization, and absolute access audit logging"},
                {"name": "FHIR Connector", "role": "Integrate securely with EPIC/Cerner health record databases"},
                {"name": "Medical Diagnostic Service", "role": "NVIDIA Clara pipeline for medical imaging and diagnostics"},
                {"name": "NIM Inference Service", "role": "LLM reasoning via NVIDIA NIM API"},
                {"name": "RAG Knowledge Service", "role": "NeMo Retriever accessing medical knowledge graph"}
            ]
            schema_desc = "HIPAA-compliant encrypted tables with full audit trails"
            schema_details = {
                "users": "id, email, password_hash, mfa_secret, role, created_at",
                "workflows": "id, user_id, patient_id, status, created_at",
                "patients": "id, first_name_encrypted, last_name_encrypted, dob_encrypted, fhir_id",
                "audit_logs": "id, user_id, action, target_table, record_id, timestamp",
                "medical_records": "id, patient_id, clinical_notes_encrypted, diagnoses_codes"
            }
        elif any(w in idea_lower for w in ["student", "college", "placement", "education", "lms", "learn", "academic", "university", "career"]):
            frontend_stack = "Next.js 14, TypeScript, TailwindCSS, Outfit Font"
            backend_stack = "Python FastAPI, LTI v1.3 Middleware, Celery"
            db_stack = "PostgreSQL, Redis, ChromaDB (vector store)"
            pattern = "Event-driven microservices with educational standards mapping"
            components = [
                {"name": "API Gateway / LTI Launch Handler", "role": "Validate LTI v1.3 requests and map institutional contexts"},
                {"name": "Adaptive Curriculum Engine", "role": "Generate dynamic graph-based learning paths based on skills assessment"},
                {"name": "Automated Evaluation Service", "role": "Evaluate exams and assignments and sync scores to Canvas gradebook"},
                {"name": "NIM Inference Service", "role": "LLM reasoning via NVIDIA NIM API"},
                {"name": "RAG Student Support Assistant", "role": "NeMo Retriever accessing course syllabus, notes, and guidelines"}
            ]
            schema_desc = "Standard academic relations and adaptive capability mapping tables"
            schema_details = {
                "users": "id, email, name, role (student/instructor), created_at",
                "workflows": "id, user_id, idea, status, created_at",
                "students": "id, user_id, enrollment_no, cgpa, resume_url",
                "courses": "id, name, code, syllabus_text",
                "adaptive_learning_paths": "id, student_id, node_id, status (unlocked/completed), confidence"
            }
        elif any(w in idea_lower for w in ["fintech", "finance", "payment", "bank", "invest", "crypto", "trading", "ledger", "double-entry"]):
            frontend_stack = "React 18, TypeScript, TailwindCSS, high-frequency charts"
            backend_stack = "Python FastAPI, WebSockets (for live quotes/transactions), Celery billing workers"
            db_stack = "PostgreSQL (with transaction levels enabled), Redis cache, InfluxDB (for price ticker)"
            pattern = "CQRS (Command Query Responsibility Segregation) with Ledger"
            components = [
                {"name": "API Gateway / Auth Broker", "role": "Route requests, PCI-DSS tokenization, rate limiting"},
                {"name": "Transaction Validator", "role": "Verify ledger entries and balance double-entry accounts"},
                {"name": "NIM Fraud Detection Service", "role": "Real-time NIM inference checks on transactional patterns"},
                {"name": "NIM Inference Service", "role": "LLM reasoning via NVIDIA NIM API"},
                {"name": "RAG Account Assistant", "role": "NeMo Retriever accessing user portfolio and compliance rules"}
            ]
            schema_desc = "PCI-compliant double-entry accounting ledger schemas"
            schema_details = {
                "users": "id, email, name, level, created_at",
                "workflows": "id, user_id, idea, status, created_at",
                "accounts": "id, user_id, account_type, currency, balance",
                "transactions": "id, debit_account_id, credit_account_id, amount, description, timestamp",
                "audit_registers": "id, transaction_id, verification_hash, verified_status"
            }
        elif any(w in idea_lower for w in ["cybersecurity", "security", "threat", "hack", "penetration", "siem", "firewall", "log"]):
            frontend_stack = "React 18, TypeScript, TailwindCSS, custom SIEM graph visuals"
            backend_stack = "FastAPI, Apache Kafka (log streamer), Celery background analyzers"
            db_stack = "ClickHouse (log analytics), PostgreSQL, Redis, Elasticsearch"
            pattern = "Log Ingestion and Stream Processing pipeline"
            components = [
                {"name": "Log Collection Agent", "role": "Gather system/network audit logs and stream via syslog/beats"},
                {"name": "SIEM Stream Processor", "role": "Filter and correlate event messages using Apache Flink/Kafka"},
                {"name": "NIM Threat Predictor", "role": "NIM inference running threat categorization on log anomalies"},
                {"name": "NIM Inference Service", "role": "LLM reasoning via NVIDIA NIM API"},
                {"name": "RAG Playbook Assistant", "role": "NeMo Retriever mapping security threats to mitigation playbooks"}
            ]
            schema_desc = "Optimized clickstream and log event ingestion tables"
            schema_details = {
                "users": "id, email, name, role, created_at",
                "workflows": "id, user_id, idea, status, created_at",
                "threat_events": "timestamp, host_ip, event_severity, alert_details, resolved_status",
                "mitigation_playbooks": "id, signature_pattern, playbook_markdown, author",
                "security_audits": "id, event_id, auditor_id, resolution_notes, timestamp"
            }
        elif any(w in idea_lower for w in ["supply chain", "logistics", "shipping", "warehouse", "inventory", "rfid", "delivery"]):
            frontend_stack = "React 18, TypeScript, TailwindCSS, Leaflet.js maps"
            backend_stack = "Python FastAPI, Celery scheduling workers, RabbitMQ queue"
            db_stack = "PostgreSQL (with GIS extension PostGIS), Redis, Neo4j (logistics route graph)"
            pattern = "GIS-aware asset tracking and logistics orchestration pattern"
            components = [
                {"name": "Logistics Route Optimizer", "role": "Neo4j graph queries to determine optimal path segments"},
                {"name": "RFID/Sensor Coordinator", "role": "Ingest location telemetry and inventory status updates"},
                {"name": "NIM Supply Advisor", "role": "NIM inference predicting stock replenishment schedules"},
                {"name": "NIM Inference Service", "role": "LLM reasoning via NVIDIA NIM API"},
                {"name": "RAG Supplier Docs", "role": "NeMo Retriever accessing supplier agreements and shipping manifests"}
            ]
            schema_desc = "Relational inventory schemas with PostGIS geospatial coordinates"
            schema_details = {
                "users": "id, email, name, created_at",
                "workflows": "id, user_id, idea, status, created_at",
                "warehouses": "id, name, location_geom (GIS point), capacity",
                "inventory_ledger": "id, item_code, quantity, location_warehouse_id, last_updated",
                "shipping_routes": "id, origin_warehouse_id, dest_warehouse_id, current_coordinates, status"
            }
        else:
            frontend_stack = "React 18, TypeScript, TailwindCSS, Vite"
            backend_stack = "Python FastAPI, OAuth2/SSO, Celery"
            db_stack = "PostgreSQL (Tenant-separated schema), Redis, ChromaDB"
            pattern = "multi-tenant event-driven microservices architecture"
            components = [
                {"name": "API Gateway / SSO Router", "role": "Route requests, authenticate tenants, rate limit users"},
                {"name": "Agent Orchestrator", "role": "NeMo-powered multi-agent workflow coordination"},
                {"name": "NIM Inference Service", "role": "LLM reasoning via NVIDIA NIM API"},
                {"name": "RAG Service", "role": "NeMo Retriever for knowledge-augmented responses"},
                {"name": "Guardrails Service", "role": "NeMo Guardrails for output validation"},
                {"name": "WebSocket Hub", "role": "Real-time agent status streaming"},
                {"name": "Memory Store", "role": "Agent memory and user history persistence"},
            ]
            schema_desc = "Tenant-separated relational database mapping for multi-tenant software models"
            schema_details = {
                "tenants": "id, name, domain, stripe_customer_id, plan_level, created_at",
                "users": "id, tenant_id, email, name, role, created_at",
                "workflows": "id, tenant_id, user_id, idea, status, created_at",
                "agent_outputs": "id, workflow_id, agent_type, content_json, confidence",
                "memory": "id, tenant_id, category, content, embedding_vector, timestamp",
            }

        return {
            "tech_stack": {
                "frontend": {
                    "claim": frontend_stack,
                    "sources": sources[1:],
                    "confidence": 0.92
                },
                "backend": {
                    "claim": backend_stack,
                    "sources": sources[1:],
                    "confidence": 0.94
                },
                "ai_ml": {
                    "claim": "NVIDIA NIM (Llama 3.3 70B), NeMo Agent Toolkit, NeMo Retriever, NeMo Guardrails",
                    "sources": sources[:1],
                    "confidence": 0.97
                },
                "database": {
                    "claim": db_stack,
                    "sources": sources,
                    "confidence": 0.93
                }
            },
            "architecture": {
                "pattern": {
                    "claim": pattern,
                    "sources": sources[:1],
                    "confidence": 0.92
                },
                "components": components,
                "diagram_description": "Client → API Gateway → Orchestrator → [Agent Pool] → NIM/Retriever/Guardrails → Response Aggregator → Client",
            },
            "database_schema": {
                "schema_description": {
                    "claim": schema_desc,
                    "sources": sources,
                    "confidence": 0.90
                },
                **schema_details
            },
            "infrastructure": {
                "provider_and_compute": {
                    "claim": "AWS Cloud with Amazon EKS and self-hosted NVIDIA NIM GPU nodes",
                    "sources": sources[1:],
                    "confidence": 0.94
                },
                "estimated_monthly_cost_mvp": {
                    "claim": "$800-1500/month",
                    "sources": sources[1:],
                    "confidence": 0.88
                }
            },
            "mvp_scope": {
                "timeline_and_resources": {
                    "claim": "8-10 weeks with 4 engineers (2 backend, 1 frontend, 1 ML/AI)",
                    "sources": sources[:1],
                    "confidence": 0.91
                },
                "critical_path": ["Auth + API", "Agent orchestration", "NIM integration", "Dashboard UI"],
            },
            "deployment_strategy": {
                "claim": "Docker Compose for local development, AWS EKS for scalable production running NVIDIA NIM microservices",
                "sources": sources,
                "confidence": 0.93
            }
        }

    def build_insights(self, content: dict[str, Any]) -> list[ExplainableInsight]:
        architecture = content.get("architecture", {})
        components = architecture.get("components", []) if isinstance(architecture, dict) else []
        evidence = [
            c.get("name", str(c)) if isinstance(c, dict) else str(c)
            for c in components[:4]
        ]
        
        deployment = content.get("deployment_strategy", {})
        dep_claim = deployment.get("claim", str(deployment)) if isinstance(deployment, dict) else str(deployment)
        
        return [
            ExplainableInsight(
                recommendation=f"Deploy on AWS EKS using: {dep_claim}",
                reasoning="Enables independent agent scaling, GPU-optimized LLM inference, and real-time workflow streaming",
                data_sources=["NVIDIA NeMo Agent Toolkit docs", "cloud architecture best practices"],
                confidence=0.90,
                evidence=evidence or ["Microservices architecture"],
            )
        ]
