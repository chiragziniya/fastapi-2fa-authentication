from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth, otp_accounts

settings = get_settings()

app = FastAPI(title="Private Auth Box API", version="1.0.0")

# Build allowed origins list: frontend URL + any chrome-extension origins
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

app.include_router(auth.router, prefix="/api")
app.include_router(otp_accounts.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
