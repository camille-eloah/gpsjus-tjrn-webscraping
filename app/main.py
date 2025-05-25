from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    # Aqui configurará a coleta automática de dados
    pass