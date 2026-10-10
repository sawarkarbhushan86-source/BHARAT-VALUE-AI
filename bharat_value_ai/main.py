"""Bharat Value AI - Application Entrypoint."""
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from bharat_value_ai.config import settings
from bharat_value_ai.core.database import init_db
from bharat_value_ai.rag.document_parser import doc_parser_service
from bharat_value_ai.api.routes import api_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI-Powered Indian Stock Market Intelligence, Valuation, Financial News NLP, RAG & Multibagger Research Platform"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and Templates
static_dir = BASE_DIR / "ui" / "static"
templates_dir = BASE_DIR / "ui" / "templates"
static_dir.mkdir(parents=True, exist_ok=True)
templates_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# Include API Router
app.include_router(api_router)

@app.on_event("startup")
def on_startup():
    """Initialize DB and seed RAG vector knowledge base."""
    init_db()
    try:
        doc_parser_service.seed_initial_knowledge_base()
    except Exception as e:
        print(f"Warning: RAG seeding encountered error: {e}")

@app.get("/", response_class=HTMLResponse)
def serve_dashboard(request: Request):
    """Serve the primary Fintech Research Platform UI."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_name": settings.app_name}
    )

