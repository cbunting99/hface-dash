from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import asyncio

from services.model_manager import ModelManager

router = APIRouter()
model_manager = ModelManager()

class DownloadRequest(BaseModel):
    model_name: str
    hf_model_id: str

    model_config = {'protected_namespaces': ()}

class GenerateRequest(BaseModel):
    model_name: str
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7

    model_config = {'protected_namespaces': ()}

@router.get("/models")
async def get_models():
    return {"models": model_manager.get_models()}

@router.get("/system")
async def get_system_info():
    return model_manager.get_system_info()

@router.post("/models/download")
async def download_model(request: DownloadRequest, background_tasks: BackgroundTasks):
    if request.model_name in model_manager.model_info:
        raise HTTPException(status_code=400, detail="Model already exists")
    
    async def stream_progress():
        async for progress in model_manager.download_model(request.model_name, request.hf_model_id):
            yield f"data: {json.dumps(progress)}\n\n"
    
    return StreamingResponse(
        stream_progress(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@router.get("/models/{model_name}/download-progress")
async def get_download_progress(model_name: str):
    if model_name in model_manager.download_progress:
        return model_manager.download_progress[model_name]
    return {"status": "not_found"}

@router.post("/models/{model_name}/load")
async def load_model(model_name: str):
    success = await model_manager.load_model(model_name)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to load model")
    return {"status": "loaded"}

@router.post("/models/{model_name}/unload")
async def unload_model(model_name: str):
    success = await model_manager.unload_model(model_name)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to unload model")
    return {"status": "unloaded"}

@router.delete("/models/{model_name}")
async def delete_model(model_name: str):
    success = await model_manager.delete_model(model_name)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete model")
    return {"status": "deleted"}

@router.post("/generate")
async def generate_text(request: GenerateRequest):
    try:
        text = await model_manager.generate_text(
            request.model_name,
            request.prompt,
            request.max_tokens,
            request.temperature
        )
        return {"generated_text": text}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
