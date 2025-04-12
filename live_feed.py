"""Module for real-time face detection and identification via live camera feed."""
import cv2
import threading
import queue
import time
from mtcnn import MTCNN
from image_processor import analyze_image
from logging_config import configure_logging
from typing import List

logger = configure_logging()
FRAME_WIDTH, FRAME_HEIGHT = 640, 480
FRAME_QUEUE = queue.Queue(maxsize=5)

def capture_frames(cap: cv2.VideoCapture, stop_event: threading.Event, cam_idx: int) -> None:
    """Capture frames from a camera.

    Args:
        cap: OpenCV VideoCapture object.
        stop_event: Event to signal thread termination.
        cam_idx: Camera index for logging.
    """
    retry_count = 0
    max_retries = 3
    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            retry_count += 1
            if retry_count >= max_retries:
                logger.error(f"Camera {cam_idx} failed after {max_retries} retries")
                break
            time.sleep(1)
            continue
        retry_count = 0
        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
        if not FRAME_QUEUE.full():
            FRAME_QUEUE.put((frame, cam_idx))
        time.sleep(0.03)
    cap.release()

def process_frames(detector: MTCNN, stop_event: threading.Event, offline_mode: bool) -> None:
    """Process captured frames to detect and identify faces.

    Args:
        detector: MTCNN face detector.
        stop_event: Event to signal thread termination.
        offline_mode: Whether to use offline database.
    """
    fps_start = time.time()
    frame_count = 0
    while not stop_event.is_set():
        if not FRAME_QUEUE.empty():
            frame, cam_idx = FRAME_QUEUE.get()
            faces = detector.detect_faces(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            for face in faces:
                x, y, width, height = face["box"]
                cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
                face_crop = frame[y:y + height, x:x + width]
                if face_crop.size > 0:
                    result = analyze_image(face_crop, offline_mode=offline_mode)
                    if result:
                        name, age, nationality, crime, danger_level = result
                        display_text = f"{name} - {danger_level}"
                        cv2.putText(frame, display_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.6, (0, 255, 0), 2)

            frame_count += 1
            if time.time() - fps_start >= 1:
                fps = frame_count / (time.time() - fps_start)
                cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0, 255, 255), 2)
                frame_count = 0
                fps_start = time.time()

            cv2.imshow(f"Camera {cam_idx}", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                stop_event.set()
                break
    cv2.destroyAllWindows()

def analyze_live_feed(camera_indices: List[int], offline_mode: bool = False) -> None:
    """Start live feed analysis for face detection and identification.

    Args:
        camera_indices: List of camera indices to process.
        offline_mode: Whether to use offline database.
    """
    caps = [cv2.VideoCapture(i) for i in camera_indices]
    detector = MTCNN()
    stop_event = threading.Event()

    for cap in caps:
        if not cap.isOpened():
            logger.error(f"Unable to access camera {caps.index(cap)}")
            continue
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    threads = [threading.Thread(target=capture_frames, args=(cap, stop_event, i))
               for i, cap in enumerate(caps)]
    for t in threads:
        t.daemon = True
        t.start()

    process_frames(detector, stop_event, offline_mode)
    stop_event.set()
    for cap in caps:
        cap.release()
    cv2.destroyAllWindows()