from abc import ABC, abstractmethod
from typing import Optional

class BaseModel(ABC):
    model_id: str

    def get_model_id(self) -> str:
        return self.model_id

    @abstractmethod
    def generate_audio(self, text: str, filepath: str) -> str:
        """
        Generates audio from the given text and saves it to the specified filepath.

        Args:
            text (str): The text to convert to speech.
            filepath (str): The path to save the generated audio file.

        Returns:
            str: The path to the generated audio file.
        """
        raise NotImplementedError

    @abstractmethod
    def change_language(self, lang_code: str, voice: Optional[str] = None):
        """Change the language and optionally the voice of the TTS model.
        
        Args:
            lang_code (str): The language code to switch to
            voice (Optional[str]): Optional voice identifier
        """
        pass

    @abstractmethod
    async def download_model(self):
        """Download the model from the internet."""
        pass

