import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import logging
from config.base_config import SAVE_MODE, OUTPUT_DIR, BASE_URL,S3_BUCKET_NAME,AWS_REGION
from config.persistence.aws_s3 import s3
from ..models.counts import FaceDetectionCount
from config.persistence.postgres_db import SyncSessionLocal
from urllib.parse import urlparse
from datetime import datetime
from io import BytesIO
import numpy as np
from .format_time import time_passed_str

import cv2

logger = logging.getLogger(__name__)

def save_image_and_metadata(frame, faces, count, original_url, customer_id, fileType):
    """Asynchronously save image + metadata depending on SAVE_MODE."""

    img_name = os.path.basename(urlparse(original_url).path)

    # Split by underscore, all image names in the URL contains imei, date and time
    parts = img_name.split("_")

    device_imei = parts[0]          # 350612079150221
    date_str = parts[1]             # 20251023
    month = date_str[4:6]           # 10
    time_str = parts[2]             # 143254

    dt = datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")

    if SAVE_MODE == "cloud":
        s3_url =  upload_to_s3(frame, customer_id + "/" + device_imei + "/" + month + "/" + date_str + "/" + img_name, fileType, dt)

        save_metadata_to_db(original_url, s3_url, faces, count,device_imei,dt, customer_id)

        return s3_url
    else:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        img_path = os.path.join(OUTPUT_DIR, img_name)
        cv2.imwrite(img_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        return f"{BASE_URL}/{img_name}"

def save_metadata_to_db(image_url, annotated_url, faces, count, imei, dt, cust_id):
    """Store detection metadata asynchronously."""

    session = SyncSessionLocal()

    try:
            record = FaceDetectionCount.from_detection(
                original_image_url=image_url,
                annotated_image_url=annotated_url,
                face_count= count,
                device_imei=imei,
                customer_id=cust_id,
                datetime=dt,
                faces_data=faces
            )
            session.add(record)
            session.commit()
            logger.info("Saved face count metadata to PostgreSQL.")
    except Exception as e:
            session.rollback()
            logger.error(f"Failed to save metadata to database  {type(e).__name__} - {e}")

def upload_to_s3(frame: np.ndarray, object_name: str, fileType: str, dt: datetime) -> str:
    """Uploads a BytesIO object to S3 asynchronously and returns its public URL."""
    try:

        bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        success, encoded_image = cv2.imencode(".jpg", bgr_frame) # only JPG for now
        if not success:
            raise ValueError("Failed to encode frame as JPEG")

        file_obj = BytesIO(encoded_image.tobytes())
        file_obj.seek(0)
        
        s3.put_object(
                Body=file_obj,
                Bucket=S3_BUCKET_NAME,
                Key=object_name,
                ContentType=fileType
            )

        url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
        timePassed = time_passed_str(dt, datetime.utcnow())
        logger.info(f"Uploaded to S3: {url}")
        return url, timePassed

    except Exception as e:
        logger.error(f"Failed to upload to S3  {type(e).__name__} - {e}")
        return None