"""
main.py — FastAPI application entry point for Med Phone backend.

Run with:
    uvicorn backend.main:app --reload --port 8000
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .firebase import get_firebase_app
from .routers import auth, products, orders, cart, contact, commandes, search, chatbot

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")
logger = logging.getLogger("med_phone")

settings = get_settings()


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        get_firebase_app()          # initialise once; raises if creds/URL missing
        logger.info("✅  Firebase Realtime Database connected successfully")
    except (FileNotFoundError, ValueError) as exc:
        logger.error(f"🔴  Firebase init failed: {exc}")
        # App still starts so you can see the error in /health
    yield
    # Shutdown (nothing to clean up for firebase-admin)
    logger.info("👋  Med Phone API shutting down")


# ── App factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description=(
        "Backend API for **Med Phone** — Morocco's premium electronics store.\n\n"
        "Backed by **Firebase Realtime Database** for data and **Firebase Auth** for identity.\n\n"
        "Supports **Cash on Delivery (COD)** orders via `/api/commandes`."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)
# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(cart.router)
app.include_router(contact.router)
app.include_router(commandes.router)   # COD — Paiement à la livraison
app.include_router(search.router)
app.include_router(chatbot.router, tags=["Chatbot"])


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"], summary="Health check")
async def health():
    """Quick endpoint to verify the API is alive."""
    return JSONResponse({"status": "ok", "service": "Med Phone API", "version": settings.app_version})


@app.get("/", include_in_schema=False)
async def root():
    return JSONResponse({
        "message": "Welcome to Med Phone API 🚀",
        "docs":    "/docs",
        "health":  "/health",
    })
