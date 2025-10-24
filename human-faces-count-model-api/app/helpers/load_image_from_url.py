import cv2
import numpy as np
import requests
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


def load_image_from_url(url: str):
    """Download and decode an image from a URL."""
    resp = requests.get(url, stream=True)
    if resp.status_code != 200:
        raise ValueError(f"Failed to download image: {url}")
    image_bytes = np.asarray(bytearray(resp.content), dtype=np.uint8)
    img = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
    if img is None:
        logger.exception("Failed to decode image")
        raise ValueError("Failed to decode image")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def load_image_from_url_safe(url: str, timeout: int = 5, max_size: int = 5_000_000):
    """Securely download an image with validation."""
    if not url.lower().startswith(("http://", "https://")):
        logger.exception("Invalid URL format.")
        raise HTTPException(status_code=422, detail="Invalid URL format.")

    try:
        response = requests.get(url, timeout=timeout, stream=True)
        if response.status_code != 200:
            logger.exception(f"Unable to fetch image (status code {response.status_code}).")
            raise HTTPException(
                status_code=400,
                detail=f"Unable to fetch image (status code {response.status_code}).",
            )

        content_length = int(response.headers.get("content-length", 0))
        if content_length > max_size:
            logger.exception("Image too large (limit 5MB).")
            raise HTTPException(status_code=413, detail="Image too large (limit 5MB).")

        image_data = np.asarray(bytearray(response.content), dtype=np.uint8)
        frame = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
        if frame is None:
            logger.exception("Invalid image format")
            raise HTTPException(status_code=422, detail="Invalid image format.")

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    except requests.exceptions.RequestException as e:
        logger.error(f"Image download failed: {e}")
        raise HTTPException(status_code=400, detail="Failed to download image.")
