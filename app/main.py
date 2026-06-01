from fastapi import FastAPI
from app.core.config import settings
from app.api.users import router as users_router

app = FastAPI(title=settings.APP_NAME)
app.include_router(users_router)


@app.get("/health")
def health_check():
    return {"status":"ok", "environment": settings.ENVIRONMENT}