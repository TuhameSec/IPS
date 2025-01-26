import face_recognition
import cv2
import requests
from database import connect_to_db
from encryption import encrypt_data
from logging_config import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import closing

def analyze_image(image, progress_callback=None):

    try:
        if progress_callback:
            progress_callback(10)  

        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        if not face_encodings:
            if progress_callback:
                progress_callback(100)  
            return None

        if progress_callback:
            progress_callback(30) 

        results = []
        db = connect_to_db()

        with ThreadPoolExecutor() as executor:
            futures = []
            for face_encoding in face_encodings:
                encrypted_face_encoding = encrypt_data(str(face_encoding))

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
                result += (ip,)  

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