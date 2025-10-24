from app.celery_app import celery_app
import cv2
import traceback
from ..helpers.load_image_from_url import load_image_from_url_safe
from ..helpers.filter_faces import is_likely_face
from ..helpers.image_enhancer import enhance_face_crop
from ..helpers.persistence import save_image_and_metadata
from app.helpers.persistence import save_image_and_metadata
from config.base_config import model, IMG_SIZE, CONF_THRESH, IOU_THRESH, DEVICE
from fastapi import HTTPException
import logging
from ..websockets.relay_count import send_json_message



logger = logging.getLogger(__name__)

@celery_app.task(name="save_image_and_metadata_task")
def save_image_and_metadata_task(original_url, customer_id, fileType, target_session):
    """Runs model inference and metadata persistence asynchronously inside Celery."""

      # Securely load image
    frame = load_image_from_url_safe(original_url)

    frame = enhance_face_crop(frame)

    # Run model inference
    try:
        results = model.predict(
            source=frame,
            imgsz=IMG_SIZE,
            conf=CONF_THRESH,
            iou=IOU_THRESH,
            device=DEVICE,
            verbose=False,
        )
    except Exception as e:
        logger.exception(f"Model inference failed. {type(e).__name__} - {e}")
        raise HTTPException(status_code=500, detail=f"Model inference failed: {type(e).__name__} - {e}")

    # Process detections
    output = {"faces": [], "count": 0}
    annotated = frame.copy()

    try:
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            confs = result.boxes.conf.cpu().numpy()

            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = map(int, box)
                conf = float(confs[i])

                h_img, w_img = frame.shape[:2]
                x1c, y1c = max(0, x1), max(0, y1)
                x2c, y2c = min(w_img, x2), min(h_img, y2)
                if x2c <= x1c or y2c <= y1c:
                    continue

                face_crop = frame[y1c:y2c, x1c:x2c]
                if face_crop.size == 0:
                    continue

                enhanced_crop = enhance_face_crop(face_crop)
                if not is_likely_face(enhanced_crop, conf):
                    continue
                
                cv2.rectangle(annotated, (x1c, y1c), (x2c, y2c), (0, 255, 0), 2)
                cv2.putText(
                    annotated,
                    f"{conf:.2f}",
                    (x1c, y1c - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )

                output["faces"].append(
                    {"bbox": [x1c, y1c, x2c - x1c, y2c - y1c], "confidence": round(conf, 2)}
                )

        output["count"] = len(output["faces"])

    except Exception as e:
        logger.error(f"Error during result processing {type(e).__name__} - {e}")
        raise HTTPException(status_code=500, detail=f"Error processing detection results: {type(e).__name__} - {e}")
    
    # save annotated image and its metadata to s3 and postgres

    try:
        annotated_url, time_passed = save_image_and_metadata(annotated, output["faces"], output["count"], original_url, customer_id, fileType)
        logger.info(f"[Celery] Saved metadata for {original_url}")
    except Exception as e:
        logger.error(f"[Celery] Failed saving metadata for {original_url}: {type(e).__name__} - {e}")
        traceback.print_exc()
    
    # Push face count and annotated image URL to websocket server for mobile app live occupancy

    try:
        payload = {
            "action": "relay_message",
            "target_session": target_session,
            "misc": {
                "action": "face_count",
                "count": output["count"],
                "annotated_url": annotated_url if annotated_url is not None else original_url,
                "original_url": original_url,
                "time_passed": time_passed
            }
        
        }
        send_json_message(payload)

        logger.info(f"[Celery] Face count relayed for {target_session}")
    except Exception as e:
        logger.error(f"[Celery] Failed to relay face count for {target_session}: {type(e).__name__} - {e}")
        traceback.print_exc()