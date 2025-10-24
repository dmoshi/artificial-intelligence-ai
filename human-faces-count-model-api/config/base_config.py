import os
from dotenv import load_dotenv
from ultralytics import YOLO

# Load environment variables
load_dotenv()

MODEL_PATH = os.getenv("MODEL_PATH", "./ai_model/yolov8x-face-lindevs.pt")
IMG_SIZE = int(os.getenv("IMG_SIZE", 1024))
CONF_THRESH = float(os.getenv("CONF_THRESH", 0.1))
IOU_THRESH = float(os.getenv("IOU_THRESH", 0.3))
ALPHA = float(os.getenv("ALPHA", 1.0))
BETA = float(os.getenv("BETA", 20))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/output")
DEVICE = os.getenv("DEVICE", "cpu")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load YOLO model
model = YOLO(MODEL_PATH)

# Environment flags
SAVE_MODE = os.getenv("SAVE_MODE", "local").lower()

# S3 Config
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME =os.getenv("S3_BUCKET_NAME")

# DB Config
DATABASE_URL = os.getenv("DATABASE_URL")
