from config import ModelIds
from models.kokoro_service import KokoroModel

MODEL_CLASSES = {
    ModelIds.KOKORO_82M.value: KokoroModel
}

MODEL_OUTPUT_PATHS = {
    ModelIds.KOKORO_82M.value: "output/kokoro/"
}
