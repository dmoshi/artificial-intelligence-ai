# app/models/face.py

from pydantic import BaseModel, Field
from typing import List


class FaceBox(BaseModel):
    bbox: List[int] = Field(
        ...,
        description="Bounding box of the detected face in [x, y, width, height] format.",
        example=[120, 80, 60, 60],
    )
    confidence: float = Field(
        ...,
        description="Confidence score of the detected face (0–1).",
        example=0.97,
    )


class FaceCountResponse(BaseModel):
    faces: List[FaceBox] = Field(..., description="List of detected faces.")
    count: int = Field(..., description="Total number of detected faces.", example=2)
    annotated_image_url: str = Field(
        ...,
        description="URL of the annotated image containing bounding boxes.",
        example="https://api.example.com/images/face_annotated.jpg",
    )

