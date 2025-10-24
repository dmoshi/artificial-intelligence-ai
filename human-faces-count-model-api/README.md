# 🧠  AI Faces Count API

An intelligent face counting API that uses **YOLO (Ultralytics)** and **OpenCV** for real-time facial detection and annotation.  
Built with **Python**, **FastAPI**, **OpenCV**, **Celery**, **RabbitMQ**, and **PostgreSQL**, the system performs asynchronous image processing and stores metadata in the cloud (via **AWS S3**) then relay faces count to a websocket server + client target session id.

---

## 🚀 Features

- 🎯 **Face Detection** using YOLOv8 (Ultralytics)
- 🧩 **Face Count Metadata Storage** in PostgreSQL
- 🪄 **Background Task Processing** powered by Celery + RabbitMQ
- ☁️ **Cloud Storage** for annotated images (AWS S3)
- 🔄 **WebSocket Relay** for real-time status updates
- 🧱 **Modular & Scalable** microservice architecture

---

## 🧰 Tech Stack

| Component | Technology |
|------------|-------------|
| **Language** | Python 3.9+ |
| **Framework** | FastAPI |
| **Model Inference** | YOLOv8 (Ultralytics) + InsightFace |
| **Task Queue** | Celery |
| **Message Broker** | RabbitMQ |
| **Database** | PostgreSQL |
| **Storage** | AWS S3 |
| **WebSockets** | `websocket-client` |
| **Async ORM** | SQLAlchemy + AsyncPG |
| **Runtime** | Uvicorn |

---

## ⚙️ Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/dmoshi/artificial-intelligence-ai.git
cd human-faces-count-model-api
```

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set up environment variables

Create a `.env` file in the project root based on the example below 👇

---

## 🧾 .env Example

```env
# ============================================================
# 🧠 Model Configuration
# ============================================================
MODEL_PATH=./ai_model/yolov8x-face-lindevs.pt

# Model augmentation (for training/inference tuning)
IMG_SIZE=1024
CONF_THRESH=0.1
IOU_THRESH=0.3
ALPHA=1.0
BETA=20
LOW_CONTRAST_THRESHOLD=25
LANDMARK_OCCLUSION_THRESHOLD=5
DARK_THRESHOLD=80
BRIGHT_THRESHOLD=180
DEVICE=cpu  # options: cpu or cuda

# ============================================================
# 📸 Face Detection Output
# ============================================================
OUTPUT_DIR=./output
BASE_URL=http://localhost:8000/output

# ============================================================
# 🧾 Logging
# ============================================================
LOGGING_LEVEL=INFO  # options: DEBUG, INFO, WARNING, ERROR

# ============================================================
# 💾 Persistence Mode
# ============================================================
SAVE_MODE=cloud  # options: local or cloud

# ============================================================
# ☁️ AWS S3 Configuration (for annotated images)
# ============================================================
AWS_ACCESS_KEY_ID=AKIAEXAMPLEKEY123
AWS_SECRET_ACCESS_KEY=abcd1234example5678secretkey
AWS_REGION=eu-west-2
S3_BUCKET_NAME=ai-faces-count

# ============================================================
# 🐘 PostgreSQL Configuration (for face metadata)
# ============================================================
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/faces_db

# ============================================================
# 🐇 RabbitMQ (for Celery background tasks)
# ============================================================
RABBITMQ_URL=amqp://guest:guest@localhost:5672/custom_vhost

# ============================================================
# 🌐  WebSocket Server
# ============================================================
WSS_SERVER=wss://localhost:8083/api/ws
RETRY_WSS_CONNECT_DELAY=10
```

---

## 🧩 Running the Application

### 1️⃣ Start all required services (RabbitMQ, PostgreSQL)

You can run them via Docker, EC2 or locally, depending on your setup.

### 2️⃣ Run the application

```bash
./run.sh
```

This will:
- Launch the FastAPI server
- Start the Celery worker
- Connect to the WebSocket server
- Connect to RabbitMQ
- Load YOLOv8 face detection model

---

## 🧠 API Overview

| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/faces` | `POST` | Send image URL for face counting |

---

## 🧮 Background Tasks

Celery is used to offload heavy model inference tasks:
- Face detection
- Image annotation
- Metadata storage in PostgreSQL
- Annotated image upload to S3

RabbitMQ is the broker managing these asynchronous tasks.

---

## 🧠 Model Notes

The model uses:
- **YOLOv8x (Ultralytics)** for detecting faces
- **OpenCV** for facial feature enhancement and accuracy before model inference
- Supports both **CPU** and **CUDA GPU** backends for training 
- You can train model with YOLO command below:
```env
yolo train model=./ai_model/yolov8x-face-lindevs.pt data=data.yml epochs=10 imgsz=640 batch=2 name=ai_yolov8x_face_buses freeze=0 save_period=2 patience=3 cache=False workers=2 lr0=0.0003 lrf=0.01 fraction=1.0
```
- I used to annotate images and generate labels for datasets inside ./train_model/datasets 
- See ./output for sample results (even in harsh conditions eg. night images with IR )

---

## ☁️ Cloud Storage

Annotated images are saved to AWS S3 when `SAVE_MODE=cloud`.  
For local testing, set:
```env
SAVE_MODE=local
```
and annotated images will be stored in `./output`.

---

## 🧱 Database Schema

| Table | Description |
|--------|-------------|
| `faces` | Stores metadata for each image (face count, confidence, timestamp, etc.) |
| `jobs` | Tracks Celery job states for async inference |

---

## 🧩 WebSocket Integration

After iinference, face count and metadata are relayed to a websocket server with a taget session id, and back to client's target websocket session.

Connection auto-reconnects if the WebSocket drops:
```python
WSS_SERVER=wss://localhost:8083/api/ws
RETRY_WSS_CONNECT_DELAY=10
```

---

## 🧑‍💻 Development Notes

To regenerate dependencies list:
```bash
pip freeze > requirements.txt
```

To create requirements automatically from imports:
```bash
pipreqs . --force
```

---

## 🧠 Author

**Daniel Moshi**  
[GitHub](https://github.com/dmoshi)

---

## 🪪 License

This project is licensed under the MIT License.
