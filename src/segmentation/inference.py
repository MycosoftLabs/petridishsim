"""SegFormer/ONNX inference utilities for MyceliumSeg."""

from __future__ import annotations

from typing import Tuple

import numpy as np
import onnxruntime as ort
from PIL import Image


def load_session(model_path: str) -> ort.InferenceSession:
    return ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])


def preprocess_image(image: Image.Image, input_size: Tuple[int, int]) -> np.ndarray:
    resized = image.convert("RGB").resize(input_size, Image.BILINEAR)
    array = np.asarray(resized).astype(np.float32) / 255.0
    array = np.transpose(array, (2, 0, 1))
    return np.expand_dims(array, axis=0)


def postprocess_mask(logits: np.ndarray) -> np.ndarray:
    if logits.ndim == 4:
        logits = logits[0]
    mask = np.argmax(logits, axis=0).astype(np.uint8)
    return mask


def segment_image(image: Image.Image, model_path: str) -> np.ndarray:
    session = load_session(model_path)
    input_meta = session.get_inputs()[0]
    input_shape = input_meta.shape
    height = int(input_shape[2]) if isinstance(input_shape[2], int) else image.height
    width = int(input_shape[3]) if isinstance(input_shape[3], int) else image.width
    input_tensor = preprocess_image(image, (width, height))

    outputs = session.run(None, {input_meta.name: input_tensor})
    return postprocess_mask(outputs[0])
