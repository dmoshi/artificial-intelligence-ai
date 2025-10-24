import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


def is_likely_face(crop, conf):
    """Simple heuristic filter for false positives."""
    if crop is None or crop.size == 0:
        return False

    h, w = crop.shape[:2]
    if h < 20 or w < 20:   # crop is too small
        return False

    gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    mean_val = np.mean(gray)
    std_val = np.std(gray)

    if mean_val < 30 or mean_val > 220:   # crop is too dark or too bright
        return False

    if std_val < 10 and conf < 0.35: # too flat, single solid color + low confidence threshold
        return False

    return True
