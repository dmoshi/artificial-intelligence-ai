import hashlib
from sqlalchemy import Column, String, Integer, JSON, DateTime
from config.persistence.postgres_db import Base

def hash_url(url: str) -> str:
    """Return a deterministic short hash for a given URL."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]  # 16 hex chars = 8 bytes

class FaceDetectionCount(Base):
    __tablename__ = "face_detection_counts"

    id = Column(String, primary_key=True, index=True)
    original_image_url = Column(String, nullable=False)
    annotated_image_url = Column(String, nullable=False)
    face_count = Column(Integer, nullable=False)
    device_imei = Column(String, nullable=False)
    customer_id = Column(String, nullable=False)
    datetime = Column(DateTime, nullable=False)
    faces_data = Column(JSON, nullable=False)

    @classmethod
    def from_detection(cls, original_image_url, annotated_image_url, face_count,
                       device_imei, customer_id, datetime, faces_data):
        """Factory method to create instance with hashed ID."""
        return cls(
            id=hash_url(original_image_url),
            original_image_url=original_image_url,
            annotated_image_url=annotated_image_url,
            face_count=face_count,
            device_imei=device_imei,
            customer_id=customer_id,
            datetime=datetime,
            faces_data=faces_data
        )
