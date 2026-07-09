from fastapi import FastAPI, Request
from app.core.config import settings
from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.api.wallet import router as wallet_router
from app.exceptions import PayLiteError
from pydantic import ValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

app = FastAPI(title=settings.APP_NAME)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(wallet_router)

logger = logging.getLogger("paylite")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)

@app.exception_handler(PayLiteError)
async def paylite_error_handler(request: Request, exc: PayLiteError):
    return JSONResponse(
        status_code=exc.status_code,
        content = {
            "error_type": type(exc).__name__,
            "message": exc.message
        }
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration:.3f}s)")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status":"ok", "environment": settings.ENVIRONMENT}
