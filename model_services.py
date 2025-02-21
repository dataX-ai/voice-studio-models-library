from model_handler import ModelHandler
from typing import Dict
import os
import uuid
from models.model_config import MODEL_CLASSES, MODEL_OUTPUT_PATHS

class ModelServices:
    def __init__(self):
        self.model_handler = ModelHandler()

    def generate_speech(self, model_id: str, text: str) -> Dict[str, str]:
        model = self.model_handler.load_model(model_id)

        # Generate a unique filename
        filename = model_id + "_" + str(uuid.uuid4())[0:6] + ".mp3"
        filepath = MODEL_OUTPUT_PATHS[model_id] + filename
        print(f"filepath: {filepath}")
        # Create the 'audio' folder if it doesn't exist
        if not os.path.exists(MODEL_OUTPUT_PATHS[model_id]):
            os.makedirs(MODEL_OUTPUT_PATHS[model_id])

        # Convert text to speech
        audio_file = model.generate_audio(text, filepath)
        print(f"Audio file: {audio_file}")
        return {"filename": audio_file}