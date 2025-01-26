# live feed
# تحليل الفيديو المباشر

import cv2
import face_recognition
from IPS.ImageAnalysis import analyze_image
from logging_config import logger

def analyze_live_feed():
    cap = cv2.VideoCapture(0)  # استخدام الكاميرا الرئيسية (0)
    if not cap.isOpened():
        logger.error("Unable to access the camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            logger.error("Failed to capture frame from camera.")
            break

        face_locations = face_recognition.face_locations(frame)
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            face_encoding = face_recognition.face_encodings(frame, [(top, right, bottom, left)])[0]
            result = analyze_image(frame, face_encoding)
            if result:
                name, age, nationality, crime, danger_level, ip = result
                cv2.putText(frame, f"{name} - {danger_level}", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow("Live Camera Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()