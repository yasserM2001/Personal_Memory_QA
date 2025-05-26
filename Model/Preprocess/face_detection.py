from mtcnn import MTCNN
import cv2

class FaceDetector:
    def __init__(self):
        self.detector = MTCNN()
        
    def detect_faces(self, image_path):
        image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
        faces = self.detector.detect_faces(image)
        return faces