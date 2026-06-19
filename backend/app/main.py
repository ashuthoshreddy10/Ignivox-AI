"""Ignivox AI - FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings
from app.services.nemo_retriever import retriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Ignivox AI — NVIDIA Agentic Workflow Platform")
    logger.info("Env file path: %s", settings.env_file_path)
    logger.info("Env file loaded: %s", settings.env_file_loaded)
    logger.info("NVIDIA_API_KEY detected: %s", settings.masked_api_key)
    logger.info("DEMO_MODE=%s", settings.demo_mode)
    logger.info("NVIDIA mode active: %s", settings.use_nvidia)
    await retriever.load()
    yield
    logger.info("Shutting down Ignivox AI")


app = FastAPI(
    title="Ignivox AI",
    description="Autonomous Startup Co-Founder — Multi-Agent Platform powered by NVIDIA Agentic AI",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "Ignivox AI",
        "tagline": "Your Autonomous Startup Co-Founder",
        "version": "1.0.0",
        "docs": "/docs",
        "api": "/api",
        "nvidia_stack": ["NeMo Agent Toolkit", "NIM", "NeMo Retriever", "NeMo Guardrails"],
    }
