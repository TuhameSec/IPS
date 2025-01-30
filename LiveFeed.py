import cv2
from mtcnn import MTCNN
from ImageAnalysis import analyze_image
from logging_config import configure_logging
logger = configure_logging()
def analyze_live_feed():
    cap = cv2.VideoCapture(0)  #الكاميرا الرئيسية (0)
    if not cap.isOpened():
        logger.error("Unable to access the camera.")
        return

    detector = MTCNN()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            logger.error("Failed to capture frame from camera.")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #الكشف عن الوجوه
        faces = detector.detect_faces(frame_rgb)
        for face in faces:
            x, y, width, height = face["box"]
            keypoints = face["keypoints"]
            
            cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
            
            for point in keypoints.values():
                cv2.circle(frame, point, 5, (255, 0, 0), -1)
            
            face_crop = frame[y:y+height, x:x+width]
            if face_crop.size > 0:
                result = analyze_image(face_crop)
                
                if result:
                    name, age, nationality, crime, danger_level, ip = result
                    display_text = f"{name} - {danger_level}"
                    cv2.putText(frame, display_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
        cv2.imshow("Live Camera Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    analyze_live_feed()
