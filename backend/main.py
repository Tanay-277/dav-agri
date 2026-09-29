import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.core.config import settings, log_startup_configuration
from app.database.session import SessionLocal
from app.database.init_db import init_db
from app.api.v1.router import api_router
from app.schemas.common import APIResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("dav")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Log startup diagnostic summary
    log_startup_configuration()

    logger.info("Initializing DAV database schema and default crops...")
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    logger.info("DAV Backend Platform ready at /api/v1")
    yield
    logger.info("DAV Backend shutting down.")

app = FastAPI(
    title="DAV — Agricultural Intelligence API",
    description="Platform-independent REST API powering mobile and web agricultural intelligence for farmers.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    clean_errors = [{"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")} for err in errors]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=APIResponse.fail(
            code="VALIDATION_ERROR",
            message="Request input validation failed",
            details={"errors": clean_errors}
        ).model_dump()
    )

# Generic Uncaught Error Handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse.fail(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected server error occurred. Please try again."
        ).model_dump()
    )

# Root & Health Endpoints
@app.get("/", response_class=HTMLResponse, tags=["Root"])
def root():
    ai_status = "GEMINI (Real API)" if settings.GEMINI_API_KEY else "MOCK (Development)"
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DAV — Digital Agricultural Voice | Backend Status</title>
  <style>
    :root {{
      --bg: #1c1917;
      --card-bg: #292524;
      --border: #44403c;
      --accent: #10b981;
      --text: #f5f5f4;
      --text-muted: #a8a29e;
      --btn-bg: #eab308;
      --btn-text: #1c1917;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 1.5rem;
    }}
    .status-card {{
      background-color: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 1.5rem;
      padding: 2.5rem;
      max-width: 520px;
      width: 100%;
      box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5), 0 8px 10px -6px rgba(0,0,0,0.5);
    }}
    .header {{
      text-align: center;
      margin-bottom: 2rem;
    }}
    .title {{
      font-size: 2.5rem;
      font-weight: 900;
      letter-spacing: -0.05em;
      color: #fafaf9;
    }}
    .subtitle {{
      font-size: 1rem;
      font-weight: 500;
      color: var(--text-muted);
      margin-top: 0.25rem;
    }}
    .status-badge-container {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      background-color: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 0.75rem 1.25rem;
      border-radius: 9999px;
      margin-bottom: 1.5rem;
    }}
    .status-badge-title {{
      font-size: 0.875rem;
      font-weight: 600;
      color: #e7e5e4;
    }}
    .status-pill {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.875rem;
      font-weight: 700;
      color: var(--accent);
    }}
    .pulse-dot {{
      width: 0.625rem;
      height: 0.625rem;
      background-color: var(--accent);
      border-radius: 50%;
      box-shadow: 0 0 10px var(--accent);
      animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.5; transform: scale(1.2); }}
    }}
    .version-meta {{
      font-size: 0.8125rem;
      color: var(--text-muted);
      text-align: center;
      margin-bottom: 1.5rem;
    }}
    .services-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      margin-bottom: 2rem;
    }}
    .service-item {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem 1rem;
      background-color: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 0.75rem;
      font-size: 0.875rem;
    }}
    .service-name {{
      font-weight: 500;
      color: #d6d3d1;
    }}
    .service-status {{
      font-weight: 600;
      color: #38bdf8;
      font-size: 0.8125rem;
    }}
    .service-status.online {{
      color: var(--accent);
    }}
    .actions {{
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0.875rem 1.5rem;
      border-radius: 9999px;
      font-size: 0.9375rem;
      font-weight: 700;
      text-decoration: none;
      transition: all 0.2s ease;
      cursor: pointer;
    }}
    .btn-primary {{
      background-color: var(--btn-bg);
      color: var(--btn-text);
      box-shadow: 0 4px 6px -1px rgba(234, 179, 8, 0.2);
    }}
    .btn-primary:hover {{
      background-color: #facc15;
      transform: translateY(-1px);
    }}
    .btn-secondary {{
      background-color: transparent;
      color: var(--text-muted);
      border: 1px solid var(--border);
      font-size: 0.8125rem;
      font-weight: 600;
    }}
    .btn-secondary:hover {{
      background-color: rgba(255, 255, 255, 0.05);
      color: var(--text);
    }}
  </style>
</head>
<body>
  <div class="status-card">
    <div class="header">
      <h1 class="title">DAV</h1>
      <p class="subtitle">Digital Agricultural Voice</p>
    </div>

    <div class="status-badge-container">
      <span class="status-badge-title">Backend Status</span>
      <span class="status-pill">
        <span class="pulse-dot"></span>
        ONLINE
      </span>
    </div>

    <div class="version-meta">
      Version: 1.0.0 &bull; Environment: {settings.ENVIRONMENT}
    </div>

    <ul class="services-list">
      <li class="service-item">
        <span class="service-name">API</span>
        <span class="service-status online">ONLINE</span>
      </li>
      <li class="service-item">
        <span class="service-name">Weather</span>
        <span class="service-status online">Open-Meteo</span>
      </li>
      <li class="service-item">
        <span class="service-name">Voice / TTS</span>
        <span class="service-status online">AVAILABLE</span>
      </li>
      <li class="service-item">
        <span class="service-name">AI</span>
        <span class="service-status">{ai_status}</span>
      </li>
      <li class="service-item">
        <span class="service-name">Authentication</span>
        <span class="service-status online">AVAILABLE</span>
      </li>
    </ul>

    <div class="actions">
      <a href="/docs" class="btn btn-primary">Open API Documentation</a>
      <a href="/health" class="btn btn-secondary">Machine Health: /health</a>
    </div>
  </div>
</body>
</html>"""
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "dav-backend", "version": "1.0.0"}

# Convenience redirects for /api/v1/docs
@app.get("/api/v1/docs", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/api/v1/openapi.json", include_in_schema=False)
def redirect_to_openapi():
    return RedirectResponse(url="/openapi.json")

# Mount API v1
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
