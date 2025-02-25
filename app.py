from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import JSONResponse
import os
import uuid
from threading import Lock
from model_handler import ModelHandler
from typing import Dict
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import WebSocketDisconnect
from asyncio import create_task
from db_utils import DatabaseManager, ModelsDAO
from concurrent.futures import ThreadPoolExecutor
import asyncio
from model_services import ModelServices, MODEL_CLASSES, MODEL_OUTPUT_PATHS
import multiprocessing

app = FastAPI(
    title="TTS API",
    description="API for text-to-speech conversion using various models",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

loaded_models = {}
models_lock = Lock()

model_handler = ModelHandler()
DatabaseManager()

models_dao = ModelsDAO()
tts_thread_pool = ThreadPoolExecutor(max_workers=max(2, multiprocessing.cpu_count() // 2))
model_services = ModelServices()

class TTSRequest(BaseModel):
    text: str
    model_id: str

class LanguageRequest(BaseModel):
    model_id: str
    lang_code: str
    voice: str | None = None

class LoadModelRequest(BaseModel):
    model_id: str

@app.get("/")
async def index():
    return {"message": "Voice Studio Models", "version": "1.0.0", "status": "online"}

@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    try:
        # Run the TTS generation in a separate thread
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            tts_thread_pool,
            model_services.generate_speech,
            request.model_id,
            request.text
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/change-language")
async def change_language(request: LanguageRequest):
    try:
        model = model_handler.load_model(request.model_id)
        model.change_language(request.lang_code, request.voice)
        return {"message": "Language changed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/download-model")
async def download_model_ws(websocket: WebSocket):
    try:
        await websocket.accept()
        
        # Receive and validate the initial message
        try:
            data = await websocket.receive_json()
            model_id = data.get('model_id')
            print(f"Downloading model {model_id}")
            if not model_id:
                await websocket.send_json({"status": "error", "error": "model_id is required"})
                await websocket.close()
                return
                
            # Send initial status
            await websocket.send_json({"status": ModelsDAO.DownloadStatus.DOWNLOADING, "model_id": model_id})
            print(f"Sending initial status for model {model_id}")
            # Create background task for download
            try:
                models_dao.insert_model_state(model_id, ModelsDAO.DownloadStatus.DOWNLOADING)
                download_task = create_task(model_handler.download_model(model_id))
                await download_task
                models_dao.insert_model_state(model_id, ModelsDAO.DownloadStatus.READY)
                print(f"Model {model_id} completed")
                await websocket.send_json({"status": ModelsDAO.DownloadStatus.READY, "model_id": model_id})
            except Exception as e:
                models_dao.insert_model_state(model_id, ModelsDAO.DownloadStatus.PENDING)
                await websocket.send_json({"status": "error", "error": str(e), "model_id": model_id})
                
        except WebSocketDisconnect:
            print(f"Client disconnected during download of model {model_id}")
        except Exception as e:
            await websocket.send_json({"status": "error", "error": f"Unexpected error: {str(e)}"})
            
    except Exception as e:
        print(f"Failed to establish WebSocket connection: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close()

@app.get("/models/download")
async def get_models():
    return models_dao.get_model_states()

@app.post("/models/load")
async def load_model(request: LoadModelRequest):
    model_handler.load_model(request.model_id)
    return {"status": "success", "message": f"Model {request.model_id} loaded successfully"}

@app.post("/models/unload")
async def unload_model(request: LoadModelRequest):
    model_handler.unload_model(request.model_id)
    return {"status": "success", "message": f"Model {request.model_id} unloaded successfully"}

@app.get("/models/load")
async def get_loaded_models():
    return model_handler.get_loaded_model_ids()

# Mount the audio directory
if not os.path.exists("output"):
    os.makedirs("output")
app.mount("/output", StaticFiles(directory="output"), name="output")