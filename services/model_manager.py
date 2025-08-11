import os
import json
import asyncio
import shutil
from typing import Dict, List, Optional, AsyncGenerator
from pathlib import Path
from huggingface_hub import snapshot_download, HfApi
from transformers import AutoModelForCausalLM, AutoTokenizer
import psutil
from transformers import AutoModelForCausalLM, AutoTokenizer
import requests

class ModelManager:
    def __init__(self):
        self.models_dir = Path("models")
        self.data_dir = Path("data")
        self.models_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        # loaded_models: Dict[str, Dict] with keys: model, tokenizer
        self.loaded_models: Dict[str, dict] = {}
        self.download_progress: Dict[str, dict] = {}
        self.model_info_file = self.data_dir / "models.json"
        self.hf_api = HfApi()
        self.model_info = {}

    async def initialize(self):
        if self.model_info_file.exists():
            with open(self.model_info_file, 'r') as f:
                self.model_info = json.load(f)
        else:
            self.model_info = {}
    
    async def cleanup(self):
        for model_name in list(self.loaded_models.keys()):
            await self.unload_model(model_name)
    
    def save_model_info(self):
        with open(self.model_info_file, 'w') as f:
            json.dump(self.model_info, f, indent=2)
    
    async def download_model(self, model_name: str, source: str, is_gguf: bool = False, hf_token: Optional[str] = None) -> AsyncGenerator[dict, None]:
        try:
            self.download_progress[model_name] = {
                "status": "starting",
                "progress": 0,
                "total_files": 0,
                "downloaded_files": 0,
                "current_file": "",
                "error": None
            }

            yield self.download_progress[model_name]

            model_path = self.models_dir / model_name

            if is_gguf:
                # Download GGUF file from HuggingFace repo
                model_path.mkdir(exist_ok=True)
                files = self.hf_api.list_repo_files(repo_id=source)
                gguf_files = [f for f in files if f.endswith(".gguf")]
                if not gguf_files:
                    raise Exception("No GGUF file found in HuggingFace repo")
                gguf_file_name = gguf_files[0]
                gguf_file_path = model_path / gguf_file_name
                from huggingface_hub import hf_hub_download
                local_path = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: hf_hub_download(repo_id=source, filename=gguf_file_name, local_dir=str(model_path), token=hf_token)
                )
                self.model_info[model_name] = {
                    "hf_model_id": source,
                    "gguf_file": gguf_file_name,
                    "path": local_path,
                    "downloaded_at": asyncio.get_event_loop().time(),
                    "loaded": False,
                    "format": "gguf"
                }
            else:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: snapshot_download(
                        repo_id=source,
                        local_dir=str(model_path),
                        local_dir_use_symlinks=False,
                        token=hf_token
                    )
                )
                self.model_info[model_name] = {
                    "hf_model_id": source,
                    "path": str(model_path),
                    "downloaded_at": asyncio.get_event_loop().time(),
                    "loaded": False,
                    "format": "huggingface"
                }
            self.save_model_info()

            self.download_progress[model_name] = {
                "status": "completed",
                "progress": 100,
                "total_files": 0,
                "downloaded_files": 0,
                "current_file": "",
                "error": None
            }

            yield self.download_progress[model_name]

        except Exception as e:
            self.download_progress[model_name] = {
                "status": "error",
                "progress": 0,
                "total_files": 0,
                "downloaded_files": 0,
                "current_file": "",
                "error": str(e)
            }
            yield self.download_progress[model_name]
    
    async def load_model(self, model_name: str) -> bool:
        try:
            if model_name in self.loaded_models:
                return True
            if model_name not in self.model_info:
                return False
            model_path = self.model_info[model_name]["path"]
            # Load model and tokenizer using transformers
            model = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: AutoModelForCausalLM.from_pretrained(model_path)
            )
            tokenizer = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: AutoTokenizer.from_pretrained(model_path)
            )
            self.loaded_models[model_name] = {"model": model, "tokenizer": tokenizer}
            self.model_info[model_name]["loaded"] = True
            self.save_model_info()
            return True
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            return False
    
    async def unload_model(self, model_name: str) -> bool:
        try:
            if model_name in self.loaded_models:
                del self.loaded_models[model_name]
                
            if model_name in self.model_info:
                self.model_info[model_name]["loaded"] = False
                self.save_model_info()
            
            return True
            
        except Exception as e:
            print(f"Error unloading model {model_name}: {e}")
            return False
    
    async def delete_model(self, model_name: str) -> bool:
        try:
            await self.unload_model(model_name)
            
            if model_name in self.model_info:
                model_path = Path(self.model_info[model_name]["path"])
                if model_path.exists():
                    shutil.rmtree(model_path)
                
                del self.model_info[model_name]
                self.save_model_info()
            
            return True
            
        except Exception as e:
            print(f"Error deleting model {model_name}: {e}")
            return False
    
    def get_models(self) -> List[dict]:
        models = []
        for name, info in self.model_info.items():
            model_path = Path(info["path"])
            size = self.get_directory_size(model_path) if model_path.exists() else 0
            
            models.append({
                "name": name,
                "hf_model_id": info["hf_model_id"],
                "loaded": info["loaded"],
                "size": size,
                "downloaded_at": info["downloaded_at"]
            })
        
        return models
    
    def get_directory_size(self, path: Path) -> int:
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size
    
    def get_system_info(self) -> dict:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            },
            "cpu_percent": psutil.cpu_percent(interval=1)
        }
    
    async def generate_text(self, model_name: str, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        if model_name not in self.loaded_models:
            raise ValueError(f"Model {model_name} is not loaded")
        model = self.loaded_models[model_name]["model"]
        tokenizer = self.loaded_models[model_name]["tokenizer"]
        # Tokenize input
        input_ids = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: tokenizer(prompt, return_tensors="pt").input_ids
        )
        # Generate output
        output_ids = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: model.generate(
                input_ids,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True
            )
        )
        # Decode output
        output_text = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: tokenizer.decode(output_ids[0], skip_special_tokens=True)
        )
        # Remove prompt from output if present
        if output_text.startswith(prompt):
            output_text = output_text[len(prompt):].strip()
        return output_text
