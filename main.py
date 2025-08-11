import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from api.dashboard import router as dashboard_router
from api.openai_api import router as openai_router
from services.model_manager import ModelManager

model_manager = ModelManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await model_manager.initialize()
    yield
    await model_manager.cleanup()

app = FastAPI(title="Transformers Dashboard", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(dashboard_router, prefix="/api")
app.include_router(openai_router, prefix="/v1")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("templates/index.html", "r") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )