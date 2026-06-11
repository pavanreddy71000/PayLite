from fastapi import FastAPI
from app.core.config import settings
from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.api.wallet import router as wallet_router

from pydantic import ValidationError
from fastapi.responses import JSONResponse

app = FastAPI(title=settings.APP_NAME)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(wallet_router)

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )

@app.get("/health")
def health_check():
    return {"status":"ok", "environment": settings.ENVIRONMENT}
