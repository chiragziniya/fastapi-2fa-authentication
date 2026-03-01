import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine
from app.routers import auth, otp_accounts

settings = get_settings()

# ── Logging ────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO if settings.environment == "production" else logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("authbox")


# ── Lifecycle ──────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — env=%s", settings.environment)
    yield
    # Dispose connection pool on shutdown
    await engine.dispose()
    logger.info("Shut down — connection pool disposed")


# ── App ────────────────────────────────────────────────────────────
app = FastAPI(
    title="Private Auth Box API",
    version="1.0.0",
    docs_url="/api/docs" if settings.environment != "production" else None,
    redoc_url="/api/redoc" if settings.environment != "production" else None,
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────
allowed_origins = [settings.frontend_url]
if settings.allowed_origins:
    allowed_origins.extend([o.strip() for o in settings.allowed_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^chrome-extension://.*$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api")
app.include_router(otp_accounts.router, prefix="/api")


# ── Health / Root ──────────────────────────────────────────────────
@app.get("/")
async def root():
    """Root redirect — confirms the server is alive."""
    return {"name": "Private Auth Box API", "version": "1.0.0", "status": "running"}


@app.get("/api/health")
async def health():
    """Health check endpoint used by Render and monitoring."""
    return {"status": "ok"}
