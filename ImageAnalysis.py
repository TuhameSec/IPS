import cv2
import numpy as np
import requests
from mtcnn import MTCNN
from database import connect_to_db
from encryption import encrypt_data
from logging_config import configure_logging
logger = configure_logging()
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import closing

def load_face_detection_model():
    return MTCNN()

def detect_faces(detector, image):
    face_locations = []
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  
    detections = detector.detect_faces(image_rgb)

    for face in detections:
        x, y, width, height = face["box"]
        startX, startY, endX, endY = x, y, x + width, y + height
        face_locations.append((startY, endX, endY, startX))  

    return face_locations

def analyze_image(image, progress_callback=None):
    try:
        if progress_callback:
            progress_callback(10)  

        detector = load_face_detection_model()

        face_locations = detect_faces(detector, image)

        if not face_locations:
            if progress_callback:
                progress_callback(100)  
            return None

        if progress_callback:
            progress_callback(30)  

        results = []
        db = connect_to_db()

        with ThreadPoolExecutor() as executor:
            futures = []
            for face_location in face_locations:
                (top, right, bottom, left) = face_location
                face_image = image[top:bottom, left:right]

                face_encoding = cv2.resize(face_image, (64, 64)) 
                encrypted_face_encoding = encrypt_data(str(face_encoding.tolist()))

                futures.append(executor.submit(search_database, db, encrypted_face_encoding))

            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)

        if progress_callback:
            progress_callback(80)  

        if results:
            ip = requests.get("https://api.ipify.org").text
            for result in results:
                result += (ip,)  # إضافة IP 

            if progress_callback:
                progress_callback(100)  
            return results
        else:
            if progress_callback:
                progress_callback(100)  
            return None

    except Exception as e:
        logger.error(f"An error occurred while analyzing the image: {e}")
        if progress_callback:
            progress_callback(100)  
        return None

def search_database(db, encrypted_face_encoding):
    try:
        with closing(db.cursor()) as cursor:
            cursor.execute("SELECT * FROM wanted_individuals WHERE face_encoding = %s", (encrypted_face_encoding,))
            result = cursor.fetchone()

            if result:
                name, age, nationality, crime, danger_level = result[1:6]
                logger.info(f"Match found: {name}, Crime: {crime}, Danger Level: {danger_level}")
                return name, age, nationality, crime, danger_level
            else:
                return None
    except Exception as e:
        logger.error(f"Database search error: {e}")
        return None
