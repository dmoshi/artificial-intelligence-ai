import cv2
import numpy as np

def enhance_face_crop(frame):
    """Automatically enhance brightness, contrast, sharpness, and color balance."""
    if len(frame.shape) == 2:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
    elif frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    mean_val = np.mean(gray)
    std_val = np.std(gray)
    focus = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Detect grayscale
    b, g, r = cv2.split(frame)
    color_diff = np.mean(np.abs(r - g) + np.abs(g - b) + np.abs(b - r))
    gray_like = color_diff < 12
    if gray_like:
        lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)
        l, a, b_lab = cv2.split(lab)
        l = cv2.add(l, 20)
        a = cv2.add(a, 5)
        b_lab = cv2.add(b_lab, 5)
        frame = cv2.cvtColor(cv2.merge((l, a, b_lab)), cv2.COLOR_LAB2RGB)
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)
        s = cv2.add(s, 40)
        frame = cv2.cvtColor(cv2.merge((h, s, v)), cv2.COLOR_HSV2RGB)

    # Color cast correction
    avg_r, avg_g, avg_b = np.mean(r), np.mean(g), np.mean(b)
    gray_mean = (avg_r + avg_g + avg_b) / 3
    r_gain = gray_mean / (avg_r + 1e-6)
    g_gain = gray_mean / (avg_g + 1e-6)
    b_gain = gray_mean / (avg_b + 1e-6)

    cast_strength = np.std([avg_r, avg_g, avg_b])
    if cast_strength > 5:
        frame = cv2.merge([
            np.clip(b * b_gain, 0, 255).astype(np.uint8),
            np.clip(g * g_gain, 0, 255).astype(np.uint8),
            np.clip(r * r_gain, 0, 255).astype(np.uint8)
        ])

    # Brightness / contrast
    if mean_val < 80 or std_val < 20:
        alpha = 1.4 + (100 - mean_val) / 150.0
        beta = 50 if mean_val < 60 else 30
    else:
        alpha = 1.0 + (100 - mean_val) / 200.0
        beta = (128 - mean_val) * 0.4

    frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

    # Sharpness
    focus_after = cv2.Laplacian(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY), cv2.CV_64F).var()
    if focus_after < 60:
        blur = cv2.GaussianBlur(frame, (0, 0), sigmaX=2)
        frame = cv2.addWeighted(frame, 1.7, blur, -0.7, 0)

    # Local contrast
    if std_val < 25 or mean_val < 70:
        lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)
        l, a, b_lab = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        l = clahe.apply(l)
        frame = cv2.cvtColor(cv2.merge((l, a, b_lab)), cv2.COLOR_LAB2RGB)

    return frame
