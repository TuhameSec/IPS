"""Module for analyzing images to detect and identify faces."""
import cv2
import numpy as np
from mtcnn import MTCNN
from database_manager import connect_to_db, search_database
from encryption import encrypt_data
from logging_config import configure_logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Callable, Optional

logger = configure_logging()

def initialize_detector() -> MTCNN:
    """Initialize MTCNN face detector with optimized settings.

    Returns:
        Configured MTCNN detector.
    """
    return MTCNN(min_face_size=40, scale_factor=0.8)

def detect_faces(detector: MTCNN, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """Detect faces in an image.

    Args:
        detector: MTCNN face detector.
        image: Input image as NumPy array.

    Returns:
        List of face bounding boxes (top, right, bottom, left).
    """
    try:
        image_small = cv2.resize(image, (320, 240))
        image_rgb = cv2.cvtColor(image_small, cv2.COLOR_BGR2RGB)
        detections = detector.detect_faces(image_rgb)
        scale_x, scale_y = image.shape[1] / 320, image.shape[0] / 240
        return [(int(d["box"][1] * scale_y), int((d["box"][0] + d["box"][2]) * scale_x),
                 int((d["box"][1] + d["box"][3]) * scale_y), int(d["box"][0] * scale_x))
                for d in detections]
    except Exception as e:
        logger.error(f"Face detection error: {e}")
        return []

def analyze_image(image: np.ndarray, progress_callback: Optional[Callable[[int], None]] = None,
                  offline_mode: bool = False) -> Optional[List[Tuple[str, int, str, str, str]]]:
    """Analyze an image to identify faces.

    Args:
        image: Input image as NumPy array.
        progress_callback: Optional callback for progress updates.
        offline_mode: Whether to use offline database.

    Returns:
        List of identified individuals (name, age, nationality, crime, danger_level) or None.
    """
    try:
        if not isinstance(image, np.ndarray) or image.size == 0:
            logger.error("Invalid image data")
            return None

        if progress_callback:
            progress_callback(10)

        detector = initialize_detector()
        face_locations = detect_faces(detector, image)
        if not face_locations:
            if progress_callback:
                progress_callback(100)
            return None

        if progress_callback:
            progress_callback(30)

        db = connect_to_db() if not offline_mode else None
        results = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = []
            for top, right, bottom, left in face_locations:
                face_crop = image[top:bottom, left:right]
                if face_crop.size == 0:
                    continue
                face_encoding = cv2.resize(face_crop, (32, 32)).flatten()
                encrypted_encoding = encrypt_data(str(face_encoding.tolist()))
                futures.append(executor.submit(search_database, db, encrypted_encoding, offline_mode))

            for future in futures:
                result = future.result()
                if result:
                    results.append(result)

        if progress_callback:
            progress_callback(100)
        return results if results else None
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        if progress_callback:
            progress_callback(100)
        return None