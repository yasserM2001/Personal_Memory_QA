import cv2
from face_detection import FaceDetector
import os

class FaceExtractor:
    def __init__(self, output_folder='detected_faces'):
        self.face_detector = FaceDetector()
        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)
        
    def extract_faces(self, image_path):
        faces = self.face_detector.detect_faces(image_path)
        image = cv2.imread(image_path)
        for i, face in enumerate(faces):
            x, y, width, height = face['box']
            face_image = image[y:y+height, x:x+width]
            face_path = os.path.join(self.output_folder, f"{os.path.basename(image_path)}_face_{i}.jpg")
            cv2.imwrite(face_path, face_image)
        return len(faces)

