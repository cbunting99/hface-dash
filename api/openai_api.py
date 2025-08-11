from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
import uuid

from services.model_manager import ModelManager

router = APIRouter()
model_manager = ModelManager()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False

class CompletionRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "transformers"

@router.get("/models")
async def list_models():
    models = model_manager.get_models()
    model_list = []
    
    for model in models:
        if model["loaded"]:
            model_list.append(ModelInfo(
                id=model["name"],
                created=int(model["downloaded_at"])
            ))
    
    return {"object": "list", "data": model_list}

@router.post("/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    if request.model not in model_manager.loaded_models:
        raise HTTPException(status_code=400, detail=f"Model {request.model} is not loaded")
    
    prompt = ""
    for message in request.messages:
        if message.role == "system":
            prompt += f"System: {message.content}\n"
        elif message.role == "user":
            prompt += f"User: {message.content}\n"
        elif message.role == "assistant":
            prompt += f"Assistant: {message.content}\n"
    
    prompt += "Assistant:"
    
    try:
        generated_text = await model_manager.generate_text(
            request.model,
            prompt,
            request.max_tokens or 100,
            request.temperature or 0.7
        )
        
        return {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": generated_text.strip()
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(generated_text.split()),
                "total_tokens": len(prompt.split()) + len(generated_text.split())
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/completions")
async def create_completion(request: CompletionRequest):
    if request.model not in model_manager.loaded_models:
        raise HTTPException(status_code=400, detail=f"Model {request.model} is not loaded")
    
    try:
        generated_text = await model_manager.generate_text(
            request.model,
            request.prompt,
            request.max_tokens or 100,
            request.temperature or 0.7
        )
        
        return {
            "id": f"cmpl-{uuid.uuid4()}",
            "object": "text_completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "text": generated_text,
                "index": 0,
                "logprobs": None,
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(request.prompt.split()),
                "completion_tokens": len(generated_text.split()),
                "total_tokens": len(request.prompt.split()) + len(generated_text.split())
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))