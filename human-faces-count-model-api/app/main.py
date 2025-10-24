from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from  app.routes.faces_routes import router
from config.base_config import OUTPUT_DIR
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.openapi.docs import get_swagger_ui_html
from config.logging.file_logging import setup_logging
from config.logging.logging_middleware import RequestLoggingMiddleware
from config.persistence.postgres_db import engine, Base
from app.websockets.websocket_connect import WebSocketManager
import threading


os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(title="AI – Face Count API",
    version="1.0.0",
    description="""
        This API provides **real-time face counting detection** using base models YOLOv8/YOLOv12 models.  
        It performs per-crop adaptive enhancement, brightness and contrast correction, and 
        filters out false positives using heuristic analysis.

        ### Key Features:
        - 🧠 YOLO-based face count
        - ✨ Automatic brightness, contrast, and sharpness enhancement
        - 🎨 Supports grayscale, color, and dark images
        - ⚙️ REST API endpoint: `/faces`
        - 📤 Returns bounding boxes + annotated image URL

""",
    contact={
        "name": "Daniel Moshi",
        "url": "https://github.com/dmoshi",
        "email": "danielmoshi4m@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url=None,     # disable default Swagger
    redoc_url=None,   
    swagger_ui_parameters={"syntaxHighlight.theme": "github"},
    openapi_url="/openapi.json")


templates = Jinja2Templates(directory="app/templates")

# Mount static directory for assets and output
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")

# Include API routes
app.include_router(router)

# Add logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Setup global logging
logger = setup_logging(os.getenv("LOGGING_LEVEL", "INFO"))

@app.get("/apidocs", include_in_schema=False)
async def custom_swagger_ui(request: Request):
    """Serve custom Swagger UI from template"""
    swagger_html = get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="AI - Face Detection API Docs",
        swagger_favicon_url="/static/favicon.ico",
    ).body.decode("utf-8")
    
    return templates.TemplateResponse(
        "swagger.html", {"request": request, "swagger_html": swagger_html}
    )

# connectToWebsocketServer()
# listenWebSocketServerForMessageOrConnectionLoss()



@app.on_event("startup")
def startup_event():
    logger.info("🚀 Application started successfully.")
    with engine.begin() as conn:
        Base.metadata.create_all(bind=conn)
    logger.info("✅ Tables created (if not already existing)")
    WebSocketManager.connect()  # Start connection once
    threading.Thread(target=WebSocketManager.listen, daemon=True).start()


@app.on_event("shutdown")
def shutdown_event():
    logger.info("🛑 Application shutting down....")