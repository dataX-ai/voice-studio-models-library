from typing import Optional
from kokoro import KPipeline
from models.base_service import BaseModel
import soundfile as sf
import os
import numpy as np
from config import ModelIds, Env

class KokoroModel(BaseModel):
    def __init__(self):
        self.model_id = ModelIds.KOKORO_82M.value
        self.voice = "af_heart"
        self.lang_code = "a"
        self.pipeline = KPipeline(lang_code=self.lang_code)

    def change_language(self, lang_code: str, voice: Optional[str] = None):
        self.lang_code = lang_code
        self.pipeline = KPipeline(lang_code=self.lang_code)
        if voice:
            self.voice = voice

    def generate_audio(self, text: str, filepath: str) -> str:
        generator = self.pipeline(
            text, voice=self.voice, # <= change voice here
            speed=1, split_pattern='<NEWLINE>'
        )
        all_audio = []
        for i, (gs, ps, audio) in enumerate(generator):
            print(i)  # i => index
            print(gs) # gs => graphemes/text
            print(ps) # ps => phonemes
            all_audio.append(audio)
        
        # Concatenate all audio chunks and write once
        final_audio = np.concatenate(all_audio)
        sf.write(filepath, final_audio, 24000)
        # Return absolute path of the generated file
        return os.path.abspath(filepath) if Env.ENV == "dev" else filepath

    async def download_model(self):
        if not os.path.exists("output/kokoro"):
            os.makedirs("output/kokoro")
        self.generate_audio("Hello, world!", "output/kokoro/test.mp3")