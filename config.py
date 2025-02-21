from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv()

class ModelIds(str, Enum):
    KOKORO_82M = "kokoro-82M"


class Env(str, Enum):
    ENV = os.getenv("ENV")
