import cv2
from fastapi import APIRouter, Form,HTTPException
from fastapi.responses import JSONResponse
from config.base_config import model, IMG_SIZE, CONF_THRESH, IOU_THRESH, DEVICE, OUTPUT_DIR, BASE_URL
import logging
from ..models.faces import FaceCountResponse
from app.tasks.face_tasks import save_image_and_metadata_task


logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/faces",
    summary="Detect and count faces in an image",
    tags=["Face Counter"],
    response_model=FaceCountResponse,
    responses={
        200: {
            "description": "Faces detected successfully",
            "content": {
                "application/json": {
                    "example": {
                        "faces": [
                            {"bbox": [120, 80, 60, 60], "confidence": 0.97},
                            {"bbox": [250, 100, 58, 58], "confidence": 0.92},
                        ],
                        "count": 2,
                        "annotated_image_url": "https://api.example.com/images/abcd1234.jpg",
                    }
                }
            },
        },
        400: {"description": "Bad Request"},
        422: {"description": "Unprocessable Entity"},
        500: {"description": "Internal Server Error"},
    },
)

def count_faces(image_url: str = Form(..., description="Public URL of the image to analyze."), 
                customer_id: str = Form(..., description="Customer id"), 
                target_session: str = Form(..., description="WSS socket session to send face counts"),
                fileType: str = Form(..., description="Image Type")):
    """
    Detect faces in the provided image URL.
    Returns bounding boxes, confidence scores, and a URL to the annotated image.
    """
    logger.info(f"Processing image from URL: {image_url}")

    # Save annotated image
    try:


        # Send async task to Celery
        save_image_and_metadata_task.delay(
            image_url,
            customer_id,
            fileType,
            target_session
        )

        logger.info(" ai - image queued for processing " + image_url)
        return JSONResponse({"message": "OK", "status": " ai - image queued for processing " + image_url})

    except Exception as e:
        logger.exception(f"Error saving annotated image {type(e).__name__} - {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save annotated image: {e}")
