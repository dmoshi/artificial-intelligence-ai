# 🚀 Human Face Count API System

A distributed real-time system for detecting human faces in vehicle-captured images using **YOLO**, **FastAPI**, **Celery**, and **RabbitMQ** — integrated with a **Java WebSocket backend**, **PostgreSQL**, and **AWS S3** for storage and metadata.

---

## 🧭 System Architecture Overview

This architecture enables real-time fleet monitoring, image analysis, and face detection through asynchronous AI processing.

### 📊 Architecture Diagram

```mermaid
sequenceDiagram
    participant A as 🚗 Vehicle (GPS + Camera)
    participant B as 🌐 Telemetry Platform
    participant C as ⚙️ Backend Server (Java + WebSocket Server)
    participant D as 🤖 Human Face Count API (FastAPI + Celery + YOLO + OpenCV)
    participant I as 🐇 RabbitMQ (Async Task Queue)
    participant G as ☁️ AWS S3 (Annotated Images)
    participant H as 🗃️ PostgreSQL (Metadata)
    participant J as 📱 Mobile App

    A->>B: Send GPS + Image Data
    J-->>C: Establish WebSocket Session
    C->>B: Poll for Latest GPS + Image URL
    B-->>C: Return GPS + Image URL
    C->>J: Send Live Location Data via WebSocket
    C->>D: Send Image URL + Target Session ID
    D->>I: Push Inference Task to Queue
    I->>D: Trigger Celery Worker (Async)
    D->>G: Save Annotated Image (after YOLO Inference)
    D->>H: Save Face Count Metadata
    D-->>C: Relay Face Count + Target Session ID via WebSocket
    C-->>J: Relay Face Count Result via WebSocket
    J-->>G: Display Annotated Image to User (as Evidence)
```

---

## 🧩 Actor Descriptions

| Actor | Description |
|:------|:-------------|
| **🚗 Vehicle (A)** | Captures live GPS and image data from the field. |
| **🌐 Telemetry Platform (B)** | Legacy GPS & image gateway that stores and exposes telemetry data. |
| **⚙️ Backend Server (C)** | Java WebSocket server managing client sessions, fetching telemetry, and relaying data. |
| **🤖 Human Face Count API (D)** | FastAPI service running YOLO for face detection asynchronously with Celery. |
| **🐇 RabbitMQ (I)** | Message broker for Celery tasks enabling non-blocking inference processing. |
| **☁️ AWS S3 (G)** | Stores YOLO-annotated images. |
| **🗃️ PostgreSQL (H)** | Persists face count metadata (timestamp, image reference, session ID). |
| **📱 Mobile App (J)** | Establishes WebSocket session, receives live face count updates, and displays annotated evidence. |

---

## ⚙️ Data Flow Summary

1. **Vehicle → Telemetry Platform:** Sends GPS and image data.  
2. **Mobile App → Backend Server:** Establishes WebSocket connection.  
3. **Backend → Telemetry Platform:** Polls for new GPS + image data.  
4. **Backend → Face Count API:** Sends image URL + session ID.  
5. **Face Count API → RabbitMQ:** Queues inference task.  
6. **Celery Worker → YOLO → S3 + PostgreSQL:** Annotates image, saves results.  
7. **Face Count API → Backend → Mobile App:** Relays face count + annotated image evidence.  

---

## 🧠 Tech Stack Overview

| Layer | Technology | Purpose |
|:------|:------------|:---------|
| **AI Inference** | YOLO (Ultralytics) | Detect human faces in images. |
| **Web Framework** | FastAPI | Serve inference API. |
| **Task Queue** | Celery + RabbitMQ | Async task handling for image processing. |
| **Database** | PostgreSQL | Store face count metadata. |
| **Storage** | AWS S3 | Save annotated images. |
| **WebSocket Server** | Java | Handle client sessions and stream updates. |
| **Frontend** | Mobile App | Displays live data and annotated images. |
| **Language** | Python | Main application logic and inference. |

---

## 🔧 Environment Variables (`.env`)

```bash
# Model
MODEL_PATH=./ai_model/yolov8x-face-lindevs.pt

# Model Augmentation
IMG_SIZE=1024
CONF_THRESH=0.1
IOU_THRESH=0.3
ALPHA=1.0
BETA=20
LOW_CONTRAST_THRESHOLD=25
LANDMARK_OCCLUSION_THRESHOLD=5
DARK_THRESHOLD=80
BRIGHT_THRESHOLD=180
DEVICE=cpu

# Face detection
OUTPUT_DIR=./output
BASE_URL=http://localhost:8000/output

# Logging
LOGGING_LEVEL=INFO

# Persistence
SAVE_MODE=cloud # "local" or "cloud"

# S3 Config
AWS_ACCESS_KEY_ID=EXAMPLEKEY12345
AWS_SECRET_ACCESS_KEY=EXAMPLESECRETKEY67890
AWS_REGION=eu-west-2
S3_BUCKET_NAME=my-facecount-bucket

# PostgreSQL
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/facecountdb

# RabbitMQ
RABBITMQ_URL=amqp://user:password@localhost:5672/facecount_vhost

# WebSocket Server
WSS_SERVER=wss://localhost:8083/api/ws
RETRY_WSS_CONNECT_DELAY=10
```

---

## 🐳 Running with Docker

```bash
docker build -t human-face-count-api .
docker run -p 8000:8000 --env-file .env human-face-count-api
```

This will install all dependencies, expose port **8000**, and run the app via `./run.sh`.

---

## 📜 License
MIT © 2025 — Neptune AI Labs
