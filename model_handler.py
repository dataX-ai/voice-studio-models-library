from models.base_service import BaseModel
from threading import Lock
from models.model_config import MODEL_CLASSES

class ModelHandler:
    _instance = None
    _init_lock = Lock()

    def __new__(cls):
        with cls._init_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        with self._init_lock:
            if not self._initialized:
                self.loaded_models = {}
                self.models_lock = Lock()
                self._initialized = True

    def load_model(self, model_id: str) -> BaseModel:
        if model_id not in MODEL_CLASSES:
            raise ValueError(f"Model {model_id} not found")
        if model_id not in self.loaded_models:
            with self.models_lock:
                if model_id not in self.loaded_models:
                    model_class = MODEL_CLASSES.get(model_id)
                    if not model_class:
                        raise ValueError(f"Model {model_id} not found")
                    model = model_class()
                    self.loaded_models[model_id] = model

        return self.loaded_models[model_id]

    def unload_model(self, model_id: str):
        if model_id in self.loaded_models:
            with self.models_lock:
                if model_id in self.loaded_models:
                    del self.loaded_models[model_id]

    async def download_model(self, model_id: str):
        """Download the model asynchronously"""
        model = self.load_model(model_id)
        await model.download_model()
        self.unload_model(model_id)

    def get_loaded_models(self) -> dict[str, BaseModel]:
        return self.loaded_models

    def get_loaded_model_ids(self) -> list[str]:
        return list(self.loaded_models.keys())
